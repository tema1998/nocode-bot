from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import ORJSONResponse
from src.bot_handlers import BotHandlers
from src.core.configs import config, logger
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)


def register_static_docs_routes(app: FastAPI):
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)  # type: ignore
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
        )


# Инициализация приложения бота
application = (
    ApplicationBuilder().read_timeout(30).token(config.bot_token).build()
)
# Регистрируем универсальный обработчик команд
bot_handlers = BotHandlers()
application.add_handler(
    MessageHandler(filters.TEXT & filters.COMMAND, bot_handlers.handle_command)
)
application.add_handler(
    CallbackQueryHandler(bot_handlers.button_callback)
)  # Обработчик инлайн-кнопок


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Установка вебхука при запуске
    await application.bot.set_webhook(
        url=config.webhook_url, secret_token=config.secret_token
    )
    logger.info(config.webhook_url)
    logger.info("Webhook установлен!")
    yield
    # Очистка при завершении (если нужно)
    logger.info("Приложение завершает работу...")


def create_app(
    create_custom_static_urls: bool = False,
) -> FastAPI:
    app = FastAPI(
        title=config.app_name,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url=None if create_custom_static_urls else "/docs",
        redoc_url=None if create_custom_static_urls else "/redoc",
    )
    if create_custom_static_urls:
        register_static_docs_routes(app)
    return app
