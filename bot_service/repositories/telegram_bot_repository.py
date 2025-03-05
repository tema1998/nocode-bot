import logging
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


logger = logging.getLogger(__name__)


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
        }

    async def update_bot(self, bot_id: int, bot_update: dict):
        bot = await self.db_repository.fetch_by_id(Bot, bot_id)

        if bot is None:
            logger.error(f"Bot with ID {bot_id} not found for updating.")
            raise HTTPException(status_code=404, detail="Bot not found")

        if bot_update.get("is_active") is not None:
            bot.is_active = bot_update["is_active"]

        if (
            bot_update.get("token") is not None
            and bot.token != bot_update["token"]
        ):
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

        try:
            bot_name = await self.tg_api_repository.get_bot_name(bot.token)
        except Exception as e:
            logger.error(
                f"Failed to fetch bot name for token {bot.token}: {e}"
            )
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
        inserted_bot = await self.db_repository.insert(db_bot)

        try:
            await self.tg_api_repository.set_webhook(
                bot_id=inserted_bot.id,
                bot_token=bot_data["token"],
                bot_secret_token=secret_token,
            )
        except Exception as e:
            await self.db_repository.delete(Bot, inserted_bot.id)
            logger.error(
                f"Failed to set webhook for bot ID {inserted_bot.id}: {e}"
            )
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
