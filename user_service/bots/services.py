import json
import logging
from typing import Any, Dict, List, Optional, cast

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from requests.exceptions import RequestException


logger = logging.getLogger("bots")


class BotService:
    """Service class for interacting with the Bot API."""

    BASE_URL = settings.BOT_SERVICE_API_URL

    @classmethod
    def get_bot_details(cls, bot_id: int) -> Dict[str, Any]:
        """Fetch bot details from the API."""
        try:
            response = requests.get(f"{cls.BASE_URL}bot/{bot_id}")
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except RequestException as e:
            logger.error(
                f"Failed to fetch bot details. Bot ID: {bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            raise ValidationError(f"Не удалось получить данные бота: {str(e)}")

    @classmethod
    def update_bot(
        cls,
        bot_id: int,
        token: Optional[str] = None,
        is_active: Optional[bool] = None,
        default_reply: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update bot data in the API."""
        payload = {
            "token": token,
            "is_active": is_active,
            "default_reply": default_reply,
        }
        try:
            response = requests.patch(
                f"{cls.BASE_URL}bot/{bot_id}", json=payload
            )
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except RequestException as e:
            logger.error(
                f"Failed to update bot. Bot ID: {bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            raise ValidationError(f"Не удалось обновить бота: {str(e)}")

    @classmethod
    def create_bot(cls, token: str) -> Dict[str, Any]:
        """Create a new bot via API."""
        try:
            response = requests.post(
                f"{cls.BASE_URL}bot/", json={"token": token}
            )
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except RequestException as e:
            logger.error(
                f"Failed to create bot. Token: {token}. Error: {str(e)}",
                exc_info=True,
            )
            raise ValidationError(f"Не удалось создать бота: {str(e)}")

    @classmethod
    def delete_bot(cls, bot_id: int) -> None:
        """Delete a bot via API."""
        try:
            response = requests.delete(f"{cls.BASE_URL}bot/{bot_id}")
            response.raise_for_status()
        except RequestException as e:
            logger.error(
                f"Failed to delete bot. Bot ID: {bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            raise ValidationError(f"Не удалось удалить бота: {str(e)}")


class BotUserService:
    """Service class for bot user-related operations."""

    BASE_URL = settings.BOT_SERVICE_API_URL

    @classmethod
    def get_bot_users(cls, bot_id: int) -> List[Dict[str, Any]]:
        """Fetch paginated bot users from the API."""
        try:
            response = requests.get(
                f"{cls.BASE_URL}bot/{bot_id}/list/", timeout=10
            )
            response.raise_for_status()
            data = cast(Dict[str, Any], response.json())

            if not isinstance(data, dict) or "users" not in data:
                logger.error(f"Unexpected API response format: {data}")
                return []

            users = data.get("users", [])
            return cast(List[Dict[str, Any]], users)
        except (RequestException, json.JSONDecodeError) as e:
            logger.error(f"Failed to get bot users: {str(e)}")
            return []
