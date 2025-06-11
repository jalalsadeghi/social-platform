# src/modules/content/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.future import select
from .models import Content, QueueStatus, MusicFile
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
        remove_audio=content.remove_audio,
        music_id=content.music_id,
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

    update_fields = data.dict(exclude_unset=True, exclude={"platforms_id"})
    for field, value in update_fields.items():
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

async def get_user_music_files(db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 30):
    result = await db.execute(
        select(MusicFile).where(MusicFile.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def delete_music_file(db: AsyncSession, music_id: UUID, user_id: UUID) -> bool:
    result = await db.execute(
        select(MusicFile).where(MusicFile.id == music_id, MusicFile.user_id == user_id)
    )
    music_file = result.scalars().first()
    if not music_file:
        return False

    await db.delete(music_file)
    await db.commit()
    return True