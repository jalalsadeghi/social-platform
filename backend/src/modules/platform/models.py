# backend/src/modules/platform/models.py
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from core.database import Base
from uuid import uuid4
import enum

class SocialPlatform(enum.Enum):
    instagram = "instagram"
    youtube = "youtube"
    tiktok = "tiktok"

class Platform(Base):
    __tablename__ = 'platforms'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    platform = Column(Enum(SocialPlatform), default=SocialPlatform.instagram, index=True)
    account_identifier = Column(String, nullable=False)  # Chanel ID
    credentials = Column(JSONB, nullable=True)
    cookies = Column(JSONB, nullable=True)
    is_oauth = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="platform", lazy="joined")