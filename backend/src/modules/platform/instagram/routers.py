# routers.py
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from core.database import 
from modules.platform.instagram import schemas, services, crud
from modules.platform.instagram.models import InstagramIntegration
from modules.auth.jwt import verify_token
import hmac
import hashlib
import os

router = APIRouter(prefix="/instagram", tags=["instagram"])

VERIFY_TOKEN = os.getenv("INSTAGRAM_VERIFY_TOKEN")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_integration(user_id, db):
    integration = db.query(InstagramIntegration).filter_by(user_id=user_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration

@router.post("/post")
async def create_post(content: schemas.PostContent, user=Depends(verify_token), db: Session = Depends(get_db)):
    integration = get_integration(user['sub'], db)
    result = await services.post_media(integration.access_token, content)
    crud.log_action(db, integration.id, "post", result, "success")
    return result

@router.post("/story")
async def create_story(content: schemas.StoryContent, user=Depends(verify_token), db: Session = Depends(get_db)):
    integration = get_integration(user['sub'], db)
    result = await services.post_story(integration.access_token, content)
    crud.log_action(db, integration.id, "story", result, "success")
    return result

@router.post("/comments/reply")
async def auto_reply(reply: schemas.CommentReply, user=Depends(verify_token), db: Session = Depends(get_db)):
    integration = get_integration(user['sub'], db)
    result = await services.reply_comment(integration.access_token, reply)
    crud.log_action(db, integration.id, "comment_reply", result, "success")
    return result

@router.get("/insights", response_model=schemas.InsightsData)
async def get_insights(user=Depends(verify_token), db: Session = Depends(get_db)):
    integration = get_integration(user['sub'], db)
    insights = await services.fetch_insights(integration.access_token)
    return insights

@router.post("/interact")
async def interact(interaction: schemas.Interaction, user=Depends(verify_token), db: Session = Depends(get_db)):
    integration = get_integration(user['sub'], db)
    result = await services.perform_interaction(integration.access_token, interaction)
    crud.log_action(db, integration.id, interaction.type, result, "success")
    return result


@router.get("/webhook")
async def verify_webhook(hub_mode: str, hub_challenge: str, hub_verify_token: str):
    if hub_verify_token != VERIFY_TOKEN:
        raise HTTPException(status_code=403, detail="Verification token mismatch")
    return int(hub_challenge)

@router.post("/webhook")
async def receive_webhook(
    payload: schemas.InstagramWebhookPayload,
    x_hub_signature: str = Header(None),
    request: Request = None
):
    body = await request.body()
    app_secret = os.getenv("INSTAGRAM_APP_SECRET")

    # بررسی امنیتی signature
    expected_signature = 'sha1=' + hmac.new(
        app_secret.encode('utf-8'), body, hashlib.sha1
    ).hexdigest()

    if not hmac.compare_digest(x_hub_signature, expected_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    await services.process_webhook_payload(payload)
    return {"status": "success"}



@router.get("/data-deletion", response_class=HTMLResponse)
async def data_deletion():
    return """
    <html>
        <head>
            <title>Data Deletion Instructions</title>
        </head>
        <body>
            <h1>Data Deletion Instructions</h1>
            <p>To request deletion of your data, please contact us at:
            <a href="mailto:your-email@example.com">your-email@example.com</a></p>
            <p>Include your account details, and we will remove your data promptly.</p>
        </body>
    </html>
    """
