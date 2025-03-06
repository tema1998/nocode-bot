from bot_service.repositories.telegram_bot_repository import (
    TelegramBotRepository,
    get_telegram_bot_repository,
)
from bot_service.schemas.bot import (
    BotCreate,
    BotCreateResponse,
    BotGetResponse,
    BotPatchRequest,
    BotPatchResponse,
)
from fastapi import APIRouter, Depends, status


router = APIRouter()


@router.get(
    "/{bot_id}",
    response_model=BotGetResponse,
    summary="Get bot details by ID",
    description="Retrieve details of a bot by its ID, including its active status, token and name.",
    response_description="The bot's details, including active status, token, and name.",
    status_code=200,
)
async def get_bot(
    bot_id: int,
    bot_repository: TelegramBotRepository = Depends(
        get_telegram_bot_repository
    ),
) -> BotGetResponse:
    """
    Retrieve details of a bot by its ID.

    Args:
        bot_id (int): The ID of the bot to retrieve.
        bot_repository (TelegramBotRepository): The repository for bot-related operations.

    Returns:
        BotGetResponse: The bot's details, including active status, token, and name.

    Raises:
        HTTPException: If the bot is not found or if there is an error fetching the bot's name.
    """
    bot_details = await bot_repository.get_bot_details(bot_id)
    return BotGetResponse(**bot_details)


@router.delete(
    "/{bot_id}",
    summary="Delete a bot by ID",
    description="Delete a bot by its ID. This operation is irreversible.",
    response_description="Confirmation of the bot deletion.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_bot(
    bot_id: int,
    bot_repository: TelegramBotRepository = Depends(
        get_telegram_bot_repository
    ),
) -> None:
    """
    Delete a bot by its ID.

    Args:
        bot_id (int): The ID of the bot to delete.
        bot_repository (TelegramBotRepository): The repository for bot-related operations.

    Returns:
        None: Returns no content on successful deletion.

    Raises:
        HTTPException: If the bot is not found or if there is an error during deletion.
    """
    await bot_repository.delete_bot(bot_id)

    # Return no content on successful deletion
    return None


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
    bot_repository: TelegramBotRepository = Depends(
        get_telegram_bot_repository
    ),
) -> BotPatchResponse:
    """
    Update bot details by ID.

    Args:
        bot_id (int): The ID of the bot to update.
        bot_update (BotPatchRequest): The data to update the bot with.
        bot_repository (TelegramBotRepository): The repository for bot-related operations.

    Returns:
        BotPatchResponse: The updated bot details, including active status, token, username, and name.

    Raises:
        HTTPException: If the bot is not found or if there is an error updating the bot.
    """
    updated_bot = await bot_repository.update_bot(
        bot_id, bot_update.model_dump()
    )
    return BotPatchResponse(**updated_bot)


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
    bot_repository: TelegramBotRepository = Depends(
        get_telegram_bot_repository
    ),
):
    """
    Create a new bot.

    Args:
        bot (BotCreate): The data to create the bot with.
        bot_repository (TelegramBotRepository): The repository for bot-related operations.

    Returns:
        BotCreateResponse: The created bot details, including ID and username.

    Raises:
        HTTPException: If the bot token is invalid or if there is an error creating the bot.
    """
    created_bot = await bot_repository.create_bot(bot.model_dump())
    return BotCreateResponse(**created_bot)
