# src/modules/product/scraper_youtube.py
import os
import yt_dlp
import requests
import cv2
import base64
from PIL import Image
from io import BytesIO
import re
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
openai_model = "gpt-4o"

async def extract_key_frames(video_path: str, threshold: float = 0.5, min_interval_seconds: float = 5, max_frames: int = 8):
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    min_interval_frames = int(fps * min_interval_seconds)

    success, prev_frame = vidcap.read()

    if not success:
        vidcap.release()
        return []

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    frames = []
    selected = 0
    count_since_last_selected = 0
    current_frame_number = 0

    while success and selected < max_frames:
        success, frame = vidcap.read()
        current_frame_number += 1
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(gray, prev_gray)
        non_zero_count = cv2.countNonZero(diff)
        diff_ratio = non_zero_count / (diff.shape[0] * diff.shape[1])

        if diff_ratio > threshold and count_since_last_selected >= min_interval_frames:
            _, buffer = cv2.imencode('.jpg', frame)
            timestamp = current_frame_number / fps
            frames.append({
                "timestamp": timestamp,
                "image_url": f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
            })
            selected += 1
            count_since_last_selected = 0
        else:
            count_since_last_selected += 1

        prev_gray = gray

    vidcap.release()
    return frames

async def generate_synced_audio_script(video_filename, key_frames, title, description):
    video_duration = VideoFileClip(video_filename).duration

    frame_intervals = [
        (key_frames[i]['timestamp'], key_frames[i+1]['timestamp'] if i+1 < len(key_frames) else video_duration)
        for i in range(len(key_frames))
    ]

    content_list = [{"type": "text", "text": f"{title}\n\n{description}\n\nFrame timestamps and durations:"}]

    for idx, frame in enumerate(key_frames):
        start_time, end_time = frame_intervals[idx]
        duration = end_time - start_time
        content_list.append({"type": "text", "text": f"Frame at {start_time:.2f}s (Duration: {duration:.2f}s)"})
        content_list.append({"type": "image_url", "image_url": {"url": frame["image_url"]}})

    messages = [
        {
            "role": "system",
            "content": (
                "Generate a SHORT NARRATION SCRIPT aligned with provided frame durations. "
                "Use '[Pause]' explicitly for silence to align with timestamps. Ensure total script duration doesn't exceed video duration."
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

    return ai_content.choices[0].message.content if ai_content.choices else ""
async def scrape_youtube_short(url: str) -> dict:
    random_name = str(uuid4())
    print(f"random_name: {random_name}")

    ydl_opts_video = {
        'format': 'best[ext=mp4]',
        'outtmpl': os.path.join(UPLOAD_DIRECTORY, f'{random_name}.%(ext)s'),
        'noplaylist': True,
        'quiet': False,  # Set to False for detailed output
        'cookiefile': 'cookies.txt',
    }

    ydl_opts_channel = {
        'quiet': True,
        'skip_download': True,  # Skip downloading video/channel data
        'extract_flat': True,   # Only extract metadata without downloading content
        'cookiefile': 'cookies.txt',
    }

    try:
        logging.info("Starting video extraction")
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            logging.info("yt-dlp configured for video extraction")
            info = ydl.extract_info(url, download=True)
            logging.info("Video information extracted")

            title = info.get("title")
            description = info.get("description", "")
            thumbnail_url = info.get("thumbnail")
            video_filename = f"{UPLOAD_DIRECTORY}/{random_name}.mp4"
            uploader = info.get("uploader", "")
            channel_url = info.get("channel_url", "")

            logging.info(f"title: {title}")
            logging.info(f"description: {description}")
            logging.info(f"thumbnail_url: {thumbnail_url}")
            logging.info(f"video_filename: {video_filename}")
            logging.info(f"uploader: {uploader}")
            logging.info(f"channel_url: {channel_url}")

        if channel_url:
            logging.info("Starting channel metadata extraction")
            with yt_dlp.YoutubeDL(ydl_opts_channel) as ydl:
                channel_info = ydl.extract_info(channel_url, download=False)
                channel_description = channel_info.get("description", "")
                logging.info(f"channel_description: {channel_description}")
        else:
            channel_description = ""
            logging.warning("No channel URL provided")

    except Exception as e:
        logging.error(f"Extraction error: {e}")


    thumb_response = requests.get(thumbnail_url, stream=True)
    thumb_ext = thumbnail_url.split('.')[-1].split('?')[0]
    thumb_filename = f"{UPLOAD_DIRECTORY}/{random_name}.{thumb_ext}"
    print(f"thumb_response: {thumb_response}")

    with open(thumb_filename, 'wb') as f:
        for chunk in thumb_response.iter_content(chunk_size=8192):
            f.write(chunk)


    key_frames = await extract_key_frames(video_filename)

    video_duration = VideoFileClip(video_filename).duration
    max_words_audio = int(video_duration * 2.2)

    content_list = [{"type": "text", "text": f"{title}\n\n{description}\n\nFrame timestamps:"}]

    for frame in key_frames:
        content_list.append({
            "type": "text",
            "text": f"Frame at {frame['timestamp']:.2f} seconds"
        })
        content_list.append({
            "type": "image_url",
            "image_url": {"url": frame["image_url"]}
        })

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a skilled freelance writer specializing in social media content. "
                f"The provided frames have timestamps indicated clearly in the text messages. "
                f"The total video duration is {video_duration:.2f} seconds. Generate:\n\n"
                "1. A SHORT NARRATION SCRIPT labeled clearly as 'NARRATION SCRIPT:' that aligns precisely with the provided frame timestamps. "
                f"The script must have a maximum of {max_words_audio} words and include clear instructions like '[Pause for X seconds]' between sections to sync audio with frames.\n\n"
                "2. A detailed INSTAGRAM CAPTION labeled clearly as 'INSTAGRAM CAPTION:' explaining the underlying technology, technique, or action with technical insights."
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

    if not audio_script:
        audio_script = "An engaging video to explore!"

    sections = re.split(r'\[Pause for (\d+) seconds\]', audio_script)

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
            pause_duration = int(sections[i + 1]) * 1000
            final_audio += AudioSegment.silent(duration=pause_duration)

    audio_filename = f"{UPLOAD_DIRECTORY}/{random_name}.wav"
    final_audio.export(audio_filename, format="wav")

    ai_audio_clip = AudioFileClip(audio_filename)
    video_clip = VideoFileClip(video_filename)
    video_duration = video_clip.duration
    print(f"video_clip added to video. {video_clip.size}")

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

    position = (5, 5)
    print(f"position added to video. {position}")

    watermark_clip = watermark_clip.with_position(position)

    video_mark = CompositeVideoClip([video_clip, watermark_clip])
    print(f"video_mark added to video. {video_mark.size}")

    original_audio = video_clip.audio.with_volume_scaled(0.15)
    final_audio = CompositeAudioClip([original_audio, ai_audio_clip])

    final_video = video_mark.with_audio(final_audio)
    print(f"final_video added to video. {final_video.size}")

    final_video_filename = f"{UPLOAD_DIRECTORY}/{random_name}_final.mp4"
    final_video.write_videofile(final_video_filename, codec='libx264', audio_codec='aac')

    ai_result = {
        "title": title,
        "description": description,
        "ai_content": instagram_caption,
        "audio_script": audio_script,
        "media_urls": [video_filename],
        "local_path": thumb_filename,
        "audio_path": audio_filename,
        "final_video_path": final_video_filename,
        "uploader": uploader,
        "channel_url": channel_url,
        "channel_description": channel_description,
    }

    return ai_result