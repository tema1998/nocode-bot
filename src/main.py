from fastapi import HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from src.create_fastapi_app import create_app
from src.models.bot import Bot
from src.repositories.async_pg_repository import get_repository
from src.routers.v1 import bot


app = create_app(
    create_custom_static_urls=True,
)


@app.middleware("http")
async def verify_secret_token(request: Request, call_next):
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


app.include_router(bot.router, prefix="/api/v1", tags=["bot"])
