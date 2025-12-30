import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from youtube_parser import extract_channel_id, parse_channel

TOKEN = os.environ["TOKEN"]
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = f"https://youtube-tg-bot-production.up.railway.app/webhook"  # замени на свой URL

# Создаём приложение
application = ApplicationBuilder().token(TOKEN).build()

# ===== Telegram Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает!\nВведите /parse <ID или @namechannel>")

async def parse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Нужен ID или @namechannel")
        return

    await update.message.reply_text("Определяю канал...")
    channel_id = extract_channel_id(context.args[0])

    if not channel_id:
        await update.message.reply_text("Не удалось определить канал")
        return

    await update.message.reply_text("Парсю видео...")
    file_path = parse_channel(channel_id)

    with open(file_path, "rb") as f:
        await update.message.reply_document(f)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("parse", parse))

# ===== Запуск webhook =====
application.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path="webhook",
    webhook_url=WEBHOOK_URL
)
