import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

from bot_service.core.configs import config
from bot_service.models.bot import Bot
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from bot_service.services.bot_service import BotService, get_bot_service
from fastapi import HTTPException
from telegram import Bot as TelegramBot


logger = logging.getLogger(__name__)


class MailingService:
    """
    Service for managing message broadcasts to bot users.

    Provides functionality to:
    - Create and manage message broadcasts
    - Track delivery status in real-time
    - Handle large user bases with chunked processing
    - Maintain delivery rate within Telegram API limits
    """

    def __init__(
        self, db_repository: PostgresAsyncRepository, bot_service: BotService
    ):
        """
        Initialize the mailing service with database repository.

        Args:
            db_repository (PostgresAsyncRepository): Repository for database operations
        """
        self.db_repository = db_repository
        # Dictionary to track active mailing tasks {mailing_id: asyncio.Task}
        self.active_tasks: Dict[int, asyncio.Task] = {}
        self.bot_service: BotService = bot_service

    async def send_to_user(
        self,
        bot_token: str,
        user_id: int,
        message: str,
        parse_mode: Optional[str] = None,
    ) -> bool:
        """
        Deliver a message to a single user.

        Args:
            bot_token (str): Bot's Telegram API token
            user_id (int): Target user's Telegram ID
            message (str): Content to deliver
            parse_mode (Optional[str]): Telegram parse mode (HTML/Markdown)

        Returns:
            bool: True if delivery succeeded, False otherwise
        """
        try:
            bot = TelegramBot(token=bot_token)
            await bot.send_message(
                chat_id=user_id, text=message, parse_mode=parse_mode
            )
            return True
        except Exception as e:
            # Log full error but don't fail the entire mailing
            logging.error(f"Failed to send to user {user_id}: {str(e)}")
            return False

    async def create_mailing(
        self,
        bot_id: int,
        message: str,
        parse_mode: Optional[str] = None,
        chunk_size: int = 30,
        delay: float = 1.0,
    ) -> Dict:
        """
        Create and start a new mailing campaign.

        Args:
            bot_id (int): Target bot ID
            message (str): Message content to broadcast
            parse_mode (Optional[str]): Telegram parse mode
            chunk_size (int): Number of users to process simultaneously
            delay (float): Seconds between chunk processing

        Returns:
            Dict: Mailing status with initial details

        Raises:
            HTTPException: If bot is not found
        """
        # Verify bot exists before starting mailing
        bot = await self.db_repository.fetch_by_id(Bot, bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        # Create and track the mailing task
        task = asyncio.create_task(
            self._execute_mailing(
                bot_id=bot_id,
                bot_token=bot.token,
                message=message,
                parse_mode=parse_mode,
                chunk_size=chunk_size,
                delay=delay,
            )
        )

        # Store task reference for status tracking
        mailing_id = id(task)
        self.active_tasks[mailing_id] = task
        # Auto-cleanup when task completes
        task.add_done_callback(
            lambda t: self.active_tasks.pop(mailing_id, None)
        )

        return {
            "mailing_id": mailing_id,
            "status": "started",
            "started_at": datetime.utcnow().isoformat(),
            "bot_id": bot_id,
        }

    async def _execute_mailing(
        self,
        bot_id: int,
        bot_token: str,
        message: str,
        parse_mode: Optional[str],
        chunk_size: int,
        delay: float,
    ) -> Dict:
        """
        Execute the mailing process in background.

        Args:
            bot_id (int): Target bot ID
            bot_token (str): Bot's Telegram API token
            message (str): Content to broadcast
            parse_mode (Optional[str]): Telegram parse mode
            chunk_size (int): Users per processing batch
            delay (float): Seconds between batches

        Returns:
            Dict: Final mailing statistics
        """
        total_users = await self.bot_service.get_bot_users_count(bot_id)
        success = failed = offset = 0

        while True:
            users = await self.bot_service.get_bot_users_chunk(
                bot_id, offset, chunk_size
            )
            if not users:
                break  # No more users to process

            # Process current batch concurrently
            batch_results = await asyncio.gather(
                *(
                    self.send_to_user(
                        bot_token, int(user.id), message, parse_mode
                    )
                    for user in users
                ),
                return_exceptions=True,
            )

            # Update success/failure counters
            success += sum(1 for r in batch_results if r is True)
            failed += sum(1 for r in batch_results if r is False)

            offset += chunk_size
            await asyncio.sleep(delay)  # Rate limiting

        return {
            "status": "completed",
            "total_users": total_users,
            "success": success,
            "failed": failed,
            "completed_at": datetime.utcnow().isoformat(),
        }

    async def get_mailing_status(self, mailing_id: int) -> Dict:
        """
        Retrieve current status of a mailing campaign.

        Args:
            mailing_id (int): ID of the mailing to check

        Returns:
            Dict: Status information with:
                - "not_found" if ID invalid
                - "in_progress" if running
                - "completed" with results if finished
                - "failed" with error if errored
        """
        task = self.active_tasks.get(mailing_id)
        if not task:
            return {"status": "not_found"}

        if task.done():
            try:
                return {"status": "completed", "result": task.result()}
            except Exception as e:
                return {"status": "failed", "error": str(e)}
        return {"status": "in_progress"}

    async def cancel_mailing(self, mailing_id: int) -> bool:
        """
        Attempt to cancel an active mailing.

        Args:
            mailing_id (int): ID of mailing to cancel

        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        task = self.active_tasks.get(mailing_id)
        if task and not task.done():
            task.cancel()
            try:
                await task  # Handle cancellation properly
                return True
            except asyncio.CancelledError:
                return True
        return False


async def get_mailing_service() -> MailingService:
    """
    Dependency injection factory for MailingService.

    Returns:
        MailingService: Configured mailing service instance
    """
    return MailingService(
        db_repository=PostgresAsyncRepository(dsn=config.dsn),
        bot_service=await get_bot_service(),
    )
