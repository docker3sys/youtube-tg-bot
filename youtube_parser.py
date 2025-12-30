import os
import pandas as pd
import requests

API_KEY_YOUTUBE = os.environ.get("API_KEY_YOUTUBE")

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
