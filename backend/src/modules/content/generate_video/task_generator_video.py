# modules/content/generate_video/task_generator_video.py

from celery import shared_task
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from core.sync_database import SyncSession
from ..models import QueueStatus, Content

@shared_task
def generate_video_task():
    logging.info("Checking for pending videos to generate...")

    session: Session = SyncSession()
    try:
        processing = session.execute(
            select(Content).where(Content.status == QueueStatus.processing)
        ).scalars().first()

        if processing:
            logging.info(f"A video is already processing: {processing.id}")
            return

        pending = session.execute(
            select(Content).where(Content.status == QueueStatus.pending).order_by(Content.created_at.asc())
        ).scalars().first()

        if not pending:
            logging.info("No pending videos.")
            return

        logging.info(f"Found pending video: {pending.id}")
        pending.status = QueueStatus.processing
        session.commit()

        logging.info(f"Video status updated to processing: {pending.id}")

    except Exception as e:
        session.rollback()
        logging.error(f"An error occurred: {e}")
    finally:
        session.close()
