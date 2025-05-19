# backend/src/modules/platform/instagram_bot/tasks/scheduler.py
from celery.schedules import crontab
from core.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "publish-instagram-posts-every-15-minutes": {
        "task": "modules.platform.instagram_bot.tasks.instagram_tasks.publish_scheduled_posts",
        "schedule": crontab(),  # هر 1 دقیقه
    },
}
