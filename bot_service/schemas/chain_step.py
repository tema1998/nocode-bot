from typing import Optional

from pydantic import BaseModel


class ChainStepCreate(BaseModel):
    chain_id: int
    name: str
    message: str
    set_as_next_step_for_button_id: Optional[int] = None
    next_step_id: Optional[int] = None
    text_input: bool = False


class ChainStepUpdate(BaseModel):
    name: Optional[str] = None
    message: Optional[str] = None
    next_step_id: Optional[int] = None
    text_input: Optional[bool] = None


class ChainStepResponse(BaseModel):
    id: int
    chain_id: int
    name: str
    message: str
    next_step_id: Optional[int]
    text_input: bool
