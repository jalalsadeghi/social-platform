import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, JSON, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.sql import func
import enum

class PromptType(enum.Enum):
    content_generation = "content_generation"
    comment_response = "comment_response"

class AIPrompt(Base):
    __tablename__ = 'ai_prompts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_name = Column(String, unique=True, nullable=False)
    prompt_content = Column(Text, nullable=False)
    prompt_type = Column(Enum(PromptType), nullable=False)
    settings = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    contents = relationship("AIContent", back_populates="prompt")

class AIContent(Base):
    __tablename__ = 'ai_contents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_queue_id = Column(UUID(as_uuid=True), ForeignKey('product_queues.id'), nullable=False)
    prompt_id = Column(UUID(as_uuid=True), ForeignKey('ai_prompts.id'), nullable=False)
    content_text = Column(Text, nullable=False)
    evaluation_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    prompt = relationship("AIPrompt", back_populates="contents")

