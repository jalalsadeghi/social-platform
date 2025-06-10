# backend/src/modules/platform/instagram_bot/utils/common.py
from core.config import settings
import random
import asyncio
import time
timestamp = int(time.time())

async def random_delay(min_seconds=3, max_seconds=7):
    await asyncio.sleep(random.uniform(min_seconds, max_seconds))

def get_headers():
    return {"User-Agent": settings.USER_AGENT}

async def safe_click(page, selector, name=None, max_attempts=3, timeout=15000, capture_on_fail=True):
    for attempt in range(1, max_attempts + 1):
        
        try:
            await page.wait_for_selector(selector, timeout=timeout, state='visible')
            element = await page.query_selector(selector)
            
            if element:
                box = await element.bounding_box()
                if box:
                    await page.mouse.move(
                        box["x"] + box["width"] / 2,
                        box["y"] + box["height"] / 2,
                        steps=random.randint(10, 20)
                    )
                    await random_delay(0.5, 1.5)
                    await page.mouse.click(
                        box["x"] + box["width"] / 2,
                        box["y"] + box["height"] / 2
                    )
                    await random_delay(2, 4)
                    print(f"✅ Successfully clicked: {name}")

                    await screenshot(page, name)

                    return True
                else:
                    raise Exception("ℹ️ Element has no bounding box.")
            else:
                raise Exception("⚠️ Element not found after selector matched.")

        except Exception as e:
            print(f"⚠️ Attempt {attempt} for clicking '{name}' failed: {e}")

            # فقط در صورت شکست نهایی اسکرین‌شات گرفته می‌شود
            if capture_on_fail and attempt == max_attempts:
                await screenshot(page, name, "error")

    print(f"❌ All attempts failed for {name}. Exiting.")
    return False


async def screenshot(page, name, status:str = ""):
    if status == "error":
        html_snapshot_path = f'uploads/{timestamp}_screenshot_{name}_{status}.html'
        with open(html_snapshot_path, 'w', encoding='utf-8') as f:
            f.write(await page.content())
        print(f"🛠️ Error snapshot saved: {html_snapshot_path}")

    screenshot_path = f'uploads/{timestamp}_screenshot_{name}_{status}.png'
    await page.screenshot(path=screenshot_path)