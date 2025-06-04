import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.sql import func
import enum

class InstagramActionType(enum.Enum):
    post = "post"
    story = "story"
    comment_reply = "comment_reply"
    like = "like"
    follow = "follow"

class ActionStatus(enum.Enum):
    success = "success"
    failed = "failed"

class InstagramIntegration(Base):
    __tablename__ = 'instagram_integrations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    access_token = Column(String, nullable=False)
    instagram_user_id = Column(String, nullable=False)
    username = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
    connected_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    action_logs = relationship("InstagramActionLog", back_populates="integration")

class InstagramActionLog(Base):
    __tablename__ = 'instagram_action_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instagram_integration_id = Column(UUID(as_uuid=True), ForeignKey('instagram_integrations.id'), nullable=False)
    action_type = Column(Enum(InstagramActionType), nullable=False)
    action_status = Column(Enum(ActionStatus), nullable=False)
    details = Column(JSONB, default=dict)
    timestamp = Column(DateTime, default=func.now())

    integration = relationship("InstagramIntegration", back_populates="action_logs")

