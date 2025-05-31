# src/modules/product/scraper_youtube.py
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
from .prompts import ai_caption_prompt, expertise_prompt, search_ai_caption_prompt, hashtag_prompt
import logging
logging.basicConfig(level=logging.INFO)

UPLOAD_DIRECTORY = settings.UPLOAD_DIRECTORY

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

client = OpenAI(api_key=settings.OPENAI_API_KEY)
openai_model = settings.OPENAI_MODEL

random_name = str(uuid4())

language = "Persian" # Persian / English / German 


async def extract_info_youtube(url: str):
    random_name = os.urandom(8).hex()

    ydl_opts_video = {
        'format': 'best[ext=mp4]',
        'outtmpl': os.path.join(UPLOAD_DIRECTORY, f'{random_name}.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
        'cookiefile': 'cookies.txt',
        'getcomments': True,
        'extractor_args': {
            'youtube': {
                'max_comments': ['5'],
                'comment_sort': ['top'],
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            info = ydl.extract_info(url, download=True)

            title = info.get("title")
            description = info.get("description", "")
            comments = info.get("comments", [])
            thumbnail_url = info.get("thumbnail")
            video_filename = f"{UPLOAD_DIRECTORY}/{random_name}.mp4"
            uploader = info.get("uploader", "")
            channel_url = info.get("channel_url", "")

        channel_description = ""
        recent_videos = []

        if channel_url:
            ydl_opts_channel = {
                'quiet': True,
                'skip_download': True,
                'extract_flat': True,
                'cookiefile': 'cookies.txt',
                'playlistend': 5,
            }

            with yt_dlp.YoutubeDL(ydl_opts_channel) as ydl:
                # ابتدا تلاش برای استخراج از تب Videos
                try:
                    channel_videos_url = f"{channel_url.rstrip('/')}/videos"
                    channel_info = ydl.extract_info(channel_videos_url, download=False)
                except Exception as e:
                    logging.warning(f"Videos tab extraction failed: {e}")
                    # در صورت عدم موفقیت، تلاش برای استخراج از تب Shorts
                    try:
                        channel_shorts_url = f"{channel_url.rstrip('/')}/shorts"
                        channel_info = ydl.extract_info(channel_shorts_url, download=False)
                    except Exception as shorts_e:
                        logging.error(f"Shorts tab extraction also failed: {shorts_e}")
                        channel_info = None

                if channel_info:
                    channel_description = channel_info.get("description", "")
                    entries = channel_info.get('entries', [])[:5]
                    recent_videos = [
                        {
                            'title': entry.get('title', ''),
                            'description': f"{entry.get('description', '')[:100]} ..."
                        }
                        for entry in entries
                    ]
        else:
            logging.warning("No channel URL provided")

    except Exception as e:
        logging.error(f"Extraction error: {e}")
        return None

    # دانلود تصویر بندانگشتی
    thumb_response = requests.get(thumbnail_url, stream=True)
    thumb_ext = thumbnail_url.split('.')[-1].split('?')[0]
    thumb_filename = f"{UPLOAD_DIRECTORY}/{random_name}.{thumb_ext}"

    with open(thumb_filename, 'wb') as f:
        for chunk in thumb_response.iter_content(chunk_size=8192):
            f.write(chunk)

    # مرتب‌سازی نظرات بر اساس تعداد لایک
    sorted_comments = sorted(comments, key=lambda c: c.get('like_count', 0), reverse=True)[:5]
    comments_text = "\n".join(
        [
            f"- {comment.get('author', 'Unknown')} ({comment.get('like_count', 0)} likes): {comment.get('text', '')[:100]}..."
            for comment in sorted_comments
        ]
    )

    video_duration = VideoFileClip(video_filename).duration

    return {
        'title': title,
        'description': description,
        'comments_text': comments_text,
        'uploader': uploader,
        'video_filename': video_filename,
        'thumb_filename': thumb_filename,
        'channel_url': channel_url,
        'channel_description': channel_description,
        'recent_videos': recent_videos,
        'video_duration': video_duration
    }

    
async def identifying_expertise(channel_description: str, recent_videos: list, title: str, description: str):
    messages = [
        {
            "role": "system",
            "content": expertise_prompt[language]["system"]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": expertise_prompt[language]["user_intro"].format(
                            channel_description=channel_description,             
                            recent_videos=recent_videos,
                            title=title,
                            description=description
                    )
                }
            ]
        }

    ]

    expertise = await generate_ai_content(messages, openai_model, 15)

    return expertise


async def extract_key_frames(video_filename: str,
                             video_duration: float,
                             threshold: float = 0.5, 
                             min_interval_seconds: float = 1, 
                             max_frames: int = 8,
                             ):


    max_frames = int(video_duration / (min_interval_seconds*3))
    vidcap = cv2.VideoCapture(video_filename)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    min_interval_frames = int(fps * min_interval_seconds)

    success, prev_frame = vidcap.read()

    if not success:
        vidcap.release()
        return []

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    key_frames = []
    selected = 0
    count_since_last_selected = 0
    current_frame_number = 0

    min_diff_ratio = 0
    while success:
        success, frame = vidcap.read()
        current_frame_number += 1
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(gray, prev_gray)
        non_zero_count = cv2.countNonZero(diff)
        diff_ratio = non_zero_count / (diff.shape[0] * diff.shape[1])

        if diff_ratio > threshold and count_since_last_selected >= min_interval_frames and min_diff_ratio < diff_ratio:
            _, buffer = cv2.imencode('.jpg', frame)
            timestamp = current_frame_number / fps
            key_frames.append({
                "timestamp": timestamp,
                "diff_ratio": diff_ratio,
                "image_url": f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
            })
            selected += 1

            if selected > max_frames:
                min_diff_ratio_frame = min(key_frames, key=lambda x: x["diff_ratio"])
                key_frames.remove(min_diff_ratio_frame)
                min_diff_ratio = min(item['diff_ratio'] for item in key_frames)
                
            count_since_last_selected = 0
        else:
            count_since_last_selected += 1

        prev_gray = gray

    vidcap.release()
    return key_frames

async def extract_ai_caption(title: str, 
                             description: str, 
                             comments_text: str, 
                             key_frames: list, 
                             expertise: str, 
                             channel_description: str, 
                             video_duration: float,
                             word_per_second: float = 2):
                             
    
    content_list = [{
        "type": "text",
        "text": (
            f"{title}\n\n"
            f"{description}\n\n"
            "Top comments on the video:\n"
            f"{comments_text}\n\n"
            "Description of the main channel where the video was published:\n"
            f"{channel_description}"
        )
    }]

    search_prompt = [
        {
            "role": "system",
            "content": search_ai_caption_prompt[language]["system"]
        },
        {
            "role": "user",
            "content": content_list
        }
    ]

    search_result = await generate_ai_content(search_prompt, "gpt-4o-mini-search-preview", int_max_tokens=500)
    print(f"search_result: {search_result}")
    content_list = [{
        "type": "text",
        "text": (
            f"{title}\n\n"
            f"{description}\n\n"
            "Top comments on the video:\n"
            f"{comments_text}\n\n"
            "Description of the main channel where the video was published:\n"
            f"{channel_description}\n\n"
            "Updated search content:\n"
            f"{search_result}\n\n"
        )
    }]
    
    frame_intervals = [
        (key_frames[i]['timestamp'],
         key_frames[i + 1]['timestamp'] if i + 1 < len(key_frames) else video_duration)
        for i in range(len(key_frames))
    ]
    for idx, frame in enumerate(key_frames):
        start_time, end_time = frame_intervals[idx]
        duration = end_time - start_time
        content_list.append({
            "type": "text",
            "text": f"Frame {idx + 1}: from {start_time:.2f}s to {end_time:.2f}s, duration {duration:.2f}s"
        })
        print(f"Info from Frame: {idx + 1}: from {start_time:.2f}s to {end_time:.2f}s, duration {duration:.2f}s")
        content_list.append({
            "type": "image_url",
            "image_url": {"url": frame["image_url"]}
        })

    max_words_allowed = int(video_duration * word_per_second)
    print(f"video_duration: {video_duration:.2f}")       
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": ai_caption_prompt[language]["system"].format(
                        expertise=expertise,             
                        video_duration=video_duration,
                        word_per_second=word_per_second,
                        max_words_allowed=max_words_allowed
                    )
                }
            ]
        },
        {
            "role": "user",
            "content": content_list
        }
    ]


    total_words = video_duration * word_per_second
    max_tokens = int(total_words / 0.75)

    ai_caption = await generate_ai_content(messages, openai_model, max_tokens)

    messages_hashtag = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": hashtag_prompt[language]["system"].format(
                        expertise=expertise,
                    )
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": hashtag_prompt[language]["user_intro"].format(
                        ai_caption=ai_caption,
                        search_result=search_result
                    )
                }
            ]
        }
    ]
    
    ai_content = await generate_ai_content(messages_hashtag, openai_model, max_tokens)

    return ai_caption, ai_content


async def generate_ai_content(messages: list, openai_model: str, int_max_tokens: int = 1500):
    """Generate content from AI based on provided messages. Adapts parameters based on model capabilities."""

    restricted_models = {
        "gpt-4o-mini-search-preview",
    }

    request_args = {
        "model": openai_model,
        "messages": messages
    }

    if openai_model not in restricted_models:
        request_args.update({
            "temperature": 0.3,
            "max_tokens": int_max_tokens
        })

    try:
        ai_response = client.chat.completions.create(**request_args)
        return ai_response.choices[0].message.content if ai_response.choices else ""
    except Exception as e:
        print(f"[AI Error] {e}")
        return ""

def generate_audio_from_script(ai_script: str):
    ai_script = ai_script.replace('second]', 'seconds]')
    sections = re.split(r'\[P ([\d.]+) S\]', ai_script)
    # print(f"ai_script: {ai_script}")
    # print(f"sections: {sections}")

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
            # print(f"text: {text}")

        if i + 1 < len(sections):
            pause_duration = float(sections[i + 1]) * 1000
            final_audio += AudioSegment.silent(duration=pause_duration)
            
            # print(f"sections[i]: {pause_duration}")

    audio_filename = f"{UPLOAD_DIRECTORY}/{random_name}.wav"
    final_audio.export(audio_filename, format="wav")

    return audio_filename


async def generate_video(audio_filename, video_filename, uploader):
    ai_audio_clip = AudioFileClip(audio_filename)
    video_clip = VideoFileClip(video_filename)
    video_duration = video_clip.duration
    print(f"video_clip added to video. {video_clip.size}")

    font_path = 'src/core/assets/ARIALBD.TTF'
    watermark_text =  #f"@{uploader}"
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

    original_audio = video_clip.audio.with_volume_scaled(0.1)
    final_audio = CompositeAudioClip([original_audio, ai_audio_clip])

    final_video = video_mark.with_audio(final_audio)
    print(f"final_video added to video. {final_video.size}")

    final_video_filename = f"{UPLOAD_DIRECTORY}/{random_name}_final.mp4"
    final_video.write_videofile(final_video_filename, codec='libx264', audio_codec='aac')

    return final_video_filename
    

async def scrape_youtube_short(url: str) -> dict:


    extract_info = await extract_info_youtube(url)

    expertise = await identifying_expertise(extract_info['channel_description'], 
                                            extract_info['recent_videos'],
                                            extract_info['title'], 
                                            extract_info['description'], 
                                            )


    key_frames = await extract_key_frames(extract_info['video_filename'], 
                                          extract_info['video_duration'],
                                          )

    ai_caption, ai_content = await extract_ai_caption(extract_info['title'], 
                                                extract_info['description'], 
                                                extract_info['comments_text'], 
                                                key_frames, 
                                                expertise, 
                                                extract_info['channel_description'],
                                                extract_info['video_duration']
                                                )

    
    audio_filename = generate_audio_from_script(ai_caption)

    final_video_filename = await generate_video(audio_filename, 
                                          extract_info['video_filename'], 
                                          extract_info['uploader']
                                          )


    ai_result = {
        "title": extract_info['title'],
        "description": extract_info['description'],
        "media_urls": extract_info['video_filename'],
        "local_path": extract_info['thumb_filename'],
        "uploader": extract_info['uploader'],
        "channel_url": extract_info['channel_url'],
        "channel_description": extract_info['channel_description'],
        "comments_text": extract_info['comments_text'],
        "recent_videos": extract_info['recent_videos'],
        "expertise": expertise,
        "ai_caption": ai_caption,
        "ai_content": ai_content,
        "audio_path": audio_filename,
        "final_video_path": final_video_filename,
    }

    return ai_result