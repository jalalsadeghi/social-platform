# modules/platform/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from .models import SocialPlatform, Language
from uuid import UUID

class PlatformBase(BaseModel):
    username: str
    password: str
    platform: SocialPlatform
    language: Language
    posts_per_day: int
    cookies: Optional[List[Dict[str, Any]]]

class PlatformCreate(PlatformBase):
    pass

class PlatformUpdate(BaseModel):
    password: Optional[str] = None
    platform: Optional[SocialPlatform] = None
    language: Optional[Language] = None
    posts_per_day: Optional[int] = None
    cookies: Optional[List[Dict[str, Any]]] = None
    schedule: Optional[Dict[str, Dict[str, str]]] = None

class PlatformOut(BaseModel):
    id: UUID
    user_id: UUID
    platform: SocialPlatform
    username: str
    language: Language
    posts_per_day: int
    schedule: Dict[str, Dict[str, str]] 
    cookies: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
