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


class ButtonUpdateRequest(BaseModel):
    button_text: str
    reply_text: str


class ButtonResponse(ButtonCreateRequest):
    id: int


class MainMenuResponse(BaseModel):
    welcome_message: Optional[str] = None
    buttons: List[ButtonResponse] = []
