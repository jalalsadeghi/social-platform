# backend/src/modules/platform/instagram_bot/services/instagram_post.py
from ..utils.common import random_delay
from modules.product.crud import get_scheduled_products, update_product_status
from modules.product.models import QueueStatus
from sqlalchemy.ext.asyncio import AsyncSession
import time
import random

async def post_to_instagram(db, user_id, page):
    timestamp = int(time.time())


    scheduled_products = await get_scheduled_products(db, user_id, limit=1)

    if not scheduled_products:
        print("No scheduled products to post.")
        return

    product = scheduled_products[0]

    # Update product status to processing
    await update_product_status(db, product.id, user_id, QueueStatus.processing)

    media_files = [media.media_url for media in product.media]
    print(f"media files: {media_files}")
    
    # 1. Click on 'Create' button
    create_button_selector = 'svg[aria-label="New post"]'
    await page.wait_for_selector(create_button_selector, timeout=15000)
    create_button = await page.query_selector(create_button_selector)
    if not create_button:
        raise Exception("Create button not found")

    # Move mouse to the button slowly and click
    bounding_box = await create_button.bounding_box()
    await page.mouse.move(
        bounding_box["x"] + bounding_box["width"] / 2,
        bounding_box["y"] + bounding_box["height"] / 2,
        steps=random.randint(10, 20)
    )
    await random_delay(0.5, 1.5)
    await page.mouse.click(
        bounding_box["x"] + bounding_box["width"] / 2,
        bounding_box["y"] + bounding_box["height"] / 2
    )

    screenshot_path = f'uploads/screenshot_PostBox_Create_ok_{timestamp}.png'
    await page.screenshot(path=screenshot_path)
    await random_delay(1, 3)

    # 2. Select 'Post' option from dropdown
    post_option_selector = 'a[role="link"]:has(svg[aria-label="Post"])'
    await page.wait_for_selector(post_option_selector, timeout=10000)
    post_option = await page.query_selector(post_option_selector)
    if not post_option:
        raise Exception("Post option not found")

    # Move mouse to the 'Post' option and click
    bounding_box_post = await post_option.bounding_box()
    await page.mouse.move(
        bounding_box_post["x"] + bounding_box_post["width"] / 2,
        bounding_box_post["y"] + bounding_box_post["height"] / 2,
        steps=random.randint(10, 20)
    )
    await random_delay(0.5, 1.5)
    await page.mouse.click(
        bounding_box_post["x"] + bounding_box_post["width"] / 2,
        bounding_box_post["y"] + bounding_box_post["height"] / 2
    )


    await random_delay(2, 5)

    screenshot_path = f'uploads/screenshot_PostBox_option_ok_{timestamp}.png'
    await page.screenshot(path=screenshot_path)

    # 3. Click on 'Select from computer' button
    select_button_selector = 'button:has-text("Select from computer")'
    await page.wait_for_selector(select_button_selector, timeout=10000)
    select_button = await page.query_selector(select_button_selector)
    if not select_button:
        raise Exception("Select from computer button not found")

    bounding_box_select = await select_button.bounding_box()
    await page.mouse.move(
        bounding_box_select["x"] + bounding_box_select["width"] / 2,
        bounding_box_select["y"] + bounding_box_select["height"] / 2,
        steps=random.randint(10, 20)
    )
    await random_delay(0.5, 1.5)
    await page.mouse.click(
        bounding_box_select["x"] + bounding_box_select["width"] / 2,
        bounding_box_select["y"] + bounding_box_select["height"] / 2
    )

    await random_delay(2, 4)

    screenshot_path = f'uploads/screenshot_Select_computer_ok_{timestamp}.png'
    await page.screenshot(path=screenshot_path)

    # 4. Upload media files (photo or video)
    input_file_selector = 'input[type="file"][multiple]'
    await page.set_input_files(input_file_selector, media_files)

    await random_delay(3, 6)

    screenshot_path = f'uploads/screenshot_MediaUploaded_{timestamp}.png'
    await page.screenshot(path=screenshot_path)
    print("Media files selected and uploaded successfully.")

    # Update product status to posted after successful upload
    await update_product_status(db, product.id, user_id, QueueStatus.posted)

    # post_next_div = 'div[role="button"]:has-text("Next")'
    # if await page.query_selector(post_next_div):
    #     screenshot_path = f'uploads/screenshot_PostBox_ok_{timestamp}.png'
    #     await page.screenshot(path=screenshot_path)
    #     print("Create post popup opened successfully.")
    # else:
    #     screenshot_path = f'uploads/screenshot_PostBox_ok_{timestamp}.png'
    #     await page.screenshot(path=screenshot_path)
    #     raise Exception("Failed to open create post popup")
