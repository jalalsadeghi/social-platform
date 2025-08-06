# File: backend/src/modules/content/generate_video/generate_video.py
import os
import re
import redis
from pydub import AudioSegment
from io import BytesIO
from openai import OpenAI
from core.config import settings
from moviepy import AudioFileClip, VideoFileClip, CompositeAudioClip, TextClip, CompositeVideoClip


from proglog import ProgressBarLogger
import logging

logging.basicConfig(level=logging.INFO)

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

UPLOAD_DIRECTORY = settings.UPLOAD_DIRECTORY

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_audio_and_video_sync(
        ai_caption: str,
        video_filename: str,
        remove_audio: bool,
        no_ai_audio: bool,
        music_filename: str):
    
    random_name = video_filename.split('/')[1].split('_')[0]

    audio_filename = ""
    if not no_ai_audio:
        audio_filename = generate_audio_sync(ai_caption, random_name)

    final_video_filename = generate_video_sync(
        audio_filename=audio_filename,
        video_filename=video_filename,
        remove_audio=remove_audio,
        music_filename=music_filename,
        random_name=random_name,
    )

    return final_video_filename


def generate_audio_sync(ai_caption: str, random_name):
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


def generate_video_sync(
        audio_filename: str, 
        video_filename: str, 
        remove_audio: bool,
        music_filename: str,
        random_name: str,
        watermark: bool = False
    ):

    video_clip = VideoFileClip(video_filename)
    video_duration = video_clip.duration

    if watermark:
        # ایجاد واترمارک ...
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
    else:
        video_mark = video_clip

    audio_clips = []

    if music_filename:
        music = AudioFileClip(music_filename)
        dur = min(music.duration, video_duration)
        music = music.subclipped(0, dur)
        if audio_filename:
            audio_clips.append(music.with_volume_scaled(0.05))
        else:
            audio_clips.append(music)

    elif not remove_audio and video_clip.audio:
        audio_clips.append(video_clip.audio.with_volume_scaled(0.05))

    if audio_filename:
        ai_audio = AudioFileClip(audio_filename)
        dur2 = min(ai_audio.duration, video_duration)
        ai_audio = ai_audio.subclipped(0, dur2)
        audio_clips.append(ai_audio)

    if audio_clips:
        final_audio = CompositeAudioClip(audio_clips)
        final_video = video_mark.with_audio(final_audio)
    else:
        final_video = video_mark.without_audio()

    final_video_filename = f"{UPLOAD_DIRECTORY}/{random_name}.mp4"

    logger = MyProgressLogger()
    final_video.write_videofile(
        final_video_filename,
        codec='libx264',
        audio_codec='aac',
        bitrate='5000k',
        preset='slow',
        threads=4,
        fps=video_clip.fps,
        audio_bitrate='192k',
        ffmpeg_params=[
            "-vf", f"scale={video_clip.size[0]}:{video_clip.size[1]}"
        ],
        logger=logger,
    )

    return final_video_filename
