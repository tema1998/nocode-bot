from bot_service.schemas.bot import (
    BotCreate,
    BotCreateResponse,
    BotGetResponse,
    BotPatchRequest,
    BotPatchResponse,
    BotUserSchema,
    PaginatedBotUsersResponse,
)
from bot_service.services.bot_service import BotService, get_bot_service
from bot_service.services.telegram_bot_service import (
    TelegramBotService,
    get_telegram_bot_service,
)
from fastapi import APIRouter, Depends, Query, status


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
    bot_service: TelegramBotService = Depends(get_telegram_bot_service),
) -> BotGetResponse:
    """
    Retrieve details of a bot by its ID.

    Args:
        bot_id (int): The ID of the bot to retrieve.
        bot_service (TelegramBotService): The service for bot-related operations.

    Returns:
        BotGetResponse: The bot's details, including active status, token, and name.

    Raises:
        HTTPException: If the bot is not found or if there is an error fetching the bot's name.
    """
    bot_details = await bot_service.get_bot_details(bot_id)
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
    bot_service: TelegramBotService = Depends(get_telegram_bot_service),
) -> None:
    """
    Delete a bot by its ID.

    Args:
        bot_id (int): The ID of the bot to delete.
        bot_service (TelegramBotService): The service for bot-related operations.

    Returns:
        None: Returns no content on successful deletion.

    Raises:
        HTTPException: If the bot is not found or if there is an error during deletion.
    """
    await bot_service.delete_bot(bot_id)
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
    bot_service: TelegramBotService = Depends(get_telegram_bot_service),
) -> BotPatchResponse:
    """
    Update bot details by ID.

    Args:
        bot_id (int): The ID of the bot to update.
        bot_update (BotPatchRequest): The data to update the bot with.
        bot_service (TelegramBotService): The service for bot-related operations.

    Returns:
        BotPatchResponse: The updated bot details, including active status, token, username, and name.

    Raises:
        HTTPException: If the bot is not found or if there is an error updating the bot.
    """
    updated_bot = await bot_service.update_bot(bot_id, bot_update.model_dump())
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
    bot_service: TelegramBotService = Depends(get_telegram_bot_service),
):
    """
    Create a new bot.

    Args:
        bot (BotCreate): The data to create the bot with.
        bot_service (TelegramBotService): The service for bot-related operations.

    Returns:
        BotCreateResponse: The created bot details, including ID and username.

    Raises:
        HTTPException: If the bot token is invalid or if there is an error creating the bot.
    """
    created_bot = await bot_service.create_bot(bot.model_dump())
    return BotCreateResponse(**created_bot)


@router.get("/{bot_id}/list/", response_model=PaginatedBotUsersResponse)
async def get_bot_users(
    bot_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=500),
    bot_service: BotService = Depends(get_bot_service),
):
    """
    Retrieve paginated list of users for a specific bot.

    Args:
        bot_id (int): ID of the bot to fetch users for
        offset (int): Pagination offset (default: 0)
        limit (int): Number of users per page (default: 100, max: 500)
        bot_service (BotService): Injected bot service instance

    Returns:
        PaginatedBotUsersResponse: Contains:
            - users: List of user objects for current page
            - total_count: Total number of users for this bot
            - offset: Current pagination offset
            - limit: Current page size
            - has_more: Flag indicating more users available
    """
    # Get total count first
    total_count = await bot_service.get_bot_users_count(bot_id)

    # Get users chunk with proper None handling
    users = await bot_service.get_bot_users_chunk(bot_id, offset, limit)

    # Convert users to schemas - handle None case
    user_schemas = []
    if users is not None:  # Explicit None check
        user_schemas = [BotUserSchema.model_validate(user) for user in users]

    return PaginatedBotUsersResponse(
        users=user_schemas,
        total_count=total_count,
        offset=offset,
        limit=limit,
        has_more=(offset + limit) < total_count,
    )
