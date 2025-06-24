# backend/src/modules/platform/bot/utils/common.py
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

                    # await screenshot(page, name)

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

async def safe_evaluate(page, selector, content_txt, name=None, max_attempts=3, timeout=15000, capture_on_fail=True):
    for attempt in range(1, max_attempts + 1):
        try:
            # کپی کردن عنوان در کلیپ‌بورد مرورگر
            await page.evaluate(f'''
                navigator.clipboard.writeText(`{content_txt}`);
            ''')
            await random_delay(0.5, 1)

            # کلیک کردن در کادر عنوان برای قرار دادن نشانگر ماوس
            await page.click(selector)
            await random_delay(0.5, 1)

            # پیست کردن متن
            await page.keyboard.down('Control')
            await page.keyboard.press('V')
            await page.keyboard.up('Control')

            await random_delay(1, 2)
            await screenshot(page, name)

        except Exception as e:
            print(f"⚠️ Error evaluating selector '{selector}': {e}")
            if capture_on_fail and attempt == max_attempts:
                await screenshot(page, name, "error")


async def screenshot(page, name, status: str = ""):
    try:
        if status == "error":
            html_snapshot_path = f'uploads/{timestamp}_screenshot_{name}_{status}.html'
            with open(html_snapshot_path, 'w', encoding='utf-8') as f:
                f.write(await page.content())
            print(f"🛠️ Error snapshot saved: {html_snapshot_path}")

        screenshot_path = f'uploads/{timestamp}_screenshot_{name}_{status}.png'

        # فونت‌ها را نادیده بگیرید
        await page.route("**/*.{woff,woff2,ttf,otf}", lambda route: route.abort())
        await page.wait_for_load_state("load", timeout=15000)
        await page.screenshot(path=screenshot_path, timeout=15000, full_page=False)
        
    except Exception as e:
        print(f"❌ Failed to take screenshot for {name}: {e}")

async def correct_samesite_value(cookies):
    valid_samesite = {'Strict', 'Lax', 'None'}
    corrected_cookies = []
    for cookie in cookies:
        samesite = cookie.get("sameSite", "Lax").capitalize()
        if samesite not in valid_samesite:
            # اگر مقدار معتبر نبود، پیش‌فرض را روی 'Lax' بگذارید
            samesite = "Lax"
        cookie["sameSite"] = samesite
        corrected_cookies.append(cookie)
    return corrected_cookies