# backend/src/modules/ai/schemas.py
from pydantic import BaseModel, UUID4
from typing import Optional, Dict
from datetime import datetime
from .models import PromptType

class PromptBase(BaseModel):
    prompt_name: str
    prompt_content: str
    prompt_type: PromptType
    settings: Optional[Dict] = {}

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    prompt_name: Optional[str] = None
    prompt_content: Optional[str] = None
    prompt_type: Optional[PromptType] = None
    settings: Optional[Dict] = None

class PromptOut(PromptBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
