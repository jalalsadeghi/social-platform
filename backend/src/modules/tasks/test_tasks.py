from core.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.print_hello_world")
def print_hello_world():
    logger.info("Hello, World! This task runs every minute.")
