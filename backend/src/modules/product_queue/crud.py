from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.product_queue.models import ProductQueue
from modules.product_queue.schemas import ProductQueueCreate, ProductQueueUpdate
import uuid

async def create_product_queue(db: AsyncSession, user_id: uuid.UUID, queue_data: ProductQueueCreate):
    db_queue = ProductQueue(user_id=user_id, **queue_data.dict())
    db.add(db_queue)
    await db.commit()
    await db.refresh(db_queue)
    return db_queue

async def get_product_queue(db: AsyncSession, queue_id: uuid.UUID):
    result = await db.execute(select(ProductQueue).where(ProductQueue.id == queue_id))
    return result.scalars().first()

async def update_product_queue(db: AsyncSession, queue_id: uuid.UUID, data: ProductQueueUpdate):
    db_queue = await get_product_queue(db, queue_id)
    if not db_queue:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_queue, key, value)
    await db.commit()
    await db.refresh(db_queue)
    return db_queue

async def get_product_queues(db: AsyncSession, user_id: uuid.UUID, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(ProductQueue)
        .where(ProductQueue.user_id == user_id)
        .order_by(ProductQueue.priority.desc(), ProductQueue.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
