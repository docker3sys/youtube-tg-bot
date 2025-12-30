import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from youtube_parser import extract_channel_id, parse_channel
import asyncio

TOKEN = os.environ["TOKEN"]

# Flask
app = Flask(__name__)  # ⚠ обязательно имя переменной app

# Telegram
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите /parse <ID или @namechannel>")

async def parse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Нужен ID или @namechannel")
        return

    channel_id = extract_channel_id(context.args[0])
    if not channel_id:
        await update.message.reply_text("Не удалось определить канал")
        return

    file_path = parse_channel(channel_id)
    with open(file_path, "rb") as f:
        await update.message.reply_document(f)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("parse", parse))

# инициализация PTB
asyncio.run(application.initialize())

# Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

# Healthcheck
@app.route("/", methods=["GET"])
def index():
    return "OK"
