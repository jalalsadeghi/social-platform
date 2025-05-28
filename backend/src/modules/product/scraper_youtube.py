# src/modules/product/scraper_youtube.py
import os
import yt_dlp
import uuid
import requests
from uuid import uuid4
from openai import OpenAI
from core.config import settings


UPLOAD_DIRECTORY = settings.UPLOAD_DIRECTORY

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

client = OpenAI(api_key=settings.OPENAI_API_KEY)
openai_model = settings.OPENAI_MODEL

random_name = str(uuid4())

async def scrape_youtube_short(url: str) -> dict:
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': os.path.join(UPLOAD_DIRECTORY, f'{random_name}.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id")
        title = info.get("title")
        description = info.get("description", "")
        thumbnail_url = info.get("thumbnail")
        video_filename = f"{UPLOAD_DIRECTORY}/{random_name}.mp4"

    thumb_response = requests.get(thumbnail_url, stream=True)
    thumb_ext = thumbnail_url.split('.')[-1].split('?')[0]
    thumb_filename = f"{UPLOAD_DIRECTORY}/{random_name}.{thumb_ext}"
    with open(thumb_filename, 'wb') as f:
        for chunk in thumb_response.iter_content(chunk_size=8192):
            f.write(chunk)

    ai_content = client.chat.completions.create(
    model=openai_model,
    messages=[
        {"role": "system", "content": "You are a skilled freelance writer and editor specializing in creating compelling and engaging content tailored specifically for social media platforms like Instagram and YouTube."},
        {"role": "user", "content": title + "\n\n" + description + "\n\n"}
    ],
    temperature=0.3,
    max_tokens=1000,
    )


    ai_result = {"title": title,
                "description": description,
                "ai_content": ai_content.choices[0].message.content if ai_content.choices else "",
                "media_urls": [video_filename] if video_filename else [],
                "local_path": thumb_filename
                }

    # ai_result = {'title': title,
    #              'description': description,
    #              'ai_content': 'Bleib aktiv und frisch mit dem Dynafit Alpine ',
    #              "media_urls": [video_filename] if video_filename else [],
    #              'local_path': thumb_filename
    #             }

    return ai_result
