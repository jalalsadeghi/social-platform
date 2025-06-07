# src/modules/product/schemas.py
from pydantic import BaseModel, UUID4, HttpUrl
from typing import List, Optional
from datetime import datetime
from enum import Enum
from .models import QueueStatus
from uuid import UUID

class MediaType(str, Enum):
    image = "image"
    video = "video"

class MediaBase(BaseModel):
    media_url: str #HttpUrl
    media_type: MediaType
    local_path: Optional[str]

class MediaCreate(MediaBase):
    pass

class MediaOut(MediaBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class InstagramStatsOut(BaseModel):
    views: int
    likes: int
    comments: int
    last_checked_at: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    product_url: Optional[HttpUrl]
    title: str
    description: Optional[str]
    ai_content: Optional[str]

class ProductCreate(ProductBase):
    media: List[MediaCreate] = []
    social_account_ids: List[UUID] = []

class ProductUpdate(ProductBase):
    media: Optional[List[MediaCreate]] = []
    social_account_ids: Optional[List[UUID]] = []
    status: Optional[QueueStatus] = None
    priority: Optional[int] = None
    scheduled_time: Optional[datetime] = None

class ProductOut(ProductBase):
    id: UUID4
    status: QueueStatus
    priority: int
    scheduled_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    media: List[MediaOut]
    instagram_stats: Optional[InstagramStatsOut] = None
    social_account_ids: List[UUID4] = []

class Config:
    from_attributes = True


