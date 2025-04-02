from typing import List, Optional

from pydantic import BaseModel


class PatchWelcomeMessageRequest(BaseModel):
    welcome_message: str


class PatchWelcomeMessageResponse(PatchWelcomeMessageRequest):
    bot_id: int


class ButtonCreateRequest(BaseModel):
    bot_id: int
    button_text: str
    reply_text: str
    chain_id: Optional[int]


class ButtonUpdateRequest(BaseModel):
    button_text: str
    reply_text: str
    chain_id: Optional[int] = None


class ButtonResponse(BaseModel):
    id: int
    bot_id: int
    button_text: str
    reply_text: str
    chain_id: Optional[int] = None
    chain: Optional[str] = None


class ButtonUpdateResponse(BaseModel):
    id: int
    bot_id: int
    button_text: str
    reply_text: str


class MainMenuResponse(BaseModel):
    welcome_message: Optional[str] = None
    buttons: List[ButtonResponse] = []
