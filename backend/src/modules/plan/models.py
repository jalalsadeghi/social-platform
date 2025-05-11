# backend/src/modules/plan/models.py
import uuid
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum

class SubscriptionStatus(enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"

class Plan(Base):
    __tablename__ = 'plans'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=True)
    features = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="plan", lazy="selectin")
    subscriptions = relationship("Subscription", back_populates="plan", lazy="selectin")

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('plans.id'), nullable=False, index=True)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.active, index=True)
    payment_id = Column(UUID(as_uuid=True), nullable=True)  # در آینده با جدول پرداخت مرتبط شود

    plan = relationship("Plan", back_populates="subscriptions", lazy="joined")
    user = relationship("User", back_populates="subscriptions", lazy="joined")
