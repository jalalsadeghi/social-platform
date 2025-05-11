# backend/src/modules/plan/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modules.plan import schemas, crud
from core.database import get_db
import uuid
from typing import List

router = APIRouter(prefix="/plans", tags=["plans"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# Plan APIs
@router.post("/", response_model=schemas.PlanOut)
def create_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    return crud.create_plan(db, plan)

@router.get("/{plan_id}", response_model=schemas.PlanOut)
def read_plan(plan_id: uuid.UUID, db: Session = Depends(get_db)):
    db_plan = crud.get_plan(db, plan_id)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.put("/{plan_id}", response_model=schemas.PlanOut)
def update_plan(plan_id: uuid.UUID, plan: schemas.PlanUpdate, db: Session = Depends(get_db)):
    return crud.update_plan(db, plan_id, plan)

@router.delete("/{plan_id}")
def delete_plan(plan_id: uuid.UUID, db: Session = Depends(get_db)):
    crud.delete_plan(db, plan_id)
    return {"ok": True}

@router.get("/", response_model=List[schemas.PlanOut])
def list_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_plans(db, skip, limit)

# Subscription APIs
@router.post("/subscriptions", response_model=schemas.SubscriptionOut)
def create_subscription(subscription: schemas.SubscriptionCreate, db: Session = Depends(get_db)):
    return crud.create_subscription(db, subscription)

@router.get("/subscriptions/{subscription_id}", response_model=schemas.SubscriptionOut)
def read_subscription(subscription_id: uuid.UUID, db: Session = Depends(get_db)):
    db_subscription = crud.get_subscription(db, subscription_id)
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return db_subscription

@router.put("/subscriptions/{subscription_id}/status", response_model=schemas.SubscriptionOut)
def update_subscription_status(subscription_id: uuid.UUID, status: schemas.SubscriptionStatus, db: Session = Depends(get_db)):
    return crud.update_subscription_status(db, subscription_id, status)
