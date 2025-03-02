from bot_service.core.configs import config
from telegram.ext import Application


async def set_webhook(
    bot_id: str, bot_token: str, bot_secret_token: str
) -> None:
    """
    Sets up a webhook for the Telegram bot.

    Args:
        bot_id (str): The unique identifier of the bot.
        bot_token (str): The Telegram bot token.
        bot_secret_token (str): The secret token for securing the webhook.
    """

    webhook_url = f"{config.webhook_url}/api/v1/webhook/{bot_id}"
    application = Application.builder().token(bot_token).build()

    await application.bot.set_webhook(
        url=webhook_url,
        secret_token=bot_secret_token,
    )
