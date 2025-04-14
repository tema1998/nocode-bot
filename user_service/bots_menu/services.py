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
    @staticmethod
    def get_bot_details(bot_id: int) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request("GET", f"bot/{bot_id}"),
        )

    @staticmethod
    def update_bot(bot_id: int, **kwargs) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "PATCH", f"bot/{bot_id}", json=kwargs
            ),
        )

    @staticmethod
    def create_bot(token: str) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "POST", "bot/", json={"token": token}
            ),
        )

    @staticmethod
    def delete_bot(bot_id: int) -> None:
        BotServiceClient._handle_request(
            "DELETE", f"bot/{bot_id}", expect_json=False
        )

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

    @staticmethod
    def get_chain_detail(chain_id: int) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "GET", f"chain/detail/{chain_id}"
            ),
        )

    @staticmethod
    def create_chain(bot_id: int, name: str) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "POST", "chain/", json={"bot_id": bot_id, "name": name}
            ),
        )

    @staticmethod
    def update_chain(chain_id: int, name: str) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "PATCH", f"chain/{chain_id}", json={"name": name}
            ),
        )

    @staticmethod
    def delete_chain(chain_id: int) -> None:
        BotServiceClient._handle_request(
            "DELETE", f"chain/{chain_id}", expect_json=False
        )

    # Chain Step operations
    @staticmethod
    def get_chain_step(step_id: int) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request("GET", f"chain-step/{step_id}"),
        )

    @staticmethod
    def create_chain_step(chain_id: int, **kwargs) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "POST", "chain-step/", json={"chain_id": chain_id, **kwargs}
            ),
        )

    @staticmethod
    def update_chain_step(step_id: int, **kwargs) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "PATCH", f"chain-step/{step_id}", json=kwargs
            ),
        )

    @staticmethod
    def delete_chain_step(step_id: int) -> None:
        BotServiceClient._handle_request(
            "DELETE", f"chain-step/{step_id}", expect_json=False
        )

    # Chain Button operations
    @staticmethod
    def create_chain_button(step_id: int, **kwargs) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "POST", "chain-button/", json={"step_id": step_id, **kwargs}
            ),
        )

    @staticmethod
    def get_chain_button(button_id: int) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "GET", f"chain-button/{button_id}"
            ),
        )

    @staticmethod
    def update_chain_button(button_id: int, **kwargs) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "PATCH", f"chain-button/{button_id}", json=kwargs
            ),
        )

    @staticmethod
    def delete_chain_button(button_id: int) -> None:
        BotServiceClient._handle_request(
            "DELETE", f"chain-button/{button_id}", expect_json=False
        )

    # Results and Users operations
    @staticmethod
    def get_chain_results(chain_id: int) -> List[Dict[str, Any]]:
        data = cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "GET", f"chain/results/{chain_id}"
            ),
        )
        return cast(List[Dict[str, Any]], data.get("items", []))

    @staticmethod
    def get_bot_users(bot_id: int) -> List[Dict[str, Any]]:
        data = cast(
            Dict[str, Any],
            BotServiceClient._handle_request("GET", f"bot/{bot_id}/list/"),
        )
        return cast(List[Dict[str, Any]], data.get("users", []))

    @staticmethod
    def send_mailing(bot_id: int, message: str) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            BotServiceClient._handle_request(
                "POST", f"mailing/{bot_id}/start/", json={"message": message}
            ),
        )
