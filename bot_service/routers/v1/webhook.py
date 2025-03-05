from bot_service.core.configs import config
from bot_service.models.bot import (
    Bot,
    FunnelStep,
    UserState,
)
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from fastapi import APIRouter, Depends, HTTPException
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
)


router = APIRouter()


@router.post(
    "/{bot_id}",
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

    if not bot.is_active:
        raise HTTPException(status_code=403, detail="Bot is deactivated.")

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
        await update.message.reply_text(bot.default_reply if bot.default_reply else config.bot_default_reply)  # type: ignore

    return {"status": "ok"}
