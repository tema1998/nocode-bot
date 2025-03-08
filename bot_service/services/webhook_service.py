from bot_service.core.configs import config
from bot_service.models.bot import Bot, Button, MainMenu
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from fastapi import HTTPException
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application


class WebhookService:
    def __init__(self, repository: PostgresAsyncRepository):
        self.repository = repository

    async def handle_webhook(self, bot_id: int, update_data: dict) -> dict:
        """
        Handle incoming webhook update.

        Args:
            bot_id (int): The ID of the bot.
            update_data (dict): The incoming update data from Telegram.

        Returns:
            dict: A status message indicating the result of the operation.
        """
        # Fetch the bot from the database
        bot = await self.repository.fetch_by_id_joinedload(
            Bot, bot_id, "main_menu"
        )
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        if not bot.is_active:
            raise HTTPException(status_code=403, detail="Bot is deactivated.")

        # Create an instance of Application using the bot's token
        application = Application.builder().token(bot.token).build()

        # Convert JSON to Update object
        update = Update.de_json(update_data, application.bot)

        # Handle the update based on the message text
        if update.message.text == "/start":  # type:ignore
            await self._handle_start_command(bot, update)  # type:ignore
        else:
            await self._handle_button_press(bot, update)  # type:ignore

        return {"status": "ok"}

    async def _handle_start_command(self, bot: Bot, update: Update) -> None:
        """
        Handle the /start command.

        Args:
            bot (Bot): The bot instance.
            update (Update): The incoming update from Telegram.
        """
        keyboard = [
            [
                KeyboardButton(
                    "Bot created using a constructor developed by tema1998"
                )
            ]
        ]
        welcome_message = config.bot_default_welcome_message

        # Check if the bot has a main menu
        if bot.main_menu:
            main_menu = await self.repository.fetch_by_id_joinedload(
                MainMenu, bot.main_menu.id, "buttons"
            )

            # Update welcome message if main menu has one
            if main_menu and main_menu.welcome_message:
                welcome_message = main_menu.welcome_message

            # Add main menu buttons to the keyboard
            if main_menu and main_menu.buttons:
                main_menu_buttons = [
                    [KeyboardButton(button.button_text)]
                    for button in main_menu.buttons
                ]
                keyboard = main_menu_buttons + keyboard

        # Send welcome message with the keyboard
        await update.message.reply_text(  # type: ignore
            welcome_message,
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )

    async def _handle_button_press(self, bot: Bot, update: Update) -> None:
        """
        Handle button press.

        Args:
            bot (Bot): The bot instance.
            update (Update): The incoming update from Telegram.
        """
        button = await self.repository.fetch_by_query_one(
            Button,
            {
                "button_text": update.message.text,  # type:ignore
                "bot_id": bot.id,
            },
        )

        if button:
            await update.message.reply_text(button.reply_text)  # type: ignore
        else:
            # Send default reply if no button is found
            await update.message.reply_text(  # type: ignore
                str(bot.default_reply)
                if bot.default_reply
                else config.bot_default_reply
            )


async def get_webhook_service() -> WebhookService:
    """Dependency function to get the WebhookService instance."""
    return WebhookService(repository=PostgresAsyncRepository(dsn=config.dsn))
