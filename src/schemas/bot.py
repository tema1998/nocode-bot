from pydantic import BaseModel


# Модели Pydantic для запросов
class BotCreate(BaseModel):
    token: str
    name: str


class CommandCreate(BaseModel):
    command: str
    response: str
    bot_id: int
