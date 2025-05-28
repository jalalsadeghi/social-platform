# src/modules/product/scraper.py
from .scraper_product import scrape_product_page
from .scraper_youtube import scrape_youtube_short
from openai import OpenAI
from core.config import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def is_youtube_url(url: str) -> bool:
    return "youtube.com/shorts/" in url or "youtu.be/" in url

async def scrape_and_extract(url: str, base_url: str, timeout: int = 60) -> dict:
    if is_youtube_url(url):
        raw_data = await scrape_youtube_short(url)
    else:
        raw_data = await scrape_product_page(url, base_url, timeout)

    return raw_data