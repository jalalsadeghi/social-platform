# backend/src/modules/plan/schemas.py
from pydantic import BaseModel, UUID4
from typing import Optional, Dict
from datetime import datetime
from enum import Enum

class SubscriptionStatus(str, Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"

class PlanBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    features: Dict[str, str]
    is_active: bool = True

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    features: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None

class PlanOut(PlanBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SubscriptionBase(BaseModel):
    user_id: UUID4
    plan_id: UUID4
    start_date: Optional[datetime] = None
    end_date: datetime
    status: SubscriptionStatus = SubscriptionStatus.active

class SubscriptionCreate(SubscriptionBase):
    payment_id: Optional[UUID4] = None

class SubscriptionOut(SubscriptionBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True
