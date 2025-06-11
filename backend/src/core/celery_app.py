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
        "modules.platform.instagram_bot.tasks.scheduler",
        # "modules.tasks.test_tasks",
        "modules.content.generate_video.task_generator_video"  # اضافه شدن وظایف تولید ویدئو
    ]
)

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
        # "print-hello-every-minute": {
        #     "task": "modules.tasks.test_tasks.print_hello_world",
        #     "schedule": crontab(),
        # },
        "video-generation-task": {
            "task": "modules.content.generate_video.task_generator_video.generate_video_task",
            "schedule": crontab(minute="*/1"),  # هر دقیقه
        },
    }
)

if __name__ == "__main__":
    celery_app.start()
