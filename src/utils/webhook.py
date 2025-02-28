from src.core.configs import config
from telegram.ext import Application


async def set_webhook(bot_id: str, bot_token: str, bot_secret_token: str):
    webhook_url = f"{config.webhook_url}/api/v1/webhook/{bot_id}"  # Замените на ваш домен
    application = Application.builder().token(bot_token).build()

    await application.bot.set_webhook(
        url=webhook_url,
        secret_token=bot_secret_token,
    )
