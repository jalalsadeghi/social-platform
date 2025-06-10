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

@router.post("/scrape/", response_model=schemas.ContentScraper)
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