from typing import Optional

from pydantic import BaseModel


class ChainButtonCreate(BaseModel):
    step_id: int
    text: str


class ChainButtonUpdate(BaseModel):
    text: Optional[str] = None
    next_step_id: Optional[int] = None


class ChainButtonResponse(BaseModel):
    id: int
    step_id: int
    text: str
    next_step_id: Optional[int]


class SetNextChainStepForButton(BaseModel):
    next_chain_step_id: int
