import secrets

from bot_service.models.bot import Bot
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from bot_service.repositories.telegram_api_repository import (
    TelegramApiRepository,
)
from fastapi import Depends, HTTPException


class TelegramBotRepository:
    """
    Repository for handling bot-related operations, combining database and Telegram API interactions.
    """

    def __init__(
        self,
        db_repository: PostgresAsyncRepository,
        tg_api_repository: TelegramApiRepository,
    ):
        self.db_repository = db_repository
        self.tg_api_repository = tg_api_repository

    async def get_bot_details(self, bot_id: int):
        """
        Retrieve bot details by ID.

        Args:
            bot_id (int): The ID of the bot to retrieve.

        Returns:
            dict: The bot's details, including active status, token, username, and name.

        Raises:
            HTTPException: If the bot is not found or if there is an error fetching the bot's name.
        """
        # Fetch the bot from the database
        bot = await self.db_repository.fetch_by_id(Bot, bot_id)

        # If the bot is not found, raise a 404 error
        if bot is None:
            raise HTTPException(status_code=404, detail="Bot not found")

        try:
            # Get the bot's name using the Telegram API
            bot_name = await self.tg_api_repository.get_bot_name(bot.token)
        except Exception as e:
            # If there is an error fetching the bot's name, raise a 500 error
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch bot name from Telegram: {str(e)}",
            )

        return {
            "is_active": bot.is_active,
            "token": bot.token,
            "username": bot.username,
            "name": bot_name,
        }

    async def update_bot(self, bot_id: int, bot_update: dict):
        """
        Update bot details by ID.

        Args:
            bot_id (int): The ID of the bot to update.
            bot_update (dict): The data to update the bot with.

        Returns:
            dict: The updated bot details, including active status, token, username, and name.

        Raises:
            HTTPException: If the bot is not found or if there is an error updating the bot.
        """
        # Fetch the bot from the database
        bot = await self.db_repository.fetch_by_id(Bot, bot_id)

        # If the bot is not found, raise a 404 error
        if bot is None:
            raise HTTPException(status_code=404, detail="Bot not found")

        # Update is_active if provided
        if bot_update.get("is_active") is not None:
            bot.is_active = bot_update["is_active"]

        # Update token if provided and it's different from the current token
        if (
            bot_update.get("token") is not None
            and bot.token != bot_update["token"]
        ):
            try:
                # Reconfigure the webhook with the new token
                await self.tg_api_repository.set_webhook(
                    bot_id=bot_id,
                    bot_token=bot_update["token"],
                    bot_secret_token=bot.secret_token,
                )

                # Reset the webhook for the previous bot (if it exists)
                await self.tg_api_repository.reset_webhook(bot_token=bot.token)

                # Update the token in the database
                bot.token = bot_update["token"]

                # Fetch the new bot's username using the updated token
                bot.username = await self.tg_api_repository.get_bot_username(
                    bot_update["token"]
                )
            except Exception as e:
                # If there is an error, raise a 500 error
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to update bot token: {str(e)}",
                )

        # Save the updated bot to the database
        await self.db_repository.update(bot)

        # Fetch the bot's name using the updated token
        try:
            bot_name = await self.tg_api_repository.get_bot_name(bot.token)
        except Exception as e:
            # If there is an error fetching the bot's name, raise a 500 error
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch bot name: {str(e)}",
            )

        return {
            "is_active": bot.is_active,
            "token": bot.token,
            "username": bot.username,
            "name": bot_name,
        }

    async def create_bot(self, bot_data: dict):
        """
        Create a new bot.

        Args:
            bot_data (dict): The data to create the bot with.

        Returns:
            dict: The created bot details, including ID and username.

        Raises:
            HTTPException: If the bot token is invalid or if there is an error creating the bot.
        """
        # Generate a secret token
        secret_token = secrets.token_hex(16)

        # Get bot username
        try:
            bot_username = await self.tg_api_repository.get_bot_username(
                bot_data["token"]
            )
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Bot token is not valid.",
            )

        # Create a bot in the database
        db_bot = Bot(
            token=bot_data["token"],
            secret_token=secret_token,
            username=bot_username,
        )
        inserted_bot = await self.db_repository.insert(db_bot)

        try:
            # Attempt to set a webhook for the newly created bot
            await self.tg_api_repository.set_webhook(
                bot_id=inserted_bot.id,
                bot_token=bot_data["token"],
                bot_secret_token=secret_token,
            )
        except Exception as e:
            # If setting the webhook fails, delete the bot from the database
            await self.db_repository.delete(Bot, inserted_bot.id)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to set webhook: {str(e)}",
            )

        return {
            "id": inserted_bot.id,
            "username": inserted_bot.username,
        }


def get_telegram_bot_repository(
    db_repository: PostgresAsyncRepository = Depends(get_repository),
    tg_repository: TelegramApiRepository = Depends(TelegramApiRepository),
) -> TelegramBotRepository:
    return TelegramBotRepository(db_repository, tg_repository)
