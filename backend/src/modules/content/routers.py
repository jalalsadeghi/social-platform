# src/modules/conent/routers.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, UploadFile, File
from fastapi.responses import StreamingResponse
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID, uuid4
from . import crud, schemas
from .models import MusicFile
from .scraper.scraper import scrape_and_extract
from core.database import get_db
from core.dependencies import get_current_user
import shutil
import os
from core.config import settings
import redis
import logging

logger = logging.getLogger(__name__)


redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

router = APIRouter(prefix="/contents", tags=["contents"])

@router.post("/scrape/", response_model=schemas.ContentScrapedOut)
async def scrape_content(
    content_scraper: schemas.ContentScraper,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    base_url = str(request.base_url).rstrip('/')
    try:
        result = await scrape_and_extract(
            db,
            content_scraper.url, 
            content_scraper.prompt_id,
            content_scraper.tip,
            current_user.id,
            base_url
        )
        return result
    except Exception as e:
        print(f"Scraping error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/", response_model=schemas.ContentOut)
async def create_content(
    content: schemas.ContentCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await crud.create_content(
            db=db,
            content=content,
            user_id=current_user.id,
        )

        result.user_name = current_user.username

        result.platforms_status = [
            {"platform_id": cp.platform_id, 
             "platform_name": cp.platform.platform.value,
             "account_identifier": cp.platform.account_identifier,
             "status": cp.status, 
             "priority": cp.priority,
             "url": ""
            }
            for cp in result.content_platforms
        ]

        return result
    except Exception as e:
        logger.error(f"Error creating content: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    
@router.get("/", response_model=List[schemas.ContentOut])
async def read_contents(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 30
):
    contents = await crud.get_contents(db, current_user.id, skip, limit)
    for content in contents:
        content.platforms_status = [
            {
                "platform_id": cp.platform_id,
                "platform_name": cp.platform.platform.value if cp.platform else None,
                "account_identifier": cp.platform.account_identifier if cp.platform else None,
                "status": cp.status,
                "priority": cp.priority
            }
            for cp in content.content_platforms
        ]
        content.user_name = content.user.username if content.user else None
    return contents


@router.get("/{content_id}", response_model=schemas.ContentOut)
async def read_content(
    content_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    content = await crud.get_content_by_id(db, content_id, current_user.id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content.platforms_status = [
        {
            "platform_id": cp.platform_id,
            "platform_name": cp.platform.platform.value if cp.platform else None,
            "account_identifier": cp.platform.account_identifier if cp.platform else None,
            "status": cp.status,
            "priority": cp.priority
        }
        for cp in content.content_platforms
    ]

    content.user_name = content.user.username if content.user else None

    return content


@router.put("/{content_id}", response_model=schemas.ContentOut)
async def update_content(
    content_id: UUID,
    content: schemas.ContentUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    # updated_content = await crud.update_content(db, content_id, current_user.id, content)
    # if not updated_content:
    #     raise HTTPException(status_code=404, detail="Content not found")
    
    # updated_content.platforms_status = [
    #     {
    #         "platform_id": cp.platform_id,
    #         "platform_name": cp.platform.platform.value if cp.platform else None,
    #         "account_identifier": cp.platform.account_identifier if cp.platform else None,
    #         "status": cp.status,
    #         "priority": cp.priority
    #     }
    #     for cp in updated_content.content_platforms
    # ]

    # updated_content.user_name = updated_content.user.username if updated_content.user else None

    # return updated_content
    content = await crud.get_content_by_id(db, content_id, current_user.id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content.platforms_status = [
        {
            "platform_id": cp.platform_id,
            "platform_name": cp.platform.platform.value if cp.platform else None,
            "account_identifier": cp.platform.account_identifier if cp.platform else None,
            "status": cp.status,
            "priority": cp.priority
        }
        for cp in content.content_platforms
    ]

    content.user_name = content.user.username if content.user else None

    return content

@router.delete("/{content_id}", response_model=dict)
async def delete_content(
    content_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_content(db, content_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"detail": "Content deleted successfully"}


@router.get("/platform/filtered", response_model=List[schemas.ContentOut])
async def get_filtered_contents(
    platform_name: Optional[str] = None,
    platform_username: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 30,
):
    contents = await crud.get_filtered_contents(
        db,
        user_id=current_user.id,
        platform_name=platform_name,
        platform_username=platform_username,
        skip=skip,
        limit=limit
    )

    for content in contents:
        content.platforms_status = [
            {"platform_id": cp.platform_id, "status": cp.status, "priority": cp.priority}
            for cp in content.content_platforms
        ]

    return contents

@router.get("/platform/{platform_id}/contents", response_model=List[schemas.PlatformContentOut])
async def get_platform_contents(
    platform_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 30
):
    contents = await crud.get_contents_by_platform_id(db, platform_id, skip, limit)
    return contents


@router.delete("/content_platform/{content_platforms_id}", response_model=dict)
async def delete_platform_content(
    content_platforms_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    success = await crud.delete_content_platform(db, content_platforms_id)
    if not success:
        raise HTTPException(status_code=404, detail="ContentPlatform record not found")
    return {"detail": "ContentPlatform deleted successfully"}


@router.post("/upload-music/")
async def upload_music(
    music_file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        file_ext = os.path.splitext(music_file.filename)[1]
        filename = f"{uuid4()}{file_ext}"
        save_path = os.path.join("uploads/music", filename)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(music_file.file, buffer)

        music_record = MusicFile(
            user_id=current_user.id,
            filename=save_path,
            original_name=music_file.filename
        )
        db.add(music_record)
        await db.commit()
        await db.refresh(music_record)

        return {"music_id": music_record.id, "filename": music_record.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/music/", response_model=List[schemas.MusicFileOut])
async def get_music_files(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 30
):
    music_files = await crud.get_user_music_files(db, current_user.id, skip, limit)
    return music_files

@router.delete("/music/{music_id}", response_model=dict)
async def delete_music(
    music_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_music_file(db, music_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Music file not found")
    return {"detail": "Music file deleted successfully"}


@router.get("/status/progress")
async def get_current_video_progress():
    progress = redis_client.get("current_video_progress")

    if progress is None:
        return {"progress": "No task running"}

    progress = progress.decode().strip()

    try:
        return {"progress": int(progress)}
    except ValueError:
        if progress in ["no_pending", "failed", "ready"]:
            return {"progress": progress}

        logger.error(f"Unexpected progress value from Redis: '{progress}'")
        return {"progress": "unknown", "detail": f"Unexpected value '{progress}'"}
    

@router.put("/priority/update", response_model=dict)
async def update_content_priorities(
    priorities: schemas.UpdatePriorities,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await crud.update_priorities(db, priorities.priorities)
        return {"detail": "Priorities updated successfully"}
    except Exception as e:
        logger.error(f"Error updating priorities: {e}")
        raise HTTPException(status_code=400, detail=str(e))