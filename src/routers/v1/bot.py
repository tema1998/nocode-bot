from typing import Any, Dict

from fastapi import APIRouter
from src.create_fastapi_app import application
from telegram import Update


router = APIRouter()


@router.post("/webhook")
async def handle_webhook(update: Dict[Any, Any]):
    telegram_update = Update.de_json(update, application.bot)
    await application.initialize()
    await application.process_update(telegram_update)
    return {"status": "ok"}
