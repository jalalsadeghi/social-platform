from pydantic import BaseModel, UUID4, HttpUrl
from typing import Optional, Dict
from datetime import datetime
from .models import QueueStatus

class ProductQueueBase(BaseModel):
    product_url: HttpUrl
    priority: Optional[int] = 0
    scheduled_time: Optional[datetime] = None

class ProductQueueCreate(ProductQueueBase):
    pass

class ProductQueueUpdate(BaseModel):
    status: Optional[QueueStatus] = None
    scraped_data: Optional[Dict] = None
    ai_generated_content: Optional[Dict] = None
    priority: Optional[int] = None
    scheduled_time: Optional[datetime] = None

class ProductQueueOut(ProductQueueBase):
    id: UUID4
    user_id: UUID4
    scraped_data: Dict
    ai_generated_content: Dict
    status: QueueStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
