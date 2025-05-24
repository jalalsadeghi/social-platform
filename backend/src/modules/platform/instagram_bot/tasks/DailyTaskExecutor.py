# backend/src/modules/platform/instagram_bot/tasks/DailyTaskExecutor.py

import asyncio
import random
from sqlalchemy.ext.asyncio import async_sessionmaker
from core.database import engine
from modules.platform.instagram_bot.services.instagram_post import post_to_instagram
from modules.platform.instagram_bot.services.instagram_comment import comment_to_instagram
from modules.platform.instagram_bot.services.instagram_like import like_to_instagram
from modules.platform.instagram_bot.services.secure_credentials import get_social_credentials
from modules.platform.instagram_bot.services.instagram_client import login_instagram
from modules.plan.crud import get_active_subscription
from modules.platform.instagram_bot.utils.common import random_delay
from modules.product.crud import get_scheduled_products
from playwright.async_api import async_playwright


async def execute_daily_tasks(user_id):
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as db:
        subscription = await get_active_subscription(db, user_id)

        if not subscription:
            print("No active subscription found.")
            return

        features = subscription.plan.features
        requested_post_count = int(features.get("Post", 0))

        scheduled_products = await get_scheduled_products(db, user_id, limit=requested_post_count)
        available_post_count = len(scheduled_products)

        product = scheduled_products[0]

        media_files2 = [f"uploads/{media.id}.{media.media_type.name}" for media in product.media]
        print(f"media files: {media_files2}")

        # post_count = min(requested_post_count, available_post_count)
        # comment_count = int(features.get("comment", 0))
        # like_count = int(features.get("like", 0))

        # print(post_count, comment_count, like_count)

        # creds = await get_social_credentials(db, user_id, "instagram")

        # async with async_playwright() as p:
        #     browser_args = [
        #         '--disable-blink-features=AutomationControlled',
        #         '--disable-infobars'
        #     ]

        #     browser = await p.chromium.launch(headless=True, args=browser_args)
        #     context = await browser.new_context(
        #         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        #         viewport={"width": random.randint(1200, 1920), "height": random.randint(800, 1080)},
        #         locale="en-US",
        #     )

        #     page = await context.new_page()

        #     login_result = await login_instagram(
        #         db=db,
        #         user_id=user_id,
        #         username=creds["username"],
        #         password=creds["password"],
        #         page=page,
        #         context=context
        #     )

        #     if not login_result["success"]:
        #         print("Login failed:", login_result["error"])
        #         await browser.close()
        #         return

        #     print("Logged in successfully.")

        #     tasks = (["post"] * post_count) + (["comment"] * comment_count) + (["like"] * like_count)
        #     random.shuffle(tasks)

        #     for task in tasks:
        #         if task == "post":
        #             await post_to_instagram(db, user_id, page)
        #             print("Post executed", task)

        #         elif task == "comment":
        #             await comment_to_instagram(page)
        #             print("Comment executed", task)

        #         elif task == "like":
        #             await like_to_instagram(page)
        #             print("Like executed", task)

        #         await random_delay(2, 10)

        #     await browser.close()

        # print("All daily tasks executed successfully.")


# این تابع را مستقیماً توسط celery فراخوانی کنید
def daily_tasks(user_id):
    asyncio.run(execute_daily_tasks(user_id))
