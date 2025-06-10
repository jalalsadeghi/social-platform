# src/modules/content/crud.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.future import select
from .schemas import ContentCreate
from .models import Content, QueueStatus
from modules.platform.models import Platform
from datetime import datetime

async def create_content(db: AsyncSession, content: ContentCreate, user_id: UUID):
    platforms = await db.execute(select(Platform).where(Platform.id.in_(content.platforms_id)))
    platforms = platforms.scalars().all()

    db_content = Content(
        user_id=user_id,
        ai_title=content.ai_title,
        ai_caption=content.ai_caption,
        ai_content=content.ai_content,
        content_url=content.content_url,
        video_filename=content.video_filename,
        thumb_filename=content.thumb_filename,
        status=QueueStatus.pending,
        scheduled_time=datetime.utcnow(),
        platform=platforms
    )

    db.add(db_content)
    await db.commit()
    await db.refresh(db_content)

    return db_content