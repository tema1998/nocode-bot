import logging
from typing import Any, Dict

from bot_service.models.bot import Button, MainMenu
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from bot_service.repositories.telegram_api_repository import (
    TelegramApiRepository,
    get_telegram_api_repository,
)
from bot_service.schemas.main_menu import (
    ButtonResponse,
    PatchWelcomeMessageResponse,
)
from fastapi import Depends, HTTPException


logger = logging.getLogger(__name__)


class MainMenuService:
    """
    Service for managing the main menu of a bot, including database and Telegram API interactions.
    """

    def __init__(
        self,
        db_repository: PostgresAsyncRepository,
        tg_api_repository: TelegramApiRepository,
    ) -> None:
        """
        Initialize the MainMenuService.

        Args:
            db_repository (PostgresAsyncRepository): The repository for database operations.
            tg_api_repository (TelegramApiRepository): The repository for Telegram API interactions.
        """
        self.db_repository = db_repository
        self.tg_api_repository = tg_api_repository

    async def main_menu_with_welcome_message(
        self, bot_id: int
    ) -> Dict[str, Any]:
        """
        Retrieve the main menu and its welcome message for a specific bot.

        Args:
            bot_id (int): The unique identifier of the bot.

        Returns:
            Dict[str, Any]: A dictionary containing the welcome message and a list of buttons.

        Raises:
            HTTPException: If the main menu for the specified bot ID is not found.
        """
        main_menu = await self.db_repository.fetch_by_query_one_joinedload(
            MainMenu, {"bot_id": bot_id}, "buttons"
        )

        if main_menu is None:
            logger.error(f"Bot with ID {bot_id} doesn't have a main menu.")
            raise HTTPException(
                status_code=404, detail="Bot's main menu not found"
            )

        main_menu_buttons = [
            ButtonResponse(
                id=button.id,
                bot_id=bot_id,
                button_text=button.button_text,
                reply_text=button.reply_text,
            )
            for button in main_menu.buttons
        ]
        return {
            "welcome_message": main_menu.welcome_message,
            "buttons": main_menu_buttons,
        }

    async def update_welcome_message(
        self, bot_id: int, welcome_message: str
    ) -> PatchWelcomeMessageResponse:
        """
        Update the welcome message of the main menu for a specific bot.

        Args:
            bot_id (int): The unique identifier of the bot.
            welcome_message (str): The new welcome message to set.


        Raises:
            HTTPException: If the main menu for the specified bot ID is not found.
        """
        main_menu = await self.db_repository.fetch_by_query_one_joinedload(
            MainMenu, {"bot_id": bot_id}, "buttons"
        )

        if main_menu is None:
            logger.error(f"Bot with ID {bot_id} doesn't have a main menu.")
            raise HTTPException(
                status_code=404, detail="Bot's main menu not found"
            )

        main_menu.welcome_message = welcome_message
        await self.db_repository.update(main_menu)

        return PatchWelcomeMessageResponse(
            bot_id=bot_id, welcome_message=welcome_message
        )

    async def create_main_menu_button(
        self, bot_id: int, button_text: str, reply_text: str
    ) -> ButtonResponse:
        """
        Create a new button for the main menu of a specific bot.

        Args:
            bot_id (int): The unique identifier of the bot to which the button belongs.
            button_text (str): The text displayed on the button.
            reply_text (str): The text sent as a reply when the button is clicked.

        Returns:
            ButtonResponse: A response model containing the details of the created button.

        Raises:
            HTTPException: If the main menu for the specified bot ID is not found.
        """

        main_menu = await self.db_repository.fetch_by_query_one_joinedload(
            MainMenu, {"bot_id": bot_id}, "buttons"
        )

        if main_menu is None:
            logger.error(f"Bot with ID {bot_id} doesn't have a main menu.")
            raise HTTPException(
                status_code=404, detail="Bot's main menu not found"
            )

        # Check if button text exists
        buttons_with_same_text = await self.db_repository.fetch_by_query(
            Button, {"bot_id": bot_id, "button_text": button_text}
        )
        if buttons_with_same_text:
            raise HTTPException(
                status_code=400,
                detail="A button with the same text already exists.",
            )

        button = Button(
            button_text=button_text,
            reply_text=reply_text,
            main_menu_id=main_menu.id,
            bot_id=bot_id,
        )

        await self.db_repository.insert(button)

        return ButtonResponse(
            id=int(button.id),
            bot_id=bot_id,
            button_text=button_text,
            reply_text=reply_text,
        )


def get_main_menu_service(
    db_repository: PostgresAsyncRepository = Depends(get_repository),
    tg_api_repository: TelegramApiRepository = Depends(
        get_telegram_api_repository
    ),
) -> MainMenuService:
    """
    Dependency function to get an instance of MainMenuService.

    Args:
        db_repository (PostgresAsyncRepository): The repository for database operations.
        tg_api_repository (TelegramApiRepository): The repository for Telegram API interactions.

    Returns:
        MainMenuService: An instance of MainMenuService.
    """
    return MainMenuService(db_repository, tg_api_repository)
