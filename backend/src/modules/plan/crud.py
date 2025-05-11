# backend/src/modules/plan/crud.py
from sqlalchemy.orm import Session
from modules.plan.models import Plan, Subscription
from modules.plan.schemas import PlanCreate, PlanUpdate, SubscriptionCreate
import uuid

# Plan operations
def create_plan(db: Session, plan: PlanCreate):
    db_plan = Plan(
        id=uuid.uuid4(),
        **plan.dict()
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def get_plan(db: Session, plan_id: uuid.UUID):
    return db.query(Plan).filter(Plan.id == plan_id).first()

def update_plan(db: Session, plan_id: uuid.UUID, plan_update: PlanUpdate):
    db_plan = get_plan(db, plan_id)
    for key, value in plan_update.dict(exclude_unset=True).items():
        setattr(db_plan, key, value)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, plan_id: uuid.UUID):
    db_plan = get_plan(db, plan_id)
    db.delete(db_plan)
    db.commit()
    return True

def get_plans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Plan).offset(skip).limit(limit).all()

# Subscription operations
def create_subscription(db: Session, subscription: SubscriptionCreate):
    db_subscription = Subscription(
        id=uuid.uuid4(),
        **subscription.dict()
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def get_subscription(db: Session, subscription_id: uuid.UUID):
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()

def update_subscription_status(db: Session, subscription_id: uuid.UUID, status: str):
    db_subscription = get_subscription(db, subscription_id)
    db_subscription.status = status
    db.commit()
    db.refresh(db_subscription)
    return db_subscription
