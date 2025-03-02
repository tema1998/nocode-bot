import secrets

from bot_service.models.bot import (
    Bot,
    Button,
    Command,
    Funnel,
    FunnelStep,
    UserState,
)
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from bot_service.schemas.bot import (
    BotCreate,
    BotCreateResponse,
    ButtonCreate,
    CommandCreate,
    FunnelCreate,
    FunnelStepCreate,
)
from bot_service.utils.bot import get_bot_username
from bot_service.utils.webhook import set_webhook
from fastapi import APIRouter, Depends, HTTPException
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
)


router = APIRouter()


@router.post(
    "/bots/",
    summary="Create a new bot",
    description="Generates a secret token and creates a new bot in the database, then sets a webhook for the new bot.",
    response_model=BotCreateResponse,
    response_description="The created bot ID and name.",
    status_code=201,
)
async def create_bot(
    bot: BotCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Generate a secret token
    secret_token = secrets.token_hex(16)  # Generating a random token

    # Get bot username
    try:
        bot_username = await get_bot_username(
            bot_token=bot.token,
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Bot token is not valid.",
        )

    # Create a bot in the database
    db_bot = Bot(token=bot.token, secret_token=secret_token, name=bot_username)
    inserted_bot = await repository.insert(db_bot)

    try:
        # Attempt to set a webhook for the newly created bot
        await set_webhook(
            bot_id=inserted_bot.id,
            bot_token=bot.token,
            bot_secret_token=secret_token,
        )
    except Exception as e:
        # If setting the webhook fails, delete the bot from the database
        await repository.delete(Bot, inserted_bot.id)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to set webhook: {str(e)}",
        )

    return BotCreateResponse(id=inserted_bot.id, name=inserted_bot.name)


@router.post(
    "/commands/",
    summary="Add a command to a bot",
    description="Creates a new command associated with a bot in the database.",
    response_description="The created command object",
    status_code=201,
)
async def add_command(
    command: CommandCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Create a command object
    db_command = Command(
        command=command.command,
        response=command.response,
        bot_id=command.bot_id,
    )
    # Insert the command into the database
    inserted_command = await repository.insert(db_command)
    return inserted_command


@router.post(
    "/funnels/",
    summary="Create a new funnel",
    description="Creates a new funnel associated with a bot in the database.",
    response_description="The created funnel object",
    status_code=201,
)
async def create_funnel(
    funnel: FunnelCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Create a funnel in the database
    db_funnel = Funnel(name=funnel.name, bot_id=funnel.bot_id)
    inserted_funnel = await repository.insert(db_funnel)
    return inserted_funnel


@router.post(
    "/funnels/{funnel_id}/steps/",
    summary="Add a step to a funnel",
    description="Creates a new step associated with a specific funnel in the database.",
    response_description="The created funnel step object",
    status_code=201,
)
async def add_funnel_step(
    funnel_id: int,
    step: FunnelStepCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Create a funnel step object
    db_step = FunnelStep(funnel_id=funnel_id, text=step.text)
    # Insert the funnel step into the database
    inserted_step = await repository.insert(db_step)
    return inserted_step


@router.post(
    "/buttons/",
    summary="Create a button",
    description="Creates a new button associated with a specific step in a funnel.",
    response_description="The created button object",
    status_code=201,
)
async def create_button(
    button: ButtonCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Create a button object
    db_button = Button(
        step_id=button.step_id,
        text=button.text,
        next_step_id=button.next_step_id,
    )
    # Insert the button into the database
    inserted_button = await repository.insert(db_button)
    return inserted_button


@router.post(
    "/webhook/{bot_id}",
    summary="Handle incoming webhook update",
    description="Processes incoming updates from a bot's webhook, managing user state and funnel steps.",
    response_description="Webhook handling status",
    status_code=200,
)
async def webhook(
    bot_id: int,
    update_data: dict,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Fetch the bot from the database using the bot_id
    bot = await repository.fetch_by_id(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Create an instance of Application using the bot's token
    application = Application.builder().token(bot.token).build()

    # Convert JSON to Update object
    update = Update.de_json(update_data, application.bot)

    # Extract user ID from the update object
    user_id = update.message.from_user.id  # type: ignore

    # Get the current state of the user
    user_state = await repository.fetch_by_query(
        UserState, {"user_id": user_id, "bot_id": bot_id}
    )
    user_state = user_state[0] if user_state else None

    # If the user has an active funnel, proceed with it
    if user_state:
        current_step = await repository.fetch_by_id_joinedload(
            FunnelStep, user_state.current_step_id, "buttons"
        )
        if not current_step:
            raise HTTPException(status_code=404, detail="Step not found")

        # Process the current step
        if update.message:  # type: ignore
            # If the user clicked a button
            button_text = update.message.text  # type: ignore
            button = next(
                (b for b in current_step.buttons if b.text == button_text),
                None,
            )

            if button:
                # Move to the next step
                next_step = await repository.fetch_by_id_joinedload(
                    FunnelStep, button.next_step_id, "buttons"
                )
                if not next_step:
                    raise HTTPException(
                        status_code=404, detail="Next step not found"
                    )

                # Update user's state
                user_state.current_step_id = next_step.id
                await repository.update(user_state)

                # Send the next step's message
                await update.message.reply_text(  # type: ignore
                    next_step.text,
                    reply_markup=ReplyKeyboardMarkup(
                        [[KeyboardButton(b.text)] for b in next_step.buttons],
                        resize_keyboard=True,
                    ),
                )
            else:
                # If the button is not found, send the current step's message
                await update.message.reply_text(  # type: ignore
                    current_step.text,
                    reply_markup=ReplyKeyboardMarkup(
                        [
                            [KeyboardButton(b.text)]
                            for b in current_step.buttons
                        ],
                        resize_keyboard=True,
                    ),
                )
    else:
        # If the user has no active funnel, start a new one
        # Fetch the first funnel associated with the bot
        funnels = await repository.fetch_by_query(Funnel, {"bot_id": bot_id})
        if not funnels:
            await update.message.reply_text("No available funnels.")  # type: ignore
            return

        first_funnel = funnels[0]
        first_step = await repository.fetch_by_query(
            FunnelStep, {"funnel_id": first_funnel.id}
        )
        if not first_step:
            await update.message.reply_text("Funnel not configured.")  # type: ignore
            return

        # Create a new user state
        user_state = UserState(
            user_id=user_id,
            bot_id=bot_id,
            funnel_id=first_funnel.id,
            current_step_id=first_step[0].id,
        )
        await repository.insert(user_state)

        # Send the first step's message
        await update.message.reply_text(  # type: ignore
            first_step[0].text,
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(b.text)] for b in first_step[0].buttons],
                resize_keyboard=True,
            ),
        )

    return {"status": "ok"}
