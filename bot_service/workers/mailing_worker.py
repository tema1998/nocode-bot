import asyncio
import logging
from datetime import datetime
from typing import Optional

from bot_service.core.configs import config
from bot_service.repositories.message_broker_repository import (
    RabbitMQRepository,
)
from bot_service.services.bot_service import BotService, get_bot_service
from telegram import Bot as TelegramBot


logger = logging.getLogger(__name__)


class MailingWorker:
    def __init__(self):
        self.broker_repo = RabbitMQRepository(
            connection_string=config.rabbitmq_url
        )
        self.bot_service: Optional[BotService] = None  # type: ignore
        self._is_running = False

    async def start(self):
        """Start the worker to process mailing tasks"""
        try:
            await self.broker_repo.connect()
            self.bot_service = await get_bot_service()
            self._is_running = True

            logger.info("Mailing worker started, waiting for tasks...")
            await self.broker_repo.consume(
                queue_name="mailing_tasks", callback=self.process_task
            )
        except asyncio.CancelledError:
            logger.info("Mailing worker received cancellation signal")
        except Exception as e:
            logger.error(f"Mailing worker failed: {str(e)}")
            raise
        finally:
            await self._cleanup()

    async def stop(self):
        """Stop the worker gracefully"""
        if not self._is_running:
            return

        self._is_running = False
        logger.info("Stopping mailing worker...")
        await self._cleanup()

    async def _cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self.broker_repo, "close"):
                await self.broker_repo.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def process_task(self, task: dict):
        """Process single mailing task"""
        mailing_id = task["mailing_id"]
        logger.info(f"Processing mailing task {mailing_id}")

        try:
            result = await self.execute_mailing(
                bot_id=task["bot_id"],
                bot_token=task["bot_token"],
                message=task["message"],
                chunk_size=task["chunk_size"],
            )
            logger.info(f"Mailing {mailing_id} completed: {result}")
        except Exception as e:
            logger.error(f"Mailing {mailing_id} failed: {str(e)}")

    async def send_to_user(
        self, bot_token: str, user_id: int, message: str
    ) -> bool:
        """Send message to single user"""
        try:
            bot = TelegramBot(token=bot_token)
            await bot.send_message(chat_id=user_id, text=message)
            return True
        except Exception as e:
            logger.error(f"Failed to send to user {user_id}: {str(e)}")
            return False

    async def execute_mailing(
        self, bot_id: int, bot_token: str, message: str, chunk_size: int
    ) -> dict:
        """Execute mailing for all bot users"""
        total_users = await self.bot_service.get_bot_users_count(bot_id)  # type: ignore
        offset = 0

        while self._is_running:
            users = await self.bot_service.get_bot_users_chunk(  # type: ignore
                bot_id, offset, chunk_size
            )
            if not users:
                break

            await asyncio.gather(
                *(
                    self.send_to_user(bot_token, int(user.user_id), message)
                    for user in users
                ),
                return_exceptions=True,
            )

            offset += chunk_size

        return {
            "status": "completed",
            "total_users": total_users,
            "completed_at": datetime.utcnow().isoformat(),
        }
