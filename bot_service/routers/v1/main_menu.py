from bot_service.schemas.main_menu import (
    ButtonCreateRequest,
    ButtonResponse,
    ButtonUpdateRequest,
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


@router.post(
    "/button",
    response_model=ButtonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new button for the main menu",
    description="Creates a new button for the main menu of a specific bot. "
    "The button text and reply text are provided in the request body.",
    response_description="The details of the created button.",
)
async def create_main_menu_button(
    request: ButtonCreateRequest,
    main_menu_service: MainMenuService = Depends(get_main_menu_service),
) -> ButtonResponse:
    """
    Create a new button for the main menu of a specific bot.

    Args:
        request (ButtonCreateRequest): The request body containing the bot ID, button text, and reply text.
        main_menu_service (MainMenuService): The service responsible for creating the button.

    Returns:
        ButtonResponse: A response model containing the details of the created button.

    Raises:
        HTTPException: If the main menu for the specified bot ID is not found.
    """

    button = await main_menu_service.create_main_menu_button(
        request.bot_id, request.button_text, request.reply_text
    )

    return button


@router.patch(
    "/button/{button_id}",
    response_model=ButtonResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a button in the main menu",
    description="Updates the text or reply text of a button in the main menu. "
    "Only the fields provided in the request body will be updated.",
    response_description="The details of the updated button.",
)
async def update_main_menu_button(
    button_id: int,
    request: ButtonUpdateRequest,
    main_menu_service: MainMenuService = Depends(get_main_menu_service),
) -> ButtonResponse:
    """
    Update a button in the main menu of a bot.

    Args:
        button_id (int): The unique identifier of the button to update.
        request (ButtonUpdateRequest): The request body containing the new button text and/or reply text.
        main_menu_service (MainMenuService): The service responsible for updating the button.

    Returns:
        ButtonResponse: A response model containing the details of the updated button.

    Raises:
        HTTPException: If the button with the specified ID is not found.
    """
    button = await main_menu_service.update_main_menu_button(
        button_id, request.button_text, request.reply_text
    )

    return button
