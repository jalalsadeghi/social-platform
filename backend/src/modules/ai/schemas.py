# backend/src/modules/ai/schemas.py
from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime
from .models import Language, PromptType, PromptSample
from uuid import UUID

class PromptBase(BaseModel):
    prompt_name: str
    language: Language 
    prompt_content: str = PromptSample
    expertise: str
    promt_type: PromptType 
    
class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    prompt_name: Optional[str] = None
    language: Optional[Language] = None 
    prompt_content: Optional[str] = None
    expertise: Optional[str] = None
    promt_type: Optional[PromptType] = None 
    
class PromptOut(PromptBase):
    id: UUID4
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LanguageBase(BaseModel):
    name: str
    value: str

class PromptSampleBase(BaseModel):
    name: str
    value: str