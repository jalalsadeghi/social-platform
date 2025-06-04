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



# async def mouse_move_click(button_selector, page, name=None, retry_attempts=3):
#     timestamp = int(time.time())
#     attempts = 0

#     while attempts < retry_attempts:
#         await random_delay(1, 3)
#         try:
#             await page.wait_for_selector(button_selector, timeout=15000) #, state='visible'
#             button_box = await page.query_selector(button_selector)

#             if not button_box:
#                 print(f"❌ Button '{name}' not found on attempt {attempts+1}")
#                 raise 

#             bounding_box_button = await button_box.bounding_box()
#             if not bounding_box_button:
#                 print(f"❌ Button '{name}' has no bounding box on attempt {attempts+1}")
#                 raise 

#             await page.mouse.move(
#                 bounding_box_button["x"] + bounding_box_button["width"] / 2,
#                 bounding_box_button["y"] + bounding_box_button["height"] / 2,
#                 steps=random.randint(10, 20)
#             )
#             await random_delay(0.5, 1.5)
#             await page.mouse.click(
#                 bounding_box_button["x"] + bounding_box_button["width"] / 2,
#                 bounding_box_button["y"] + bounding_box_button["height"] / 2
#             )
#             await random_delay(2, 4)

#             screenshot_path = f'uploads/screenshot_{name}_{timestamp}.png'
#             await page.screenshot(path=screenshot_path)
#             print(f"✅ Clicked on {name}, screenshot saved: {screenshot_path}")

#             # Verify action succeeded if required
#             return True

#         except Exception as e:
#             print(f"⚠️ Attempt {attempts+1} for clicking '{name}' failed: {e}")
#             attempts += 1
#             await random_delay(2, 4)

#     print(f"❌ All attempts to click '{name}' have failed.")
#     return False