from typing import Any, Dict, List, Optional, TypedDict, Union


class MainMenuData(TypedDict):
    welcome_message: str
    buttons: List["MainMenuButtonData"]


class MainMenuButtonData(TypedDict):
    id: int
    button_text: str
    reply_text: str
    chain_id: Optional[int]


class ChainData(TypedDict):
    id: int
    name: str
    steps: List["ChainStepData"]


class ChainStepData(TypedDict):
    id: int
    name: str
    message: str
    text_input: bool
    next_step_id: Optional[int]


class BotResponse(TypedDict):
    success: bool
    data: Union[Dict[str, Any], List[Dict[str, Any]]]
    error: Optional[str]
