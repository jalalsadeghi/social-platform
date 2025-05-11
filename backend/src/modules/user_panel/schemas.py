# schemas.py
from pydantic import BaseModel, UUID4, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime

class DashboardReport(BaseModel):
    posts_count: int
    comments_count: int
    queue_products_count: int

class UserProfileUpdate(BaseModel):
    full_name: Optional[str]
    profile_picture: Optional[HttpUrl]

class ProductQueueOut(BaseModel):
    id: UUID4
    product_url: HttpUrl
    status: str
    priority: int
    scheduled_time: Optional[datetime]

class ScrapedData(BaseModel):
    title: str
    description: str
    images: List[HttpUrl]

class AIGeneratedContent(BaseModel):
    content_text: str

class PostArchiveOut(BaseModel):
    id: UUID4
    content_text: str
    status: str
    insights: Dict

class CommentOut(BaseModel):
    id: UUID4
    content: str
    created_at: datetime

class CommentReply(BaseModel):
    content: str

class PaymentRequest(BaseModel):
    plan_id: UUID4
    payment_method: str

class PaymentResponse(BaseModel):
    payment_url: HttpUrl
    status: str