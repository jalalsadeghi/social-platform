# src/modules/platform/instagram_bot/routers.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from .services.secure_credentials import (
    store_social_credentials,
    get_social_credentials
)
from .services.instagram_client import login_instagram
from modules.auth.utils import verify_access_token

router = APIRouter(prefix="/instagram-bot", tags=["Instagram Bot"])

# مدل pydantic برای ذخیره کردن credential
from pydantic import BaseModel

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_id = verify_access_token(token.replace("Bearer ", ""))
    return user_id

class InstagramCredential(BaseModel):
    username: str
    password: str

@router.post("/store-credentials")
async def store_credentials(
    credentials: InstagramCredential,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user(request)
    try:
        await store_social_credentials(
            db=db,
            user_id=user_id,
            platform="instagram",
            identifier=credentials.username,
            credentials={"username": credentials.username, "password": credentials.password},
            is_oauth=False
        )
        return {"message": "Credentials stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-credentials")
async def retrieve_credentials(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user(request)
    try:
        creds = await get_social_credentials(db=db, user_id=user_id, platform="instagram")
        return {"credentials": creds}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/test-login")
async def test_instagram_login(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user(request)
    try:
        creds = await get_social_credentials(db=db, user_id=user_id, platform="instagram")
        result = await login_instagram(username=creds["username"], password=creds["password"])
        
        if result["success"]:
            return {"message": "Login successful", "cookies": result["cookies"]}
        else:
            raise HTTPException(status_code=400, detail=f"Login failed: {result['error']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
