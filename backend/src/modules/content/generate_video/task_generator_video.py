# modules/content/generate_video/task_generator_video.py
from celery import shared_task
import asyncio
import logging
import redis
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from core.sync_database import SyncSession
from modules.content.models import QueueStatus, Content, PostStatus, ContentPlatform
from .generate_video import generate_audio_and_video
from core.config import settings

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)
LOCK_EXPIRE = 60 * 10  # 10 minutes lock

def sync_generate_video(pending: Content):
    return asyncio.run(
        generate_audio_and_video(
            ai_caption=pending.ai_caption,
            video_filename=pending.video_filename,
            remove_audio=pending.remove_audio,
            no_ai_audio=pending.no_ai_audio,
            music_filename=pending.music.filename if pending.music else None,
        )
    )

@shared_task(bind=True)
def generate_video_task(self):
    lock = redis_client.lock("video_task_lock", timeout=LOCK_EXPIRE)
    have_lock = lock.acquire(blocking=False)

    if not have_lock:
        logging.info("Another video task is already running.")
        return {"status": "skipped", "message": "Another video task is already running"}

    session = SyncSession()
    pending = None

    try:
        logging.info("Checking for pending videos to generate...")

        processing_exists = session.execute(
            select(Content).where(Content.status == QueueStatus.processing)
        ).scalars().first()

        if processing_exists:
            logging.info(f"A video is already processing: {processing_exists.id}")
            return {"status": "skipped", "message": "A video is already processing"}

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

        # اجرای تسک async در محیط sync
        final_video_filename = sync_generate_video(pending)

        # بروزرسانی وضعیت video و platform
        pending.status = QueueStatus.ready
        pending.video_filename = final_video_filename
        session.commit()

        # به روز رسانی وضعیت ContentPlatform
        content_platform = session.execute(
            select(ContentPlatform).where(ContentPlatform.content_id == pending.id)
        ).scalars().first()

        if content_platform:
            content_platform.status = PostStatus.ready
            session.commit()

        redis_client.set("current_video_progress", 100)
        logging.info(f"Video processing completed successfully: {pending.id}")

        return {
            "status": "success",
            "message": "Video generated successfully",
            "video_filename": final_video_filename
        }

    except Exception as e:
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
        session.close()
        if have_lock:
            try:
                lock.release()
                logging.info("Lock released successfully.")
            except redis.exceptions.LockError as e:
                logging.error(f"Error releasing lock: {e}")