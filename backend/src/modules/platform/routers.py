# backend/src/modules/platform/routers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from typing import List
from core.database import get_db
from modules.platform import schemas, crud
from core.dependencies import get_current_user
from uuid import UUID

router = APIRouter(prefix="/platforms", tags=["platforms"])

@router.post("/")
async def create_platform(
    credentials: schemas.PlatformBase,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await crud.create_platform(
            db=db,
            user_id=current_user.id,
            platform=credentials.platform,
            identifier=credentials.username,
            credentials={"username": credentials.username, "password": credentials.password},
            cookies=credentials.cookies,
            is_oauth=False
        )
        return {"message": "Credentials stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.get("/", response_model=List[schemas.PlatformOut])
async def get_platforms(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0, 
    limit: int = 100,
):
    return await crud.get_platforms(db=db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{platform_id}", response_model=schemas.PlatformOut)
async def read_platform(
    platform_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    platform = await crud.get_platform(db, platform_id, user_id=current_user.id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform


@router.put("/{platform_id}", response_model=schemas.PlatformOut)
async def update_platform(
    platform_id: UUID, 
    platform: schemas.PlatformUpdate, 
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated_platform = await crud.update_platforms(db, platform_id, current_user.id, platform)
    if not updated_platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return updated_platform


@router.delete("/{platform_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_platform(
    platform_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_platform(db, platform_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Platform not found or Unauthorized")
    return {"detail": "Platform deleted successfully"}