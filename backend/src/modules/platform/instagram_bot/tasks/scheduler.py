# modules.platform.instagram_bot.tasks.scheduler.py
from celery import shared_task
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_
from core.sync_database import SyncSession
from modules.content.models import ContentPlatform, PostStatus
from modules.platform.models import Platform
from .DailyTaskExecutor import generate_instagram_posting
import logging
import asyncio
import redis
from core.config import settings

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

LOCK_EXPIRE = 60 * 10  # 10 minutes lock

@shared_task(bind=True)
def generate_reels_task(self):
    print("generate_reels_task")
    lock_id = "reels_task_lock"
    have_lock = False
    lock = redis_client.lock(lock_id, timeout=LOCK_EXPIRE)

    session = None

    try:
        
        have_lock = lock.acquire(blocking=False)
        if not have_lock:
            logging.info("Another reels task is already running.")
            return {"status": "skipped", "message": "Another task is already running"}

        logging.info("Checking for pending reelss to generate...")

        session = SyncSession()
        posting = session.execute(
            select(ContentPlatform).where(ContentPlatform.status == PostStatus.posting)
        ).scalars().first()

        if posting:
            logging.info(f"A reels is already posting: {posting.id}")
            return {"status": "skipped", "message": "A reels is already posting"}

        pending = session.execute(
            select(ContentPlatform)
            .options(joinedload(ContentPlatform.platform))
            .where(
                and_(
                    ContentPlatform.status == PostStatus.pending,
                    ContentPlatform.priority == 0
                )
            )
            .order_by(ContentPlatform.created_at.asc())
        ).scalars().first()

        if not pending:
            redis_client.set("current_reels_progress", "ready")
            logging.info("No pending reelss.")
            return {"status": "no_pending", "message": "No pending reelss"}
        else:
            content_id = pending.content_id
            platform_id = pending.platform_id
            platform_name = pending.platform.platform.value
            user_id = pending.platform.user_id
            print(f"Content ID: {content_id}, Platform: {platform_name}, user_id: {user_id}")

        logging.info(f"Found pending reels: {pending.id}")
        pending.status = PostStatus.posting
        session.commit()

        redis_client.set("🔄 current_reels_progress", 0)
        logging.info(f"Reels status updated to posting: {pending.id}")

        final_reels_filename = asyncio.run(generate_instagram_posting(content_id, user_id, platform_id))

        if final_reels_filename:
            pending.status = PostStatus.posted
        else: 
            pending.status = PostStatus.failed
        session.commit()

        redis_client.set("🔄 current_reels_progress", 100)
        logging.info(f"Reels posting completed successfully: {pending.id}")

        return {
            "status": "success",
            "message": "Reels generated successfully",
            "reels_filename": final_reels_filename
        }

    except Exception as e:
        if session:
            session.rollback()
            if pending:
                pending.status = PostStatus.failed
                session.commit()

        redis_client.set("current_reels_progress", "failed")
        logging.error(f"An error occurred: {e}")

        self.update_state(
            state='FAILURE',
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),
            }
        )

        return {
            "status": "failure",
            "error": str(e)
        }
    finally:
        if session:
            session.close()
        if have_lock:
            try:
                lock.release()
                logging.info("Lock released successfully.")
            except redis.exceptions.LockError as e:
                logging.error(f"Error releasing lock: {e}")
