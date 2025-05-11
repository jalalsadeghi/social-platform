# schemas.py
from pydantic import BaseModel, UUID4, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class PostContent(BaseModel):
    caption: Optional[str]
    media_url: HttpUrl

class StoryContent(BaseModel):
    media_url: HttpUrl

class CommentReply(BaseModel):
    comment_id: str
    message: str

class InsightsData(BaseModel):
    followers_count: int
    impressions: int
    reach: int

class Interaction(BaseModel):
    target_id: str
    type: str  # like, comment, follow
    comment_text: Optional[str] = None

class InstagramWebhookEntry(BaseModel):
    id: str
    time: int
    changes: List[Dict[str, Any]]

class InstagramWebhookPayload(BaseModel):
    object: str
    entry: List[InstagramWebhookEntry]