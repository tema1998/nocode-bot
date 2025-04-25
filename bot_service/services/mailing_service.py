import logging
from datetime import datetime
from typing import Optional

from bot_service.core.configs import config
from bot_service.models.bot import Bot
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from bot_service.repositories.message_broker_repository import (
    RabbitMQRepository,
)
from bot_service.services.bot_service import BotService, get_bot_service
from fastapi import HTTPException


logger = logging.getLogger(__name__)


class MailingService:
    def __init__(
        self,
        db_repository: PostgresAsyncRepository,
        bot_service: BotService,
        broker_repository: RabbitMQRepository,
    ):
        self.db_repository = db_repository
        self.bot_service = bot_service
        self.broker_repository = broker_repository

    async def create_mailing(
        self,
        bot_id: int,
        message: str,
        chunk_size: int = 30,
    ) -> dict:
        """Create and enqueue mailing task"""
        bot = await self.db_repository.fetch_by_id(Bot, bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        mailing_task = {
            "mailing_id": int(datetime.utcnow().timestamp()),
            "bot_id": bot_id,
            "bot_token": bot.token,
            "message": message,
            "chunk_size": chunk_size,
        }

        await self.broker_repository.publish(
            queue_name="mailing_tasks", message=mailing_task
        )

        return {
            "mailing_id": mailing_task["mailing_id"],
            "status": "queued",
            "bot_id": bot_id,
        }


async def get_mailing_service() -> Optional[MailingService]:
    """Dependency injection factory for MailingService."""
    broker_repo = None
    try:
        broker_repo = RabbitMQRepository(connection_string=config.rabbitmq_url)
        await broker_repo.connect()

        mailing_service = MailingService(
            db_repository=PostgresAsyncRepository(dsn=config.dsn),
            bot_service=await get_bot_service(),
            broker_repository=broker_repo,
        )

        return mailing_service

    except Exception as e:
        if broker_repo:
            await broker_repo.close()
        logger.error(f"Failed to create mailing service: {str(e)}")
        raise

    finally:
        await broker_repo.close()  # type: ignore
