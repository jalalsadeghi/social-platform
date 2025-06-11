# src/modules/conent/models.py
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from sqlalchemy import Table
import enum

class QueueStatus(enum.Enum):
    pending = "pending..."
    processing = "processing..."
    ready = "ready"
    posting= "posting..."
    posted = "posted"
    failed = "failed"

content_platforms = Table(
    "content_platform",
    Base.metadata,
    Column("content_id", UUID(as_uuid=True), ForeignKey("contents.id", ondelete="CASCADE"), primary_key=True),
    Column("platform_id", UUID(as_uuid=True), ForeignKey("platforms.id", ondelete="CASCADE"), primary_key=True)
)

class Content(Base):
    __tablename__ = 'contents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content_url = Column(String, nullable=True)
    ai_title = Column(String, nullable=False)
    ai_caption = Column(Text, nullable=True)
    ai_content = Column(Text, nullable=True)
    video_filename = Column(String, nullable=False)
    thumb_filename = Column(String, nullable=True)
    remove_audio = Column(Boolean, default=False)
    music_id = Column(UUID(as_uuid=True), ForeignKey('music_files.id'), nullable=True)
    status = Column(Enum(QueueStatus), default=QueueStatus.pending, index=True)
    priority = Column(Integer, default=0)
    scheduled_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    platform = relationship("Platform", secondary=content_platforms, lazy="selectin")
    user = relationship("User", backref="contents", lazy="selectin")
    music = relationship("MusicFile", backref="contents", lazy="selectin")

class MusicFile(Base):
    __tablename__ = 'music_files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="music_files", lazy="selectin")
