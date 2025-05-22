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

async def execute_daily_tasks(user_id):
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as db:
        subscription = await get_active_subscription(db, user_id)

        if not subscription:
            print("No active subscription found.")
            return

        features = subscription.plan.features
        post_count = int(features.get("Post", 0))
        comment_count = int(features.get("comment", 0))
        like_count = int(features.get("like", 0))

        print(post_count, comment_count, like_count)

        creds = await get_social_credentials(db, user_id, "instagram")
        login_result = await login_instagram(
            db=db,
            user_id=user_id,
            username=creds["username"],
            password=creds["password"]
        )

        if not login_result["success"]:
            print("Login failed:", login_result["error"])
            return

        print("Logged in successfully.")

        tasks = (["post"] * post_count) + (["comment"] * comment_count) + (["like"] * like_count)
        random.shuffle(tasks)

        for task in tasks:
            if task == "post":
                await post_to_instagram()
                print("Post executed", task)

            elif task == "comment":
                await comment_to_instagram()
                print("Comment executed", task)

            elif task == "like":
                await like_to_instagram()
                print("Like executed", task)

            await random_delay(10, 60)

        print("All daily tasks executed successfully.")

# این تابع را مستقیماً توسط celery فراخوانی کنید
def daily_tasks(user_id):
    asyncio.run(execute_daily_tasks(user_id))
