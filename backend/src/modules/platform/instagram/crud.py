# crud.py
from sqlalchemy.orm import Session
from modules.platform.instagram.models import InstagramIntegration, InstagramActionLog
import uuid, enum

class ActionType(enum.Enum):
    post = "post"
    story = "story"
    comment_reply = "comment_reply"
    like = "like"
    follow = "follow"

def log_action(db: Session, integration_id, action_type: ActionType, details: dict, status: str):
    log_entry = InstagramActionLog(
        id=uuid.uuid4(),
        instagram_integration_id=integration_id,
        action_type=action_type,
        action_status=status,
        details=details
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry