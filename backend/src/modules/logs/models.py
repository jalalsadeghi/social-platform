import uuid
from sqlalchemy import Column, String, DateTime, Enum, JSON, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from core.database import Base
from sqlalchemy.sql import func
import enum

class LogLevel(enum.Enum):
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"

class AppLog(Base):
    __tablename__ = 'app_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    log_level = Column(Enum(LogLevel), nullable=False)
    component = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    additional_info = Column(JSONB, default=dict)
    timestamp = Column(DateTime, default=func.now())
