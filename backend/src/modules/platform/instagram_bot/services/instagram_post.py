# backend/src/modules/platform/instagram_bot/services/instagram_post.py
from ..utils.common import random_delay, safe_click, screenshot #mouse_move_click
from modules.product.crud import get_scheduled_products, update_product_status
from modules.product.models import QueueStatus
from sqlalchemy.ext.asyncio import AsyncSession
from playwright.async_api import async_playwright
import random
import time

async def post_to_instagram(db, user_id, page):

    scheduled_products = await get_scheduled_products(db, user_id, limit=1)

    if not scheduled_products:
        print("No scheduled products to post.")
        return

    product = scheduled_products[0]

    # Update product status to processing
    await update_product_status(db, product.id, user_id, QueueStatus.processing)

    video_file = [media.media_url for media in product.media]
    thumbnail_file = [media.local_path for media in product.media]
    media = video_file

    steps = [
        ('svg[aria-label="New post"]', "Create"),
        ('a[role="link"]:has(svg[aria-label="Post"])', "Post"),
        ('button:has-text("Select from computer")', "Select_Video"),
        ('div[role="dialog"]:has-text("Video posts are now shared as reels") button:has-text("OK")', "Popup_Reels"),
        ('svg[aria-label="Select crop"]', "Select_crop"),
        ('svg[aria-label="Crop portrait icon"]', "Select_9_16_crop"),
        ('div[role="button"]:has-text("Next")', "Next_1"),
        ('div[role="button"][tabindex="0"]:has-text("Select from computer")', "Select_thumbnail"),
        ('div[role="button"]:has-text("Next")', "Next_2"),
        ('div[aria-label="Write a caption..."][contenteditable="true"]', "Content_Box")
    ]
    
    for index, (selector, name) in enumerate(steps, start=201):

        if name == "Popup_Reels":
            crop_selector = 'div[role="heading"]:has-text("Crop")'
            try:
                await page.wait_for_selector(crop_selector, state='visible', timeout=30000)
                print("✅ Crop detected on the page.")
            except:
                print("❌ Crop not detected within timeout. Exiting safely.")
                await screenshot(page, "Popup_Reels", "error")
                return False
        
        clicked = await safe_click(page, selector, f"{index}_{name}")
        if not clicked:
            print(f"❌ Could not complete step: {name}. Exiting safely.")
            return
        
        if name == "Select_Video" or name == "Select_thumbnail":
            # Upload media files
            file_input_selector = 'input[type="file"]._ac69'
            try:
                await page.set_input_files(file_input_selector, media)
                media = thumbnail_file  # سری اول ویدئو را آپلود میکند و سری دو تامب نیل را
                print("✅ Media files uploaded successfully.")
                
            except Exception as e:
                print(f"❌ Failed to upload media files: {e}")
                await screenshot(page, "upload_media", "error")
                return
        
        if name == "Content_Box":
            # Type content (بعد از اطمینان از کلیک قبلی)
            ai_content = product.ai_content
            await page.keyboard.type(ai_content, delay=random.randint(50, 150))
            await random_delay(2, 5)
            await screenshot(page, "210_Content_Box")
            # انتقال فوکوس به دکمه Share با 7 بار فشردن Tab
            for _ in range(7):
                await page.keyboard.press("Tab")
                await random_delay(0.5, 0.7)

            # focused_element = await page.evaluate("document.activeElement.outerHTML")
            # print(f"🔍 Element focused now: {focused_element}")

            # حالا دکمه Share باید فوکوس شده باشد
            await page.keyboard.press("Enter")
            await screenshot(page, "210_Share")


    spinner_selector = 'img[alt="Spinner placeholder"][src*="ShFi4iY4Fd9.gif"]' 

    try:
        # منتظر Spinner با timeout کمتر (20 ثانیه)
        await page.wait_for_selector(spinner_selector, state='visible', timeout=20000)
        print("✅ Spinner appeared, upload in progress.")
        
        # انتظار تا زمانی که Spinner ناپدید شود
        await page.wait_for_selector(spinner_selector, state='hidden', timeout=3600000)
        print("🚀 Spinner disappeared, upload completed.")
        await random_delay(1, 3)
        await screenshot(page, "219_Spinner")
    except Exception as e:
        print(f"⚠️ Spinner did not appear promptly: {e}")
        await screenshot(page, "219_Spinner", "error")

    error_popup_selector = 'div[role="dialog"]:has-text("Something went wrong.") button[aria-label="Close"]'
    close_button_selector = "div[role='button'][tabindex='0']:has(svg[aria-label='Close'])"
    try:
        # بررسی پیام خطا
        await page.wait_for_selector(error_popup_selector, state='visible', timeout=5000)
        print("⚠️ Error popup detected. Closing popup.")
        #Update product status to posted after successful upload
        await update_product_status(db, product.id, user_id, QueueStatus.ready)

        clicked = await safe_click(page, close_button_selector, "220_wrong")

        if not clicked:
            print(f"❌ Could not complete step: wrong. Exiting safely.")
            return
        return False  # بازگشت یک مقدار مشخص جهت آگاهی از وضعیت
    except:
        print("✅ No error popup detected, continuing process.")
        await random_delay(1, 3)
        print("🎉 Post shared successfully.")

        #Update product status to posted after successful upload
        await update_product_status(db, product.id, user_id, QueueStatus.posted)

        await screenshot(page, "220_successfully")

    await screenshot(page, "221_Final", "error")

    await page.goto("https://www.instagram.com/ki.blick/")
    