# backend/src/modules/platform/instagram_bot/services/instagram_post.py
from ..utils.common import random_delay, mouse_move_click
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
    # await update_product_status(db, product.id, user_id, QueueStatus.processing)

    media_files = [media.media_url for media in product.media]
    print(f"media files: {media_files}")
    
    # 1. Click on 'Create' button
    create_button_selector = 'svg[aria-label="New post"]'

    await mouse_move_click(create_button_selector, page, "2_1_Create")


    # 2. Select 'Post' option from dropdown
    post_option_selector = 'a[role="link"]:has(svg[aria-label="Post"])'

    await mouse_move_click(post_option_selector, page, "2_2_Post")


    # 3. Click on 'Select from computer' button
    select_button_selector = 'button:has-text("Select from computer")'

    await mouse_move_click(select_button_selector, page, "2_3_Select_from_computer")


    # 4. Upload media file directly (element might be hidden)
    file_input_selector = 'input[type="file"]._ac69'
    await page.set_input_files(file_input_selector, media_files)


    # 5. Reels Popup Handling
    select_popup_reels = 'div[role="dialog"]:has-text("Video posts are now shared as reels") button:has-text("OK")'

    try:
        print("⚠️ Popup about Reels detected. Clicking OK...")
        await mouse_move_click(select_popup_reels, page, "2_4_Popup_Reels")

    except Exception as e:
        print("ℹ️ No Reels popup detected. Proceeding normally...")

    # 6. Click on 'Next' button to proceed
    for i in range(2):
        next_button_selector = 'div[role="button"]:has-text("Next")'
        await mouse_move_click(next_button_selector, page, f"2_5_Next_{i+1}")
    
    # 8. Add Content Description
    ai_content = product.ai_content

    # Selector for content editable textbox
    content_box_selector = 'div[aria-label="Write a caption..."][contenteditable="true"]'

    await mouse_move_click(content_box_selector, page, "2_6_Content_Box")

    # Type the ai_content slowly, simulating human behavior
    await page.keyboard.type(ai_content, delay=random.randint(50, 150))
    await random_delay(2, 5)

    # 9. Click on 'Share' button
    # share_button_selector = '//div[@role="button" and normalize-space(.)="Share"]'

    # await mouse_move_click(share_button_selector, page, "2_7_Share_Button")

    # # # 6. Wait for the spinner to appear (upload started)
    # # spinner_selector = 'img[alt="Spinner placeholder"][src*="ShFi4iY4Fd9.gif"]'
    # # await page.wait_for_selector(spinner_selector, state='visible', timeout=30000)
    # # print("✅ Spinner appeared, upload in progress.")


    # # screenshot_path = f'uploads/screenshot_spinner_selector_{timestamp}.png'
    # # await page.screenshot(path=screenshot_path)
    # # print(f"✅ Spinner selector screenshot saved")

    # # # 7. Wait for spinner to disappear (upload finished)
    # # await page.wait_for_selector(spinner_selector, state='hidden', timeout=3600000)
    # # print("🚀 Upload completed, spinner is gone.")

    # # # Optional: Verify that sharing was successful
    # # success_message_selector = 'div[role="heading"]:has-text("Post shared")'
    # # try:
    # #     await page.wait_for_selector(success_message_selector, timeout=10000)
    # #     print("🎉 Post shared successfully on Instagram.")
    # # except:
    # #     print("⚠️ Post might have been shared, but verification message was not found.")

    # # screenshot_path = f'uploads/screenshot_finish_{timestamp}.png'
    # # await page.screenshot(path=screenshot_path)
    # # print(f"✅ Screenshot finish screenshot saved")

    # # # Update product status to posted after successful upload
    # # # await update_product_status(db, product.id, user_id, QueueStatus.posted)

    timestamp = int(time.time())
    screenshot_path = f'uploads/screenshot_2_100_finish_{timestamp}.png'
    await page.screenshot(path=screenshot_path)
    print(f"🎉 Screenshot finish screenshot saved")

    