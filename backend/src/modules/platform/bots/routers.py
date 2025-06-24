# src/modules/platform/bot/routers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.dependencies import get_current_user
from .utils.secure_credentials import (
    store_social_credentials,
    get_social_credentials
)
from .instagram.instagram_client import login_instagram
from pydantic import BaseModel
from uuid import UUID
from typing import List
from typing import Optional

router = APIRouter(prefix="/instagram-bot", tags=["Instagram Bot"])

class PlatformCredential(BaseModel):
    username: str
    password: str
    platform:str
    lang:str

@router.post("/store-credentials")
async def store_credentials(
    credentials: PlatformCredential,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await store_social_credentials(
            db=db,
            user_id=current_user.id,
            platform=credentials.platform,
            lang=credentials.lang,
            identifier=credentials.username,
            credentials={"username": credentials.username, "password": credentials.password},
            is_oauth=False
        )
        return {"message": "Credentials stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-credentials/", response_model=List[PlatformCredential])
async def list_users(
    user_id: Optional[str] = "",
    db: AsyncSession = Depends(get_db),
    skip: int = 0, 
    limit: int = 100,
    ):
    return await get_social_credentials(db=db, skip=skip, limit=limit, user_id=user_id)

# @router.get("/get-credentials/{user_id}", response_model=List[PlatformCredential])
# async def list_users(
#     db: AsyncSession = Depends(get_db),
#     skip: int = 0, limit: int = 100, 
#     user_id=str
#     ):
#     return await get_social_credentials(db=db, skip=skip, limit=limit) 

# @router.get("/get-credentials/{user_id}")
# async def retrieve_credentials(
#     user_id: UUID,
#     db: AsyncSession = Depends(get_db),
# ):
#     try:
#         creds = await get_social_credentials(db=db, user_id=user_id, platform="instagram")
#         return {"credentials": creds}
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))


@router.post("/test-login")
async def test_instagram_login(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        creds = await get_social_credentials(db=db, user_id=current_user.id, platform="instagram")
        result = await login_instagram(username=creds["username"], password=creds["password"])

        if result["success"]:
            return {"message": "Login successful", "cookies": result["cookies"]}
        else:
            raise HTTPException(status_code=400, detail=f"Login failed: {result['error']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
