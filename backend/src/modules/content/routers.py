# src/modules/conent/routers.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from . import crud, schemas
from .scraper.scraper import scrape_and_extract
from core.database import get_db
from core.dependencies import get_current_user

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

        result.platforms_id = [p.id for p in result.platform]

        return result
    except Exception as e:
        print(f"Scraping error: {e}")
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
        content.platforms_id = [p.id for p in content.platform]
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
    content.platforms_id = [p.id for p in content.platform]
    return content


@router.put("/{content_id}", response_model=schemas.ContentOut)
async def update_content(
    content_id: UUID,
    content: schemas.ContentBase,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated_content = await crud.update_content(db, content_id, current_user.id, content)
    if not updated_content:
        raise HTTPException(status_code=404, detail="Content not found")
    updated_content.platforms_id = [p.id for p in updated_content.platform]
    return updated_content


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