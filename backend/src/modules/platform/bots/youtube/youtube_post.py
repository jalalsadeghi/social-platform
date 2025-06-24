# backend/src/modules/platform/bot/youtube/youtube_post.py
from ..utils.common import random_delay, safe_click, screenshot, safe_evaluate
from sqlalchemy.ext.asyncio import AsyncSession
from modules.content.crud import get_content_by_id
from playwright.async_api import async_playwright
import random
import time

async def post_to_youtube(db, user_id, page, content_id, platform_name):
    print(f"Platform name: {platform_name}")
    content = await get_content_by_id(db, content_id, user_id)

    thumbnail_file = content.thumb_filename
    media = content.video_filename
    title = content.ai_title
    ai_content = content.ai_content

    steps = [
        ('button[aria-label="Create"]', "Create"),
        ('yt-formatted-string:has-text("Upload video")', "Upload_Video"),
        ('div.dialog-content div#title:has-text("Upload videos")', "Upload_Dialog_Opened"),
        ('ytcp-button#select-files-button button', "Select_Files"),
        ('ytcp-social-suggestions-textbox#title-textarea div#textbox[contenteditable="true"]', "Title_Box"),
        ('div#description-textarea div#textbox[contenteditable="true"]', "Description_Box"),
        ('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]', "Select_Not_Made_For_Kids"),
        ('ytcp-button#next-button button', "Next_Button"),
    ]
    
    for index, (selector, name) in enumerate(steps, start=201):

        if name == "Upload_Dialog_Opened":
            try:
                await page.wait_for_selector(selector, state='visible', timeout=30000)
                print(f"✅ Upload Dialog is visible. {index}_{name}")
            except:
                print("❌ Upload Dialog did not appear within timeout. Exiting safely.")
                await screenshot(page, name, "error")
                return False
        elif name == "Title_Box":
            safe_evaluate(page, selector, title, f"{index}_{name}")
        
        elif name == "Description_Box":
            safe_evaluate(page, selector, ai_content, f"{index}_{name}")

        else:
            clicked = await safe_click(page, selector, f"{index}_{name}")
            if not clicked:
                print(f"❌ Could not complete step: {name}. Exiting safely.")
                return False
            
            if name == "Select_Files":
                file_input_selector = 'input[type="file"][name="Filedata"]'
                try:
                    await page.set_input_files(file_input_selector, media)
                    
                    # After successfully uploading media, wait for the Details box to appear
                    details_selector = 'ytcp-video-metadata-editor-basics h1:has-text("Details")'
                    try:
                        await page.wait_for_selector(details_selector, state='visible', timeout=30000)
                        print(f"✅ Media files uploaded successfully. {index}_{name}")
                    except:
                        print("❌ Details box did not appear within timeout.")
                        await screenshot(page, "details_box", "error")
                        return False
                    
                except Exception as e:
                    print(f"❌ Failed to upload media files: {e}")
                    await screenshot(page, "upload_media", "error")
                    return False
                
        
    #     if name == "Select_Video" or name == "Select_thumbnail":
    #         # Upload media files
    #         file_input_selector = 'input[type="file"]._ac69'
    #         try:
    #             await page.set_input_files(file_input_selector, media)
    #             media = thumbnail_file  # سری اول ویدئو را آپلود میکند و سری دو تامب نیل را
    #             print("✅ Media files uploaded successfully.")
                
    #         except Exception as e:
    #             print(f"❌ Failed to upload media files: {e}")
    #             await screenshot(page, "upload_media", "error")
    #             return
        
    #     if name == "Content_Box":
    #         ai_content = content.ai_content

    #         # کپی کردن ai_content در کلیپ‌بورد مرورگر
    #         await page.evaluate(f'''
    #             navigator.clipboard.writeText(`{ai_content}`);
    #         ''')
    #         await random_delay(0.5, 1)

    #         # کلیک کردن در کادر محتوا برای قرار دادن نشانگر ماوس
    #         await page.click(selector)
    #         await random_delay(0.5, 1)

    #         # پیست کردن متن
    #         await page.keyboard.down('Control')
    #         await page.keyboard.press('V')
    #         await page.keyboard.up('Control')

    #         await random_delay(1, 2)
    #         await screenshot(page, "210_Content_Box")

    #         # انتقال فوکوس به دکمه Share با 7 بار فشردن Tab
    #         for _ in range(7):
    #             await page.keyboard.press("Tab")
    #             await random_delay(0.5, 0.7)

    #         # ارسال محتوا
    #         await page.keyboard.press("Enter")
    #         await screenshot(page, "210_Share")



    # spinner_selector = 'img[alt="Spinner placeholder"][src*="ShFi4iY4Fd9.gif"]' 

    # try:
    #     # منتظر Spinner با timeout کمتر (20 ثانیه)
    #     await page.wait_for_selector(spinner_selector, state='visible', timeout=20000)
    #     print("✅ Spinner appeared, upload in progress.")
        
    #     # انتظار تا زمانی که Spinner ناپدید شود
    #     await page.wait_for_selector(spinner_selector, state='hidden', timeout=3600000)
    #     print("🚀 Spinner disappeared, upload completed.")
    #     await random_delay(1, 3)
    #     await screenshot(page, "219_Spinner")
    # except Exception as e:
    #     print(f"⚠️ Spinner did not appear promptly: {e}")
    #     await screenshot(page, "219_Spinner", "error")

    # error_popup_selector = 'div[role="heading"]:has-text("Something went wrong")'
    # close_button_selector = "div[role='button'][tabindex='0']:has(svg[aria-label='Close'])"
    # try:
    #     # بررسی پیام خطا
    #     await page.wait_for_selector(error_popup_selector, state='visible', timeout=5000)
    #     print("⚠️ Error popup detected. Closing popup.")
        
    #     clicked = await safe_click(page, close_button_selector, "220_wrong")

    #     if not clicked:
    #         print(f"❌ Could not complete step: wrong. Exiting safely.")
    #         return
    #     return False  # بازگشت یک مقدار مشخص جهت آگاهی از وضعیت
    # except:
    #     print("✅ No error popup detected, continuing process.")
    #     await random_delay(1, 3)
    #     print("🎉 Post shared successfully.")

    #     await screenshot(page, "220_successfully")

    # await screenshot(page, "221_Final", "error")

    # await page.goto(f"https://www.youtube.com/{platform_name}/")

    # await page.wait_for_selector('a[href*="/reel/"]', timeout=30000)

    # ai_content_snippet = content.ai_content[:50]
    # elements = await page.query_selector_all('a[href*="/reel/"]')

    # for elem in elements:
    #     img = await elem.query_selector('img[alt]')
    #     if img:
    #         alt_text = await img.get_attribute('alt')
    #         if ai_content_snippet in alt_text:
    #             href = await elem.get_attribute('href')
    #             reel_id = href.split('/')[-2]
    #             print(f"✅ Found reel ID: {reel_id}")
    #             return reel_id

    # print("⚠️ Could not find the posted reel.")
    return False