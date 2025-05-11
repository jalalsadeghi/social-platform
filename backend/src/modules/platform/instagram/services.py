# services.py
from modules.platform.instagram.utils import instagram_api_call
from modules.platform.instagram.schemas import InstagramWebhookPayload


async def post_media(token, content):
    data = {"caption": content.caption, "media_url": content.media_url}
    return await instagram_api_call("me/media", method="POST", token=token, data=data)

async def post_story(token, content):
    data = {"media_url": content.media_url}
    return await instagram_api_call("me/stories", method="POST", token=token, data=data)

async def reply_comment(token, reply):
    data = {"message": reply.message}
    endpoint = f"{reply.comment_id}/replies"
    return await instagram_api_call(endpoint, method="POST", token=token, data=data)

async def fetch_insights(token):
    return await instagram_api_call("me/insights", token=token)

async def perform_interaction(token, interaction):
    if interaction.type == "like":
        endpoint = f"{interaction.target_id}/likes"
        return await instagram_api_call(endpoint, method="POST", token=token)
    elif interaction.type == "comment":
        endpoint = f"{interaction.target_id}/comments"
        data = {"message": interaction.comment_text}
        return await instagram_api_call(endpoint, method="POST", token=token, data=data)
    elif interaction.type == "follow":
        endpoint = f"me/follows/{interaction.target_id}"
        return await instagram_api_call(endpoint, method="POST", token=token)
    

async def process_webhook_payload(payload: InstagramWebhookPayload):
    for entry in payload.entry:
        for change in entry.changes:
            field = change.get("field")
            value = change.get("value")

            # مدیریت انواع مختلف تغییرات اینستاگرام
            if field == "comments":
                await handle_comment_event(value)
            elif field == "mentions":
                await handle_mention_event(value)
            elif field == "story_insights":
                await handle_story_insights(value)

async def handle_comment_event(value):
    # منطق مدیریت رویداد کامنت‌ها
    print(f"New comment event received: {value}")

async def handle_mention_event(value):
    # منطق مدیریت رویداد mentions
    print(f"New mention event received: {value}")

async def handle_story_insights(value):
    # منطق مدیریت رویداد insights استوری‌ها
    print(f"New story insights event received: {value}")