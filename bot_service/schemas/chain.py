from typing import Optional

from pydantic import BaseModel


class ChainCreate(BaseModel):
    bot_id: int
    name: str


class ChainUpdate(BaseModel):
    name: Optional[str] = None


class ChainResponse(BaseModel):
    id: int
    bot_id: int
    name: str

    class Config:
        from_attributes = True


class ChainsResponse(BaseModel):
    chains: list[ChainResponse]
