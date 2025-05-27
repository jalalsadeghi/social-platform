# backend/src/modules/platform/instagram_bot/utils/common.py
from core.config import settings
import random
import asyncio
import time

async def random_delay(min_seconds=3, max_seconds=7):
    await asyncio.sleep(random.uniform(min_seconds, max_seconds))

def get_headers():
    return {"User-Agent": settings.USER_AGENT}

async def mouse_move_click(button_selector, page, name=None):
    timestamp = int(time.time())

    await page.wait_for_selector(button_selector, timeout=15000)
    button_box = await page.query_selector(button_selector)
    if not button_box:
        raise Exception(f"❌ button {name} not found")

    # Move mouse to the button slowly and click
    bounding_box_button = await button_box.bounding_box()
    await page.mouse.move(
        bounding_box_button["x"] + bounding_box_button["width"] / 2,
        bounding_box_button["y"] + bounding_box_button["height"] / 2,
        steps=random.randint(10, 20)
    )
    await random_delay(0.5, 1.5)
    await page.mouse.click(
        bounding_box_button["x"] + bounding_box_button["width"] / 2,
        bounding_box_button["y"] + bounding_box_button["height"] / 2
    )

    await random_delay(3, 8)

    screenshot_path = f'uploads/screenshot_{name}_{timestamp}.png'
    await page.screenshot(path=screenshot_path)

    print(f"✅ Clicked on {name} and took a screenshot: {screenshot_path}")
    
