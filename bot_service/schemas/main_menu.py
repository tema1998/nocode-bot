from typing import List, Optional

from pydantic import BaseModel


class ButtonResponse(BaseModel):
    id: int
    button_text: str
    reply_text: str


class MainMenuResponse(BaseModel):
    welcome_message: Optional[str] = None
    buttons: List[ButtonResponse] = []
