# src/modules/content/scraper/scraper.py
from sqlalchemy.ext.asyncio import AsyncSession
from .scrape_youtube_short import scrape_youtube_short


def is_youtube_url(url: str) -> bool:
    return "youtube.com/shorts/" in url or "youtu.be/" in url

async def scrape_and_extract(db: AsyncSession, url: str, prompr_id: str, tip: str, user_id: str, base_url: str) -> dict:
    if is_youtube_url(url):
        raw_data = await scrape_youtube_short(db, url, prompr_id, tip, user_id, base_url)
    # else:
    #     raw_data = await scrape_product_page(url, base_url, timeout)

    return raw_data