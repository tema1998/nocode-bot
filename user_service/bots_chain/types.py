from typing import Dict, List, Optional, TypedDict, Union


class ChainData(TypedDict):
    id: int
    name: str


class ChainStepData(TypedDict):
    id: int
    name: str
    message: str
    text_input: Optional[bool]
    next_step_id: Optional[int]


class ChainButtonData(TypedDict):
    id: int
    text: str
    step_id: int
    next_step_id: Optional[int]


class ChainResultsData(TypedDict):
    items: List[Dict[str, Union[str, int, bool]]]
