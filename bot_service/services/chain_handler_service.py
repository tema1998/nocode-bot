import json
from typing import Any, Optional

import telegram
from bot_service.core.configs import config
from bot_service.models.chain import Chain, ChainButton, ChainStep, UserState
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from fastapi import HTTPException
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
)


class ChainHandlerService:
    """
    Service to handle chain-related operations for the bot, including starting chains,
    processing steps, handling text input, and sending messages with inline keyboards.
    """

    def __init__(self, db_repository: PostgresAsyncRepository):
        """
        Initialize the ChainHandlerService with a database repository.

        Args:
            db_repository (PostgresAsyncRepository): The repository for database operations.
        """
        self.db_repository = db_repository

    async def start_chain(
        self, bot_id: int, update: Update, chain_id: int
    ) -> None:
        """
        Start a chain of steps for the user.

        Args:
            bot_id (int): The ID of the bot.
            update (Update): The incoming update from Telegram.
            chain_id (int): The ID of the chain to start.

        Raises:
            HTTPException: If the update has no valid user ID or the chain/step is not found.
        """
        user_id = self._extract_user_id(update)
        if not user_id:
            raise HTTPException(
                status_code=400, detail="Update has no valid user ID."
            )

        chain, first_step = await self._fetch_chain_and_first_step(chain_id)
        if not chain or not first_step:
            await self._send_chain_not_found_message(update)
            return

        user_state = await self._create_user_state(
            user_id, bot_id, chain, first_step
        )
        await self.send_step_message(update, first_step, user_state)

    async def process_chain_step(self, update: Update) -> None:
        """
        Process the current step in the chain and move to the next step.

        Args:
            update (Update): The incoming update from Telegram.

        Raises:
            HTTPException: If the callback query or its data is invalid.
        """
        callback_data = self._validate_and_parse_callback_query(update)
        user_state, button = await self._fetch_user_state_and_button(
            callback_data
        )
        if not user_state or not button:
            return

        step = await self.db_repository.fetch_by_id(
            ChainStep, user_state.step_id
        )
        if not step:
            return

        await self._acknowledge_callback_query(update)
        await self._save_chain_step_result(
            user_state,
            step.message,
            button.text,
        )

        next_step = await self._fetch_next_step(button.next_step_id)
        if not next_step:
            return

        await self._update_user_state_and_send_next_step(
            update, user_state, next_step
        )

    async def handle_chain_text_input(
        self, update: Update, user_state: UserState
    ) -> None:
        """
        Handle text input from the user during a chain step.

        Args:
            update (Update): The incoming update from Telegram.
            user_state (UserState): The user's current state.
        """
        if not update.message:
            return

        text_input = update.message.text
        current_step = await self._fetch_current_step(user_state)
        if not current_step:
            return

        await self._save_chain_step_result(
            user_state, current_step.message, text_input
        )
        await self.remove_reply_buttons(update, user_state)

        if current_step.next_step_id:
            next_step = await self._fetch_next_step(current_step.next_step_id)
            if next_step:
                await self._update_user_state_and_send_next_step(
                    update, user_state, next_step
                )

        user_state.expects_text_input = False  # type: ignore
        await self.db_repository.update(user_state)

    async def remove_reply_buttons(
        self, update: Update, user_state: UserState
    ) -> None:

        if not update.message or not user_state.last_message_id:
            raise HTTPException(
                status_code=400,
                detail="Update has no valid message or last_message_id is not set.",
            )

        try:
            await update.get_bot().edit_message_reply_markup(
                chat_id=int(update.message.chat_id),
                message_id=int(user_state.last_message_id),
                reply_markup=None,
            )
        except telegram.error.BadRequest as e:

            if "Message is not modified" not in str(
                e
            ) and "Message to edit not found" not in str(e):
                raise

    async def send_step_message(
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
        buttons = await self._fetch_buttons_for_step(int(step.id))
        keyboard = self._create_keyboard(buttons, user_state)

        message = await self._send_or_edit_message(
            update, str(step.message), keyboard
        )
        if message:
            user_state.last_message_id = message.message_id  # type: ignore
            await self.db_repository.update(user_state)

    async def _create_user_state(
        self, user_id: int, bot_id: int, chain: Chain, first_step: ChainStep
    ) -> UserState:
        """
        Create and save a new UserState object in the database.

        Args:
            user_id (int): The ID of the user.
            bot_id (int): The ID of the bot.
            chain (Chain): The chain object.
            first_step (ChainStep): The first step of the chain.

        Returns:
            UserState: The created UserState object.
        """
        user_state = UserState(
            user_id=user_id,
            bot_id=bot_id,
            chain_id=chain.id,
            step_id=first_step.id,
            expects_text_input=bool(first_step.text_input),
        )
        await self.db_repository.insert(user_state)
        return user_state

    def _validate_and_parse_callback_query(self, update: Update) -> dict | Any:
        """
        Validate and parse the callback query data.

        Args:
            update (Update): The incoming update from Telegram.

        Returns:
            dict: The parsed callback data.

        Raises:
            HTTPException: If the callback query or its data is invalid.
        """
        if not update.callback_query or not update.callback_query.data:
            raise HTTPException(
                status_code=400,
                detail="Callback query or its data is missing.",
            )

        try:
            callback_data = json.loads(update.callback_query.data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, detail="Invalid callback data format."
            )

        return callback_data

    async def _save_chain_step_result(
        self, user_state: UserState, message: str, result: str | None
    ) -> None:
        """
        Save the result of a specific step in the user's state.

        Args:
            user_state (UserState): The user's current state.
            message (str): The text of the step.
            result (str | None): The result to save.
        """
        if user_state.result is None:
            user_state.result = {}

        user_state.result.update({message: result})
        await self.db_repository.update(user_state)

    async def _fetch_chain_and_first_step(self, chain_id: int):
        """Fetch the chain and its first step from the database."""
        chain = await self.db_repository.fetch_by_query_one(
            Chain, {"id": chain_id}
        )
        if not chain:
            return None, None

        first_step = await self.db_repository.fetch_by_query_one(
            ChainStep, {"id": chain.first_chain_step_id}
        )
        return chain, first_step

    async def _fetch_user_state_and_button(self, callback_data: dict):
        """Fetch the user's state and the button from the database."""
        user_state = await self.db_repository.fetch_by_query_one(
            UserState, {"id": callback_data.get("user_state_id")}
        )
        button = await self.db_repository.fetch_by_query_one(
            ChainButton, {"id": callback_data.get("button_id")}
        )
        return user_state, button

    async def _fetch_next_step(self, next_step_id: int):
        """Fetch the next step in the chain."""
        return await self.db_repository.fetch_by_id(ChainStep, next_step_id)

    async def _fetch_current_step(self, user_state: UserState):
        """Fetch the current step from the database."""
        return await self.db_repository.fetch_by_id(
            ChainStep, int(user_state.step_id)
        )

    async def _fetch_buttons_for_step(self, step_id: int):
        """Fetch buttons for the current step."""
        return await self.db_repository.fetch_by_query(
            ChainButton, {"step_id": step_id}
        )

    def _create_keyboard(
        self, buttons: list[ChainButton], user_state: UserState
    ):
        """Create an inline keyboard for the step."""
        return (
            [
                [
                    InlineKeyboardButton(
                        str(button.text),
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
            if buttons
            else []
        )

    async def _send_or_edit_message(
        self, update: Update, message_text: str, keyboard: list
    ) -> Optional[Message]:
        """Send or edit a message with the given text and keyboard."""
        if update.callback_query and isinstance(
            update.callback_query.message, Message
        ):
            return await update.callback_query.message.reply_text(
                message_text, reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif update.message:
            return await update.message.reply_text(
                message_text, reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Update has no valid message or callback query.",
            )

    def _extract_user_id(self, update: Update) -> Optional[int]:
        """Extract the user ID from the update."""
        if update.callback_query and update.callback_query.from_user:
            return update.callback_query.from_user.id
        elif update.message and update.message.from_user:
            return update.message.from_user.id
        return None

    async def _send_chain_not_found_message(self, update: Update) -> None:
        """Send a message indicating that the chain or step was not found."""
        if update.message:
            await update.message.reply_text("Цепочка не найдена.")

    async def _acknowledge_callback_query(self, update: Update) -> None:
        """Acknowledge the callback query and update the message."""
        if update.callback_query:
            try:
                await update.callback_query.answer()
                await update.callback_query.edit_message_reply_markup(
                    reply_markup=None
                )
            except telegram.error.BadRequest as e:
                if "Query is too old" in str(e):
                    pass
                else:
                    raise

    async def _update_user_state_and_send_next_step(
        self, update: Update, user_state: UserState, next_step: ChainStep
    ) -> None:
        """Update the user's state and send the message for the next step."""
        user_state.step_id = next_step.id
        user_state.expects_text_input = next_step.text_input
        await self.db_repository.update(user_state)
        await self.send_step_message(update, next_step, user_state)


async def get_chain_handler_service() -> ChainHandlerService:
    """
    Dependency function to get an instance of ChainHandlerService.

    Returns:
        ChainHandlerService: An instance of ChainHandlerService.
    """
    return ChainHandlerService(
        db_repository=PostgresAsyncRepository(dsn=config.dsn)
    )
