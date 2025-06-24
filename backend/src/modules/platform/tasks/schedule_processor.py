# src/modules/platform/tasks/schedule_processor.py
from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from core.sync_database import SyncSession
from modules.content.models import ContentPlatform, PostStatus
from modules.platform.models import Platform
import logging
import redis
from core.config import settings
from datetime import datetime, timezone

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)
LOCK_EXPIRE = 60 * 5  # 5 minutes lock

def generate_operation_key(platform_id, day, send_time):
    return f"priority_shift:{platform_id}:{day}:{send_time}"

@shared_task(bind=True)
def schedule_priority_shift_task(self):
    lock_id = "schedule_priority_shift_lock"
    lock = redis_client.lock(lock_id, timeout=LOCK_EXPIRE)

    if not lock.acquire(blocking=False):
        logging.info("Another schedule priority shift task is running.")
        return

    session = SyncSession()

    try:
        current_time = datetime.now(timezone.utc)
        current_day = current_time.strftime("%a")  # e.g. "Fri"
        current_hour_minute = current_time.strftime("%H:%M")

        logging.info(f"Checking schedules for {current_day} at {current_hour_minute} UTC.")

        platforms = session.execute(select(Platform)).scalars().all()

        for platform in platforms:
            schedule = platform.schedule.get(current_day, {})
            
            sorted_send_times = sorted(schedule.values())

            for idx, send_time in enumerate(sorted_send_times):
                operation_key = generate_operation_key(platform.id, current_day, send_time)

                if redis_client.get(operation_key):
                    continue
                
                next_send_time = sorted_send_times[idx + 1] if idx + 1 < len(sorted_send_times) else None

                if (current_hour_minute >= send_time) and (next_send_time is None or current_hour_minute < next_send_time):
                    session.execute(
                        update(ContentPlatform)
                        .where(
                            ContentPlatform.platform_id == platform.id,
                            ContentPlatform.status.in_([PostStatus.ready, PostStatus.pending]),
                            ContentPlatform.priority > 0
                        )
                        .values(priority=ContentPlatform.priority - 1)
                    )

                    session.commit()

                    redis_client.setex(operation_key, 86400, "completed")
                    logging.info(f"Priority updated for platform_id {platform.id} at {send_time}.")
                    break

        logging.info("Priority shift task completed.")

    except Exception as e:
        session.rollback()
        logging.error(f"Error occurred: {e}")
        self.update_state(
            state='FAILURE',
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),
            }
        )
    finally:
        session.close()
        lock.release()
