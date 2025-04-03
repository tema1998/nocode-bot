import logging
from typing import Any, List, Optional

from bot_service.core.configs import config
from bot_service.models import BotUser
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)


logger = logging.getLogger(__name__)


class BotService:

    def __init__(self, db_repository: PostgresAsyncRepository):
        self.db_repository = db_repository

    async def get_bot_users_count(self, bot_id: int) -> int:
        """
        Get total count of users for a specific bot.

        Args:
            bot_id (int): ID of the target bot

        Returns:
            int: Total number of users subscribed to the bot
        """
        return await self.db_repository.count_by_query(
            BotUser, "bot_id", bot_id
        )

    async def get_bot_users_chunk(
        self, bot_id: int, offset: int = 0, limit: int = 100
    ) -> Optional[List[Any]]:
        """
        Retrieve a paginated chunk of bot users.

        Args:
            bot_id (int): ID of the target bot
            offset (int): Pagination offset
            limit (int): Maximum number of users to retrieve

        Returns:
            List[BotUser]: List of user records
        """
        return await self.db_repository.fetch_by_query_with_pagination(
            BotUser, "bot_id", bot_id, skip=offset, limit=limit
        )


async def get_bot_service() -> BotService:

    return BotService(db_repository=PostgresAsyncRepository(dsn=config.dsn))
