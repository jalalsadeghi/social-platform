# src/modules/platform/bot/instagram/instagram_client.py
from playwright.async_api import Page, BrowserContext
from ..utils.common import random_delay
from ..utils.secure_credentials import get_cookies, store_cookies
from ..utils.common import correct_samesite_value
import random
import json

async def login_instagram(db, page: Page, context: BrowserContext, user_id, username, password, cookies):

    try:
        # if there are existing cookies, try to use them first
        if cookies:
            if isinstance(cookies, str):
                cookies = json.loads(cookies)
            
            cookies = await correct_samesite_value(cookies)

            await context.add_cookies(cookies)
            await page.goto("https://www.instagram.com/", timeout=60000)
            await random_delay(5, 8)
            if await page.query_selector('nav'):
                # Login with cookies was successful
                return {"success": True, "log": "✅ Login successful with cookies."}
            else:
                return {"success": False, "log": "❌ Stored cookies invalid or expired, attempting fresh login."}

        # # 1. entering the Instagram homepage
        # await page.goto("https://www.instagram.com/", timeout=60000)
        # await random_delay(5, 8)

        # # Manage first popup: Allow all cookies
        # try:
        #     consent_button_selector = 'text="Allow all cookies"'
        #     await page.wait_for_selector(consent_button_selector, timeout=10000)
        #     await page.click(consent_button_selector)
        #     await random_delay(2, 4)
        # except:
        #     pass

        # # 2. going to login page
        # await page.goto("https://www.instagram.com/accounts/login/", timeout=60000)
        # await random_delay(3, 6)

        # # Manage second popup (cookie repeat)
        # try:
        #     consent_button_selector = 'text="Allow all cookies"'
        #     await page.wait_for_selector(consent_button_selector, timeout=5000)
        #     await page.click(consent_button_selector)
        #     await random_delay(1, 3)
        # except:
        #     pass

        # # 3. Entering username and password
        # await page.wait_for_selector('input[name="username"]', timeout=60000)

        # await page.click('input[name="username"]')
        # await random_delay(1, 3)
        # await page.keyboard.type(username, delay=random.randint(100, 200))

        # await random_delay(1, 2)

        # await page.click('input[name="password"]')
        # await random_delay(1, 2)
        # await page.keyboard.type(password, delay=random.randint(100, 200))

        # await random_delay(2, 4)

        # # 4. Click on Login button
        # login_buttons = await page.query_selector_all('button[type="submit"]')
        # if login_buttons:
        #     await login_buttons[0].click()
        # else:
        #     raise Exception("Login button not found")

        # await random_delay(5, 10)

        # # Manage third popup: Save your login info
        # try:
        #     save_info_selector = 'text="Not now"'
        #     await page.wait_for_selector(save_info_selector, timeout=15000)
        #     await page.click(save_info_selector)
        #     await random_delay(1, 3)
        # except:
        #     pass

        # # Ensure successful login
        # await page.wait_for_selector('nav', timeout=60000)
        # await random_delay(2, 5)

        # # Getting cookies after successful login
        # cookies = await context.cookies()
        # await store_cookies(db, user_id, "instagram", cookies)
        # return {"success": True, "cookies": cookies}

    except Exception as e:
        return {"success": False, "log": str(e)}
