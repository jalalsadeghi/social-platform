# src/modules/platform/instagram_bot/services/instagram_client.py
from playwright.async_api import Page, BrowserContext
from ..utils.common import get_headers, random_delay
from .secure_credentials import get_cookies, store_cookies
import random
import time

async def login_instagram(db, page: Page, context: BrowserContext, user_id, username, password):
    timestamp = int(time.time())
    existing_cookies = await get_cookies(db, user_id, "instagram")

    try:
        # if there are existing cookies, try to use them first
        if existing_cookies:
            await context.add_cookies(existing_cookies)
            await page.goto("https://www.instagram.com/", timeout=60000)
            await random_delay(5, 8)
            if await page.query_selector('nav'):
                # Login with cookies was successful
                
                # screenshot_path = f'uploads/screenshot_01_login_cookie_ok_{timestamp}.png'
                # await page.screenshot(path=screenshot_path)

                return {"success": True, "cookies": existing_cookies}
            else:
                print("Stored cookies invalid or expired, attempting fresh login.")

        # 1. entering the Instagram homepage
        await page.goto("https://www.instagram.com/", timeout=60000)
        await random_delay(5, 8)

        # Manage first popup: Allow all cookies
        try:
            consent_button_selector = 'text="Allow all cookies"'
            await page.wait_for_selector(consent_button_selector, timeout=10000)
            await page.click(consent_button_selector)
            await random_delay(2, 4)
        except:
            pass

        # 2. going to login page
        await page.goto("https://www.instagram.com/accounts/login/", timeout=60000)
        await random_delay(3, 6)

        # Manage second popup (cookie repeat)
        try:
            consent_button_selector = 'text="Allow all cookies"'
            await page.wait_for_selector(consent_button_selector, timeout=5000)
            await page.click(consent_button_selector)
            await random_delay(1, 3)
        except:
            pass

        # 3. Entering username and password
        await page.wait_for_selector('input[name="username"]', timeout=60000)

        await page.click('input[name="username"]')
        await random_delay(1, 3)
        await page.keyboard.type(username, delay=random.randint(100, 200))

        await random_delay(1, 2)

        await page.click('input[name="password"]')
        await random_delay(1, 2)
        await page.keyboard.type(password, delay=random.randint(100, 200))

        await random_delay(2, 4)

        # 4. Click on Login button
        login_buttons = await page.query_selector_all('button[type="submit"]')
        if login_buttons:
            await login_buttons[0].click()
        else:
            raise Exception("Login button not found")

        await random_delay(5, 10)

        # Manage third popup: Save your login info
        try:
            save_info_selector = 'text="Not now"'
            await page.wait_for_selector(save_info_selector, timeout=15000)
            await page.click(save_info_selector)
            await random_delay(1, 3)
        except:
            pass

        # Ensure successful login
        await page.wait_for_selector('nav', timeout=60000)
        await random_delay(2, 5)

        # Getting cookies after successful login
        cookies = await context.cookies()
        await store_cookies(db, user_id, "instagram", cookies)
        # screenshot_path = f'uploads/screenshot_01_login_ok_{timestamp}.png'
        # await page.screenshot(path=screenshot_path)
        return {"success": True, "cookies": cookies}

    except Exception as e:
        # screenshot_path = f'uploads/screenshot_01_login_error_{timestamp}.png'
        # await page.screenshot(path=screenshot_path)
        return {"success": False, "error": str(e)}
