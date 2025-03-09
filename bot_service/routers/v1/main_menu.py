from bot_service.schemas.main_menu import MainMenuResponse
from bot_service.services.main_menu_service import (
    MainMenuService,
    get_main_menu_service,
)
from fastapi import APIRouter, Depends


router = APIRouter()


@router.get(
    "/{bot_id}",
    response_model=MainMenuResponse,
    status_code=200,
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
