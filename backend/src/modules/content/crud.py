# src/modules/content/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy import func
from .models import Content, QueueStatus, MusicFile, ContentPlatform, PostStatus
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
    )

    db.add(db_content)
    await db.flush()

    for platform in platforms:
        if content.priority_zero:
            priority = 0
        else:
            priority = await get_max_priority(db, user_id, platform.id) + 1
        content_platform = ContentPlatform(
            content_id=db_content.id,
            platform_id=platform.id,
            status=PostStatus.pending,
            priority=priority
        )
        db.add(content_platform)

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

    await db.execute(
        ContentPlatform.__table__.delete().where(ContentPlatform.content_id == db_content.id)
    )

    for platform_id in data.platforms_id:
        priority = await get_max_priority(db, user_id, platform_id) + 1
        db_content_platform = ContentPlatform(
            content_id=db_content.id,
            platform_id=platform_id,
            status=PostStatus.pending,
            priority=priority
        )
        db.add(db_content_platform)

    update_fields = data.dict(exclude_unset=True, exclude={"platforms_id"})
    for field, value in update_fields.items():
        setattr(db_content, field, value)

    await db.commit()
    await db.refresh(db_content)
    return db_content


async def get_max_priority(db: AsyncSession, user_id: UUID, platform_id: UUID) -> int:
    result = await db.execute(
        select(func.max(ContentPlatform.priority))
        .join(Content)
        .where(
            Content.user_id == user_id,
            ContentPlatform.platform_id == platform_id,
            ContentPlatform.status == PostStatus.pending
        )
    )
    max_priority = result.scalar()
    return max_priority if max_priority is not None else 0


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

async def get_exist_processing_video(session: AsyncSession) -> Optional[Content]:
    #Check if there's any video currently being processed
    processing_count = await session.execute(
        select(func.count()).select_from(Content).where(Content.status == QueueStatus.processing)
    )
    return processing_count.scalar_one()

async def get_next_pending_video(session: AsyncSession) -> Optional[Content]:
    result = await session.execute(
        select(Content)
        .where(Content.status == QueueStatus.pending)
        .order_by(Content.created_at.asc())
    )
    return result.scalars().first()