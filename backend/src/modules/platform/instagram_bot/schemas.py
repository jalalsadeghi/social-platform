# backend/src/modules/platform/instagram_bot/schemas.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Dict, Any

class InstagramBotReportCreate(BaseModel):
    user_id: UUID
    report_data: Dict[str, Any]

class InstagramBotReportRead(InstagramBotReportCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
