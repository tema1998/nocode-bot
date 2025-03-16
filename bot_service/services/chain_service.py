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
    Service to handle chain-related operations for the bot.
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
                await update.message.reply_text("Цепочка не найдена.")
            return

        # Fetch the first step of the chain
        first_step = await self.db_repository.fetch_by_query_one(
            ChainStep, {"id": chain.first_chain_step_id}
        )
        if not first_step:
            if update.message is not None:
                await update.message.reply_text("Первый шаг цепочки не задан.")
            return

        # Save the user's state in the database
        user_state = UserState(
            user_id=user_id,
            bot_id=bot_id,
            chain_id=chain.id,
            step_id=first_step.id,
        )
        await self.db_repository.insert(user_state)

        # Send the message and inline buttons for the first step
        await self.send_step_message(update, first_step, user_state)

    async def process_chain_step(self, bot_id: int, update: Update) -> None:
        """
        Process the current step in the chain and move to the next step.

        Args:
            bot_id (int): The ID of the bot.
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
        await self.send_step_message(update, next_step, user_state)

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


async def get_chain_service() -> ChainService:
    """
    Dependency function to get an instance of ChainService.

    Returns:
        ChainService: An instance of ChainService.
    """

    return ChainService(db_repository=PostgresAsyncRepository(dsn=config.dsn))
