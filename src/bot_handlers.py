from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.configs import config, logger
from src.models.bot import Button, Command
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes


class BotHandlers:
    def __init__(self, dsn: str = config.dsn):
        self.engine = create_async_engine(dsn, echo=True)
        self.session = sessionmaker(  # type:ignore
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def handle_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        # Проверяем, что update.message не None
        if update.message is None:
            logger.warning("Получен update без message.")
            return

        command_text = (
            update.message.text
        )  # Текст команды (например, "/start")

        async with self.session() as session:
            # Ищем команду в базе данных
            stmt = select(Command).where(Command.command == command_text)
            result = await session.execute(stmt)
            command = result.scalars().first()

            if command:
                # Если команда найдена, отправляем ответ
                stmt = select(Button).where(Button.command_id == command.id)
                result = await session.execute(stmt)
                buttons = result.scalars().all()

                if buttons:
                    # Если есть кнопки, создаем клавиатуру
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                button.text, callback_data=button.callback_data
                            )
                        ]
                        for button in buttons
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(
                        command.response, reply_markup=reply_markup
                    )
                else:
                    # Если кнопок нет, просто отправляем ответ
                    await update.message.reply_text(command.response)
            else:
                await update.message.reply_text("Команда не найдена.")

    # Обработчик нажатия инлайн-кнопок
    async def button_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        # Проверяем, что update.callback_query не None
        if update.callback_query is None:
            logger.warning("Получен update без callback_query.")
            return

        query = update.callback_query
        await query.answer()  # Подтверждаем нажатие кнопки

        async with self.session() as session:
            # Ищем кнопку в базе данных
            stmt = select(Button).where(Button.callback_data == query.data)
            result = await session.execute(stmt)
            button = result.scalars().first()

            if button:
                await query.edit_message_text(f"Вы нажали: {button.text}")
