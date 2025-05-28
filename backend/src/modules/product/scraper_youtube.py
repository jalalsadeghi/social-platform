# src/modules/product/scraper_youtube.py
import os
import yt_dlp
import requests
import cv2
import base64
import re
from uuid import uuid4
from openai import OpenAI
from core.config import settings
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


UPLOAD_DIRECTORY = settings.UPLOAD_DIRECTORY

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

client = OpenAI(api_key=settings.OPENAI_API_KEY)
openai_model = "gpt-4o"

async def extract_key_frames(video_path: str, interval_seconds: int = 3, max_frames: int = 5):
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(fps * interval_seconds)

    frames = []
    success, frame = vidcap.read()
    count = 0
    selected = 0
    while success and selected < max_frames:
        if count % interval_frames == 0:
            _, buffer = cv2.imencode('.jpg', frame)
            frames.append(base64.b64encode(buffer).decode('utf-8'))
            selected += 1
        success, frame = vidcap.read()
        count += 1

    vidcap.release()
    return frames

async def scrape_youtube_short(url: str) -> dict:
    random_name = str(uuid4())

    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': os.path.join(UPLOAD_DIRECTORY, f'{random_name}.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title")
        description = info.get("description", "")
        thumbnail_url = info.get("thumbnail")
        video_filename = f"{UPLOAD_DIRECTORY}/{random_name}.mp4"
        uploader = info.get("uploader", "")
        channel_url = info.get("channel_url", "")
        
        channel_info = ydl.extract_info(channel_url, download=False)
        channel_description = channel_info.get("description", "")

        print(f"channel_description: {channel_description}")



    thumb_response = requests.get(thumbnail_url, stream=True)
    thumb_ext = thumbnail_url.split('.')[-1].split('?')[0]
    thumb_filename = f"{UPLOAD_DIRECTORY}/{random_name}.{thumb_ext}"

    with open(thumb_filename, 'wb') as f:
        for chunk in thumb_response.iter_content(chunk_size=8192):
            f.write(chunk)

    key_frames = await extract_key_frames(video_filename)

    video_duration = VideoFileClip(video_filename).duration
    max_words_audio = int(video_duration * 2.2)

    content_list = [{"type": "text", "text": f"{title}\n\n{description}"}]
    content_list += [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}}
        for frame in key_frames
    ]

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a skilled freelance writer specializing in social media content. "
                f"Based on provided frames, video title, description, and video duration ({video_duration:.2f} seconds), generate:\n\n"
                f"1. A SHORT NARRATION SCRIPT labeled clearly as 'NARRATION SCRIPT:' "
                f"with a maximum of {max_words_audio} words to ensure the audio ends slightly before the video.\n\n"
                "2. A detailed INSTAGRAM CAPTION labeled clearly as 'INSTAGRAM CAPTION:' "
                "explaining the underlying technology, technique, or action with technical insights."
            )
        },
        {"role": "user", "content": content_list},
    ]

    ai_content = client.chat.completions.create(
        model=openai_model,
        messages=messages,
        temperature=0.3,
        max_tokens=1500,
    )

    ai_content_input = ai_content.choices[0].message.content if ai_content.choices else ""

    audio_script_match = re.search(r'NARRATION SCRIPT:\s*(.*?)\s*INSTAGRAM CAPTION:', ai_content_input, re.DOTALL)
    caption_match = re.search(r'INSTAGRAM CAPTION:\s*(.*)', ai_content_input, re.DOTALL)

    audio_script = audio_script_match.group(1).strip() if audio_script_match else ""
    instagram_caption = caption_match.group(1).strip() if caption_match else ai_content_input

    # بررسی متن صوتی خالی نبودن
    if not audio_script:
        audio_script = "An engaging video to explore!"

    audio_response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="echo",
        input=audio_script,
        response_format="wav"
    )

    audio_filename = f"{UPLOAD_DIRECTORY}/{random_name}.wav"
    with open(audio_filename, "wb") as f:
        f.write(audio_response.content)

    ai_audio_clip = AudioFileClip(audio_filename)
    video_clip = VideoFileClip(video_filename)
    video_duration = video_clip.duration
    print(f"video_clip added to video. {video_clip.size}")

    # ایجاد کلیپ متنی برای واترمارک
    font_path = 'src/core/assets/ARIALBD.TTF'
    watermark_text = f"@{uploader}"
    watermark_clip = TextClip(
        text=watermark_text,
        font_size=14,
        color='white',
        font=font_path,
        duration=video_duration 
    )
    print(f"watermark_clip added to video. {watermark_clip.size}")

    # محاسبه موقعیت (گوشه بالا راست با فاصله ۵ پیکسل)
    # video_width, video_height = video_clip.size
    # text_width, text_height = watermark_clip.size
    position = (5, 5)
    print(f"position added to video. {position}")

    # تعیین موقعیت واترمارک
    watermark_clip = watermark_clip.with_position(position)

    # ترکیب واترمارک با ویدیو
    video_mark = CompositeVideoClip([video_clip, watermark_clip])
    print(f"video_mark added to video. {video_mark.size}")

    original_audio = video_clip.audio.with_volume_scaled(0.15)
    final_audio = CompositeAudioClip([original_audio, ai_audio_clip])
    # video_audio = video_clip.with_audio(final_audio)
    # print(f"video_audio added to video. {video_audio.size}")

    final_video = video_mark.with_audio(final_audio)
    print(f"final_video added to video. {final_video.size}")

    final_video_filename = f"{UPLOAD_DIRECTORY}/{random_name}_final.mp4"
    final_video.write_videofile(final_video_filename, codec='libx264', audio_codec='aac')

    ai_result = {
        "title": title,
        "description": description,
        "ai_content": instagram_caption,
        "media_urls": [video_filename],
        "local_path": thumb_filename,
        "audio_path": audio_filename,
        "final_video_path": final_video_filename,
        "uploader": uploader,
        "channel_url": channel_url,
        "channel_description": channel_description,
    }

    return ai_result