import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from youtube_parser import extract_channel_id, parse_channel

TOKEN = os.environ["TOKEN"]
APP_URL = "https://hello-tg-bot-production.up.railway.app"

# ===== Handlers =====
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

    # Отправка Excel пользователю
    with open(file_path, "rb") as f:
        await update.message.reply_document(f)

# ===== Telegram Bot =====
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("parse", parse))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Запуск webhook-сервера PTB (Flask не нужен)
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{APP_URL}/webhook",
    )
