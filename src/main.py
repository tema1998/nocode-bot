from fastapi import HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from src.core.configs import config
from src.create_fastapi_app import create_app
from src.routers.v1 import bot


app = create_app(
    create_custom_static_urls=True,
)


# Middleware для проверки секретного токена
@app.middleware("http")
async def verify_secret_token(request: Request, call_next):
    if request.url.path == "/webhook":
        if (
            request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            != config.secret_token
        ):
            raise HTTPException(status_code=403, detail="Forbidden")
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
