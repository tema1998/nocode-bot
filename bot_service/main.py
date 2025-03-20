import logging
from logging.handlers import TimedRotatingFileHandler

from bot_service.create_fastapi_app import create_app
from bot_service.models.bot import Bot
from bot_service.repositories.async_pg_repository import get_repository
from bot_service.routers.v1 import (
    bot,
    button,
    chain,
    command,
    main_menu,
    webhook,
)
from fastapi import HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware


app = create_app(
    create_custom_static_urls=True,
)

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        TimedRotatingFileHandler(
            "error.log", when="midnight", backupCount=7
        ),  # Ротация каждый день
        logging.StreamHandler(),
    ],
)


@app.middleware("http")
async def verify_secret_token(request: Request, call_next):
    if not request.url.path.startswith("/api/v1/webhook/"):
        return await call_next(request)

    # Получаем bot_id из пути
    bot_id = request.url.path.split("/")[-1]
    if not bot_id.isdigit():
        return await call_next(request)

    # Получаем secret_token из заголовка
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if not secret_token:
        raise HTTPException(status_code=403, detail="Secret token is missing")

    # Получаем бота из базы данных
    repository = await get_repository()
    bot = await repository.fetch_by_id(Bot, int(bot_id))
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Проверяем secret_token
    if bot.secret_token != secret_token:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    # Продолжаем обработку запроса
    return await call_next(request)


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "http://0.0.0.0:8080",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(bot.router, prefix="/api/v1/bot", tags=["bot"])
app.include_router(
    main_menu.router, prefix="/api/v1/main-menu", tags=["main-menu"]
)
app.include_router(button.router, prefix="/api/v1/button", tags=["button"])
app.include_router(webhook.router, prefix="/api/v1/webhook", tags=["webhook"])
app.include_router(command.router, prefix="/api/v1/command", tags=["command"])
app.include_router(chain.router, prefix="/api/v1/chain", tags=["chain"])
