from pydantic import BaseModel


class BotCreate(BaseModel):
    token: str


class BotCreateResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class BotResponse(BaseModel):
    """
    Pydantic model for representing bot details in API responses.
    """

    is_active: bool
    token: str
    username: str
    name: str | None

    class Config:
        from_attributes = True


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
