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
from pydub import AudioSegment
from uuid import uuid4
from openai import OpenAI
from core.config import settings
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import logging
logging.basicConfig(level=logging.INFO)

UPLOAD_DIRECTORY = settings.UPLOAD_DIRECTORY

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

client = OpenAI(api_key=settings.OPENAI_API_KEY)
openai_model = settings.OPENAI_MODEL

def generate_audio(ai_script: str, random_name):
    sections = re.split(r'\[P ([\d.]+) S\]', ai_script)

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

async def generate_video(audio_filename, video_filename, random_name):
    ai_audio_clip = AudioFileClip(audio_filename)
    video_clip = VideoFileClip(video_filename)
    video_duration = video_clip.duration

    font_path = 'src/core/assets/ARIALBD.TTF'
    watermark_text =  chanel_name[language] #f"@{uploader}"
    watermark_clip = TextClip(
        text=watermark_text,
        font_size=14,
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
    # مهم: استفاده از تنظیمات بهتر برای افزایش کیفیت
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
        ]
    )

    return final_video_filename
    
