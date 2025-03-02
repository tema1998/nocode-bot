from telegram.ext import Application


async def get_bot_username(bot_token: str) -> str | None:
    """
    Retrieves the bot's username.

    Args:
        bot_token (str): The Telegram bot token.

    Returns:
        str: The username of the bot (e.g., "@my_bot").
    """

    application = Application.builder().token(bot_token).build()

    bot_info = await application.bot.get_me()
    bot_username = bot_info.username

    return bot_username


async def get_bot_name(bot_token: str) -> str | None:
    """
    Retrieves the bot's name.

    Args:
        bot_token (str): The Telegram bot token.

    Returns:
        str: The name of the bot.
    """

    application = Application.builder().token(bot_token).build()

    bot_info = await application.bot.get_me()
    bot_name = bot_info.first_name

    return bot_name
