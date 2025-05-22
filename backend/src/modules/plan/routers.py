# src/modules/plan/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from modules.plan import schemas, crud
from core.database import get_db
import uuid
from typing import List

router = APIRouter(prefix="/plans", tags=["plans"])

# مسیرهای Plan
@router.post("/", response_model=schemas.PlanOut)
async def create_plan(plan: schemas.PlanCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_plan(db, plan)

@router.get("/", response_model=List[schemas.PlanOut])
async def list_plans(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_plans(db, skip, limit)

# Subscription APIs (قبل از مسیرهای UUID)
@router.post("/subscriptions", response_model=schemas.SubscriptionOut)
async def create_subscription(subscription: schemas.SubscriptionCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_subscription(db, subscription)

@router.get("/subscriptions/{subscription_id}", response_model=schemas.SubscriptionOut)
async def read_subscription(subscription_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    db_subscription = await crud.get_subscription(db, subscription_id)
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return db_subscription

@router.get("/subscriptions", response_model=List[schemas.SubscriptionOut])
async def list_subscriptions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_subscriptions(db, skip, limit)

@router.put("/subscriptions/{subscription_id}/status", response_model=schemas.SubscriptionOut)
async def update_subscription_status(subscription_id: uuid.UUID, status: schemas.SubscriptionStatus, db: AsyncSession = Depends(get_db)):
    return await crud.update_subscription_status(db, subscription_id, status)

# مسیرهای UUID باید همیشه آخر باشند
@router.get("/{plan_id}", response_model=schemas.PlanOut)
async def read_plan(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    db_plan = await crud.get_plan(db, plan_id)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.put("/{plan_id}", response_model=schemas.PlanOut)
async def update_plan(plan_id: uuid.UUID, plan: schemas.PlanUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.update_plan(db, plan_id, plan)

@router.delete("/{plan_id}")
async def delete_plan(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await crud.delete_plan(db, plan_id)
    return {"ok": True}
