from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Кнопка 1", "Кнопка 2"],  # Первая строка кнопок
        ["Кнопка 3"],  # Вторая строка кнопок
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Отправляем сообщение с клавиатурой
    await update.message.reply_text("Выберите кнопку:", reply_markup=reply_markup)

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()  # Приводим текст к нижнему регистру

    if text == "привет":
        await update.message.reply_text("Привет! Как дела?")
    else:
        await update.message.reply_text(f"Вы сказали: {text}")


