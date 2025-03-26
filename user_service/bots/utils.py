import json
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


def get_bot_chains(bot_id: int) -> Dict[str, Any]:

    try:
        # Make a GET request to the API to retrieve the chain details
        response = requests.get(f"{BOT_SERVICE_API_URL}chain/{bot_id}")
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
            f"Failed to fetch bot's chains. Bot ID: {bot_id}. Error: {str(e)}",
            exc_info=True,
        )
        # Raise an exception to signal that there was a problem
        raise RequestException(f"Failed to fetch bot's chains: {str(e)}")

    except ValueError as e:
        logger.error(
            f"Invalid response data for getting chains bot ID: {bot_id}. Error: {str(e)}"
        )
        raise RequestException(f"Invalid response data: {str(e)}")


def create_chain(bot_id: int, name: str) -> Optional[Dict[str, Any]]:
    """
    Create a new chain for a bot via the Bot-Service API.

    Args:
        bot_id: The ID of the bot to create the chain for
        name: The name of the new chain

    Returns:
        Dictionary containing the created chain data if successful, None otherwise

    Raises:
        RequestException: If the API request fails or returns invalid data
    """
    try:
        # Prepare API request payload
        payload = {
            "bot_id": bot_id,
            "name": name,
        }

        # Log the attempt to create a chain
        logger.info(
            f"Attempting to create chain. Bot ID: {bot_id}, Name: '{name}'"
        )

        # Make API request
        response = requests.post(
            f"{BOT_SERVICE_API_URL}chain/",
            json=payload,
            timeout=10,  # Added timeout for better reliability
        )
        response.raise_for_status()

        # Parse and validate response
        data = response.json()

        if not isinstance(data, dict):
            error_msg = "Invalid response format: expected dictionary, got {type(data)}"
            logger.error(error_msg)
            raise RequestException(error_msg)

        # Log successful creation
        logger.info(
            f"Successfully created chain. Bot ID: {bot_id}, "
            f"Chain Name: '{name}', Response: {data}"
        )

        return data

    except RequestException as e:
        error_msg = f"API request failed for bot {bot_id}: {str(e)}"
        logger.error(
            error_msg,
            exc_info=True,
            extra={
                "bot_id": bot_id,
                "chain_name": name,
                "api_endpoint": f"{BOT_SERVICE_API_URL}chain/",
            },
        )
        raise RequestException(error_msg) from e


def update_chain(chain_id: int, new_name: str) -> Optional[Dict[str, Any]]:
    """
    Updates an existing chain via the Bot-Service API.

    Makes a PATCH request to update the chain's name and returns the updated chain data.

    Args:
        chain_id: The ID of the chain to update
        new_name: The new name for the chain

    Returns:
        Optional[Dict[str, Any]]: The updated chain data if successful, None otherwise

    Raises:
        RequestException: If the API request fails or returns invalid data

    """
    try:
        # Prepare API request payload with new chain name
        payload = {
            "name": new_name,
        }

        logger.info(
            f"Attempting to update chain. Chain ID: {chain_id}, New name: '{new_name}'"
        )

        # Make authenticated PATCH request to update chain
        response = requests.patch(
            f"{BOT_SERVICE_API_URL}chain/{chain_id}",
            json=payload,
            timeout=10,  # 10 seconds timeout
        )
        response.raise_for_status()  # Raises for 4XX/5XX status codes

        # Parse and validate response
        data = response.json()

        if not isinstance(data, dict):
            error_msg = f"Invalid response format: expected dictionary, got {type(data)}"
            logger.error(error_msg)
            raise RequestException(error_msg)

        logger.info(
            f"Successfully updated chain. Chain ID: {chain_id}, Response: {data}"
        )
        return data

    except RequestException as e:
        error_msg = f"API request failed for chain {chain_id}: {str(e)}"
        logger.error(
            error_msg,
            exc_info=True,
            extra={
                "chain_id": chain_id,
                "new_name": new_name,
                "api_endpoint": f"{BOT_SERVICE_API_URL}chain/{chain_id}",
                "status_code": getattr(e.response, "status_code", None),
            },
        )
        raise RequestException(error_msg) from e

    except json.JSONDecodeError as e:
        error_msg = (
            f"Failed to parse JSON response for chain {chain_id}: {str(e)}"
        )
        logger.error(error_msg, exc_info=True)
        raise RequestException(error_msg) from e


def delete_chain(chain_id: int) -> bool:
    """
    Deletes a chain via the Bot-Service API.

    Args:
        chain_id: ID of the chain to delete

    Returns:
        bool: True if deletion was successful, False otherwise

    Raises:
        RequestException: If the API request fails
        ValueError: If invalid chain_id is provided

    """
    if not isinstance(chain_id, int) or chain_id <= 0:
        error_msg = f"Invalid chain_id: {chain_id}. Must be positive integer"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        logger.info(f"Attempting to delete chain. Chain ID: {chain_id}")

        response = requests.delete(
            f"{BOT_SERVICE_API_URL}chain/{chain_id}",
            headers={
                "Content-Type": "application/json",
            },
            timeout=10,
        )

        if response.status_code == 204:
            logger.info(f"Successfully deleted chain. Chain ID: {chain_id}")
            return True

        # Если код ответа не 204, обрабатываем как ошибку
        response.raise_for_status()

        # Этот код выполнится только если API вернул неожиданный успешный код
        logger.warning(
            f"Unexpected success status code: {response.status_code}"
        )
        return True

    except requests.Timeout as e:
        error_msg = f"Timeout while deleting chain {chain_id}"
        logger.error(error_msg)
        raise RequestException(error_msg) from e

    except requests.ConnectionError as e:
        error_msg = f"Connection error while deleting chain {chain_id}"
        logger.error(error_msg)
        raise RequestException(error_msg) from e

    except requests.HTTPError as e:
        status_code = (
            e.response.status_code if hasattr(e, "response") else None
        )
        error_msg = (
            f"HTTP error deleting chain {chain_id}. Status: {status_code}"
        )
        logger.error(
            f"{error_msg}. Response: {e.response.text if hasattr(e, 'response') else 'None'}"
        )
        raise RequestException(error_msg) from e

    except Exception as e:
        error_msg = f"Unexpected error deleting chain {chain_id}"
        logger.error(f"{error_msg}: {str(e)}", exc_info=True)
        raise RequestException(error_msg) from e


def get_chain_step(step_id: int) -> Dict[str, Any]:
    """
    Retrieve a chain step by its ID from the API.

    Args:
        step_id: The ID of the step to retrieve

    Returns:
        Dictionary containing the step data

    Raises:
        RequestException: If API request fails or response is invalid
        ValueError: If input validation fails
    """
    if not isinstance(step_id, int) or step_id <= 0:
        error_msg = f"Invalid step_id: {step_id}. Must be positive integer"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        response = requests.get(
            f"{BOT_SERVICE_API_URL}chain-step/{step_id}", timeout=10
        )
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, dict):
            raise ValueError(f"Expected dictionary, got {type(data)}")

        return data

    except RequestException as e:
        logger.error(
            f"Failed to fetch chain step {step_id}. Error: {str(e)}",
            exc_info=True,
            extra={"step_id": step_id},
        )
        raise RequestException(f"API request failed: {str(e)}") from e
    except json.JSONDecodeError as e:
        logger.error(
            f"Invalid JSON response for step {step_id}", exc_info=True
        )
        raise RequestException("Invalid API response format") from e


def create_chain_step(
    chain_id: int,
    name: str,
    message: str,
    is_first_step_of_chain: bool,
    set_as_next_step_for_button_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Create a new chain step via API.

    Args:
        chain_id: ID of the parent chain
        name: Step name
        message: Step message content
        is_first_step_of_chain: Whether this is the chain's first step
        set_as_next_step_for_button_id: Optional button ID to link this step to

    Returns:
        Dictionary containing created step data

    Raises:
        RequestException: If API request fails
        ValueError: For invalid input parameters
    """
    if not isinstance(chain_id, int) or chain_id <= 0:
        raise ValueError("chain_id must be positive integer")

    payload = {
        "chain_id": chain_id,
        "name": name,
        "message": message,
        "is_first_step_of_chain": is_first_step_of_chain,
    }

    if set_as_next_step_for_button_id:
        if (
            not isinstance(set_as_next_step_for_button_id, int)
            or set_as_next_step_for_button_id <= 0
        ):
            raise ValueError("button_id must be positive integer")
        payload["set_as_next_step_for_button_id"] = (
            set_as_next_step_for_button_id
        )

    try:
        response = requests.post(
            f"{BOT_SERVICE_API_URL}chain-step", json=payload, timeout=10
        )
        response.raise_for_status()
        response_data = response.json()
        if not isinstance(response_data, dict):
            raise ValueError("Expected dictionary response from API")

        return response_data

    except RequestException as e:
        logger.error(
            f"Failed to create step in chain {chain_id}. Error: {str(e)}",
            exc_info=True,
            extra={"chain_id": chain_id, "payload": payload},
        )
        raise RequestException(f"Step creation failed: {str(e)}") from e


def update_chain_step(step_id: int, name: str, message: str) -> Dict[str, Any]:
    """
    Update an existing chain step.

    Args:
        step_id: ID of the step to update
        name: New step name
        message: New message content

    Returns:
        Updated step data

    Raises:
        RequestException: If API request fails
        ValueError: For invalid parameters
    """
    if not isinstance(step_id, int) or step_id <= 0:
        raise ValueError("step_id must be positive integer")

    payload = {"name": name, "message": message}

    try:
        response = requests.patch(
            f"{BOT_SERVICE_API_URL}chain-step/{step_id}",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        response_data = response.json()
        if not isinstance(response_data, dict):
            raise ValueError("Expected dictionary response from API")

        return response_data

    except RequestException as e:
        logger.error(
            f"Failed to update step {step_id}. Error: {str(e)}",
            exc_info=True,
            extra={"step_id": step_id, "payload": payload},
        )
        raise RequestException(f"Step update failed: {str(e)}") from e


def delete_chain_step(step_id: int) -> bool:
    """
    Delete a chain step via API.

    Args:
        step_id: ID of the step to delete

    Returns:
        bool: True if deletion was successful

    Raises:
        RequestException: If API request fails
        ValueError: For invalid step_id
    """
    if not isinstance(step_id, int) or step_id <= 0:
        raise ValueError("step_id must be positive integer")

    try:
        response = requests.delete(
            f"{BOT_SERVICE_API_URL}chain-step/{step_id}", timeout=10
        )

        if response.status_code == 204:
            return True

        response.raise_for_status()
        return False

    except RequestException as e:
        logger.error(
            f"Failed to delete step {step_id}. Status: {getattr(e.response, 'status_code', 'unknown')}. Error: {str(e)}",
            exc_info=True,
            extra={"step_id": step_id},
        )
        raise RequestException(f"Step deletion failed: {str(e)}") from e
