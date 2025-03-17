from bot_service.core.configs import config
from bot_service.models import UserState
from bot_service.models.bot import Bot
from bot_service.models.main_menu import Button, MainMenu
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from bot_service.services.chain_service import ChainService, get_chain_service
from fastapi import HTTPException
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application


class WebhookService:
    """
    Service to handle incoming Telegram webhook updates and process bot interactions.
    """

    def __init__(
        self,
        db_repository: PostgresAsyncRepository,
        chain_service: ChainService,
    ):
        """
        Initialize the WebhookService with a database repository and a chain service.

        Args:
            db_repository (PostgresAsyncRepository): The repository for database operations.
            chain_service (ChainService): The service for handling chain-related operations.
        """
        self.db_repository = db_repository
        self.chain_service = chain_service

    async def handle_webhook(self, bot_id: int, update_data: dict) -> dict:
        """
        Handle incoming webhook update from Telegram.

        Args:
            bot_id (int): The ID of the bot.
            update_data (dict): The incoming update data from Telegram.

        Returns:
            dict: A status message indicating the result of the operation.

        Raises:
            HTTPException: If the bot is not found, is deactivated, or the update data is invalid.
        """
        # Fetch the bot from the database
        bot = await self.db_repository.fetch_by_id_joinedload(
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
        if update is None:
            raise HTTPException(
                status_code=400, detail="Failed to parse update data."
            )

        # Process the update based on its type
        if update.callback_query is not None:
            await self.chain_service.process_chain_step(update)
        elif update.message is not None and update.message.text == "/start":
            await self._handle_start_command(bot, update)
        elif update.message is not None:
            await self._handle_message(bot, update)
        else:
            raise HTTPException(
                status_code=400, detail="Unsupported update type."
            )

        return {"status": "ok"}

    async def _handle_start_command(self, bot: Bot, update: Update) -> None:
        """
        Handle the /start command.

        Args:
            bot (Bot): The bot instance.
            update (Update): The incoming update from Telegram.

        Raises:
            HTTPException: If the update has no message.
        """
        if update.message is None:
            raise HTTPException(
                status_code=400, detail="Update has no message."
            )

        # Create a default keyboard
        keyboard = [
            [
                KeyboardButton(
                    "Bot created using a constructor developed by tema1998"
                )
            ]
        ]
        welcome_message = config.bot_default_welcome_message

        # Fetch the main menu from the database
        main_menu = await self.db_repository.fetch_by_id_joinedload(
            MainMenu, bot.main_menu.id, "buttons"
        )

        # Update the welcome message if the main menu has a custom message
        if main_menu and main_menu.welcome_message:
            welcome_message = main_menu.welcome_message

        # Add main menu buttons to the keyboard
        if main_menu and main_menu.buttons:
            main_menu_buttons = [
                [KeyboardButton(button.button_text)]
                for button in main_menu.buttons
            ]
            keyboard = main_menu_buttons + keyboard

        # Send the welcome message with the keyboard
        await update.message.reply_text(
            welcome_message,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )

    async def _handle_button_press(self, bot: Bot, update: Update) -> None:
        """
        Handle button press events.

        Args:
            bot (Bot): The bot instance.
            update (Update): The incoming update from Telegram.

        Raises:
            HTTPException: If the update has no message.
        """

        if not update.message:
            return

        # Fetch the button from the database
        button = await self.db_repository.fetch_by_query_one(
            Button,
            {
                "button_text": update.message.text,
                "bot_id": bot.id,
            },
        )

        if button and button.chain_id:
            # Start a chain if the button is linked to one
            await self.chain_service.start_chain(
                int(bot.id), update, button.chain_id
            )
        elif button and button.reply_text:
            # Send the button's reply text
            reply_text = str(button.reply_text)  # Convert Column[str] to str
            await update.message.reply_text(reply_text)
        else:
            # Send a default reply if no button is found
            await update.message.reply_text(
                str(bot.default_reply)
                if bot.default_reply
                else config.bot_default_reply
            )

    async def _handle_message(self, bot: Bot, update: Update) -> None:

        if not update.message or not update.message.from_user:
            return
        # Get user state
        user_state = await self.db_repository.fetch_by_query_one_last_updated(
            UserState,
            {
                "user_id": update.message.from_user.id,
                "expects_text_input": True,
            },
        )

        # Check user.state.expects_text_input
        if user_state:
            await self.chain_service.handle_chain_text_input(
                update, user_state
            )
        else:
            await self._handle_button_press(bot, update)


async def get_webhook_service() -> WebhookService:
    """
    Dependency function to get an instance of WebhookService.

    Returns:
        WebhookService: An instance of WebhookService.
    """

    return WebhookService(
        db_repository=PostgresAsyncRepository(dsn=config.dsn),
        chain_service=await get_chain_service(),
    )
