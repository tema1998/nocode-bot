from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, HttpUrl
from pydantic.v1 import Field


class ChainCreate(BaseModel):
    bot_id: int
    name: str


class ChainUpdate(BaseModel):
    name: Optional[str] = None
    first_chain_step_id: Optional[int] = None


class ChainResponse(BaseModel):
    id: int
    bot_id: int
    name: str

    class Config:
        from_attributes = True


class ChainsResponse(BaseModel):
    chains: list[ChainResponse]


class UserResult(BaseModel):
    user_id: int = Field(...)
    username: Optional[str] = Field(None)
    first_name: str = Field(...)
    last_name: Optional[str] = Field(None)
    photo: Optional[HttpUrl] = Field(None)
    answers: Dict[str, str] = Field(...)
    last_interaction: datetime = Field(...)
    current_step: Optional[int] = Field(None)


class ChainResultsResponse(BaseModel):
    items: List[UserResult]
    total: int = Field(...)
    page: int = Field(...)
    per_page: int = Field(...)
    total_pages: int = Field(...)
