import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum

class QueueStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    posted = "posted"
    failed = "failed"

class ProductQueue(Base):
    __tablename__ = 'product_queues'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    product_url = Column(String, nullable=False)
    scraped_data = Column(JSONB, default=dict)
    ai_generated_content = Column(JSONB, default=dict)
    status = Column(Enum(QueueStatus), default=QueueStatus.pending)
    priority = Column(Integer, default=0)
    scheduled_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
