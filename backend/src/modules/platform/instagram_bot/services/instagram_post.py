# backend/src/modules/platform/instagram_bot/services/instagram_post.py
from ..utils.common import random_delay
from modules.product.crud import get_scheduled_products, update_product_status
from modules.product.models import QueueStatus
from sqlalchemy.ext.asyncio import AsyncSession
from playwright.async_api import async_playwright
import time
import random
import base64

async def post_to_instagram(db, user_id, page):
    timestamp = int(time.time())


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

    
    # 4. Upload media file directly (element might be hidden)

    async def launch_browser():
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True, args=[
                '--autoplay-policy=no-user-gesture-required',
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
            ]
        )
        context = await browser.new_context()
        page = await context.new_page()

        return playwright, browser, context, page


    file_input_selector = 'input[type="file"]._ac69'
    await page.set_input_files(file_input_selector, media_files)

    uploaded_files_info = await page.evaluate("""
        (fileInputSelector) => {
            const input = document.querySelector(fileInputSelector);
            if (input && input.files.length > 0) {
                return Array.from(input.files).map(file => ({
                    name: file.name,
                    size: file.size,
                    type: file.type
                }));
            }
            return [];
        }
    """, file_input_selector)

    print("✅ Uploaded files info:", uploaded_files_info)

    try:
        video_blob_url = await page.evaluate("""
            (fileInputSelector) => {
                return new Promise((resolve, reject) => {
                    const input = document.querySelector(fileInputSelector);
                    if (!input || !input.files.length) {
                        return reject('File not found.');
                    }

                    const file = input.files[0];
                    const blobURL = URL.createObjectURL(file);
                    const videoElem = document.createElement('video');
                    videoElem.src = blobURL;
                    videoElem.muted = true;
                    videoElem.autoplay = true;
                    videoElem.playsInline = true;
                    videoElem.style.display = 'none';

                    document.body.appendChild(videoElem);

                    videoElem.onloadedmetadata = () => {
                        resolve({
                            blobURL: blobURL,
                            duration: videoElem.duration,
                            width: videoElem.videoWidth,
                            height: videoElem.videoHeight,
                            readyState: videoElem.readyState,
                            paused: videoElem.paused,
                            isBlobSrc: blobURL.startsWith('blob:')
                        });
                    };

                    videoElem.onerror = (e) => reject('Error loading video: ' + e.message);
                });
            }
        """, file_input_selector)

        print("🎥 Instagram-style Video Blob URL Info:", video_blob_url)

        # Final check for video element
        await page.wait_for_selector(f"video[src='{video_blob_url['blobURL']}']", timeout=15000, state='attached')

        video_status = await page.evaluate("""
            (blobURL) => {
                const video = document.querySelector(`video[src="${blobURL}"]`);
                return video ? {
                    src: video.src,
                    duration: video.duration,
                    readyState: video.readyState,
                    paused: video.paused,
                    width: video.videoWidth,
                    height: video.videoHeight,
                    isBlobSrc: video.src.startsWith('blob:')
                } : null;
            }
        """, video_blob_url['blobURL'])

        if video_status:
            print("🎥 Final Video status after Blob URL creation:", video_status)
        else:
            print("⚠️ Video element not found after Blob URL creation.")

    except Exception as e:
        print(f"❌ Error creating Blob URL: {e}")

    screenshot_path = f'uploads/screenshot_VideoBlobURL_{timestamp}.png'
    await page.screenshot(path=screenshot_path)


    # 5. Wait and verify thumbnails (cover.jpg) creation after video upload
    await random_delay(5, 8)  # اطمینان از تولید کامل previewها

    video_canvas_info = await page.evaluate("""
    () => {
        const videoElements = Array.from(document.querySelectorAll('video'));
        const canvasElements = Array.from(document.querySelectorAll('canvas'));

        const videoData = videoElements.map(video => ({
            src: video.src,
            hasBlobSrc: video.src.startsWith('blob:'),
            width: video.videoWidth,
            height: video.videoHeight,
            paused: video.paused,
            duration: video.duration,
            readyState: video.readyState
        }));

        const canvasData = canvasElements.map(canvas => ({
            width: canvas.width,
            height: canvas.height,
            dataURLPreview: canvas.toDataURL('image/jpeg').substring(0, 100) + '...'
        }));

        return { videoData, canvasData };
    }
    """)



    if video_canvas_info["canvasData"]:
        print("🖼️ Canvas elements detected (likely thumbnails):")
        for idx, canvas in enumerate(video_canvas_info["canvasData"], start=1):
            print(f"Canvas {idx}: Resolution: {canvas['width']}x{canvas['height']}, "
                f"DataURL Preview: {canvas['dataURLPreview']}")
    else:
        print("⚠️ No canvas elements detected.")


    # Take a screenshot for verification
    screenshot_path = f'uploads/screenshot_ThumbnailGeneration_{timestamp}.png'
    await page.screenshot(path=screenshot_path)   

    # Wait briefly to ensure canvas elements have loaded properly
    await random_delay(1, 2)

    # # Change the title from 'Create new post' to 'Crop'
    # result = await page.evaluate("""
    # () => {
    #     const headingElement = document.querySelector('div[role="heading"]._ac7a');
    #     if (headingElement && headingElement.innerText === 'Create new post') {
    #         headingElement.innerText = 'Crop';
    #         headingElement.setAttribute('aria-label', 'Crop');
    #         return {
    #             success: true,
    #             oldText: 'Create new post',
    #             newText: headingElement.innerText,
    #             newAriaLabel: headingElement.getAttribute('aria-label')
    #         };
    #     }
    #     return {
    #         success: false,
    #         message: 'Heading element not found or already changed.'
    #     };
    # }
    # """)

    # # Log result for verification
    # if result['success']:
    #     print(f"✅ Title successfully updated from '{result['oldText']}' to '{result['newText']}'.")
    #     print(f"✅ aria-label successfully updated to '{result['newAriaLabel']}'.")
    # else:
    #     print(f"⚠️ Failed to update title: {result['message']}")

    # # Capture screenshot after update for verification
    # screenshot_path = f'uploads/screenshot_TitleUpdatedToCrop_{timestamp}.png'
    # await page.screenshot(path=screenshot_path)

    
    # await random_delay(1, 2)

    # # 6. Update UI with Next and Back buttons
    # ui_update_result = await page.evaluate("""
    # () => {
    #     const headingWrapper = document.querySelector('div._ac78');
    #     const videoContainer = document.querySelector('div[role="presentation"] > div > div');

    #     if (!headingWrapper || !videoContainer) {
    #         return { success: false, message: 'Required elements not found.' };
    #     }

    #     // Set heading wrapper style
    #     headingWrapper.style.width = 'calc(100% - 124.5px)';

    #     // Set video container dimensions
    #     videoContainer.style.height = '621.046px';
    #     videoContainer.style.width = '348px';
    #     videoContainer.style.transform = 'none';

    #     // Fade-in effect for video container
    #     const fadeElement = videoContainer.parentElement;
    #     fadeElement.style.opacity = 0;

    #     const fadeIntervals = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0];
    #     fadeIntervals.forEach((opacity, index) => {
    #         setTimeout(() => fadeElement.style.opacity = opacity, index * 100);
    #     });

    #     // Precisely set Back and Next buttons
    #     const headerContainer = headingWrapper.closest('._ac76._ar86');

    #     if (!headerContainer) {
    #         return { success: false, message: 'Header container not found.' };
    #     }

    #     // Clear existing buttons
    #     headerContainer.querySelectorAll('._ac7b').forEach(btn => btn.remove());

    #     // Create Back button
    #     const backButtonHtml = `
    #         <div class="_ac7b _ac7c">
    #             <div class="x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1i64zmx x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1">
    #                 <div class="x1i10hfl x972fbf xcfux6l x1qhh985 xm0m39n x9f619 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x6s0dn4 xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x1ypdohk x78zum5 xl56j7k x1y1aw1k x1sxyh0 xwib8y2 xurb0ha xcdnw81" role="button" tabindex="0">
    #                     <div class="x6s0dn4 x78zum5 xdt5ytf xl56j7k">
    #                         <span style="display: inline-block; transform: rotate(0deg);">
    #                             <svg aria-label="Back" class="x1lliihq x1n2onr6 x5n08af" fill="currentColor" height="24" role="img" viewBox="0 0 24 24" width="24">
    #                                 <title>Back</title>
    #                                 <line fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" x1="2.909" x2="22.001" y1="12.004" y2="12.004"></line>
    #                                 <polyline fill="none" points="9.276 4.726 2.001 12.004 9.276 19.274" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></polyline>
    #                             </svg>
    #                         </span>
    #                     </div>
    #                 </div>
    #             </div>
    #         </div>`;

    #     // Create Next button
    #     const nextButtonHtml = `
    #         <div class="_ac7b _ac7d">
    #             <div class="x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh xyamay9 x1pi30zi x1l90r2v x1swvt13 x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1">
    #                 <div class="x1i10hfl xjqpnuy xa49m3k xqeqjp1 x2hbi6w xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x1lku1pv x1a2a7pz x6s0dn4 xjyslct x1ejq31n xd10rxx x1sy0etr x17r0tee x9f619 x1ypdohk x1f6kntn xwhw2v2 xl56j7k x17ydfre x2b8uid xlyipyv x87ps6o x14atkfc xcdnw81 x1i0vuye xjbqb8w xm3z3ea x1x8b98j x131883w x16mih1h x972fbf xcfux6l x1qhh985 xm0m39n xt0psk2 xt7dq6l xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x1n5bzlp x173jzuc x1yc6y37" role="button" tabindex="0">Next</div>
    #             </div>
    #         </div>`;

    #     headerContainer.insertAdjacentHTML('beforeend', backButtonHtml);
    #     headerContainer.insertAdjacentHTML('beforeend', nextButtonHtml);

    #     return {
    #         success: true,
    #         buttonsCreated: true,
    #         headingWrapperWidth: headingWrapper.style.width,
    #         videoDimensions: { width: videoContainer.style.width, height: videoContainer.style.height }
    #     };
    # }
    # """)

    # # Log for verification
    # if ui_update_result['success']:
    #     print("✅ UI updated with Next and Back buttons accurately.")
    #     print(f"- Heading Wrapper Width: {ui_update_result['headingWrapperWidth']}")
    #     print(f"- Video Dimensions: {ui_update_result['videoDimensions']['width']} x {ui_update_result['videoDimensions']['height']}")
    # else:
    #     print(f"⚠️ UI update failed: {ui_update_result['message']}")

    # await random_delay(1, 2)

    # Screenshot for verification
    timestamp = int(time.time())
    screenshot_path = f'uploads/screenshot_UIWithButtons_{timestamp}.png'
    await page.screenshot(path=screenshot_path)

    # 6. Hide the interfering element

    # First, find the interfering element and disable pointer-events
    popup_selector = 'div[role="dialog"]:has-text("Video posts are now shared as reels") button:has-text("OK")'

    try:
        # Wait for the popup to appear
        await page.wait_for_selector(popup_selector, timeout=5000)

        # Screenshot for verification
        timestamp = int(time.time())
        screenshot_path = f'uploads/screenshot_ReelsPopup_{timestamp}.png'
        await page.screenshot(path=screenshot_path)

        print("⚠️ 1Popup about Reels detected. Clicking OK...")

        # Click on the OK button in the popup
        await page.click(popup_selector)

        print("✅ 1Popup handled successfully.")

        await random_delay(2, 4)

    except Exception as e:
        print("ℹ️ 1No Reels popup detected. Proceeding normally...")


    await random_delay(1, 2)

    # Screenshot for verification
    timestamp = int(time.time())
    screenshot_path = f'uploads/screenshot_InterferingElementHidden_{timestamp}.png'
    await page.screenshot(path=screenshot_path)

    # 7. Click on the Next button
    next_button_selector = 'div[role="button"]:has-text("Next")'

    await page.wait_for_selector(next_button_selector, timeout=5000)
    next_button = await page.query_selector(next_button_selector)

    if next_button:
        await random_delay(1, 2)
        await next_button.click()
        print("✅ Next button clicked successfully. Checking next step...")

    else:
        raise Exception("❌ Next button not found or not operational.")
    await random_delay(1, 2)

    # Screenshot for verification
    timestamp = int(time.time())
    screenshot_path = f'uploads/screenshot_Next_{timestamp}.png'
    await page.screenshot(path=screenshot_path)

    