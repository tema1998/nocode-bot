from typing import List, Optional

from pydantic import BaseModel


class PatchWelcomeMessageRequest(BaseModel):
    welcome_message: str


class PatchWelcomeMessageResponse(PatchWelcomeMessageRequest):
    bot_id: int


class ButtonResponse(BaseModel):
    id: int
    button_text: str
    reply_text: str


class MainMenuResponse(BaseModel):
    welcome_message: Optional[str] = None
    buttons: List[ButtonResponse] = []
