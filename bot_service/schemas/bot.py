from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BotCreate(BaseModel):
    token: str


class BotCreateResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class BotGetResponse(BaseModel):
    is_active: bool
    token: str
    username: str
    name: str | None
    default_reply: str | None

    class Config:
        from_attributes = True


class BotPatchRequest(BaseModel):
    is_active: Optional[bool] = None
    token: Optional[str] = None
    default_reply: Optional[str] = None


class BotPatchResponse(BaseModel):
    is_active: bool
    token: str
    username: str
    default_reply: str


class CommandCreate(BaseModel):
    command: str
    response: str
    bot_id: int


class FunnelCreate(BaseModel):
    name: str
    bot_id: int


class FunnelStepCreate(BaseModel):
    text: str


class ButtonCreate(BaseModel):
    step_id: int
    text: str
    next_step_id: int


class BotUserSchema(BaseModel):
    """Schema for BotUser representation"""

    id: int
    bot_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedBotUsersResponse(BaseModel):
    """Response model for paginated bot users"""

    users: List[BotUserSchema]  # Use the Pydantic schema here
    total_count: int
    offset: int
    limit: int
    has_more: bool


class MailingRequest(BaseModel):
    message: str
