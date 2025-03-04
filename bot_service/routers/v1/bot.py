import secrets

from bot_service.models.bot import (
    Bot,
)
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from bot_service.schemas.bot import (
    BotCreate,
    BotCreateResponse,
    BotGetResponse,
    BotPatchRequest,
    BotPatchResponse,
)
from bot_service.utils.bot import get_bot_name, get_bot_username
from bot_service.utils.webhook import reset_webhook, set_webhook
from fastapi import APIRouter, Depends, HTTPException


router = APIRouter()


@router.get(
    "/{bot_id}",
    response_model=BotGetResponse,
    summary="Get bot details by ID",
    description="Retrieve details of a bot by its ID, including its active status, token, and name.",
    response_description="The bot's details, including active status, token, and name.",
    status_code=200,
)
async def get_bot(
    bot_id: int,
    repository: PostgresAsyncRepository = Depends(get_repository),
) -> BotGetResponse:
    """
    Retrieve details of a bot by its ID.

    Args:
        bot_id (int): The ID of the bot to retrieve.
        repository (PostgresAsyncRepository): The repository for database operations.

    Returns:
        BotGetResponse: The bot's details, including active status, token, and name.

    Raises:
        HTTPException: If the bot is not found (404) or if there is an error fetching the bot's name (500).
    """
    # Fetch the bot from the database
    bot = await repository.fetch_by_id(Bot, bot_id)

    # If the bot is not found, raise a 404 error
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")

    try:
        # Get the bot's name using the Telegram API
        bot_name = await get_bot_name(bot.token)
    except Exception as e:
        # If there is an error fetching the bot's name, raise a 500 error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch bot name from Telegram: {str(e)}",
        )

    # Return the bot's details in the response
    return BotGetResponse(
        is_active=bot.is_active,
        token=bot.token,
        username=bot.username,
        name=bot_name,  # Include the bot's name
    )


@router.patch(
    "/{bot_id}",
    response_model=BotPatchResponse,
    summary="Update bot details by ID",
    description="""Update bot details such as `is_active` and `token`.
    If the token is updated, the webhook is reconfigured, and the previous bot's webhook is reset.""",
    response_description="The updated bot details, including active status, token, username, and name.",
    status_code=200,
)
async def update_bot(
    bot_id: int,
    bot_update: BotPatchRequest,
    repository: PostgresAsyncRepository = Depends(get_repository),
) -> BotPatchResponse:
    """
    Update bot details by ID.

    Args:
        bot_id (int): The ID of the bot to update.
        bot_update (BotPatchRequest): The data to update the bot with.
        repository (PostgresAsyncRepository): The repository for database operations.

    Returns:
        BotPatchResponse: The updated bot details, including active status, token, username, and name.

    Raises:
        HTTPException: If the bot is not found (404) or if there is an error updating the bot (500).
    """
    # Fetch the bot from the database
    bot = await repository.fetch_by_id(Bot, bot_id)

    # If the bot is not found, raise a 404 error
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Update is_active if provided
    if bot_update.is_active is not None:
        bot.is_active = bot_update.is_active

    # Update token if provided and it's different from the current token
    if bot_update.token is not None and bot.token != bot_update.token:
        try:
            # Reconfigure the webhook with the new token
            await set_webhook(
                bot_id=bot_id,
                bot_token=bot_update.token,
                bot_secret_token=bot.secret_token,
            )

            # Reset the webhook for the previous bot (if it exists)
            await reset_webhook(bot_token=bot.token)

            # Update the token in the database
            bot.token = bot_update.token

            # Fetch the new bot's username using the updated token
            bot.username = await get_bot_username(bot_update.token)
        except Exception as e:
            # If there is an error, raise a 500 error
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update bot token: {str(e)}",
            )

    # Save the updated bot to the database
    await repository.update(bot)

    # Fetch the bot's name using the updated token
    try:
        bot_name = await get_bot_name(bot.token)
    except Exception as e:
        # If there is an error fetching the bot's name, raise a 500 error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch bot name: {str(e)}",
        )

    # Return the updated bot details
    return BotPatchResponse(
        is_active=bot.is_active,
        token=bot.token,
        username=bot.username,
        name=bot_name,
    )


@router.post(
    "/",
    summary="Create a new bot",
    description="Generates a secret token and creates a new bot in the database, then sets a webhook for the new bot.",
    response_model=BotCreateResponse,
    response_description="The created bot ID and name.",
    status_code=201,
)
async def add_bot(
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
    db_bot = Bot(
        token=bot.token, secret_token=secret_token, username=bot_username
    )
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

    return BotCreateResponse(
        id=inserted_bot.id, username=inserted_bot.username
    )
