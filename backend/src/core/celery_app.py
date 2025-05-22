# backend/src/core/celery_app.py
from celery import Celery
from celery.schedules import crontab
from core.config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
)

celery_app = Celery(
    "social_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "modules.platform.instagram_bot.tasks.scheduler"
    ]
)

# تنظیمات Celery با Beat Schedule مستقیماً اینجا تعریف شود
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    beat_scheduler='celery.beat:PersistentScheduler',
    beat_schedule_filename='/tmp/celerybeat-schedule',
    beat_schedule={
        "publish-instagram-posts-every-minute": {
            "task": "modules.platform.instagram_bot.tasks.scheduler.schedule_test_call",
            "schedule": crontab(hour=6, minute=0),  # هر دقیقه برای تست
        },
    }
)

if __name__ == "__main__":
    celery_app.start()
