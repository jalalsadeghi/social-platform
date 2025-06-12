from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import select
from core.sync_database import SyncSession
from modules.content.models import QueueStatus, Content
from .DailyTaskExecutor import execute_daily_tasks
import logging
import asyncio
import redis
from core.config import settings

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

LOCK_EXPIRE = 60 * 10  # 10 minutes lock

@shared_task(bind=True)
def generate_reels_task(self):
    lock_id = "Reels_task_lock"
    have_lock = False
    lock = redis_client.lock(lock_id, timeout=LOCK_EXPIRE)

    session = None

    try:
        have_lock = lock.acquire(blocking=False)
        if not have_lock:
            logging.info("Another Reels task is already running.")
            return {"status": "skipped", "message": "Another Reels task is already running"}

        logging.info("Checking for pending Reels to posting...")

        session = SyncSession()
        posting = session.execute(
            select(Content).where(Content.status == QueueStatus.posting)
        ).scalars().first()

        if posting:
            logging.info(f"A reels is already posting: {posting.id}")
            return {"status": "skipped", "message": "A reels is already posting"}

        pending = session.execute(
            select(Content).where(Content.status == QueueStatus.pending).order_by(Content.created_at.asc())
        ).scalars().first()

        if not pending:
            redis_client.set("current_reels_progress", "ready")
            logging.info("No pending reels.")
            return {"status": "no_pending", "message": "No pending reels"}

        logging.info(f"Found pending reels: {pending.id}")
        pending.status = QueueStatus.posting
        session.commit()

        redis_client.set("current_reels_progress", 0)
        logging.info(f"Reels status updated to posting: {pending.id}")

        final_reels_filename = asyncio.run(execute_daily_tasks(
            pending.id))

        pending.status = QueueStatus.ready
        pending.reels_filename = final_reels_filename
        session.commit()

        redis_client.set("current_reels_progress", 100)
        logging.info(f"Reels posting completed successfully: {pending.id}")

        return {
            "status": "success",
            "message": "Reels generated successfully",
            "Reels_filename": final_reels_filename
        }

    except Exception as e:
        if session:
            session.rollback()
            if pending:
                pending.status = QueueStatus.failed_generate
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
