# src/core/celery_app.py
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
        "modules.content.generate_video.task_generator_video",
        "modules.platform.bots.tasks.scheduler",
        "modules.platform.tasks.schedule_processor",
    ]
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_track_started=True, 
    beat_scheduler='celery.beat:PersistentScheduler',
    beat_schedule_filename='/tmp/celerybeat-schedule',
    beat_schedule={
        "video-generation-task": {
            "task": "modules.content.generate_video.task_generator_video.generate_video_task",
            "schedule": crontab(minute="*/1"),
        },
        "post-executor-task": {
            "task": "modules.platform.bots.tasks.scheduler.generate_reels_task",
            "schedule": crontab(minute="*/1"), 
        },
        "schedule-processor-task": {
            "task": "modules.platform.tasks.schedule_processor.schedule_priority_shift_task",
            "schedule": crontab(minute="*/1"), 
        },
    }
)

if __name__ == "__main__":
    celery_app.start()