# backend/src/modules/platform/instagram_bot/tasks/scheduler.py
from celery.schedules import crontab
from core.celery_app import celery_app
from random import randint
import time
# from .instagram_tasks import publish_scheduled_posts
from .DailyTaskExecutor import execute_daily_tasks
import asyncio

# @celery_app.task
# def schedule_random_daily_posts(user_id):
#     random_delay_minutes = randint(0, 120)  # تأخیر بین 0 تا 120 دقیقه (6 تا 8 صبح)
#     print(f"Scheduled post will run after {random_delay_minutes} minutes.")
#     time.sleep(random_delay_minutes * 60)
#     asyncio.run(daily_tasks(user_id))

# celery_app.conf.beat_schedule = {
#     "schedule-random-instagram-posts-daily": {
#         "task": "modules.platform.instagram_bot.tasks.scheduler.schedule_random_daily_posts",
#         "schedule": crontab(hour=6, minute=0),  # هر روز ساعت ۶ صبح اجرا شود
#     },
# }

@celery_app.task
def schedule_test_call(user_id):
    """Execute daily tasks for testing."""
    return asyncio.run(execute_daily_tasks(user_id))