# File: backend/src/modules/platform/bots/utils/platform_utils.py
import random
from modules.platform.bots.instagram.instagram_client import login_instagram
from modules.platform.bots.youtube.youtube_client import login_youtube
from playwright.async_api import async_playwright


async def get_page():
    playwright = await async_playwright().start()
    browser_args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-infobars'
    ]

    browser = await playwright.chromium.launch(
        headless=True,
        args=browser_args,
        channel='chrome'
    )

    context = await browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        viewport={
            "width": random.randint(1200, 1920),
            "height": random.randint(800, 1080)
        },
        locale="en-US",
    )

    page = await context.new_page()
    return playwright, browser, context, page

async def login_to_platform(db, page, context, user_id, username, password, cookies, platform):

    login_methods = {
        "instagram": login_instagram,
        "youtube": login_youtube
    }

    platform = platform

    login_result = await login_methods[platform](
        db=db,
        user_id=user_id,
        username=username,
        password=password,
        page=page,
        context=context,
        cookies=cookies,
    )

    print(login_result['log'])
    
    return login_result