from bot_service.schemas.main_menu import (
    MainMenuResponse,
    PatchWelcomeMessageRequest,
    PatchWelcomeMessageResponse,
)
from bot_service.services.main_menu_service import (
    MainMenuService,
    get_main_menu_service,
)
from fastapi import APIRouter, Depends
from starlette import status


router = APIRouter()


@router.get(
    "/{bot_id}",
    response_model=MainMenuResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Main Menu and Buttons by Bot ID",
    description="Retrieves the main menu and associated buttons for a specific bot using its ID. "
    "The response includes the welcome message and a list of buttons with their text and reply text.",
    response_description="A JSON object containing the welcome message and a list of buttons.",
)
async def get_main_menu(
    bot_id: int,
    main_menu_service: MainMenuService = Depends(get_main_menu_service),
):
    """
    Fetch the main menu and associated buttons for a specific bot.

    Args:
        bot_id (int): The unique identifier of the bot.
        main_menu_service (MainMenuService): The service responsible for fetching main menu data.

    Returns:
        MainMenuResponse: A response model containing the welcome message and a list of buttons.

    Raises:
        HTTPException: If the main menu or buttons for the specified bot ID are not found.
    """
    main_menu_with_welcome_message = (
        await main_menu_service.main_menu_with_welcome_message(bot_id)
    )
    return MainMenuResponse(**main_menu_with_welcome_message)


@router.patch(
    "/{bot_id}",
    status_code=status.HTTP_200_OK,
    summary="Update the welcome message for a bot",
    description="Updates the welcome message of the main menu for a specific bot. "
    "The new welcome message is provided in the request body.",
    response_model=PatchWelcomeMessageResponse,
    response_description="A confirmation message indicating the welcome message was updated.",
)
async def update_welcome_message(
    bot_id: int,
    request: PatchWelcomeMessageRequest,
    main_menu_service: MainMenuService = Depends(get_main_menu_service),
):
    """
    Update the welcome message for a bot.

    Args:
        bot_id (int): The unique identifier of the bot.
        request (PatchWelcomeMessageRequest): The request body containing the new welcome message.
        main_menu_service (MainMenuService): The service responsible for updating the welcome message.

    Returns:
        PatchWelcomeMessageResponse: Bot ID and updated welcome message

    Raises:
        HTTPException: If the main menu for the specified bot ID is not found.
    """
    updated_welcome_message = await main_menu_service.update_welcome_message(
        bot_id, request.welcome_message
    )

    return updated_welcome_message
