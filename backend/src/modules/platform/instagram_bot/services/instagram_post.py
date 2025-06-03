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

    media_files = [media.media_url for media in product.media]
    
    steps = [
        ('svg[aria-label="New post"]', "Create"),
        ('a[role="link"]:has(svg[aria-label="Post"])', "Post"),
        ('button:has-text("Select from computer")', "Select_from_computer"),
        ('div[role="dialog"]:has-text("Video posts are now shared as reels") button:has-text("OK")', "Popup_Reels"),
        ('svg[aria-label="Select crop"]', "Select_crop"),
        ('svg[aria-label="Crop portrait icon"]', "Select_9_16_crop"),
        ('div[role="button"]:has-text("Next")', "Next_1"),
        ('div[role="button"]:has-text("Next")', "Next_2"),
        ('div[aria-label="Write a caption..."][contenteditable="true"]', "Content_Box")
    ]
    # ('//div[@role="button" and normalize-space(.)="Share"]', "Share"),
    # ('//div[@role="button" and text()="Share" and contains(@class, "x1n5bzlp")]', "Share_Button")

    
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
        
        if name == "Select_from_computer":
            # Upload media files
            file_input_selector = 'input[type="file"]._ac69'
            try:
                await page.set_input_files(file_input_selector, media_files)
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
    error_popup_selector = 'div[role="dialog"]:has-text("Something went wrong") button[aria-label="Close"]'
    
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
        
    try:
        # بررسی پیام خطا
        await page.wait_for_selector(error_popup_selector, state='visible', timeout=5000)
        print("⚠️ Error popup detected. Closing popup.")
        await screenshot(page, "220_wrong", "error")
        return False  # بازگشت یک مقدار مشخص جهت آگاهی از وضعیت
    except:
        print("✅ No error popup detected, continuing process.")
        await random_delay(1, 3)
        await screenshot(page, "220_wrong")
        
    await page.goto("https://www.instagram.com/ki.blick/")
    print("🎉 Post shared successfully.")
    await screenshot(page, "223_successfully")




# async def post_to_instagram(db, user_id, page):

#     scheduled_products = await get_scheduled_products(db, user_id, limit=1)
#     if not scheduled_products:
#         print("No scheduled products to post.")
#         return

#     product = scheduled_products[0]

#     # Update product status to processing
#     # await update_product_status(db, product.id, user_id, QueueStatus.processing)

#     media_files = [media.media_url for media in product.media]
#     print(f"media files: {media_files}")
    
#     # 1. Click on 'Create' button
#     create_button_selector = 'svg[aria-label="New post"]'

#     if not await mouse_move_click(create_button_selector, page, "2_1_Create"):
#         print("⚠️ Unable to click Create button. Exiting.")
#         return

#     # 2. Select 'Post' option from dropdown
#     post_option_selector = 'a[role="link"]:has(svg[aria-label="Post"])'
#     if not await mouse_move_click(post_option_selector, page, "2_2_Post"):
#         print("⚠️ Unable to click Post button. Exiting.")
#         return

#     # 3. Click on 'Select from computer' button
#     select_button_selector = 'button:has-text("Select from computer")'
#     if not await mouse_move_click(select_button_selector, page, "2_3_Select_from_computer"):
#         print("⚠️ Unable to click Select from computer button. Exiting.")
#         return

#     # 4. Upload media file directly (element might be hidden)
#     file_input_selector = 'input[type="file"]._ac69'
#     if not await page.set_input_files(file_input_selector, media_files):
#         print("⚠️ Unable to set_input_files. Exiting.")
#         return

#     # 5. Reels Popup Handling
#     select_popup_reels = 'div[role="dialog"]:has-text("Video posts are now shared as reels") button:has-text("OK")'
#     try:
#         print("⚠️ Popup about Reels detected. Clicking OK...")
#         if not await mouse_move_click(select_popup_reels, page, "2_4_Popup_Reels"):
#             print("⚠️ Unable to click Reels OK button. Exiting.")
#             return
#     except Exception as e:
#         print("ℹ️ No Reels popup detected. Proceeding normally...")

#     # 6. Click on 'Next' button to proceed
#     for i in range(2):
#         next_button_selector = 'div[role="button"]:has-text("Next")'
#         if not await mouse_move_click(next_button_selector, page, f"2_5_Next_{i+1}"):
#             print(f"⚠️ Unable to click Next_{i+1} button. Exiting.")
#             return
        
#     # 8. Add Content Description
#     ai_content = product.ai_content

#     # Selector for content editable textbox
#     content_box_selector = 'div[aria-label="Write a caption..."][contenteditable="true"]'
#     if not await mouse_move_click(content_box_selector, page, "2_6_Content_Box"):
#         print(f"⚠️ Unable to click content editable button. Exiting.")
#         return
    
#     # Type the ai_content slowly, simulating human behavior
#     await page.keyboard.type(ai_content, delay=random.randint(50, 150))
#     await random_delay(2, 5)

#     # 9. Click on 'Share' button
#     share_button_selector = '//div[@role="button" and normalize-space(.)="Share"]'
#     if not await mouse_move_click(share_button_selector, page, "2_7_Share_Button"):
#         print(f"⚠️ Unable to click Share button. Exiting.")
#         return

#     # 10. Wait for the spinner to appear (upload started)
#     spinner_selector = 'img[alt="Spinner placeholder"][src*="ShFi4iY4Fd9.gif"]'
#     try:
#         await page.wait_for_selector(spinner_selector, state='visible', timeout=30000)
#         print("✅ Spinner appeared, upload in progress.")

#         # 11. Wait for spinner to disappear (upload finished)
#         await page.wait_for_selector(spinner_selector, state='hidden', timeout=3600000)
#         print("🚀 Upload completed, spinner is gone.")

#         screenshot_path = f'uploads/screenshot_2_8_spinner_selector_{timestamp}.png'
#         await page.screenshot(path=screenshot_path)
#         print(f"✅ Spinner selector screenshot saved")
#     except:
#         print(f"❌ Issue detecting spinner: {e}")
#         return

#     # Optional: Verify that sharing was successful
#     success_message_selector = 'div[role="heading"]:has-text("Post shared")'
#     try:
#         await page.wait_for_selector(success_message_selector, timeout=10000)
#         print("🎉 Post shared successfully on Instagram.")
#     except:
#         print("⚠️ Post might have been shared, but verification message was not found.")

#     # # Update product status to posted after successful upload
#     # # await update_product_status(db, product.id, user_id, QueueStatus.posted)

#     timestamp = int(time.time())
#     screenshot_path = f'uploads/screenshot_2_100_finish_{timestamp}.png'
#     await page.screenshot(path=screenshot_path)
#     print(f"🎉 Screenshot finish screenshot saved")

    