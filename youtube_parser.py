import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from youtube_parser import extract_channel_id, parse_channel
import asyncio

TOKEN = os.environ["TOKEN"]
APP_URL = "https://hello-tg-bot-production.up.railway.app"

# Flask app
app = Flask(__name__)

# Telegram bot
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Бот работает.\nИспользуй команду:\n/parse <ID или @namechannel>"
    )

async def parse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Передай ID или @namechannel")
        return

    await update.message.reply_text("Определяю канал...")
    channel_id = extract_channel_id(context.args[0])
    if not channel_id:
        await update.message.reply_text("Не удалось определить ID канала")
        return

    await update.message.reply_text("Парсю видео...")
    file_path = parse_channel(channel_id)

    with open(file_path, "rb") as f:
        await update.message.reply_document(f)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("parse", parse))

# Инициализация Telegram
asyncio.run(application.initialize())

# Webhook endpoint для Flask
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

# Healthcheck
@app.route("/", methods=["GET"])
def index():
    return "OK"