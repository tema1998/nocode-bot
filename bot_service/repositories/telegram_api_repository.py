from bot_service.core.configs import config
from fastapi import HTTPException
from telegram.error import TelegramError
from telegram.ext import Application


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
            webhook_url = f"{config.webhook_url}/api/v1/webhook/{bot_id}"

            # Initialize the Telegram bot application
            application = Application.builder().token(bot_token).build()

            # Set the webhook with the specified URL and secret token
            await application.bot.set_webhook(
                url=webhook_url,
                secret_token=bot_secret_token,
            )
        except TelegramError as e:
            # Handle Telegram-specific errors
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set webhook due to a Telegram error: {str(e)}",
            )
        except Exception as e:
            # Handle any other unexpected errors
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
            # Initialize the Telegram bot application
            application = Application.builder().token(bot_token).build()

            # Set the webhook with the specified URL and secret token
            await application.bot.set_webhook(
                url="https://reset-url.com/",
                secret_token="secret",
            )
        except Exception:
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
            bot_info = await application.bot.get_me()
            return bot_info.username
        except Exception as e:
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
            bot_info = await application.bot.get_me()
            return bot_info.first_name
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch bot name: {str(e)}",
            )
