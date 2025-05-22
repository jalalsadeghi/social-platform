# backend/src/modules/platform/instagram_bot/tasks/instagram_tasks.py
# from celery import shared_task
# from sqlalchemy.ext.asyncio import async_sessionmaker
# from core.database import engine
# from modules.product.crud import get_scheduled_products
# from ..services.instagram_poster import post_to_instagram
# import asyncio
# import logging

# logger = logging.getLogger(__name__)

# @shared_task
# def publish_scheduled_posts():
#     session_maker = async_sessionmaker(engine, expire_on_commit=False)

#     async def async_publish():
#         async with session_maker() as db:
#             products = await get_scheduled_products(db)
#             if not products:
#                 logger.info("No scheduled products found.")
#             for product in products:
#                 logger.info(f"Attempting to post product: {product.title}")
#                 await post_to_instagram(db, product)
#                 logger.info(f"Product {product.title} posted successfully.")

#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(async_publish())
