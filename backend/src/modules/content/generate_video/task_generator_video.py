from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import select
from core.sync_database import SyncSession
from modules.content.models import QueueStatus, Content
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

    pending = None
    session = None

    try:
        have_lock = lock.acquire(blocking=False)
        if not have_lock:
            logging.info("Another Video task is already running.")
            return {"status": "skipped", "message": "Another Video task is already running"}

        logging.info("Checking for pending videos to generate...")

        session = SyncSession()
        processing = session.execute(
            select(Content).where(Content.status == QueueStatus.processing)
        ).scalars().first()

        if processing:
            logging.info(f"A video is already processing: {processing.id}")
            return {"status": "skipped", "message": "A video is already processing"}

        from sqlalchemy.orm import joinedload

        pending = session.execute(
            select(Content)
            .options(joinedload(Content.music))
            .where(Content.status == QueueStatus.pending)
            .order_by(Content.created_at.asc())
        ).scalars().first()

        if not pending:
            redis_client.set("current_video_progress", "ready")
            logging.info("No pending videos.")
            return {"status": "no_pending", "message": "No pending videos"}

        logging.info(f"Found pending video: {pending.id}")
        pending.status = QueueStatus.processing
        session.commit()

        redis_client.set("current_video_progress", 0)
        logging.info(f"Video status updated to processing: {pending.id}")

        final_video_filename = asyncio.run(generate_audio_and_video(
            ai_caption=pending.ai_caption,
            video_filename=pending.video_filename,
            remove_audio=pending.remove_audio,
            no_ai_audio=pending.no_ai_audio,
            music_filename=pending.music.filename if pending.music else None,
        ))

        pending.status = QueueStatus.ready
        pending.video_filename = final_video_filename
        session.commit()

        redis_client.set("current_video_progress", 100)
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

        redis_client.set("current_video_progress", "failed")
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
