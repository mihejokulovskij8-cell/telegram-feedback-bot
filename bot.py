import logging
from dotenv import load_dotenv
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Пожалуйста, оцените качество нашей работы по шкале от 1 до 5:"
    )
    keyboard = [
        [InlineKeyboardButton("⭐ 1", callback_data="1"),
         InlineKeyboardButton("⭐ 2", callback_data="2"),
         InlineKeyboardButton("⭐ 3", callback_data="3")],
        [InlineKeyboardButton("⭐ 4", callback_data="4"),
         InlineKeyboardButton("⭐ 5", callback_data="5")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    rating = query.data
    user = query.from_user
    username = user.username or "без username"
    full_name = user.full_name
    
    report = (
        f"📊 **Новая оценка!**\n\n"
        f"👤 Пользователь: {full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"🔹 Username: @{username}\n"
        f"⭐ Оценка: {rating}/5"
    )
    
    await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=report)
    await query.edit_message_text(f"✅ Спасибо! Вы поставили оценку {rating}/5.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используйте /start, чтобы начать оценку.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🤖 Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()