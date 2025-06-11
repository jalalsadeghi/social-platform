from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import select
from core.sync_database import SyncSession
from ..models import QueueStatus, Content
from .generate_video import generate_audio_and_video
import logging
import asyncio
import redis
from core.config import settings

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

LOCK_EXPIRE = 60 * 10  # 10 minutes lock

@shared_task(bind=True)
def generate_video_task(self):
    lock_id = "video_task_lock"
    have_lock = False
    lock = redis_client.lock(lock_id, timeout=LOCK_EXPIRE)

    session = None

    try:
        have_lock = lock.acquire(blocking=False)
        if not have_lock:
            logging.info("Another task is already running.")
            return {"status": "skipped", "message": "Another task is already running"}

        logging.info("Checking for pending videos to generate...")

        session = SyncSession()
        processing = session.execute(
            select(Content).where(Content.status == QueueStatus.processing)
        ).scalars().first()

        if processing:
            logging.info(f"A video is already processing: {processing.id}")
            return {"status": "skipped", "message": "A video is already processing"}

        pending = session.execute(
            select(Content).where(Content.status == QueueStatus.pending).order_by(Content.created_at.asc())
        ).scalars().first()

        if not pending:
            logging.info("No pending videos.")
            return {"status": "no_pending", "message": "No pending videos"}

        logging.info(f"Found pending video: {pending.id}")
        pending.status = QueueStatus.processing
        session.commit()

        logging.info(f"Video status updated to processing: {pending.id}")

        final_video_filename = asyncio.run(generate_audio_and_video(
            pending.ai_caption, 
            pending.video_filename))

        pending.status = QueueStatus.ready
        pending.video_filename = final_video_filename
        session.commit()

        logging.info(f"Video processing completed successfully: {pending.id}")

        return {
            "status": "success",
            "message": "Video generated successfully",
            "video_filename": final_video_filename
        }

    except Exception as e:
        if session:
            session.rollback()
            if pending:
                pending.status = QueueStatus.failed_generate
                session.commit()

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
