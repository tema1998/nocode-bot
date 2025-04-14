import json
import logging
from typing import Any, Dict, List, Optional, Union

import requests
from django.conf import settings
from requests.exceptions import RequestException


logger = logging.getLogger("bots")

BOT_SERVICE_API_URL = settings.BOT_SERVICE_API_URL


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
    set_as_next_step_for_button_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Create a new chain step via API.

    Args:
        chain_id: ID of the parent chain
        name: Step name
        message: Step message content
        set_as_next_step_for_button_id: Optional button ID to link this step to

    Returns:
        Dictionary containing created step data

    Raises:
        RequestException: If API request fails
        ValueError: For invalid input parameters
    """
    if not isinstance(chain_id, int) or chain_id <= 0:
        raise ValueError("chain_id must be positive integer")

    payload = {"chain_id": chain_id, "name": name, "message": message}

    if set_as_next_step_for_button_id:
        payload["set_as_next_step_for_button_id"] = int(
            set_as_next_step_for_button_id
        )

    response = requests.post(
        f"{BOT_SERVICE_API_URL}chain-step/", json=payload, timeout=10
    )
    response.raise_for_status()
    response_data = response.json()
    if not isinstance(response_data, dict):
        raise ValueError("Expected dictionary response from API")

    return response_data


def update_chain_step(
    step_id: int,
    name: Optional[str] = None,
    message: Optional[str] = None,
    next_step_id: Optional[int] = None,
    text_input: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Update an existing chain step with optional parameters.

    Args:
        step_id: ID of the step to update (required)
        name: New step name (optional)
        message: New message content (optional)
        next_step_id: Next step ID for text input flow (optional)
        text_input: Enable/disable text input after step (optional)

    Returns:
        Updated step data

    Raises:
        RequestException: If API request fails
        ValueError: For invalid parameters
    """
    if not isinstance(step_id, int) or step_id <= 0:
        raise ValueError("step_id must be positive integer")

    # Build payload dynamically with only provided parameters
    payload = {}
    if name is not None:
        payload["name"] = name
    if message is not None:
        payload["message"] = message
    if next_step_id is not None:
        payload["next_step_id"] = str(next_step_id)
    if text_input is not None:
        payload["text_input"] = str(text_input)

    if not payload:
        raise ValueError("At least one parameter must be provided for update")

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


def create_chain_button(
    step_id: int, text: str, next_step_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Creates a new button in a conversation chain step.

    Args:
        step_id: ID of the parent step this button belongs to
        text: Display text for the button
        next_step_id: Optional ID of the next step this button links to

    Returns:
        Dictionary containing the created button data

    Raises:
        RequestException: If API communication fails
        ValueError: For invalid input parameters
    """
    if not isinstance(step_id, int) or step_id <= 0:
        raise ValueError("step_id must be a positive integer")

    payload = {"step_id": step_id, "text": text}

    if next_step_id is not None:
        if not isinstance(next_step_id, int) or next_step_id <= 0:
            raise ValueError("next_step_id must be a positive integer")
        payload["next_step_id"] = next_step_id

    try:
        response = requests.post(
            f"{BOT_SERVICE_API_URL}chain-button/", json=payload, timeout=10
        )
        response.raise_for_status()

        response_data = response.json()
        if not isinstance(response_data, dict):
            raise ValueError(
                "API response format invalid - expected dictionary"
            )

        return response_data

    except RequestException as e:
        logger.error(
            "Button creation failed for step %d. Error: %s. Payload: %s",
            step_id,
            str(e),
            payload,
            exc_info=True,
        )
        raise RequestException(f"Button creation failed: {str(e)}") from e


def get_chain_button(button_id: int) -> Dict[str, Any]:
    """
    Retrieves details of a specific chain button.

    Args:
        button_id: Unique identifier of the button

    Returns:
        Dictionary containing button configuration

    Raises:
        RequestException: If API request fails
        ValueError: For invalid ID format or response data
    """
    if not isinstance(button_id, int) or button_id <= 0:
        raise ValueError("button_id must be a positive integer")

    try:
        response = requests.get(
            f"{BOT_SERVICE_API_URL}chain-button/{button_id}", timeout=10
        )
        response.raise_for_status()

        response_data = response.json()
        if not isinstance(response_data, dict):
            raise ValueError(
                "API response format invalid - expected dictionary"
            )

        return response_data

    except RequestException as e:
        logger.error(
            "Failed to retrieve button %d. Error: %s",
            button_id,
            str(e),
            exc_info=True,
        )
        raise RequestException(f"Button retrieval failed: {str(e)}") from e


def update_chain_button(
    button_id: int,
    text: Optional[str] = None,
    next_step_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Updates configuration of an existing chain button.

    Args:
        button_id: ID of the button to update
        text: New display text (optional)
        next_step_id: New target step ID (optional)

    Returns:
        Updated button configuration

    Raises:
        RequestException: If update operation fails
        ValueError: For invalid parameters
    """
    if not isinstance(button_id, int) or button_id <= 0:
        raise ValueError("button_id must be a positive integer")

    payload = {}
    if text is not None:
        payload["text"] = text
    if next_step_id is not None:
        if not isinstance(next_step_id, int) or next_step_id <= 0:
            raise ValueError("next_step_id must be a positive integer")
        payload["next_step_id"] = int(next_step_id)  # type: ignore

    try:
        response = requests.patch(
            f"{BOT_SERVICE_API_URL}chain-button/{button_id}",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()

        response_data = response.json()
        if not isinstance(response_data, dict):
            raise ValueError(
                "API response format invalid - expected dictionary"
            )

        return response_data

    except RequestException as e:
        logger.error(
            "Failed to update button %d. Error: %s. Changes: %s",
            button_id,
            str(e),
            payload,
            exc_info=True,
        )
        raise RequestException(f"Button update failed: {str(e)}") from e


def delete_chain_button(button_id: int) -> bool:
    """
    Permanently removes a chain button.

    Args:
        button_id: ID of the button to delete

    Returns:
        bool: True if deletion was successful, False otherwise

    Raises:
        RequestException: If deletion operation fails
        ValueError: For invalid button ID
    """
    if not isinstance(button_id, int) or button_id <= 0:
        raise ValueError("button_id must be a positive integer")

    try:
        response = requests.delete(
            f"{BOT_SERVICE_API_URL}chain-button/{button_id}", timeout=10
        )

        if response.status_code == 204:
            return True

        response.raise_for_status()
        return False

    except RequestException as e:
        logger.error(
            "Failed to delete button %d. Status: %s. Error: %s",
            button_id,
            getattr(e.response, "status_code", "N/A"),
            str(e),
            exc_info=True,
        )
        raise RequestException(f"Button deletion failed: {str(e)}") from e


def get_paginated_chain_results(chain_id: int) -> List[Dict[str, Any]]:
    """
    Fetch paginated chain results from the API.

    Args:
        chain_id: ID of the chain to get results for

    Returns:
        List of result dictionaries. Returns empty list on any error.

    Note:
        The API is expected to return a dictionary with 'items' key containing
        the actual results list. Any other format will return empty list.
    """
    try:
        # Make API request
        response = requests.get(
            f"{BOT_SERVICE_API_URL}chain/results/{chain_id}", timeout=10
        )
        response.raise_for_status()  # Raises exception for 4XX/5XX responses

        data = response.json()

        # Validate response structure
        if not isinstance(data, dict) or "items" not in data:
            logger.error(f"Unexpected API response format: {data}")
            return []

        return data["items"]  # type: ignore

    except requests.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse API response: {str(e)}")
        return []
