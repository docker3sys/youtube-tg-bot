import os
import pandas as pd
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["TOKEN"]
API_KEY_YOUTUBE = os.environ["API_KEY_YOUTUBE"]

app = Flask(__name__)

application = ApplicationBuilder().token(TOKEN).build()

# ===== Парсинг =====
def extract_channel_id(url_or_id):
    url_or_id = url_or_id.strip()
    if url_or_id.startswith("UC"):
        return url_or_id

    handle = url_or_id.split("/")[-1]
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": API_KEY_YOUTUBE,
            "q": handle,
            "part": "snippet",
            "type": "channel",
            "maxResults": 1,
        },
        timeout=10
    ).json()

    items = r.get("items", [])
    if not items:
        return None

    return items[0]["snippet"]["channelId"]


def parse_channel(channel_id):
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": API_KEY_YOUTUBE,
            "channelId": channel_id,
            "part": "snippet",
            "maxResults": 50,
            "order": "date",
            "type": "video",
        },
        timeout=10
    ).json()

    videos = []
    for item in r.get("items", []):
        videos.append({
            "title": item["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "published": item["snippet"]["publishedAt"],
        })

    path = "videos.xlsx"
    pd.DataFrame(videos).to_excel(path, index=False)
    return path


# ===== Telegram handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Бот работает.\nИспользуй:\n/parse <id или ссылка>"
    )


async def parse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Передай ID или ссылку на канал")
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


# ===== WEBHOOK =====
@app.route("/", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
