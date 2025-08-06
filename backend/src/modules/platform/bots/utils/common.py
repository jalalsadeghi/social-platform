# File: backend/src/modules/platform/bots/utils/common.py
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

async def safe_evaluate(page, selector, content_txt, name=None, max_attempts=3, timeout=30000, capture_on_fail=True):
    for attempt in range(1, max_attempts + 1):
        try:
            await page.wait_for_selector(selector, state='visible', timeout=timeout)
            await page.focus(selector)
            await random_delay(0.5, 1)
            await page.click(selector, timeout=timeout)
            await random_delay(0.5, 1)
            await page.keyboard.down('Control')
            await page.keyboard.press('A')
            await page.keyboard.press('Backspace')
            await page.keyboard.up('Control')

            # Copy-paste logic instead of typing
            await page.evaluate(f"""navigator.clipboard.writeText(`{content_txt}`)""")
            await random_delay(0.5, 1)
            await page.keyboard.down('Control')
            await page.keyboard.press('V')
            await page.keyboard.up('Control')

            await random_delay(1, 2)
            await screenshot(page, name)
            print(f"✅ Successfully evaluated selector: {selector}")
            return True
        except Exception as e:
            print(f"⚠️ Error evaluating selector '{selector}': {e}")
            await screenshot(page, name, "error")
            await random_delay(2, 4)
    return False


async def screenshot(page, name, status: str = ""):
    try:
        if status == "error":
            html_snapshot_path = f'uploads/{timestamp}_screenshot_{name}_{status}.html'
            with open(html_snapshot_path, 'w', encoding='utf-8') as f:
                f.write(await page.content())
            print(f"🛠️ Error snapshot saved: {html_snapshot_path}")

        screenshot_path = f'uploads/{timestamp}_screenshot_{name}_{status}.png'
        await page.screenshot(path=screenshot_path)
        
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

