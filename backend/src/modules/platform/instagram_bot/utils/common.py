# backend/src/modules/platform/instagram_bot/utils/common.py
from core.config import settings

def get_headers():
    return {"User-Agent": settings.USER_AGENT}
