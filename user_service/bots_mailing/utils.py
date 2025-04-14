import json
import logging
from typing import Any, Dict

import requests
from django.conf import settings
from requests.exceptions import RequestException


logger = logging.getLogger("bots")

BOT_SERVICE_API_URL = settings.BOT_SERVICE_API_URL


def send_mail_to_bot_users(bot_id: int, message_text: str) -> Dict[str, Any]:
    """
    Send message to all bot users via API

    Args:
        bot_id: Telegram ID of the bot
        message_text: Content to broadcast (must be non-empty)

    Returns:
        Dictionary with mailing results from API

    Raises:
        ValueError: If message is empty
        RequestException: If API request fails
        JSONDecodeError: If API returns invalid JSON
    """
    if not message_text.strip():
        raise ValueError("Message text cannot be empty")

    payload = {
        "message": message_text,
    }

    try:
        response = requests.post(
            f"{BOT_SERVICE_API_URL}mailing/{bot_id}/start/",
            json=payload,
            timeout=15,
        )
        response.raise_for_status()

        response_data = response.json()

        if not isinstance(response_data, dict):
            logger.error(
                f"Invalid API response format for bot {bot_id}. Response: {response.text}"
            )
            raise ValueError(
                "Invalid API response format - expected dictionary"
            )

        return response_data

    except RequestException as e:
        error_msg = f"Mailing API request failed for bot {bot_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RequestException(error_msg) from e
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse API response for bot {bot_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise json.JSONDecodeError(error_msg, e.doc, e.pos) from e
