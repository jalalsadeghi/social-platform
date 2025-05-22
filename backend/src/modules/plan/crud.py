# src/modules/plan/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.plan.models import Plan, Subscription
from modules.plan.schemas import PlanCreate, PlanUpdate, SubscriptionCreate
import uuid
from datetime import datetime, timezone

# Plan operations
async def create_plan(db: AsyncSession, plan: PlanCreate):
    now = datetime.now(timezone.utc)
    db_plan = Plan(
        id=uuid.uuid4(),
        created_at=now,
        updated_at=now,
        **plan.dict()
    )
    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)
    return db_plan

async def get_plan(db: AsyncSession, plan_id: uuid.UUID):
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    return result.scalars().first()

async def update_plan(db: AsyncSession, plan_id: uuid.UUID, plan_update: PlanUpdate):
    db_plan = await get_plan(db, plan_id)
    update_data = plan_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan, key, value)

    db_plan.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(db_plan)
    return db_plan

async def delete_plan(db: AsyncSession, plan_id: uuid.UUID):
    db_plan = await get_plan(db, plan_id)
    await db.delete(db_plan)
    await db.commit()
    return True

async def get_plans(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Plan).offset(skip).limit(limit))
    return result.scalars().all()

# Subscription operations
async def create_subscription(db: AsyncSession, subscription: SubscriptionCreate):
    now = datetime.now(timezone.utc)
    db_subscription = Subscription(
        id=uuid.uuid4(),
        start_date=now,
        **subscription.dict()
    )
    db.add(db_subscription)
    await db.commit()
    await db.refresh(db_subscription)
    return db_subscription

async def get_subscription(db: AsyncSession, subscription_id: uuid.UUID):
    result = await db.execute(select(Subscription).where(Subscription.id == subscription_id))
    return result.scalars().first()

async def update_subscription_status(db: AsyncSession, subscription_id: uuid.UUID, status: str):
    db_subscription = await get_subscription(db, subscription_id)
    db_subscription.status = status
    await db.commit()
    await db.refresh(db_subscription)
    return db_subscription
