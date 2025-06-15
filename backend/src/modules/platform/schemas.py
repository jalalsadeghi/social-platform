# backend/src/modules/platform/schemas.py
from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime
from typing import Optional
from .models import SocialPlatform
from uuid import UUID

class PlatformBase(BaseModel):
    username: str
    password: str
    platform: SocialPlatform
    cookies: Optional[str]

class PlatformCreate(PlatformBase):
    pass

class PlatformUpdate(BaseModel):
    password: Optional[str] = None
    platform: Optional[SocialPlatform] = None
    cookies: Optional[str] = None

class PlatformOut(BaseModel):
    id: UUID
    user_id: UUID
    platform: SocialPlatform
    username: str
    password: str
    cookies: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True