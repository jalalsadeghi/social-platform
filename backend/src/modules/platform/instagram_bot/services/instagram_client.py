# backend/src/modules/platform/instagram_bot/services/instagram_client.py
from playwright.async_api import async_playwright
from ..utils.common import get_headers
import random
import asyncio
import time

async def random_delay(min_seconds=2, max_seconds=5):
    await asyncio.sleep(random.uniform(min_seconds, max_seconds))

async def login_instagram(username: str, password: str, proxy: str = None):
    timestamp = int(time.time())
    async with async_playwright() as p:
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars'
        ]

        context_args = {
            "user_agent": get_headers()["User-Agent"],
            "viewport": {"width": random.randint(1200, 1920), "height": random.randint(800, 1080)},
            "locale": "en-US",
        }

        if proxy:
            context_args["proxy"] = {"server": proxy}

        browser = await p.chromium.launch(headless=True, args=browser_args)
        context = await browser.new_context(**context_args)

        page = await context.new_page()

        try:
            # بازدید اولیه برای طبیعی‌تر شدن رفتار
            await page.goto("https://www.instagram.com/", timeout=60000)
            await random_delay(5, 10)

            await page.goto("https://www.instagram.com/accounts/login/", timeout=60000)
            await random_delay(3, 6)

            # تایپ طبیعی‌تر نام کاربری و رمز عبور
            await page.wait_for_selector('input[name="username"]', timeout=60000)
            
            await page.click('input[name="username"]')
            await random_delay(1, 3)
            await page.keyboard.type(username, delay=random.randint(100, 200))

            await random_delay(1, 2)

            await page.click('input[name="password"]')
            await random_delay(1, 2)
            await page.keyboard.type(password, delay=random.randint(100, 200))

            await random_delay(2, 4)

            # کلیک روی دکمه Login
            login_buttons = await page.query_selector_all('button[type="submit"]')
            if login_buttons:
                await login_buttons[0].click()
            else:
                raise Exception("Login button not found")

            await random_delay(5, 10)

            # بستن پاپ‌آپ ذخیره اطلاعات ورود (Not now)
            try:
                await page.wait_for_selector('text="Not Now"', timeout=15000)
                await random_delay(1, 3)
                await page.click('text="Not Now"')
            except:
                pass

            # بررسی لاگین موفق
            await page.wait_for_selector('nav', timeout=60000)
            await random_delay(2, 5)

            cookies = await context.cookies()
            return {"success": True, "cookies": cookies}

        except Exception as e:
            screenshot_path = f'uploads/error_screenshot_{timestamp}.png'
            await page.screenshot(path=screenshot_path)
            return {"success": False, "error": str(e), "screenshot": screenshot_path}

        finally:
            await browser.close()