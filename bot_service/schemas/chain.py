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
    user_id: int = Field(..., example=123456789)
    username: Optional[str] = Field(None, example="john_doe")
    first_name: str = Field(..., example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    photo: Optional[HttpUrl] = Field(
        None, example="https://example.com/photo.jpg"
    )
    answers: Dict[str, str] = Field(..., example={"1": "Yes", "2": "No"})
    last_interaction: datetime = Field(..., example="2023-01-01T12:00:00Z")
    current_step: Optional[int] = Field(None, example=5)


class ChainResultsResponse(BaseModel):
    items: List[UserResult]
    total: int = Field(..., example=100)
    page: int = Field(..., example=1)
    per_page: int = Field(..., example=10)
    total_pages: int = Field(..., example=10)
