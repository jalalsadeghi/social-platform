# backend/src/modules/platform/instagram_bot/utils/common.py
from core.config import settings
import random
import asyncio

async def random_delay(min_seconds=3, max_seconds=7):
    await asyncio.sleep(random.uniform(min_seconds, max_seconds))

def get_headers():
    return {"User-Agent": settings.USER_AGENT}
