import json
import logging
from typing import Any, Dict, List

import requests
from django.conf import settings
from requests.exceptions import RequestException


logger = logging.getLogger("bots")

BOT_SERVICE_API_URL = settings.BOT_SERVICE_API_URL


def get_bot_details(bot_id):
    """
    Fetches bot details from the FastAPI service.

    Args:
        bot_id (int): The ID of the bot.

    Returns:
        dict: Bot details.

    Raises:
        RequestException: If the request fails.
    """
    try:
        response = requests.get(f"{BOT_SERVICE_API_URL}bot/{bot_id}")
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(
            f"Failed to fetch bot details. Bot ID: {bot_id}. Error: {str(e)}",
            exc_info=True,
        )
        raise RequestException(f"Failed to fetch bot details: {str(e)}")


def update_bot(bot_id, token=None, is_active=None, default_reply=None):
    """
    Updates bot data in the FastAPI service.

    Args:
        bot_id (int): The ID of the bot.
        token (str): The bot token.
        is_active (bool): The bot's active status.
        default_reply (bool): The bot's default reply message.

    Returns:
        dict: Updated bot data.

    Raises:
        RequestException: If the request fails.
    """
    try:
        response = requests.patch(
            f"{BOT_SERVICE_API_URL}bot/{bot_id}",
            json={
                "token": token,
                "is_active": is_active,
                "default_reply": default_reply,
            },
        )
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(
            f"Failed to update bot. Bot ID: {bot_id}. Error: {str(e)}",
            exc_info=True,
        )
        raise RequestException(f"Failed to update bot: {str(e)}")


def create_bot(token):
    """
    Creates a new bot in the FastAPI service.

    Args:
        token (str): The bot token.

    Returns:
        dict: Created bot data.

    Raises:
        RequestException: If the request fails.
    """
    try:
        response = requests.post(
            f"{BOT_SERVICE_API_URL}bot/",
            json={"token": token},
        )
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(
            f"Failed to create bot. Token: {token}. Error: {str(e)}",
            exc_info=True,
        )
        raise RequestException(f"Failed to create bot: {str(e)}")


def delete_bot(bot_id):
    """
    Deletes a bot with the specified bot ID from the bot service.

    Args:
        bot_id (str): The ID of the bot from Bot-Service that needs to be deleted.

    Raises:
        RequestException: If the request to delete the bot fails.

    Returns:
        Response status code.
    """
    try:
        response = requests.delete(
            f"{BOT_SERVICE_API_URL}bot/{bot_id}",
        )
        response.raise_for_status()
        return response.status_code
    except RequestException as e:
        logger.error(
            f"Failed to delete bot. Bot-service bot ID: {bot_id}. Error: {str(e)}",
            exc_info=True,
        )
        raise RequestException(f"Failed to create bot: {str(e)}")


def get_paginated_bot_users(bot_id: int) -> List[Dict[str, Any]]:
    """
    Fetch paginated bot users from the API.

    Args:
        bot_id: ID of the bot to get users for

    Returns:
        List of user dictionaries. Returns empty list on any error.

    Note:
        The API is expected to return a dictionary with 'users' key containing
        the actual users list. Any other format will return empty list.
    """
    try:
        # Make API request
        response = requests.get(
            f"{BOT_SERVICE_API_URL}bot/{bot_id}/list/", timeout=10
        )
        response.raise_for_status()

        data = response.json()

        # Validate response structure
        if not isinstance(data, dict) or "users" not in data:
            logger.error(f"Unexpected API response format: {data}")
            return []

        return data["users"]  # type: ignore

    except requests.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse API response: {str(e)}")
        return []


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
