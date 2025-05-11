import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum

class PostStatus(enum.Enum):
    queued = "queued"
    published = "published"
    failed = "failed"

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    content_text = Column(Text, nullable=True)
    content_media = Column(JSONB, nullable=True)
    scheduled_time = Column(DateTime, nullable=True)
    status = Column(Enum(PostStatus), default=PostStatus.queued)
    insights = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey('comments.id'), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    post = relationship("Post", back_populates="comments")
    replies = relationship("Comment", backref='parent', remote_side=[id])
