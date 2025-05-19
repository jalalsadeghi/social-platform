# backend/src/modules/platform/instagram_bot/services/instagram_poster.py
from .secure_credentials import get_social_credentials
from .instagram_client import login_instagram
import random
import asyncio

async def random_delay(min_seconds=3, max_seconds=7):
    await asyncio.sleep(random.uniform(min_seconds, max_seconds))

async def post_to_instagram(db, product):
    user_id = product.user_id
    creds = await get_social_credentials(db, user_id, platform="instagram")

    login_result = await login_instagram(creds["username"], creds["password"])
    if not login_result["success"]:
        print("Login Failed:", login_result["error"])
        return

    cookies = login_result["cookies"]

    # ادامه منطق ارسال پست (آپلود عکس و محتوا)
    # دقت در پیاده‌سازی تا طبیعی و غیرقابل شناسایی باشد:
    print(f"Posting product: {product.title}")

    # برای این مثال فقط لاگ گذاشته شده است.
    # شما در مرحله بعد منطق کامل پست را اضافه خواهید کرد.

    await random_delay()
    print("Post published successfully!")
