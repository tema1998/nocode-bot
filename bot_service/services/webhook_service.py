from datetime import datetime, timedelta

from bot_service.core.configs import config
from bot_service.models import UserState
from bot_service.models.bot import Bot, BotUser
from bot_service.models.main_menu import Button, MainMenu
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from bot_service.services.chain_handler_service import (
    ChainHandlerService,
    get_chain_handler_service,
)
from fastapi import HTTPException
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application


class WebhookService:
    """
    Service to handle incoming Telegram webhook updates and process bot interactions.
    """

    def __init__(
        self,
        db_repository: PostgresAsyncRepository,
        chain_handler_service: ChainHandlerService,
    ):
        """
        Initialize the WebhookService with a database repository and a chain service.

        Args:
            db_repository (PostgresAsyncRepository): The repository for database operations.
            chain_handler_service (ChainHandlerService): The service for handling chain-related operations.
        """
        self.db_repository = db_repository
        self.chain_handler_service = chain_handler_service
        self.default_keyboard = [
            [
                KeyboardButton(
                    "Бот создан с помощью платформы nocode-bot.ru",
                    web_app=WebAppInfo(url="https://nocode-bot.ru"),
                )
            ]
        ]

    async def handle_webhook(
        self,
        bot_id: int,
        update_data: dict,
        x_telegram_bot_api_secret_token: str,
    ) -> dict:
        """
        Handle incoming webhook update from Telegram with time-based filtering.

        Args:
            bot_id (int): The ID of the bot.
            update_data (dict): The incoming update data from Telegram.
            x_telegram_bot_api_secret_token (str): Secret token of the telegram bot.

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

        if bot.secret_token != x_telegram_bot_api_secret_token:
            return {"status": "error", "detail": "secret_token_check_error"}

        if not bot.is_active:
            return {"status": "ok", "detail": "bot_deactivated"}

        # Create an instance of Application using the bot's token
        application = Application.builder().token(bot.token).build()

        # Convert JSON to Update object
        update = Update.de_json(update_data, application.bot)
        if update is None:
            raise HTTPException(
                status_code=400, detail="Failed to parse update data."
            )

        # Save bot's user to DB
        await self._save_bot_user(bot_id, update)

        # Get current time for time comparison
        current_time = datetime.now()

        # Process the update based on its type with time checks
        if update.callback_query is not None:
            try:
                # Check callback message age
                callback_time = datetime.fromtimestamp(
                    update.callback_query.message.date.timestamp()  # type:ignore
                )
                # If the message is older than one minute, ignore it
                if current_time - callback_time > timedelta(minutes=1):
                    return {"status": "ok", "detail": "ignored_old_callback"}

                await self.chain_handler_service.process_chain_step(update)
            except AttributeError:
                # Handle case where callback message or date is missing
                return {"status": "error", "detail": "invalid_callback_format"}

        elif update.message is not None:
            try:
                # Check message age
                message_time = datetime.fromtimestamp(
                    update.message.date.timestamp()
                )
                # If the message is older than one minute, ignore it
                if current_time - message_time > timedelta(minutes=1):
                    return {"status": "ok", "detail": "ignored_old_message"}

                # Process specific commands
                if update.message.text == "/start":
                    await self._handle_start_command(bot, update)
                elif update.message.text == "/update":
                    await self._handle_update_command(bot, update)
                else:
                    await self._handle_message(bot, update)
            except AttributeError:
                # Handle non-text messages or missing date
                if (
                    update.message.date
                ):  # If it's a non-text message with valid date
                    return {
                        "status": "ok",
                        "detail": "unsupported_message_type",
                    }
                raise HTTPException(
                    status_code=400, detail="Invalid message format"
                )

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

        welcome_message = config.bot_default_welcome_message

        # Fetch the main menu from the database
        main_menu = await self.db_repository.fetch_by_id_joinedload(
            MainMenu, bot.main_menu.id, "buttons"
        )

        # Update the welcome message if the main menu has a custom message
        if main_menu and main_menu.welcome_message:
            welcome_message = main_menu.welcome_message

        # Get default keyboard with advertisement
        keyboard = self.default_keyboard
        # Add main menu buttons to the default keyboard
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

    async def _handle_update_command(self, bot: Bot, update: Update) -> None:
        """
        Handle the /update command.

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

        menu_update_message = "Главное меню успешно обновлено."

        # Fetch the main menu from the database
        main_menu = await self.db_repository.fetch_by_id_joinedload(
            MainMenu, bot.main_menu.id, "buttons"
        )

        # Get default keyboard with advertisement
        keyboard = self.default_keyboard
        # Add main menu buttons to the keyboard
        if main_menu and main_menu.buttons:
            main_menu_buttons = [
                [KeyboardButton(button.button_text)]
                for button in main_menu.buttons
            ]
            keyboard = main_menu_buttons + keyboard

        # Send the message that main menu was updated with the keyboard
        await update.message.reply_text(
            menu_update_message,
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

        if button:
            # Send button reply text
            if button.reply_text:
                await update.message.reply_text(str(button.reply_text))

            # Start chain
            if button.chain_id:
                await self.chain_handler_service.start_chain(
                    int(bot.id), update, button.chain_id
                )
        else:
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

        # Check if there are any chains waiting for text input
        if user_state:
            await self.chain_handler_service.handle_chain_text_input(
                update, user_state
            )
        # If not - process the button press
        else:
            await self._handle_button_press(bot, update)

    async def _save_bot_user(self, bot_id: int, update: Update) -> None:
        """
        Saves or updates bot user information in the database.

        Args:
            bot_id: The ID of the bot associated with the user
            update: Telegram Update object containing user information

        Returns:
            None: This method doesn't return anything but performs database operations
        """
        # Return early if there's no effective user in the update
        if not update.effective_user:
            return

        user = update.effective_user
        # Prepare user data dictionary for saving
        bot_user_data = {
            "user_id": user.id,
            "bot_id": bot_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

        # Check if user already exists in database
        existing_user = await self.db_repository.fetch_by_query_one(
            BotUser, {"user_id": user.id, "bot_id": bot_id}
        )

        if existing_user:
            # Update existing user record
            for key, value in bot_user_data.items():
                setattr(existing_user, key, value)
            await self.db_repository.update(existing_user)
        else:
            # Create new user record
            new_user = BotUser(**bot_user_data)
            await self.db_repository.insert(new_user)


async def get_webhook_service() -> WebhookService:
    """
    Dependency function to get an instance of WebhookService.

    Returns:
        WebhookService: An instance of WebhookService.
    """

    return WebhookService(
        db_repository=PostgresAsyncRepository(dsn=config.dsn),
        chain_handler_service=await get_chain_handler_service(),
    )
