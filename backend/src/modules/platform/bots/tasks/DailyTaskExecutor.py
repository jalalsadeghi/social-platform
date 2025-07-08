# backend/src/modules/platform/bot/tasks/DailyTaskExecutor.py

import asyncio
import random
import redis
from sqlalchemy.ext.asyncio import async_sessionmaker
from core.database import engine
from core.config import settings
from modules.platform.bots.instagram.instagram_post import post_to_instagram
from modules.platform.bots.youtube.youtube_post import post_to_youtube
from modules.platform.crud import get_platform
from modules.platform.bots.utils.platform_utils import login_to_platform, get_page
import logging
from uuid import UUID

logging.basicConfig(level=logging.INFO)

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

async def generate_posting(content_id: UUID, user_id: UUID, platform_id: UUID, platform_name: str):
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as db:
        print(f"2. Content ID: {content_id}, 2. platform_name: {platform_name}")

        creds = await get_platform(db, platform_id, user_id)

        playwright, browser, context, page = await get_page()
        
        login_result = await login_to_platform(
            db=db,
            page=page,
            context=context,
            user_id=user_id,
            username=creds["username"],
            password=creds["password"],
            cookies=creds["cookies"],
            platform=creds["platform"]
        )

        if not login_result["success"]:
            print(f"❌ Login to {creds['platform']} failed: {login_result['log']}")
            await browser.close()
            return

        if creds["platform"] == "instagram":
            post_content = await post_to_instagram(db, user_id, page, content_id, platform_name)
        elif creds["platform"] == "youtube":
            post_content = await post_to_youtube(db, user_id, page, content_id, platform_name)
        
        await browser.close()
        await playwright.stop()


    return post_content