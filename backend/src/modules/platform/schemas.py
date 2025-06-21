# modules/platform/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict
from .models import SocialPlatform, Language
from uuid import UUID

class PlatformBase(BaseModel):
    username: str
    password: str
    platform: SocialPlatform
    language: Language
    posts_per_day: int
    cookies: Optional[str]

class PlatformCreate(PlatformBase):
    pass

class PlatformUpdate(BaseModel):
    password: Optional[str] = None
    platform: Optional[SocialPlatform] = None
    language: Optional[Language] = None
    posts_per_day: Optional[int] = None
    cookies: Optional[str] = None
    schedule: Optional[Dict[str, Dict[str, str]]] = None

class PlatformOut(BaseModel):
    id: UUID
    user_id: UUID
    platform: SocialPlatform
    username: str
    language: Language
    posts_per_day: int
    schedule: Dict[str, Dict[str, str]] 
    cookies: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
