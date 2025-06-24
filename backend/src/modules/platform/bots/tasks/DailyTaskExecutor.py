# backend/src/modules/platform/bot/tasks/DailyTaskExecutor.py

import asyncio
import random
import redis
from sqlalchemy.ext.asyncio import async_sessionmaker
from core.database import engine
from core.config import settings
from modules.platform.bots.instagram.instagram_post import post_to_instagram
from modules.platform.bots.instagram.instagram_client import login_instagram
from modules.platform.bots.youtube.youtube_client import login_youtube
from modules.platform.bots.youtube.youtube_post import post_to_youtube
from modules.platform.crud import get_platform
from modules.platform.bots.utils.common import random_delay
from playwright.async_api import async_playwright
import logging
from uuid import UUID

logging.basicConfig(level=logging.INFO)

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

async def generate_posting(content_id: UUID, user_id: UUID, platform_id: UUID, platform_name: str):
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as db:
        print(f"2. Content ID: {content_id}, 2. platform_name: {platform_name}")

        creds = await get_platform(db, platform_id, user_id)

        async with async_playwright() as p:
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars'
            ]

            browser = await p.chromium.launch(
                headless=True,
                args=browser_args,
                channel='chrome'
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": random.randint(1200, 1920), "height": random.randint(800, 1080)},
                locale="en-US",
            )

            page = await context.new_page()

            if creds["platform"] is "instagram":
                login_result = await login_instagram(
                    db=db,
                    user_id=user_id,
                    username=creds["username"],
                    password=creds["password"],
                    page=page,
                    context=context,
                    cookies=creds["cookies"],
                )
            elif creds["platform"] is "youtube":
                login_result = await login_youtube(
                    db=db,
                    user_id=user_id,
                    username=creds["username"],
                    password=creds["password"],
                    page=page,
                    context=context,
                    cookies=creds["cookies"],
                )

            if not login_result["success"]:
                print(f"Login to {creds['platform']} failed: {login_result['error']}")
                await browser.close()
                return

            print(f"Logged in {creds['platform']} successfully.")
            
            if creds["platform"] is "instagram":
                post_content = await post_to_instagram(db, user_id, page, content_id, platform_name)
            elif creds["platform"] is "youtube":
                post_content = await post_to_youtube(db, user_id, page, content_id, platform_name)
            await browser.close()


    return post_content