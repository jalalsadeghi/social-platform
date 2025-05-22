# backend/src/modules/platform/instagram_bot/tasks/DailyTaskExecutor.py

from modules.platform.instagram_bot.services.instagram_client import login_instagram
from sqlalchemy.ext.asyncio import async_sessionmaker
from core.database import engine
from modules.platform.instagram_bot.services.secure_credentials import get_social_credentials

async def daily_tasks(user_id):
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as db:
        creds = await get_social_credentials(db, user_id, "instagram")
        login_result = await login_instagram(
            db=db,
            user_id=user_id,
            username=creds["username"],
            password=creds["password"]
        )
        if login_result["success"]:
            print("Logged in successfully.")
        else:
            print("Login failed:", login_result["error"])
