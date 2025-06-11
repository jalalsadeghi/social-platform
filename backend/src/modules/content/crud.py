# src/modules/content/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.future import select
from .models import Content, QueueStatus
from modules.platform.models import Platform
from datetime import datetime
from typing import List, Optional
from .schemas import ContentCreate, ContentBase

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

async def get_contents(db: AsyncSession, user_id: UUID, skip=0, limit=30) -> List[Content]:
    result = await db.execute(
        select(Content).where(Content.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def get_content_by_id(db: AsyncSession, content_id: UUID, user_id: UUID) -> Optional[Content]:
    result = await db.execute(
        select(Content).where(Content.id == content_id, Content.user_id == user_id)
    )
    return result.scalars().first()

async def update_content(
    db: AsyncSession, content_id: UUID, user_id: UUID, data: ContentBase
) -> Optional[Content]:
    db_content = await get_content_by_id(db, content_id, user_id)
    if not db_content:
        return None

    platforms = await db.execute(select(Platform).where(Platform.id.in_(data.platforms_id)))
    db_content.platform = platforms.scalars().all()

    for field, value in data.dict(exclude_unset=True).items():
        if field != "platforms_id":
            setattr(db_content, field, value)

    await db.commit()
    await db.refresh(db_content)
    return db_content

async def delete_content(db: AsyncSession, content_id: UUID, user_id: UUID) -> bool:
    db_content = await get_content_by_id(db, content_id, user_id)
    if not db_content:
        return False
    await db.delete(db_content)
    await db.commit()
    return True