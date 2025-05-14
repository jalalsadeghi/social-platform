# src/modules/product/schemas.py
from pydantic import BaseModel, UUID4, HttpUrl
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MediaType(str, Enum):
    image = "image"
    video = "video"

class MediaBase(BaseModel):
    media_url: HttpUrl
    media_type: MediaType

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

class ProductUpdate(ProductBase):
    media: Optional[List[MediaCreate]] = []

class ProductOut(ProductBase):
    id: UUID4
    status: str
    priority: int
    scheduled_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    media: List[MediaOut]
    instagram_stats: Optional[InstagramStatsOut] = None

class Config:
    from_attributes = True


