import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from core.database import Base
from sqlalchemy.sql import func
import enum

class ReportType(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class PerformanceReport(Base):
    __tablename__ = 'performance_reports'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    content = Column(JSONB, default=dict)
    generated_at = Column(DateTime, default=func.now())
