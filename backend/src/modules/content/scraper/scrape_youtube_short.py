# src/modules/content/scraper/scraper_youtube.py
import os
import yt_dlp
import requests
import cv2
import base64
from PIL import Image
import re
from uuid import uuid4
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from modules.ai.prompts import (
    ai_caption_prompt, 
    ai_content_prompt, 
    search_ai_caption_prompt, 
    ai_title_prompt)
from core.config import settings
from modules.ai.crud import get_prompt
from moviepy.video.io.VideoFileClip import VideoFileClip
import pprint
import logging
logging.basicConfig(level=logging.INFO)

UPLOAD_DIRECTORY = settings.UPLOAD_DIRECTORY
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

client = OpenAI(api_key=settings.OPENAI_API_KEY)
openai_model = settings.OPENAI_MODEL

async def scrape_youtube_short(db: AsyncSession, url: str, prompt_id: str, tip: str, user_id: str, base_url:str) -> dict:

    prompt = await get_prompt(db, prompt_id, user_id)
    expertise = prompt.expertise
    language = prompt.language.value
    prompt_content = prompt.prompt_content

    random_name = str(uuid4())

    extract_info = await extract_info_youtube(url, random_name)

    message_content = extract_info['message_content']
    
    video_filename = extract_info['video_filename']

    key_frames = await extract_key_frames(video_filename, extract_info['video_duration'])
    
    ai_title, ai_caption, ai_content = await extract_ai_caption(
                                            message_content=message_content,
                                            message_tip=tip,
                                            key_frames=key_frames, 
                                            video_duration=float(extract_info['video_duration']),
                                            prompt_content=prompt_content,
                                            expertise=expertise,
                                            language=language,
                                            base_url=base_url,
    )
    
    result = {
        "ai_title": ai_title,
        "ai_caption": ai_caption,
        "ai_content": ai_content,
        "video_filename": video_filename,
        "thumb_filename": extract_info['thumb_filename'],
    }
    print(result)
    return result


async def extract_info_youtube(url: str, random_name:str):
    
    cookies = 'src/modules/content/scraper/cookies.txt'

    ydl_opts_video = {
        # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'format': 'bv*+bestaudio/best',
        'outtmpl': os.path.join(UPLOAD_DIRECTORY, f'{random_name}_initial.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': False,
        'cookiefile': cookies,
        'getcomments': True,
        'extractor_args': {
            'youtube': {
                'client': 'ios',
                'formats': 'l',
                'max_comments': ['5'],
                'comment_sort': ['top'],
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            info = ydl.extract_info(url, download=True)

            if not info:
                logging.error("yt_dlp returned None for video extraction.")
                return None
            
            title = info.get("title")
            description = info.get("description", "")
            comments = info.get("comments", [])
            thumbnail_url = info.get("thumbnail")
            video_filename = f"{UPLOAD_DIRECTORY}/{random_name}_initial.mp4"
            uploader = info.get("uploader", "")
            channel_url = info.get("channel_url", "")

        channel_description = ""
        recent_videos = []

        if channel_url:
            ydl_opts_channel = {
                'quiet': True,
                'skip_download': True,
                'extract_flat': True,
                'cookiefile': cookies,
                'playlistend': 5,
            }

            with yt_dlp.YoutubeDL(ydl_opts_channel) as ydl:
                # First try to extract from the Videos tab
                try:
                    channel_videos_url = f"{channel_url.rstrip('/')}/videos"
                    channel_info = ydl.extract_info(channel_videos_url, download=False)
                except Exception as e:
                    logging.warning(f"Videos tab extraction failed: {e}")
                    # If that fails, try extracting from the Shorts tab.
                    try:
                        channel_shorts_url = f"{channel_url.rstrip('/')}/shorts"
                        channel_info = ydl.extract_info(channel_shorts_url, download=False)
                    except Exception as shorts_e:
                        logging.error(f"Shorts tab extraction also failed: {shorts_e}")
                        channel_info = None

                if channel_info:
                    entries = channel_info.get('entries', [])[:5]
                    # logging.info(f"Extracted entries: {entries}")
                    try:
                        recent_videos = [
                            {
                                'title': entry.get('title', ''),
                                'description': f"{entry.get('description', '')[:100]} ..."
                            }
                            for entry in entries if entry and isinstance(entry, dict)
                        ]
                    except:
                        print(f"Error entries")
                else:
                    logging.warning("Channel info not found or empty")
        else:
            logging.warning("No channel URL provided")

    except Exception as e:
        logging.error(f"Extraction error: {e}")
        return None

    thumb_filename = ""
    if thumbnail_url:
        thumb_response = requests.get(thumbnail_url, stream=True)
        thumb_ext = thumbnail_url.split('.')[-1].split('?')[0]
        thumb_filename = f"{UPLOAD_DIRECTORY}/{random_name}.{thumb_ext}"

        with open(thumb_filename, 'wb') as f:
            for chunk in thumb_response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        logging.warning("No thumbnail URL provided.")
    
    # Sort by likes
    sorted_comments = sorted(comments, key=lambda c: c.get('like_count', 0), reverse=True)[:5]
    comments_text = "\n".join(
        [
            f"- {comment.get('author', 'Unknown')} ({comment.get('like_count', 0)} likes): {comment.get('text', '')[:100]}..."
            for comment in sorted_comments
        ]
    )

    video_duration = VideoFileClip(video_filename).duration

    sections = []
    if title:
        sections.append(f"Title:\n{title}")

    if description:
        sections.append(f"Description:\n{description}")

    if comments_text:
        comments_raw = comments_text.splitlines()
        cleaned_comments = []
        for comment in comments_raw:
            cleaned_comment = re.sub(r"- @.+?\(\d+ likes\):\s*", "", comment).strip()
            if cleaned_comment:
                cleaned_comments.append("- " + cleaned_comment)
        if cleaned_comments:
            sections.append(f"Comments:\n" + "\n".join(cleaned_comments))

    if channel_description:
        sections.append(f"Channel Description:\n{channel_description}")

    message_content = "\n\n".join(sections)
    return {
        'message_content': message_content, 
        'uploader': uploader,
        'video_filename': video_filename,
        'thumb_filename': thumb_filename,
        'channel_url': channel_url,
        'recent_videos': recent_videos,
        'video_duration': video_duration
    }


async def extract_key_frames(
    video_filename: str,
    video_duration: float,
    threshold: float = 0.5, 
    min_interval_seconds: float = 1, 
    max_frames: int = 8,
):

    if not os.path.exists(video_filename):
        return []

    vidcap = cv2.VideoCapture(video_filename)
    if not vidcap.isOpened():
        return []

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

        # قبل از ارسال بر روی سرور این بخش فعال گردد و بخش مشابه این در بالا غیر فعال گردد
        # if diff_ratio > threshold and count_since_last_selected >= min_interval_frames and min_diff_ratio < diff_ratio:
        #     filename = f"{uuid4()}.jpg"
        #     filepath = os.path.join(UPLOAD_DIRECTORY, filename)

        #     cv2.imwrite(filepath, frame)

        #     timestamp = current_frame_number / fps
        #     key_frames.append({
        #         "timestamp": timestamp,
        #         "diff_ratio": diff_ratio,
        #         "image_url": filepath
        #     })
        #     selected += 1

        #     if selected > max_frames:
        #         min_diff_ratio_frame = min(key_frames, key=lambda x: x["diff_ratio"])
        #         os.remove(min_diff_ratio_frame["image_url"])  # حذف عکس ذخیره شده از دیسک
        #         key_frames.remove(min_diff_ratio_frame)
        #         min_diff_ratio = min(item['diff_ratio'] for item in key_frames)
                
            count_since_last_selected = 0
        else:
            count_since_last_selected += 1

        prev_gray = gray

    vidcap.release()
    return key_frames


async def extract_ai_caption(
                             message_content: str, 
                             message_tip: str,
                             key_frames: list,  
                             video_duration: float,
                             prompt_content: str,
                             expertise: str,
                             language: str,
                             base_url: str,
                             word_per_second: float = 2
                             ):
                             

    search_prompt = [
        {
            "role": "system",
            "content": search_ai_caption_prompt[language]["system"]
        },
        {
            "role": "user",
            "content": search_ai_caption_prompt[language]["user_intro"].format(
                message_content=message_content,
                message_tip=message_tip,
                )
        }
    ]
    search_result = await generate_ai_content(search_prompt, "gpt-4o-mini-search-preview", int_max_tokens=500)
        
    content_list = [
        {"type": "text", "text": f"{search_result}\n\n{message_tip}"}
    ]

    frame_intervals = [
        (key_frames[i]['timestamp'], key_frames[i + 1]['timestamp'] if i + 1 < len(key_frames) else video_duration)
        for i in range(len(key_frames))
    ]

    for idx, frame in enumerate(key_frames):
        start_time, end_time = frame_intervals[idx]
        duration = end_time - start_time
        content_list.append({
            "type": "text",
            "text": f"متن مربوط به بازه زمانی {start_time:.2f} تا {end_time:.2f} ثانیه (مدت: {duration:.2f} ثانیه):"
        })

        content_list.append({
            "type": "image_url",
            "image_url": {"url": frame['image_url']}
            # "image_url": {"url": f"{base_url}/{frame['image_url']}"}  # قبل از ارسال به سرور این سطر فعال شود.
        })

    max_words_allowed = int(video_duration * word_per_second)

    messages_caption = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": ai_caption_prompt[language]["system"].format(
                        prompt_content = prompt_content,
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

    ai_caption = await generate_ai_content(messages_caption, openai_model, max_tokens)

    messages_content = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": ai_content_prompt[language]["system"].format(
                        prompt_content = prompt_content,
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
                    "text": ai_content_prompt[language]["user_intro"].format(
                        ai_caption=ai_caption,
                        search_result=search_result,
                        message_tip=message_tip
                    )
                }
            ]
        }
    ]
    
    
    ai_content = await generate_ai_content(messages_content, openai_model, 300)

    messages_title = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": ai_title_prompt[language]["system"].format(
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
                    "text": ai_title_prompt[language]["user_intro"].format(
                        ai_content = ai_content,
                    )
                }
            ]
        }
    ]
    
    
    ai_title = await generate_ai_content(messages_title, openai_model, 300)
    return ai_title, ai_caption, ai_content
    

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

