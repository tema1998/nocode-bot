from pathlib import Path
from typing import Annotated, Dict, Any

from fastapi import APIRouter, Body, Depends, status
from telegram import Update

from src.create_fastapi_app import application

router = APIRouter()

# Обработчик вебхука
@router.post("/webhook")
async def handle_webhook(update: Dict[Any, Any]):
    telegram_update = Update.de_json(update, application.bot)
    await application.initialize()  # Инициализация приложения
    await application.process_update(telegram_update)
    return {"status": "ok"}