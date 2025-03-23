import logging
from typing import Any, Dict, Optional, Union

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


def get_bot_main_menu_button(button_id: int) -> Dict[str, Any]:
    """
    Fetch the main menu button details for a specific button ID from the Bot-Service API.

    Args:
        button_id (int): The ID of the main menu button to retrieve.

    Returns:
        Dict[str, Any]: A dictionary containing the button details.

    Raises:
        RequestException: If the request to the Bot-Service API fails or returns an unexpected response.
    """
    try:
        # Send a GET request to retrieve the button data
        response = requests.get(
            f"{BOT_SERVICE_API_URL}main-menu/button/{button_id}"
        )
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        # Ensure the response data is a dictionary
        if not isinstance(data, dict):
            raise RequestException("Failed to fetch bot's main menu button.")

        return data

    except RequestException as e:
        # Log the error if the API request fails
        logger.error(
            f"Failed to fetch bot's main menu button. Button ID: {button_id}. Error: {str(e)}",
            exc_info=True,
        )
        raise RequestException(f"Failed to fetch bot main menu: {str(e)}")


def update_main_menu_button(
    button_id: int, button_text: str, reply_text: str
) -> Optional[Dict[str, Any]]:
    """
    Update the main menu button for a specific button ID in the Bot-Service API.

    Args:
        button_id (int): The ID of the main menu button to update.
        button_text (str): The new text for the button.
        reply_text (str): The new reply text associated with the button.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the updated button details,
                                   or None if the update was unsuccessful.

    Raises:
        RequestException: If the request to the Bot-Service API fails or returns an unexpected response.
    """
    try:
        # Send a PATCH request to update the button data
        response = requests.patch(
            f"{BOT_SERVICE_API_URL}main-menu/button/{button_id}",
            json={"button_text": button_text, "reply_text": reply_text},
        )
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        # Ensure the response data is a dictionary
        if not isinstance(data, dict):
            raise RequestException("Failed to update bot main menu button.")

        return data

    except RequestException as e:
        # Log the error if the API request fails
        logger.error(
            f"Failed to update bot's main menu button. Button ID: {button_id}. Error: {str(e)}",
            exc_info=True,
        )
        raise RequestException(
            f"Failed to update bot's main menu button: {str(e)}"
        )


def create_main_menu_button(
    bot_id: int, button_text: str, reply_text: str
) -> Optional[Dict[str, Any]]:
    """
    Creates a new main menu button for a bot.

    Args:
        bot_id (int): The ID of the bot for which the button is being created.
        button_text (str): The text that will be displayed on the button.
        reply_text (str): The text that will be sent as a reply when the button is clicked.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the created button's data if successful,
                                  otherwise None.

    Raises:
        RequestException: If the API request fails or the response is invalid.
    """
    try:
        # Send a POST request to create a main menu button
        response = requests.post(
            f"{BOT_SERVICE_API_URL}main-menu/button",
            json={
                "bot_id": bot_id,
                "button_text": button_text,
                "reply_text": reply_text,
            },
        )
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()

        # Ensure the response data is a dictionary
        if not isinstance(data, dict):
            raise RequestException(
                "Invalid response format: expected a dictionary."
            )

        return data

    except RequestException as e:
        # Log the error if the API request fails
        logger.error(
            f"Failed to create bot's main menu button. Bot ID: {bot_id}. Error: {str(e)}",
            exc_info=True,
        )
        raise RequestException(
            f"Failed to create bot's main menu button: {str(e)}"
        )


def delete_bot_main_menu_button(button_id: int) -> None:
    """
    Deletes a main menu button for a bot.

    Args:
        button_id (int): The ID of the button to be deleted.

    Raises:
        RequestException: If the API request fails.
    """
    try:
        # Send a DELETE request to remove the main menu button
        response = requests.delete(
            f"{BOT_SERVICE_API_URL}main-menu/button/{button_id}",
        )
        response.raise_for_status()  # Raise an exception for HTTP errors

    except RequestException as e:
        # Log the error if the API request fails
        logger.error(
            f"Failed to delete bot's main menu button. Button ID: {button_id}. Error: {str(e)}",
            exc_info=True,
        )
        raise RequestException(
            f"Failed to delete bot's main menu button: {str(e)}"
        )


def get_bot_chain(chain_id: int) -> Dict[str, Any]:
    """
    Fetches the details of a bot's chain by the specified chain identifier.

    :param chain_id: The identifier of the chain for which details are to be fetched.
    :return: A dictionary containing the details of the chain retrieved from the API.
    :raises RequestException: If the request to the API fails, an exception will be raised.
    """
    try:
        # Make a GET request to the API to retrieve the chain details
        response = requests.get(
            f"{BOT_SERVICE_API_URL}chain/detail/{chain_id}"
        )
        # Check if the request was successful (status code 200-299)
        response.raise_for_status()

        # Attempt to parse the JSON response and return it
        json_response: Union[Dict[str, Any], None] = (
            response.json()
        )  # Explicitly specify the expected type
        if json_response is None:
            raise ValueError("Received None instead of expected data.")
        return json_response

    except RequestException as e:
        # Log the error with details
        logger.error(
            f"Failed to fetch bot chain's detail. Chain ID: {chain_id}. Error: {str(e)}",
            exc_info=True,
        )
        # Raise an exception to signal that there was a problem
        raise RequestException(f"Failed to fetch bot chain's detail: {str(e)}")

    except ValueError as e:
        logger.error(
            f"Invalid response data for chain ID: {chain_id}. Error: {str(e)}"
        )
        raise RequestException(f"Invalid response data: {str(e)}")
