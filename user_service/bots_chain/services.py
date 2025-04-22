import logging
from typing import Any, Dict, List, Optional, Union, cast

import requests
from django.conf import settings
from requests.exceptions import RequestException

from .types import ChainButtonData, ChainData, ChainStepData


logger = logging.getLogger("bots")


class BaseAPIService:
    BASE_URL = settings.BOT_SERVICE_API_URL

    @classmethod
    def _make_request(
        cls,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        timeout: int = 10,
    ) -> Dict[str, Any]:
        url = f"{cls.BASE_URL}{endpoint}"
        try:
            response = requests.request(
                method, url, params=params, json=json_data, timeout=timeout
            )
            response.raise_for_status()
            if response.content:
                return response.json()  # type: ignore
            return {}
        except RequestException as e:
            logger.error(
                f"API request failed. Endpoint: {endpoint}. Error: {str(e)}",
                exc_info=True,
            )
            raise


class ChainService(BaseAPIService):
    @classmethod
    def get_chain(cls, chain_id: int) -> ChainData:
        response = cls._make_request("GET", f"chains/detail/{chain_id}")
        return cast(ChainData, response)

    @classmethod
    def get_bot_chains(cls, bot_id: int) -> Dict[str, List[ChainData]]:
        response = cls._make_request("GET", f"chains/{bot_id}")
        return cast(Dict[str, List[ChainData]], response)

    @classmethod
    def create_chain(cls, bot_id: int, name: str) -> ChainData:
        response = cls._make_request(
            "POST", "chains/", json_data={"bot_id": bot_id, "name": name}
        )
        return cast(ChainData, response)

    @classmethod
    def update_chain(cls, chain_id: int, name: str) -> ChainData:
        response = cls._make_request(
            "PATCH", f"chains/{chain_id}", json_data={"name": name}
        )
        return cast(ChainData, response)

    @classmethod
    def delete_chain(cls, chain_id: int) -> bool:
        try:
            cls._make_request("DELETE", f"chains/{chain_id}")
            return True
        except RequestException:
            return False

    @classmethod
    def get_chain_results(
        cls, chain_id: int
    ) -> List[Dict[str, Union[str, int, bool]]]:
        try:
            response = cls._make_request("GET", f"chains/results/{chain_id}")
            return cast(
                List[Dict[str, Union[str, int, bool]]],
                response.get("items", []),
            )
        except RequestException:
            return []


class ChainStepService(BaseAPIService):
    @classmethod
    def get_step(cls, step_id: int) -> ChainStepData:
        response = cls._make_request("GET", f"steps/{step_id}")
        return cast(ChainStepData, response)

    @classmethod
    def create_step(
        cls,
        chain_id: int,
        name: str,
        message: str,
        button_id: Optional[int] = None,
    ) -> ChainStepData:
        payload: Dict[str, Union[int, str]] = {
            "chain_id": chain_id,
            "name": name,
            "message": message,
        }
        if button_id:
            payload["set_as_next_step_for_button_id"] = button_id

        response = cls._make_request("POST", "steps/", json_data=payload)
        return cast(ChainStepData, response)

    @classmethod
    def update_step(
        cls,
        step_id: int,
        name: Optional[str] = None,
        message: Optional[str] = None,
        next_step_id: Optional[int] = None,
        text_input: Optional[bool] = None,
    ) -> ChainStepData:
        payload: Dict[str, Union[str, int, bool]] = {}
        if name is not None:
            payload["name"] = name
        if message is not None:
            payload["message"] = message
        if next_step_id is not None:
            payload["next_step_id"] = next_step_id
        if text_input is not None:
            payload["text_input"] = text_input

        response = cls._make_request(
            "PATCH", f"steps/{step_id}", json_data=payload
        )
        return cast(ChainStepData, response)

    @classmethod
    def delete_step(cls, step_id: int) -> bool:
        try:
            cls._make_request("DELETE", f"steps/{step_id}")
            return True
        except RequestException:
            return False


class ChainButtonService(BaseAPIService):
    @classmethod
    def get_button(cls, button_id: int) -> ChainButtonData:
        response = cls._make_request("GET", f"buttons/{button_id}")
        return cast(ChainButtonData, response)

    @classmethod
    def create_button(
        cls, step_id: int, text: str, next_step_id: Optional[int] = None
    ) -> ChainButtonData:
        payload: Dict[str, Union[int, str]] = {
            "step_id": step_id,
            "text": text,
        }
        if next_step_id:
            payload["next_step_id"] = next_step_id

        response = cls._make_request("POST", "buttons/", json_data=payload)
        return cast(ChainButtonData, response)

    @classmethod
    def update_button(
        cls,
        button_id: int,
        text: Optional[str] = None,
        next_step_id: Optional[int] = None,
    ) -> ChainButtonData:
        payload: Dict[str, Union[str, int]] = {}
        if text is not None:
            payload["text"] = text
        if next_step_id is not None:
            payload["next_step_id"] = next_step_id

        response = cls._make_request(
            "PATCH", f"buttons/{button_id}", json_data=payload
        )
        return cast(ChainButtonData, response)

    @classmethod
    def delete_button(cls, button_id: int) -> bool:
        try:
            cls._make_request("DELETE", f"buttons/{button_id}")
            return True
        except RequestException:
            return False
