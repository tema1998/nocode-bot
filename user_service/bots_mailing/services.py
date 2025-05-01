import logging
from typing import Any, Dict, Optional

import requests
from django.conf import settings
from requests.exceptions import RequestException
from requests.models import Response


logger = logging.getLogger("bots")


class MailingService:
    """Service for handling mailing operations"""

    BASE_URL = settings.BOT_SERVICE_API_URL

    @classmethod
    def send_mailing(cls, bot_id: int, message_text: str) -> Dict[str, Any]:
        """
        Send message to all bot users via API

        Args:
            bot_id: Telegram ID of the bot
            message_text: Content to broadcast

        Returns:
            Dictionary with mailing results from API

        Raises:
            ValueError: If message is empty
            RequestException: If API request fails
            json.JSONDecodeError: If API returns invalid JSON
        """
        if not message_text.strip():
            raise ValueError("Message text cannot be empty")

        payload = {"message": message_text}

        try:
            response = cls._make_request(
                method="POST",
                endpoint=f"mailing/{bot_id}/start/",
                json_data=payload,
                timeout=15,
            )
            return cls._validate_response(response, bot_id)
        except RequestException as e:
            logger.error(
                f"Mailing API request failed for bot {bot_id}: {str(e)}",
                exc_info=True,
            )
            raise RequestException(f"Mailing failed: {str(e)}") from e

    @classmethod
    def _make_request(
        cls,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        timeout: int = 10,
    ) -> Response:
        """Make an API request"""
        url = f"{cls.BASE_URL}{endpoint}"
        return requests.request(method, url, json=json_data, timeout=timeout)

    @classmethod
    def _validate_response(
        cls, response: Response, bot_id: int
    ) -> Dict[str, Any]:
        """Validate and parse API response"""
        response.raise_for_status()
        response_data = response.json()

        if not isinstance(response_data, dict):
            error_msg = f"Invalid API response format for bot {bot_id}"
            logger.error(
                f"{error_msg}. Response: {response.text}", exc_info=True
            )
            raise ValueError(error_msg)

        return response_data
