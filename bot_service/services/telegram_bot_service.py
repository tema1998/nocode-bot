import logging
import secrets
from typing import Any, Dict

from bot_service.models.bot import Bot
from bot_service.models.main_menu import MainMenu
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from bot_service.repositories.telegram_api_repository import (
    TelegramApiRepository,
    get_telegram_api_repository,
)
from fastapi import Depends, HTTPException


logger = logging.getLogger(__name__)


class TelegramBotService:
    """
    Service for managing Telegram bot operations, including database and Telegram API interactions.
    """

    def __init__(
        self,
        db_repository: PostgresAsyncRepository,
        tg_api_repository: TelegramApiRepository,
    ):
        """
        Initialize the TelegramBotService.

        Args:
            db_repository (PostgresAsyncRepository): The repository for database operations.
            tg_api_repository (TelegramApiRepository): The repository for Telegram API interactions.
        """
        self.db_repository = db_repository
        self.tg_api_repository = tg_api_repository

    async def get_bot_details(self, bot_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a bot by its ID.

        Args:
            bot_id (int): The ID of the bot to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the bot's details, including:
                - is_active (bool): Whether the bot is active.
                - token (str): The bot's token.
                - username (str): The bot's username.
                - name (str): The bot's name.
                - default_reply (str): The bot's default reply message.

        Raises:
            HTTPException: If the bot is not found or if there is an error fetching the bot's name.
        """
        bot = await self.db_repository.fetch_by_id(Bot, bot_id)

        if bot is None:
            logger.error(f"Bot with ID {bot_id} not found.")
            raise HTTPException(status_code=404, detail="Bot not found")

        try:
            bot_name = await self.tg_api_repository.get_bot_name(bot.token)
        except Exception as e:
            logger.error(
                f"Failed to fetch bot name from Telegram for token {bot.token}: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch bot name from Telegram: {str(e)}",
            )

        return {
            "is_active": bot.is_active,
            "token": bot.token,
            "username": bot.username,
            "name": bot_name,
            "default_reply": bot.default_reply,
        }

    async def update_bot(
        self, bot_id: int, bot_update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a bot's details.

        Args:
            bot_id (int): The ID of the bot to update.
            bot_update (Dict[str, Any]): A dictionary containing the fields to update:
                - is_active (Optional[bool]): Whether the bot should be active.
                - default_reply (Optional[str]): The bot's default reply message.
                - token (Optional[str]): The bot's new token.

        Returns:
            Dict[str, Any]: A dictionary containing the updated bot's details:
                - is_active (bool): Whether the bot is active.
                - token (str): The bot's token.
                - username (str): The bot's username.
                - default_reply (str): The bot's default reply message.

        Raises:
            HTTPException: If the bot is not found or if there is an error updating the bot.
        """
        bot = await self.db_repository.fetch_by_id(Bot, bot_id)

        if bot is None:
            logger.error(f"Bot with ID {bot_id} not found for updating.")
            raise HTTPException(status_code=404, detail="Bot not found")

        if bot_update.get("is_active") is not None:
            bot.is_active = bot_update["is_active"]

        if bot_update.get("default_reply") is not None:
            bot.default_reply = bot_update["default_reply"]

        if bot_update.get("token") is not None:
            try:
                await self.tg_api_repository.set_webhook(
                    bot_id=bot_id,
                    bot_token=bot_update["token"],
                    bot_secret_token=bot.secret_token,
                )
                await self.tg_api_repository.reset_webhook(bot_token=bot.token)
                bot.token = bot_update["token"]
                bot.username = await self.tg_api_repository.get_bot_username(
                    bot_update["token"]
                )
            except Exception as e:
                logger.error(
                    f"Failed to update bot token for bot ID {bot_id}: {e}"
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to update bot token: {str(e)}",
                )

        await self.db_repository.update(bot)

        return {
            "is_active": bot.is_active,
            "token": bot.token,
            "username": bot.username,
            "default_reply": bot.default_reply,
        }

    async def delete_bot(self, bot_id: int) -> None:
        """
        Delete a bot by its ID.

        Args:
            bot_id (int): The ID of the bot to delete.

        Raises:
            HTTPException: If the bot is not found or if there is an error deleting the bot.
        """
        bot = await self.db_repository.fetch_by_id(Bot, bot_id)

        if bot is None:
            logger.error(f"Bot with ID {bot_id} not found for deleting.")
            raise HTTPException(status_code=404, detail="Bot not found")

        try:
            await self.tg_api_repository.reset_webhook(bot_token=bot.token)
        except Exception as e:
            logger.error(f"Failed to reset webhook for bot ID {bot_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to reset webhook: {str(e)}",
            )

        # Delete bot's main menu
        bot_main_menu = await self.db_repository.fetch_by_query_one(
            MainMenu, {"bot_id": bot_id}
        )
        await self.db_repository.delete(
            MainMenu, bot_main_menu.id  # type:ignore
        )

        await self.db_repository.delete(Bot, bot_id)

        return None

    async def create_bot(self, bot_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new bot.

        Args:
            bot_data (Dict[str, Any]): A dictionary containing the bot's data:
                - token (str): The bot's token.

        Returns:
            Dict[str, Any]: A dictionary containing the created bot's details:
                - id (int): The ID of the created bot.
                - username (str): The bot's username.

        Raises:
            HTTPException: If the bot token is invalid or if there is an error setting the webhook.
        """
        secret_token = secrets.token_hex(16)

        try:
            bot_username = await self.tg_api_repository.get_bot_username(
                bot_data["token"]
            )
        except Exception as e:
            logger.error(f"Invalid bot token provided in create_bot: {e}")
            raise HTTPException(
                status_code=400,
                detail="Bot token is not valid.",
            )

        db_bot = Bot(
            token=bot_data["token"],
            secret_token=secret_token,
            username=bot_username,
        )
        bot = await self.db_repository.insert(db_bot)
        bot_main_menu = await self.db_repository.insert(
            MainMenu(bot_id=bot.id)
        )
        try:
            await self.tg_api_repository.set_webhook(
                bot_id=bot.id,
                bot_token=bot_data["token"],
                bot_secret_token=secret_token,
            )
        except Exception as e:
            await self.db_repository.delete(Bot, bot.id)
            await self.db_repository.delete(MainMenu, bot_main_menu.id)
            logger.error(f"Failed to set webhook for bot ID {bot.id}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to set webhook: {str(e)}",
            )

        return {
            "id": bot.id,
            "username": bot.username,
        }


def get_telegram_bot_service(
    db_repository: PostgresAsyncRepository = Depends(get_repository),
    tg_api_repository: TelegramApiRepository = Depends(
        get_telegram_api_repository
    ),
) -> TelegramBotService:
    """
    Dependency function to get an instance of TelegramBotService.

    Args:
        db_repository (PostgresAsyncRepository): The repository for database operations.
        tg_api_repository (TelegramApiRepository): The repository for Telegram API interactions.

    Returns:
        TelegramBotService: An instance of TelegramBotService.
    """
    return TelegramBotService(db_repository, tg_api_repository)
