import os
import pandas as pd
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== Переменные окружения =====
TOKEN = os.environ["TOKEN"]
API_KEY_YOUTUBE = os.environ["API_KEY_YOUTUBE"]

bot = Bot(token=TOKEN)
app = Flask(__name__)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ===== Функции парсинга YouTube =====
def extract_channel_id(url_or_id):
    """
    Определяет ID канала по ссылке, нику или напрямую UC ID
    """
    url_or_id = url_or_id.strip()
    if url_or_id.startswith("UC"):
        return url_or_id
    handle = url_or_id.split("/")[-1]
    api_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": API_KEY_YOUTUBE,
        "q": handle,
        "part": "snippet",
        "type": "channel",
        "maxResults": 1
    }
    r = requests.get(api_url, params=params, timeout=10).json()
    items = r.get("items", [])
    if not items:
        return None
    return items[0]["snippet"]["channelId"]

def parse_channel(channel_id):
    """
    Получает последние 50 видео канала и сохраняет в Excel
    """
    videos = []
    api_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": API_KEY_YOUTUBE,
        "channelId": channel_id,
        "part": "snippet",
        "maxResults": 50,
        "order": "date",
        "type": "video"
    }
    r = requests.get(api_url, params=params, timeout=10).json()
    for item in r.get("items", []):
        snippet = item["snippet"]
        videos.append({
            "title": snippet["title"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "published": snippet["publishedAt"]
        })
    file_path = "videos.xlsx"
    pd.DataFrame(videos).to_excel(file_path, index=False)
    return file_path

# ===== Обработчики команд =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает. Используй /parse <id или ссылка на канал>")

async def parse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Передай ID или ссылку на канал")
        return
    channel_input = context.args[0]
    await update.message.reply_text("Определяю ID канала...")
    channel_id = extract_channel_id(channel_input)
    if not channel_id:
        await update.message.reply_text("Не удалось определить ID канала. Проверь ссылку или никнейм.")
        return
    await update.message.reply_text("Начал парсинг...")
    file_path = parse_channel(channel_id)
    with open(file_path, "rb") as f:
        await update.message.reply_document(f)

# ===== Создание Application =====
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("parse", parse))

# =====
