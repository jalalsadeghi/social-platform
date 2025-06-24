# src/modules/content/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from .models import Content, QueueStatus, MusicFile, ContentPlatform, PostStatus
from modules.platform.models import Platform
from datetime import datetime
from typing import List, Optional
from .schemas import ContentCreate, ContentBase, UpdatePriority

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
        no_ai_audio=content.no_ai_audio,
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
            priority=priority,
            url=""
        )
        db.add(content_platform)

    await db.commit()
    await db.refresh(db_content)
    return db_content


async def get_contents(db: AsyncSession, user_id: UUID, skip=0, limit=30) -> List[Content]:
    result = await db.execute(
        select(Content)
            .where(Content.user_id == user_id)
            .order_by(Content.created_at.desc())
            .offset(skip).limit(limit)
    )
    return result.scalars().all()

async def get_content_by_id(db: AsyncSession, content_id: UUID, user_id: UUID) -> Optional[Content]:
    result = await db.execute(
        select(Content).where(Content.id == content_id, Content.user_id == user_id)
    )
    return result.scalars().first()


async def update_content(
    db: AsyncSession, content_id: UUID, user_id: UUID, platforms_id: List[UUID]
) -> Optional[Content]:
    db_content = await get_content_by_id(db, content_id, user_id)

    if not db_content or db_content.status != QueueStatus.ready:
        return None

    current_platform_ids = {cp.platform_id for cp in db_content.content_platforms}
    new_platform_ids = set(platforms_id)

    # Platforms to add and remove
    platforms_to_add = new_platform_ids - current_platform_ids
    platforms_to_remove = current_platform_ids - new_platform_ids

    # Remove platforms that are not selected anymore
    if platforms_to_remove:
        await db.execute(
            ContentPlatform.__table__.delete().where(
                ContentPlatform.content_id == db_content.id,
                ContentPlatform.platform_id.in_(platforms_to_remove)
            )
        )

    # Add new platforms
    for platform_id in platforms_to_add:
        priority = await get_max_priority(db, user_id, platform_id) + 1
        new_content_platform = ContentPlatform(
            content_id=db_content.id,
            platform_id=platform_id,
            priority=priority,
            url="",
            status=PostStatus.ready
        )
        db.add(new_content_platform)

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
            ContentPlatform.status == PostStatus.ready,
            ContentPlatform.status == PostStatus.pending,
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


async def get_contents_by_platform_id(db: AsyncSession, platform_id: UUID, skip=0, limit=30):
    result = await db.execute(
        select(ContentPlatform)
        .options(joinedload(ContentPlatform.content))
        .where(ContentPlatform.platform_id == platform_id)
        .order_by(ContentPlatform.priority.asc())
        .offset(skip)
        .limit(limit)
    )

    content_platforms = result.scalars().all()

    return [
        {
            "id": cp.id,
            "content_id": cp.content_id,
            "title": cp.content.ai_title,
            "video_filename": cp.content.video_filename,
            "thumb_filename": cp.content.thumb_filename,
            "status": cp.status,
            "priority": cp.priority,
            "url": cp.url,
            "updated_at": cp.content.updated_at,
        }
        for cp in content_platforms
    ]



async def delete_content_platform(
    db: AsyncSession, content_platforms_id: UUID
) -> bool:
    result = await db.execute(
        select(ContentPlatform)
        .where(
            ContentPlatform.id == content_platforms_id,
        )
    )
    content_platform = result.scalars().first()

    if not content_platform:
        return False

    await db.delete(content_platform)
    await db.commit()
    return True

async def update_priorities(
    db: AsyncSession, 
    priorities: List[UpdatePriority]
):
    for item in priorities:
        await db.execute(
            select(ContentPlatform)
            .filter(ContentPlatform.id == item.content_platform_id)
            .execution_options(synchronize_session="fetch")
        )

        await db.execute(
            ContentPlatform.__table__.update()
            .where(ContentPlatform.id == item.content_platform_id)
            .values(priority=item.priority)
        )
    await db.commit()