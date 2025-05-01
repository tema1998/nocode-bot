import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from bot_service.create_fastapi_app import create_app
from bot_service.models.bot import Bot
from bot_service.repositories.async_pg_repository import get_repository
from bot_service.routers.v1 import (
    bot,
    chain,
    chain_button,
    chain_step,
    mailing,
    main_menu,
    webhook,
)
from fastapi import HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware


app = create_app(
    create_custom_static_urls=True,
)

LOG_DIR = Path(__file__).resolve().parent / "logs" / "bot-service"
LOG_DIR.mkdir(parents=True, exist_ok=True)


log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

log_file = LOG_DIR / "bot_service.log"
file_handler = RotatingFileHandler(
    str(log_file), maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


@app.middleware("http")
async def verify_secret_token(request: Request, call_next):
    if not request.url.path.startswith("/api/v1/webhook/"):
        return await call_next(request)

    bot_id = request.url.path.split("/")[-1]
    if not bot_id.isdigit():
        return await call_next(request)

    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if not secret_token:
        raise HTTPException(status_code=403, detail="Secret token is missing")

    repository = await get_repository()
    bot = await repository.fetch_by_id(Bot, int(bot_id))
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    if bot.secret_token != secret_token:
        raise HTTPException(status_code=403, detail="Invalid secret token")

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


app.include_router(bot.router, prefix="/api/v1/bots", tags=["bot"])
app.include_router(main_menu.router, prefix="/api/v1/menu", tags=["main-menu"])
app.include_router(webhook.router, prefix="/api/v1/webhook", tags=["webhook"])
app.include_router(chain.router, prefix="/api/v1/chains", tags=["chain"])
app.include_router(
    chain_step.router, prefix="/api/v1/steps", tags=["chain-step"]
)
app.include_router(
    chain_button.router, prefix="/api/v1/buttons", tags=["chain-button"]
)
app.include_router(mailing.router, prefix="/api/v1/mailing", tags=["mailing"])
