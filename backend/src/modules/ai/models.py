# src/modules/ai/models.py
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.sql import func
from .prompts import ai_prompt_english
import enum

class Language(enum.Enum):
    English = "English"
    German = "German"
    Persian = "Persian"

class PromptType(enum.Enum):
    caption_prompt = "caption_prompt"
    comment_prompt = "comment_prompt"

class AIPrompt(Base):
    __tablename__ = 'ai_prompts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    prompt_name = Column(String, unique=True, nullable=False)
    prompt_content = Column(Text, default=ai_prompt_english ,nullable=False)
    language = Column(Enum(Language), default=Language.English, index=True)
    expertise = Column(String, unique=True, nullable=False)
    promt_type = Column(Enum(PromptType), default=PromptType.caption_prompt, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="ai_prompts", lazy="joined")
    social_accounts = relationship("SocialAccount", back_populates="ai_prompts", lazy="selectin")
