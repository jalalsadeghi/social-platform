# modules.platform.instagram_bot.tasks.scheduler.py
from celery import shared_task
import asyncio
import logging
import redis
from sqlalchemy.orm import joinedload
from sqlalchemy import select, and_, or_
from core.sync_database import SyncSession
from modules.content.models import ContentPlatform, PostStatus
from core.config import settings
from .DailyTaskExecutor import generate_instagram_posting

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)
LOCK_EXPIRE = 600  # 10 minutes lock

# Wrapper to run async functions synchronously
def sync_generate_reels(content_id, user_id, platform_id):
    return asyncio.run(
        generate_instagram_posting(content_id, user_id, platform_id)
    )

@shared_task(bind=True)
def generate_reels_task(self):
    lock = redis_client.lock("reels_task_lock", timeout=LOCK_EXPIRE)
    have_lock = lock.acquire(blocking=False)

    if not have_lock:
        logging.info("Another reels task is already running.")
        return {"status": "skipped", "message": "Another reels task is already running"}

    session = SyncSession()

    try:
        logging.info("Checking for ready reels to generate...")

        posting_exists = session.execute(
            select(ContentPlatform).where(ContentPlatform.status == PostStatus.posting)
        ).scalars().first()

        if posting_exists:
            logging.info(f"A reel is already posting: {posting_exists.id}")
            return {"status": "skipped", "message": "A reel is already posting"}

        ready_reel = session.execute(
            select(ContentPlatform)
            .options(joinedload(ContentPlatform.platform))
            .where(
                and_(
                    or_(
                        ContentPlatform.status == PostStatus.ready,
                        ContentPlatform.status == PostStatus.failed
                    ),
                    ContentPlatform.priority == 0
                )
            )
            .order_by(ContentPlatform.created_at.asc())
        ).scalars().first()

        if not ready_reel:
            redis_client.set("current_reels_progress", "ready")
            logging.info("No ready reels.")
            return {"status": "no_ready", "message": "No ready reels"}

        content_id = ready_reel.content_id
        platform_id = ready_reel.platform_id
        user_id = ready_reel.platform.user_id
        logging.info(f"Found ready reel: {ready_reel.id}, Content ID: {content_id}")

        ready_reel.status = PostStatus.posting
        session.commit()

        redis_client.set("current_reels_progress", 0)
        logging.info(f"Reel status updated to posting: {ready_reel.id}")

        try:
            final_reels = sync_generate_reels(content_id, user_id, platform_id)

            ready_reel.status = PostStatus.posted if final_reels else PostStatus.failed
            session.commit()

            progress_status = 100 if final_reels else "failed"
            redis_client.set("current_reels_progress", progress_status)

            logging.info(f"Reel posting completed successfully: {ready_reel.id}")

            return {
                "status": "success",
                "message": "Reel generated successfully",
                "reels_filename": final_reels
            }

        except Exception as e:
            session.rollback()
            ready_reel.status = PostStatus.failed
            session.commit()

            redis_client.set("current_reels_progress", "failed")
            logging.error(f"An error occurred during reel posting: {e}")

            self.update_state(
                state='FAILURE',
                meta={'exc_type': type(e).__name__, 'exc_message': str(e)}
            )

            return {
                "status": "failure",
                "error": str(e)
            }

    except Exception as general_e:
        logging.error(f"Unexpected error during task execution: {general_e}")
        self.update_state(
            state='FAILURE',
            meta={'exc_type': type(general_e).__name__, 'exc_message': str(general_e)}
        )
        return {
            "status": "failure",
            "error": str(general_e)
        }

    finally:
        session.close()
        if have_lock:
            try:
                lock.release()
                logging.info("Lock released successfully.")
            except redis.exceptions.LockError as lock_error:
                logging.error(f"Error releasing lock: {lock_error}")