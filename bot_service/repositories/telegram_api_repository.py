import logging
from typing import Any, Dict, Optional

import telegram
from bot_service.core.configs import config
from fastapi import HTTPException
from telegram.error import TelegramError
from telegram.ext import Application


logger = logging.getLogger(__name__)


class TelegramApiRepository:
    """
    Repository for interacting with the Telegram API.
    """

    async def set_webhook(
        self, bot_id: int, bot_token: str, bot_secret_token: str
    ) -> None:
        """
        Sets up a webhook for the Telegram bot.

        Args:
            bot_id (int): The unique identifier of the bot.
            bot_token (str): The Telegram bot token.
            bot_secret_token (str): The secret token for securing the webhook.

        Raises:
            HTTPException: If there is an error setting up the webhook.
        """
        try:
            # Construct the webhook URL
            webhook_url = f"{config.webhook_url}/{bot_id}"

            # Initialize the Telegram bot application
            application = Application.builder().token(bot_token).build()

            # Set the webhook with the specified URL and secret token
            await application.bot.set_webhook(
                url=webhook_url,
                secret_token=bot_secret_token,
            )
        except TelegramError as e:
            # Handle Telegram-specific errors
            logger.error(
                f"Telegram error while setting webhook for bot {bot_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set webhook due to a Telegram error: {str(e)}",
            )
        except Exception as e:
            # Handle any other unexpected errors
            logger.error(
                f"Unexpected error while setting webhook for bot {bot_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while setting the webhook: {str(e)}",
            )

    async def reset_webhook(self, bot_token: str) -> None:
        """
        Reset a webhook for the Telegram bot.

        Args:
            bot_token (str): The Telegram bot token.
        """
        try:
            # Fake webhook URL to bot
            webhook_url = "https://com.com/api/v1/blocked"

            # Initialize the Telegram bot application
            application = Application.builder().token(bot_token).build()

            # Set the webhook with the specified URL and secret token
            await application.bot.set_webhook(
                url=webhook_url,
                secret_token="secret",
            )
        except Exception as e:
            logger.error(
                f"Error resetting webhook for bot with token {bot_token}: {str(e)}"
            )
            pass

    async def get_bot_username(self, bot_token: str) -> str | None:
        """
        Retrieves the bot's username.

        Args:
            bot_token (str): The Telegram bot token.

        Returns:
            str: The username of the bot (e.g., "@my_bot").

        Raises:
            HTTPException: If the bot token is invalid or the request fails.
        """
        try:

            application = Application.builder().token(bot_token).build()

            # Get bot info from TG
            bot_info = await application.bot.get_me()
            username = bot_info.username

            return username
        except Exception as e:
            logger.error(
                f"Failed to fetch username for bot with token {bot_token}: {str(e)}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch bot username: {str(e)}",
            )

    async def get_bot_name(self, bot_token: str) -> str:
        """
        Retrieves the bot's name.

        Args:
            bot_token (str): The Telegram bot token.

        Returns:
            str: The name of the bot.

        Raises:
            HTTPException: If the bot token is invalid or the request fails.
        """
        try:

            application = Application.builder().token(bot_token).build()

            # Get bot info from TG
            bot_info = await application.bot.get_me()
            name = bot_info.first_name

            return name
        except Exception as e:
            logger.error(
                f"Failed to fetch name for bot with token {bot_token}: {str(e)}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch bot name: {str(e)}",
            )

    async def get_user_info(
        self, bot_token: str, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves Telegram user information including profile details and avatar.

        Args:
            bot_token: Telegram bot token for API access
            user_id: Telegram user ID to look up

        Returns:
            Dictionary with user information or None if failed
        """
        try:
            bot = telegram.Bot(token=bot_token)

            user = await bot.get_chat(user_id)

            user_info = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "photo_url": None,
                "profile_link": f"tg://user?id={user.id}",
            }

            # Get profile photo if available
            try:
                photos = await bot.get_user_profile_photos(user_id, limit=1)
                if photos and photos.photos:
                    file = await bot.get_file(photos.photos[0][-1].file_id)
                    user_info["photo_url"] = file.file_path
            except telegram.error.TelegramError as photo_error:
                logger.debug(
                    f"Profile photo unavailable for user {user_id}: {photo_error}"
                )

            return user_info

        except telegram.error.TelegramError as tg_error:
            logger.warning(
                f"Telegram API error for user {user_id}: {tg_error}"
            )
        except Exception as e:
            logger.error(
                f"Error getting user info {user_id}: {e}", exc_info=True
            )

        return None


def get_telegram_api_repository() -> TelegramApiRepository:
    """
    Dependency function to get an instance of TelegramApiRepository.

    Returns:
        TelegramApiRepository: An instance of TelegramApiRepository.
    """
    return TelegramApiRepository()
