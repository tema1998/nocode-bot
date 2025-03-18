import json

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


class ChainService:
    """
    Service to handle chain-related operations for the bot, including starting chains,
    processing steps, handling text input, and sending messages with inline keyboards.
    """

    def __init__(self, db_repository: PostgresAsyncRepository):
        """
        Initialize the ChainService with a database repository.

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
        # Extract user ID from the update (either from callback_query or message)
        if update.callback_query and update.callback_query.from_user:
            user_id = update.callback_query.from_user.id
        elif update.message and update.message.from_user:
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
            if update.message:
                await update.message.reply_text("Цепочка не найдена.")
            return

        # Fetch the first step of the chain
        first_step = await self.db_repository.fetch_by_query_one(
            ChainStep, {"id": chain.first_chain_step_id}
        )
        if not first_step:
            if update.message:
                await update.message.reply_text("Первый шаг цепочки не задан.")
            return

        # Save the user's state in the database
        user_state = UserState(
            user_id=user_id,
            bot_id=bot_id,
            chain_id=chain.id,
            step_id=first_step.id,
            expects_text_input=bool(
                first_step.text_input
            ),  # Set expects_text_input based on the step
        )
        await self.db_repository.insert(user_state)

        # Send the message and inline buttons for the first step
        await self.send_step_message(update, first_step, user_state)

    async def process_chain_step(self, update: Update) -> None:
        """
        Process the current step in the chain and move to the next step.

        Args:
            update (Update): The incoming update from Telegram.

        Raises:
            HTTPException: If the callback query or its data is invalid.
        """
        # Validate that the update contains a callback query and data
        if not update.callback_query or update.callback_query.data is None:
            raise HTTPException(
                status_code=400,
                detail="Callback query or its data is missing.",
            )

        # Parse callback data from the inline button
        callback_data = json.loads(update.callback_query.data)
        button_id = callback_data.get("button_id")
        user_state_id = callback_data.get("user_state_id")

        # Validate that the callback data contains required fields
        if button_id is None or user_state_id is None:
            raise HTTPException(
                status_code=400, detail="Invalid callback data."
            )

        # Fetch the user's current state from the database
        user_state = await self.db_repository.fetch_by_query_one(
            UserState, {"id": user_state_id}
        )
        if not user_state:
            return

        # Fetch the button that was pressed from the database
        button = await self.db_repository.fetch_by_query_one(
            ChainButton, {"id": button_id}
        )
        if not button:
            return

        # Acknowledge the callback query to Telegram
        await update.callback_query.answer()

        # Update the message with the button's callback text
        await update.callback_query.edit_message_text(
            f"You pressed: {button.callback}"
        )

        # Save result to JSON
        await self._save_chain_step_result(
            user_state, user_state.step_id, button.callback
        )

        # Fetch the next step in the chain
        next_step = await self.db_repository.fetch_by_id(
            ChainStep, button.next_step_id
        )
        if not next_step:
            return

        # Update the user's state to the next step
        user_state.step_id = next_step.id

        # Set expects_text_input based on the next step's configuration
        user_state.expects_text_input = bool(next_step.text_input)

        # Save the updated user state to the database
        await self.db_repository.update(user_state)

        # Send the message and buttons for the next step
        await self.send_step_message(update, next_step, user_state)

    async def handle_chain_text_input(
        self, update: Update, user_state: UserState
    ) -> None:
        """
        Handle text input from the user during a chain step.

        Args:
            update (Update): The incoming update from Telegram.
            user_state (UserState): The user's current state.
        """
        # Get the text input from the user's message
        if not update.message:
            return
        text_input = update.message.text

        # Reply to the user with the text they entered
        await update.message.reply_text(f"Вы напечатали: {text_input}")

        # Fetch the current step from the database
        current_step = await self.db_repository.fetch_by_id(
            ChainStep, int(user_state.step_id)
        )
        if not current_step:
            return

        # Save result to JSON
        await self._save_chain_step_result(
            user_state, current_step.id, text_input
        )

        # If there is a next step, move to it
        if current_step.next_step_id:
            next_step = await self.db_repository.fetch_by_id(
                ChainStep, current_step.next_step_id
            )
            if not next_step:
                return  # Обработка случая, когда следующий шаг не найден

            # Update the user's state to the next step
            user_state.step_id = next_step.id

            # Set expects_text_input based on the next step's configuration
            user_state.expects_text_input = next_step.text_input

            # Send the message and buttons for the next step
            await self.send_step_message(update, next_step, user_state)

        # Update expects_text_input and save the user's state in the database
        user_state.expects_text_input = False  # type: ignore
        await self.db_repository.update(user_state)

    async def _save_chain_step_result(
        self, user_state: UserState, step_id: int, result: str | None
    ) -> None:
        """
        Save the result of a specific step in the user's state.

        This method updates the result attribute of the provided UserState object
        by adding or updating the result corresponding to the given step ID.
        If the result attribute is None, it initializes it as an empty dictionary
        before updating.

        Parameters:
        ----------
        user_state : UserState
            The current state of the user, containing results of previous steps.

        step_id : int
            The identifier of the step whose result is being saved.

        result : str
            The result of the step to be saved.

        Returns
        -------
        None
            This method does not return a value. It updates the user state
            and saves changes to the database asynchronously.
        """
        if user_state.result is None:
            user_state.result = {}

        user_state.result.update({step_id: result})

        await self.db_repository.update(user_state)

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
        # Fetch buttons for the current step from the database
        buttons = await self.db_repository.fetch_by_query(
            ChainButton, {"step_id": step.id}
        )

        # If there are no buttons or the step expects text input, use an empty keyboard
        if not buttons or step.text_input:
            keyboard = []
        else:
            # Create inline keyboard buttons for the step
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

        # Send the message with inline buttons
        if update.callback_query and isinstance(
            update.callback_query.message, Message
        ):
            await update.callback_query.message.reply_text(
                str(step.message),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        elif update.message:
            await update.message.reply_text(
                str(step.message),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Update has no valid message or callback query.",
            )


async def get_chain_service() -> ChainService:
    """
    Dependency function to get an instance of ChainService.

    Returns:
        ChainService: An instance of ChainService.
    """
    return ChainService(db_repository=PostgresAsyncRepository(dsn=config.dsn))
