# modules.platform.instagram_bot.tasks.scheduler.py

from celery import shared_task
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload
from sqlalchemy import select, and_
from modules.content.models import ContentPlatform, PostStatus
from modules.platform.models import Platform
from core.database import engine
from .DailyTaskExecutor import generate_instagram_posting
import logging
import asyncio
import redis
from core.config import settings

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

LOCK_EXPIRE = 600  # 10 minutes lock

@shared_task(bind=True)
def generate_reels_task(self):
    lock_id = "reels_task_lock"
    lock = redis_client.lock(lock_id, timeout=LOCK_EXPIRE)

    if lock.acquire(blocking=False):
        try:
            asyncio.run(async_generate_reels_task())
        except Exception as e:
            logging.error(f"Unexpected error during task execution: {e}")
        finally:
            lock.release()
            logging.info("Lock released successfully.")
    else:
        logging.info("Another reels task is already running.")


async def async_generate_reels_task():
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as session:
        logging.info("Checking for ready reels to generate...")

        posting = await session.execute(
            select(ContentPlatform).where(ContentPlatform.status == PostStatus.posting)
        )
        posting = posting.scalars().first()

        if posting:
            logging.info(f"A reel is already posting: {posting.id}")
            return

        ready = await session.execute(
            select(ContentPlatform)
            .options(joinedload(ContentPlatform.platform))
            .where(
                and_(
                    ContentPlatform.status == PostStatus.ready,
                    ContentPlatform.priority == 0
                )
            )
            .order_by(ContentPlatform.created_at.asc())
        )
        ready = ready.scalars().first()
        
        if not ready:
            redis_client.set("current_reels_progress", "ready")
            logging.info("No ready reels.")
            return

        content_id = ready.content_id
        platform_id = ready.platform_id
        user_id = ready.platform.user_id
        logging.info(f"Found ready reel: {ready.id}, Content ID: {content_id}")
       
        ready.status = PostStatus.posting
        await session.commit()

        redis_client.set("current_reels_progress", 0)
        logging.info(f"Reel status updated to posting: {ready.id}")

        try:
            final_reels = await generate_instagram_posting(content_id, user_id, platform_id)

            ready.status = PostStatus.posted if final_reels else PostStatus.ready
            await session.commit()

            progress_status = 100 if final_reels else "failed"
            redis_client.set("current_reels_progress", progress_status)

            logging.info(f"Reel posting completed successfully: {ready.id}")

        except Exception as e:
            await session.rollback()
            ready.status = PostStatus.failed
            await session.commit()

            redis_client.set("current_reels_progress", "failed")
            logging.error(f"An error occurred during reel posting: {e}")



# # modules.platform.instagram_bot.tasks.scheduler.py
# from celery import shared_task
# from sqlalchemy.orm import Session, joinedload
# from sqlalchemy import select, and_
# from core.sync_database import SyncSession
# from modules.content.models import ContentPlatform, PostStatus
# from modules.platform.models import Platform
# from .DailyTaskExecutor import generate_instagram_posting
# import logging
# import asyncio
# import redis
# from core.config import settings

# redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

# LOCK_EXPIRE = 60 * 10  # 10 minutes lock

# @shared_task(bind=True)
# def generate_reels_task(self):
#     print("generate_reels_task")
#     lock_id = "reels_task_lock"
#     have_lock = False
#     lock = redis_client.lock(lock_id, timeout=LOCK_EXPIRE)

#     session = None

#     try:
        
#         have_lock = lock.acquire(blocking=False)
#         if not have_lock:
#             logging.info("Another reels task is already running.")
#             return {"status": "skipped", "message": "Another task is already running"}

#         logging.info("Checking for ready reelss to generate...")

#         session = SyncSession()
#         posting = session.execute(
#             select(ContentPlatform).where(ContentPlatform.status == PostStatus.posting)
#         ).scalars().first()

#         if posting:
#             logging.info(f"A reels is already posting: {posting.id}")
#             return {"status": "skipped", "message": "A reels is already posting"}

#         ready = session.execute(
#             select(ContentPlatform)
#             .options(joinedload(ContentPlatform.platform))
#             .where(
#                 and_(
#                     ContentPlatform.status == PostStatus.ready,
#                     ContentPlatform.priority == 0
#                 )
#             )
#             .order_by(ContentPlatform.created_at.asc())
#         ).scalars().first()

#         if not ready:
#             redis_client.set("current_reels_progress", "ready")
#             logging.info("No ready reelss.")
#             return {"status": "no_ready", "message": "No ready reelss"}
#         else:
#             content_id = ready.content_id
#             platform_id = ready.platform_id
#             platform_name = ready.platform.platform.value
#             user_id = ready.platform.user_id
#             print(f"Content ID: {content_id}, Platform: {platform_name}, user_id: {user_id}")

#         logging.info(f"Found ready reels: {ready.id}")
#         ready.status = PostStatus.posting
#         session.commit()

#         redis_client.set("🔄 current_reels_progress", 0)
#         logging.info(f"Reels status updated to posting: {ready.id}")

#         final_reels_filename = asyncio.run(generate_instagram_posting(content_id, user_id, platform_id))

#         if final_reels_filename:
#             ready.status = PostStatus.posted
#         else: 
#             ready.status = PostStatus.failed
#         session.commit()

#         redis_client.set("🔄 current_reels_progress", 100)
#         logging.info(f"Reels posting completed successfully: {ready.id}")

#         return {
#             "status": "success",
#             "message": "Reels generated successfully",
#             "reels_filename": final_reels_filename
#         }

#     except Exception as e:
#         if session:
#             session.rollback()
#             if ready:
#                 ready.status = PostStatus.failed
#                 session.commit()

#         redis_client.set("current_reels_progress", "failed")
#         logging.error(f"An error occurred: {e}")

#         self.update_state(
#             state='FAILURE',
#             meta={
#                 'exc_type': type(e).__name__,
#                 'exc_message': str(e),
#             }
#         )

#         return {
#             "status": "failure",
#             "error": str(e)
#         }
#     finally:
#         if session:
#             session.close()
#         if have_lock:
#             try:
#                 lock.release()
#                 logging.info("Lock released successfully.")
#             except redis.exceptions.LockError as e:
#                 logging.error(f"Error releasing lock: {e}")
