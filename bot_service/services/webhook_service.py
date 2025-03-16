import json

from bot_service.core.configs import config
from bot_service.models.bot import (
    Bot,
    Button,
    Chain,
    ChainButton,
    ChainStep,
    MainMenu,
    UserState,
)
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from fastapi import HTTPException
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import Application


class WebhookService:
    """
    Service to handle incoming Telegram webhook updates and process bot interactions.
    """

    def __init__(self, db_repository: PostgresAsyncRepository):
        """
        Initialize the WebhookService with a database repository.

        Args:
            db_repository (PostgresAsyncRepository): The repository for database operations.
        """
        self.db_repository = db_repository

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
            await self._process_chain_step(bot, update)
        elif update.message is not None and update.message.text == "/start":
            await self._handle_start_command(bot, update)
        elif update.message is not None:
            await self._handle_button_press(bot, update)
        else:
            raise HTTPException(
                status_code=400, detail="Unsupported update type."
            )

        return {"status": "ok"}

    async def _start_chain(
        self, bot: Bot, update: Update, chain_id: int
    ) -> None:
        """
        Start a chain of steps for the user.

        Args:
            bot (Bot): The bot instance.
            update (Update): The incoming update from Telegram.
            chain_id (int): The ID of the chain to start.

        Raises:
            HTTPException: If the update has no valid user ID or the chain/step is not found.
        """
        if (
            update.callback_query is not None
            and update.callback_query.from_user is not None
        ):
            user_id = update.callback_query.from_user.id
        elif (
            update.message is not None and update.message.from_user is not None
        ):
            user_id = update.message.from_user.id
        else:
            raise HTTPException(
                status_code=400, detail="Update has no valid user ID."
            )

        # Fetch the chain from the database
        chain = await self.db_repository.fetch_by_query_one(
            Chain, {"id": chain_id}
        )
        if not chain:
            if update.message is not None:
                await update.message.reply_text("Chain not found.")
            return

        # Fetch the first step of the chain
        first_step = await self.db_repository.fetch_by_query_one(
            ChainStep, {"id": chain.first_chain_step_id}
        )
        if not first_step:
            if update.message is not None:
                await update.message.reply_text("Error: First step not found.")
            return

        # Save the user's state in the database
        user_state = UserState(
            user_id=user_id,
            bot_id=bot.id,
            chain_id=chain.id,
            step_id=first_step.id,
        )
        await self.db_repository.insert(user_state)

        # Send the message and inline buttons for the first step
        await self._send_step_message(update, first_step, user_state)

    async def _process_chain_step(self, bot: Bot, update: Update) -> None:
        """
        Process the current step in the chain and move to the next step.

        Args:
            bot (Bot): The bot instance.
            update (Update): The incoming update from Telegram.

        Raises:
            HTTPException: If the callback query or its data is invalid.
        """
        if update.callback_query is None or update.callback_query.data is None:
            raise HTTPException(
                status_code=400,
                detail="Callback query or its data is missing.",
            )

        # Parse callback data from the inline button
        callback_data = json.loads(update.callback_query.data)
        button_id = callback_data.get("button_id")
        user_state_id = callback_data.get("user_state_id")

        if button_id is None or user_state_id is None:
            raise HTTPException(
                status_code=400, detail="Invalid callback data."
            )

        # Fetch the user's current state
        user_state = await self.db_repository.fetch_by_query_one(
            UserState, {"id": user_state_id}
        )
        if not user_state:
            return

        # Fetch the button that was pressed
        button = await self.db_repository.fetch_by_query_one(
            ChainButton, {"id": button_id}
        )
        if not button:
            return

        # Acknowledge the callback query
        await update.callback_query.answer()

        # Update the message with the button's callback text
        await update.callback_query.edit_message_text(
            f"You pressed: {button.callback}"
        )

        # Fetch the next step in the chain
        next_step = await self.db_repository.fetch_by_id(
            ChainStep, button.next_step_id
        )
        if not next_step:
            return

        # Update the user's state to the next step
        user_state.step_id = next_step.id
        await self.db_repository.update(user_state)

        # Send the message and buttons for the next step
        await self._send_step_message(update, next_step, user_state)

    async def _send_step_message(
        self, update: Update, step: ChainStep, user_state: UserState
    ) -> None:
        """
        Send a message with inline keyboard buttons for the current step.

        Args:
            update (Update): The incoming update from Telegram.
            step (ChainStep): The current step in the chain.
            user_state (UserState): The user's current state.

        Raises:
            HTTPException: If the update has no valid message or callback query.
        """
        # Fetch buttons for the current step
        buttons = await self.db_repository.fetch_by_query(
            ChainButton, {"step_id": step.id}
        )

        if buttons:
            # Create inline keyboard buttons
            keyboard = [
                [
                    InlineKeyboardButton(
                        button.text,
                        callback_data=json.dumps(
                            {
                                "button_id": button.id,
                                "user_state_id": user_state.id,
                            }
                        ),
                    )
                ]
                for button in buttons
            ]
        else:
            keyboard = []

        # Send the message with inline buttons
        if update.callback_query is not None and isinstance(
            update.callback_query.message, Message
        ):
            await update.callback_query.message.reply_text(
                str(step.message),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        elif update.message is not None:
            await update.message.reply_text(
                str(step.message),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Update has no valid message or callback query.",
            )

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
        if update.message is None:
            raise HTTPException(
                status_code=400, detail="Update has no message."
            )

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
            await self._start_chain(
                bot=bot, update=update, chain_id=button.chain_id
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


async def get_webhook_service() -> WebhookService:
    """
    Dependency function to get an instance of WebhookService.

    Returns:
        WebhookService: An instance of WebhookService.
    """
    return WebhookService(
        db_repository=PostgresAsyncRepository(dsn=config.dsn)
    )
