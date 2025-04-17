import logging
from typing import Any, Dict, List, Union, cast

import requests
from django.conf import settings
from requests.exceptions import RequestException


logger = logging.getLogger("bots")


class BotServiceClient:
    """Client for interacting with the Bot-Service API."""

    @staticmethod
    def _handle_request(
        method: str, endpoint: str, *, expect_json: bool = True, **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], str]:
        """
        Handle API requests with common error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            expect_json: Whether to expect JSON response
            **kwargs: Additional arguments for requests.request

        Returns:
            Parsed JSON response if expect_json=True, otherwise response text
        """
        try:
            response = requests.request(
                method, f"{settings.BOT_SERVICE_API_URL}{endpoint}", **kwargs
            )
            response.raise_for_status()

            if not expect_json:
                return response.text

            if not response.content:
                return {}

            return cast(
                Union[Dict[str, Any], List[Dict[str, Any]]], response.json()
            )

        except RequestException as e:
            logger.error(
                f"API request failed. Endpoint: {endpoint}. Error: {str(e)}",
                exc_info=True,
            )
            raise RequestException(f"API request failed: {str(e)}")

    # Bot operations

    # Main Menu operations
    @staticmethod
    def get_main_menu(bot_id: int) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request("GET", f"main-menu/{bot_id}"),
        )

    @staticmethod
    def update_main_menu(bot_id: int, welcome_message: str) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "PATCH",
                f"main-menu/{bot_id}",
                json={"welcome_message": welcome_message},
            ),
        )

    @staticmethod
    def get_main_menu_button(button_id: int) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "GET", f"main-menu/button/{button_id}"
            ),
        )

    @staticmethod
    def update_main_menu_button(button_id: int, **kwargs) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "PATCH", f"main-menu/button/{button_id}", json=kwargs
            ),
        )

    @staticmethod
    def create_main_menu_button(bot_id: int, **kwargs) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "POST", "main-menu/button/", json={"bot_id": bot_id, **kwargs}
            ),
        )

    @staticmethod
    def delete_main_menu_button(button_id: int) -> None:
        BotServiceClient._handle_request(
            "DELETE", f"main-menu/button/{button_id}", expect_json=False
        )

    # Chain operations
    @staticmethod
    def get_bot_chains(bot_id: int) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request("GET", f"chain/{bot_id}"),
        )
