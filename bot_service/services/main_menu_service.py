import logging
from typing import Any, Dict

from bot_service.models.bot import MainMenu
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from bot_service.repositories.telegram_api_repository import (
    TelegramApiRepository,
    get_telegram_api_repository,
)
from bot_service.schemas.main_menu import ButtonResponse
from fastapi import Depends, HTTPException


logger = logging.getLogger(__name__)


class MainMenuService:
    """
    Service for managing main menu of the bot, including database and Telegram API interactions.
    """

    def __init__(
        self,
        db_repository: PostgresAsyncRepository,
        tg_api_repository: TelegramApiRepository,
    ):
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

        main_menu = await self.db_repository.fetch_by_query_one_joinedload(
            MainMenu, {"bot_id": bot_id}, "buttons"
        )

        if main_menu is None:
            logger.error(f"Bot with ID {bot_id} doesn't have main menu.")
            raise HTTPException(
                status_code=404, detail="Bot's main menu not found"
            )

        main_menu_buttons = [
            ButtonResponse(
                id=button.id,
                button_text=button.button_text,
                reply_text=button.reply_text,
            )
            for button in main_menu.buttons
        ]
        return {
            "welcome_message": main_menu.welcome_message,
            "buttons": main_menu_buttons,
        }


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
        TelegramBotService: An instance of MainMenuService.
    """
    return MainMenuService(db_repository, tg_api_repository)
