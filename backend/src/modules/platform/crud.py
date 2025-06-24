# background/src/modules/platform/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.future import select
from typing import Optional, List, Dict, Any
from .models import Platform, SocialPlatform
from modules.ai.models import Language
from modules.ai.crud import generate_ai_content
from .schemas import PlatformUpdate
from core.security import encrypt, decrypt
from uuid import UUID
import json
from core.config import settings
import re

openai_model = settings.OPENAI_MODEL

async def generate_schedule_with_ai(language: str, posts_per_day: int) -> dict:
    prompt = (
        f"You are a JSON generator. Provide a weekly posting schedule in JSON format for social media posts, "
        f"optimized specifically for an audience speaking {language}. "
        f"The schedule should exactly contain {posts_per_day} posts each day, distributed optimally based on "
        f"peak engagement times for regions where this language ({language}) is primarily spoken. "
        f"All times must be provided in Greenwich Mean Time (GMT/UTC). "
        f"The JSON must strictly follow this structure without any additional text or explanation:\n"
        f"Ensure that all weekdays (\"Mon\", \"Tue\", \"Wed\", \"Thu\", \"Fri\", \"Sat\", \"Sun\") are correctly followed, "
        f"and no other day names or variations are used. \n\n"
        f"{{\n"
        f"    \"Mon\":{{\"send01\":\"HH:MM\", \"send02\":\"HH:MM\", ...}},\n"
        f"    \"Tue\":{{\"send01\":\"HH:MM\", \"send02\":\"HH:MM\", ...}},\n"
        f"    \"Wed\":{{\"send01\":\"HH:MM\", \"send02\":\"HH:MM\", ...}},\n"
        f"    \"Thu\":{{\"send01\":\"HH:MM\", \"send02\":\"HH:MM\", ...}},\n"
        f"    \"Fri\":{{\"send01\":\"HH:MM\", \"send02\":\"HH:MM\", ...}},\n"
        f"    \"Sat\":{{\"send01\":\"HH:MM\", \"send02\":\"HH:MM\", ...}},\n"
        f"    \"Sun\":{{\"send01\":\"HH:MM\", \"send02\":\"HH:MM\", ...}}\n"
        f"}}\n\n"
        f"Replace \"HH:MM\" with appropriate 24-hour format times in GMT/UTC.. \n"
        f"Do NOT add any explanatory text or notes. Return ONLY the JSON."
    )

    messages = [
        {"role": "system", "content": "You are an expert JSON programmer."},
        {"role": "user", "content": prompt}
    ]

    response_content = await generate_ai_content(messages, openai_model)
    
    cleaned_json = re.sub(r"```json|```", "", response_content).strip()
    try:
        schedule_dict = json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw content received: {cleaned_json}")
        return {}

    return schedule_dict


# def parse_netscape_cookies(cookie_str: str):
#     cookies = []
#     for line in cookie_str.strip().split("\n"):
#         if line.startswith('#') or not line.strip():
#             continue
#         domain, _, path, secure, expires, name, value = line.strip().split("\t")
#         cookies.append({
#             "domain": domain,
#             "path": path,
#             "name": name,
#             "value": value,
#             "secure": secure.lower() == "true",
#             "expires": int(expires)
#         })
#     return cookies


async def create_platform(
        db: AsyncSession, 
        user_id: UUID, 
        platform: SocialPlatform,
        identifier: str, 
        credentials: dict, 
        cookies: Optional[List[Dict[str, Any]]],
        language: Language,
        posts_per_day: int,
        is_oauth: bool,
        ):
    
    existing_platform = await get_platform_by_identifier(db, user_id, identifier)
    
    if existing_platform:
        raise HTTPException(
            status_code=400,
            detail="This account_identifier already exists."
        )
    encrypted_creds = {key: encrypt(value) for key, value in credentials.items()}
    # cookie_list = parse_netscape_cookies(cookies)
    schedule = await generate_schedule_with_ai(language.value, posts_per_day)
    print(f"Raw content received schedule: {schedule}")

    account = Platform(
        user_id=user_id,
        platform=platform,
        account_identifier=identifier,
        credentials=encrypted_creds,
        language=language,
        posts_per_day=posts_per_day,
        schedule=schedule,
        cookies=cookies,
        is_oauth=is_oauth,
    )
    db.add(account)
    await db.commit()


async def get_platform_by_identifier(db: AsyncSession, user_id: UUID, identifier: str):
    result = await db.execute(
        select(Platform).where(Platform.account_identifier == identifier, Platform.user_id == user_id)
    )
    platform = result.scalars().first()
    if not platform:
        return None
    
    credentials = platform.credentials or {}

    schedule = platform.schedule if isinstance(platform.schedule, dict) else {}

    return {
        "id": platform.id,
        "user_id": platform.user_id,
        "platform": platform.platform.value,
        "username": decrypt(credentials.get('username', '')),
        "language": platform.language,
        "posts_per_day": platform.posts_per_day,
        "schedule": schedule, 
        "cookies": platform.cookies,
        "created_at": platform.created_at,
        "updated_at": platform.updated_at
    }

async def get_platforms(user_id: UUID, db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(Platform).where(Platform.user_id == user_id).offset(skip).limit(limit)

    result = await db.execute(query)
    platforms = result.scalars().all()

    decrypted_creds_list = []
    for platform in platforms:
        credentials = platform.credentials or {}
        decrypted_creds = {
            "id": platform.id,
            "user_id": platform.user_id,
            "platform": platform.platform.value,
            "account_identifier": platform.account_identifier,
            "username": decrypt(credentials.get('username', '')),
            "password": decrypt(credentials.get('password', '')),
            "language": platform.language,
            "posts_per_day": platform.posts_per_day,
            "schedule": platform.schedule, 
            "cookies": platform.cookies,
            "updated_at": platform.updated_at,
            "created_at": platform.created_at
        }
        decrypted_creds_list.append(decrypted_creds)

    return decrypted_creds_list


async def get_platform(db: AsyncSession, platform_id: UUID, user_id: UUID):
    result = await db.execute(
        select(Platform).where(Platform.id == platform_id, Platform.user_id == user_id)
    )
    platform = result.scalars().first()

    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found."
        )

    credentials = platform.credentials or {}

    decrypted_creds = {
        "id": platform.id,
        "user_id": platform.user_id,
        "platform": platform.platform.value,  # حتماً باید مقدار Enum را برگردانید
        "account_identifier": platform.account_identifier,
        "username": decrypt(credentials.get('username', '')),
        "password": decrypt(credentials.get('password', '')),
        "language": platform.language,
        "posts_per_day": platform.posts_per_day,
        "schedule": platform.schedule,         
        "cookies": platform.cookies,
        "updated_at": platform.updated_at,
        "created_at": platform.created_at
    }

    return decrypted_creds


async def update_platforms(db: AsyncSession, platforms_id: UUID, user_id: UUID, data: PlatformUpdate):
    result = await db.execute(
        select(Platform).where(
            Platform.id == platforms_id,
            Platform.user_id == user_id
        )
    )
    db_platform = result.scalars().first()

    if not db_platform:
        return None

    credentials = db_platform.credentials or {}
    update_data = data.dict(exclude_unset=True)

    # تشخیص تغییرات
    posts_per_day_changed = 'posts_per_day' in update_data and update_data['posts_per_day'] != db_platform.posts_per_day
    language_changed = 'language' in update_data and update_data['language'] != db_platform.language
    schedule_changed = 'schedule' in update_data

    if 'password' in update_data and update_data['password']:
        credentials['password'] = encrypt(update_data['password'])

    if 'cookies' in update_data:
        cookie_list = update_data['cookies']
        if isinstance(cookie_list, list):
            db_platform.cookies = cookie_list
        else:
            raise ValueError("Cookies data must be a list of dictionaries")

    if 'platform' in update_data:
        db_platform.platform = update_data['platform']

    if language_changed:
        db_platform.language = update_data['language']

    if posts_per_day_changed:
        db_platform.posts_per_day = update_data['posts_per_day']

    # تولید یا به‌روزرسانی schedule
    if posts_per_day_changed or language_changed:
        lang = db_platform.language.value
        posts_per_day = db_platform.posts_per_day
        new_schedule = await generate_schedule_with_ai(lang, posts_per_day)
        db_platform.schedule = new_schedule
    elif schedule_changed:
        db_platform.schedule = update_data['schedule']

    db_platform.credentials = credentials

    await db.commit()
    await db.refresh(db_platform)

    response_data = {
        "id": db_platform.id,
        "user_id": db_platform.user_id,
        "platform": db_platform.platform,
        "username": decrypt(credentials.get('username', '')),
        "language": db_platform.language,
        "posts_per_day": db_platform.posts_per_day,
        "schedule": db_platform.schedule,
        "cookies": db_platform.cookies,
        "created_at": db_platform.created_at,
        "updated_at": db_platform.updated_at
    }

    return response_data




async def delete_platform(db: AsyncSession, platform_id: UUID, user_id: UUID):
    result = await db.execute(select(Platform).where(Platform.id == platform_id, Platform.user_id == user_id))
    db_platform = result.scalars().first()
    if db_platform:
        await db.delete(db_platform)
        await db.commit()
        return True
    return False




