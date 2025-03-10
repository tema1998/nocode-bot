import logging
from typing import Any, Dict, Optional

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
            f"{BOT_SERVICE_API_URL}bot",
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


def get_bot_main_menu(bot_id: int) -> Dict[str, Any]:
    """
    Fetch the main menu configuration for a specific bot.

    Args:
        bot_id (int): The unique identifier of the bot.

    Returns:
        Dict[str, Any]: A dictionary containing the main menu configuration.

    Raises:
        RequestException: If the request to fetch the main menu fails.
    """
    try:
        response = requests.get(f"{BOT_SERVICE_API_URL}main-menu/{bot_id}")
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        if not isinstance(data, dict):
            raise RequestException("Failed to fetch bot main menu.")
        return data

    except RequestException as e:
        logger.error(
            f"Failed to fetch bot main menu. Bot ID: {bot_id}. Error: {str(e)}",
            exc_info=True,
        )
        raise RequestException(f"Failed to fetch bot main menu: {str(e)}")


def update_main_menu(
    bot_id: int, welcome_message: str
) -> Optional[Dict[str, Any]]:
    """
    Update the welcome message in the main menu configuration for a specific bot.

    Args:
        bot_id (int): The unique identifier of the bot.
        welcome_message (str): The new welcome message to set.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the updated main menu configuration,
                                  or None if the update fails.

    Raises:
        RequestException: If the request to update the main menu fails.
    """
    try:
        response = requests.patch(
            f"{BOT_SERVICE_API_URL}main-menu/{bot_id}",
            json={"welcome_message": welcome_message},
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if not isinstance(data, dict):
            raise RequestException("Failed to fetch bot main menu.")
        return data

    except RequestException as e:
        logger.error(
            f"Failed to update bot's main menu. Bot ID: {bot_id}. Error: {str(e)}",
            exc_info=True,
        )
        raise RequestException(f"Failed to update bot's main menu: {str(e)}")
