# src/modules/content/generate_video/generate_video.py
import os
import yt_dlp
import requests
import cv2
import base64
from PIL import Image
from io import BytesIO
import re
import json
import redis
from pydub import AudioSegment
from uuid import uuid4
from openai import OpenAI
from core.config import settings
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from proglog import ProgressBarLogger
import logging

logging.basicConfig(level=logging.INFO)

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

UPLOAD_DIRECTORY = settings.UPLOAD_DIRECTORY

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

client = OpenAI(api_key=settings.OPENAI_API_KEY)
openai_model = settings.OPENAI_MODEL

def generate_audio_and_video(ai_caption, video_filename):

    random_name = video_filename.split('/')[1].split('_')[0]
    audio_filename = generate_audio(ai_caption, random_name)
    # return f"random_name: {random_name}"

    final_video_filename = generate_video(audio_filename, video_filename, random_name)

    return final_video_filename


def generate_audio(ai_caption: str, random_name):
    sections = re.split(r'\[P ([\d.]+) S\]', ai_caption)

    final_audio = AudioSegment.empty()

    for i in range(0, len(sections), 2):
        text = sections[i].strip()
        if text:
            audio_response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="echo",
                input=text,
                response_format="wav"
            )
            segment_audio = AudioSegment.from_file(BytesIO(audio_response.content), format="wav")
            final_audio += segment_audio

        if i + 1 < len(sections):
            pause_duration = float(sections[i + 1]) * 1000
            final_audio += AudioSegment.silent(duration=pause_duration)
            
    audio_filename = f"{UPLOAD_DIRECTORY}/{random_name}.wav"
    final_audio.export(audio_filename, format="wav")

    return audio_filename


class MyProgressLogger(ProgressBarLogger):
    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        percent = int(value / total * 100)
        if bar == 'frame_index':
            if percent % 3 == 0 and old_value is not None and int(old_value/total*100) != percent:
                redis_client.set("current_video_progress", percent)
                logging.info(f"🔄 Rendering video: {percent}%")
        super().bars_callback(bar, attr, value, old_value)

    def callback(self, **changes):
        # اگر نیاز دارید پیام‌های دیگر لاگ شوند
        super().callback(**changes)


async def generate_video(audio_filename, video_filename, random_name):
    ai_audio_clip = AudioFileClip(audio_filename)
    video_clip = VideoFileClip(video_filename)
    video_duration = video_clip.duration

    font_path = 'src/core/assets/ARIALBD.TTF'
    watermark_text =  "KI-Blick" #f"@{uploader}"
    watermark_clip = TextClip(
        text=watermark_text,
        font_size=24,
        color='white',
        font=font_path,
        duration=video_duration 
    )

    position = (5, 5)

    watermark_clip = watermark_clip.with_position(position)

    video_mark = CompositeVideoClip([video_clip, watermark_clip])

    original_audio = video_clip.audio.with_volume_scaled(0.05)
    final_audio = CompositeAudioClip([original_audio, ai_audio_clip])

    final_video = video_mark.with_audio(final_audio)

    final_video_filename = f"{UPLOAD_DIRECTORY}/{random_name}.mp4"

    logger = MyProgressLogger()
    final_video.write_videofile(
        final_video_filename,
        codec='libx264',
        audio_codec='aac',
        bitrate='5000k',            # افزایش بیت‌ریت (برای ویدئوهای FullHD و Shorts اینستاگرام مناسب است)
        preset='slow',              # تنظیم کیفیت و فشرده‌سازی (slow یا medium)
        threads=4,                  # استفاده بهینه از منابع CPU
        fps=video_clip.fps,         # حفظ fps اصلی ویدئو
        audio_bitrate='192k',       # افزایش کیفیت صدا
        ffmpeg_params=[
            "-vf", f"scale={video_clip.size[0]}:{video_clip.size[1]}"
        ],
        # verbose=False,
        # progress_bar=False,
        logger=logger,
    )

    
    return final_video_filename
    
