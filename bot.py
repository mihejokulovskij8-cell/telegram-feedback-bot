import logging
from dotenv import load_dotenv
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Временное хранилище (для простоты, без базы данных)
user_comments = {}
user_ratings = []

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
    
    rating = int(query.data)
    user = query.from_user
    username = user.username or "без username"
    full_name = user.full_name
    
    # Сохраняем оценку
    user_ratings.append(rating)
    user_comments[user.id] = {"rating": rating, "name": full_name, "username": username}
    
    # Отправляем владельцу
    report = (
        f"📊 **Новая оценка!**\n\n"
        f"👤 Пользователь: {full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"🔹 Username: @{username}\n"
        f"⭐ Оценка: {rating}/5"
    )
    await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=report)
    
    # Просим комментарий
    await query.edit_message_text(f"✅ Спасибо за оценку {rating}/5!\n✍️ Напишите, что можно улучшить?")

async def handle_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    comment = update.message.text
    
    # Отправляем комментарий владельцу
    if user.id in user_comments:
        rating = user_comments[user.id]["rating"]
        name = user_comments[user.id]["name"]
        username = user_comments[user.id]["username"]
        
        report = (
            f"💬 **Новый комментарий!**\n\n"
            f"👤 Пользователь: {name}\n"
            f"🆔 ID: {user.id}\n"
            f"🔹 Username: @{username}\n"
            f"⭐ Оценка: {rating}/5\n"
            f"📝 Комментарий: {comment}"
        )
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=report)
        await update.message.reply_text("🙏 Спасибо за ваш отзыв! Он очень важен для нас.")
    else:
        await update.message.reply_text("Пожалуйста, сначала поставьте оценку через /start.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_CHAT_ID:
        await update.message.reply_text("⛔ Эта команда только для владельца.")
        return
    
    if len(user_ratings) == 0:
        await update.message.reply_text("📊 Пока нет ни одной оценки.")
        return
    
    avg = sum(user_ratings) / len(user_ratings)
    report = (
        f"📊 **Статистика**\n\n"
        f"📌 Всего оценок: {len(user_ratings)}\n"
        f"⭐ Средний балл: {avg:.1f}/5\n"
        f"👍 5 звезд: {user_ratings.count(5)} раз\n"
        f"👎 1 звезда: {user_ratings.count(1)} раз"
    )
    await update.message.reply_text(report)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Команды бота:**\n"
        "/start — начать оценку\n"
        "/stats — статистика (только для владельца)"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_comment))
    
    print("🤖 Бот запущен с новыми фичами!")
    app.run_polling()

if __name__ == "__main__":
    main()
    main()
