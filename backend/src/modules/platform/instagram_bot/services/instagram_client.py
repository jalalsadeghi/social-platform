# backend/src/modules/platform/instagram_bot/services/instagram_client.py
from playwright.async_api import async_playwright
from ..utils.common import get_headers
import time

async def login_instagram(username: str, password: str, proxy: str = None):
    timestamp = int(time.time())
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context_args = {
            "user_agent": get_headers()["User-Agent"],
            "viewport": {"width": 1280, "height": 720}
        }

        if proxy:
            context_args["proxy"] = {"server": proxy}

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            await page.goto("https://www.instagram.com/accounts/login/", timeout=60000)
            await page.wait_for_selector('input[name="username"]', timeout=60000)

            await page.fill('input[name="username"]', username)
            await page.fill('input[name="password"]', password)

            await page.keyboard.press('Enter')

            # بررسی popup مربوط به ذخیره لاگین و کلیک روی "Not now"
            try:
                await page.wait_for_selector('div[role="button"]:text("Not now")', timeout=15000)
                await page.click('div[role="button"]:text("Not now")')
            except:
                pass  # اگر popup نیامد، عبور می‌کنیم

            # منتظر ظاهر شدن منوی اصلی یا پروفایل برای تایید لاگین موفق
            await page.wait_for_selector('a[href="/"]', timeout=60000)

            cookies = await context.cookies()

            return {"success": True, "cookies": cookies}

        except Exception as e:
            screenshot_path = f'uploads/error_screenshot_{timestamp}.png'
            await page.screenshot(path=screenshot_path)
            return {"success": False, "error": str(e), "screenshot": screenshot_path}

        finally:
            await browser.close()
