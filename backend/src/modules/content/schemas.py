# src/modules/content/schemas.py
from pydantic import BaseModel, UUID4, HttpUrl
from typing import List, Optional
from .models import QueueStatus
from uuid import UUID
from datetime import datetime

class ContentScraper(BaseModel):
    url: str
    prompt_id: str 
    tip: str

class ContentScrapedOut(BaseModel):
    ai_title: str
    ai_caption: str
    ai_content: str
    video_filename: str
    thumb_filename: str

class ContentBase(BaseModel):
    ai_title: str
    ai_caption: str
    ai_content: str
    platforms_id: List[UUID]
    content_url: str
    video_filename: str
    thumb_filename: str
    remove_audio: Optional[bool] = False
    music_id: Optional[UUID] = None

class ContentCreate(ContentBase):
    pass

class ContentGenerate(BaseModel):
    ai_caption: str
    video_filename: str 
    random_name: str

class ContentOut(ContentBase):
    id: UUID
    user_id: UUID
    platforms_id: List[UUID]
    status: QueueStatus
    priority: int
    scheduled_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MusicFileOut(BaseModel):
    id: UUID
    filename: str
    original_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ProgressResponse(BaseModel):
    progress: str

