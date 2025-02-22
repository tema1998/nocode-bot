import secrets

from fastapi import APIRouter, Depends, HTTPException
from src.models.bot import Bot, Command
from src.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from src.schemas.bot import BotCreate, CommandCreate
from src.utils.webhook import set_webhook
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


router = APIRouter()


@router.post("/bots/")
async def create_bot(
    bot: BotCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Генерируем секретный токен
    secret_token = secrets.token_hex(16)  # Генерация случайного токена

    # Создаем бота в базе данных
    db_bot = Bot(token=bot.token, name=bot.name, secret_token=secret_token)
    inserted_bot = await repository.insert(db_bot)

    try:
        await set_webhook(
            bot_id=inserted_bot.id,
            bot_token=bot.token,
            bot_secret_token=secret_token,
        )
    except Exception as e:
        await repository.delete(Bot, inserted_bot.id)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to set webhook: {str(e)}",
        )

    return inserted_bot


@router.post("/commands/")
async def add_command(
    command: CommandCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    db_command = Command(
        command=command.command,
        response=command.response,
        bot_id=command.bot_id,
    )
    inserted_command = await repository.insert(db_command)
    return inserted_command


@router.post("/webhook/{bot_id}")
async def webhook(
    bot_id: int,
    update_data: dict,
    repository: PostgresAsyncRepository = Depends(get_repository),
):

    bot = await repository.fetch_by_id(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    application = Application.builder().token(bot.token).build()
    await application.initialize()

    # Получаем команды для этого бота
    commands = await repository.fetch_by_query(Command, "bot_id", bot_id)

    # Добавляем обработчики команд
    if commands:
        for cmd in commands:

            async def command_handler(
                update: Update, context: ContextTypes.DEFAULT_TYPE
            ):
                await update.message.reply_text(cmd.response)  # type: ignore

            application.add_handler(
                CommandHandler(cmd.command, command_handler)
            )
    else:
        # Если у бота нет команд, добавляем обработчик по умолчанию
        async def default_handler(
            update: Update, context: ContextTypes.DEFAULT_TYPE
        ):
            await update.message.reply_text(  # type: ignore
                "Этот бот пока не имеет команд. Пожалуйста, свяжитесь с администратором."
            )

        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, default_handler)
        )

    # Обрабатываем входящее обновление
    update_obj = Update.de_json(update_data, application.bot)
    await application.process_update(update_obj)

    # Завершаем работу Application
    await application.shutdown()

    return {"status": "ok"}
