# crud.py
from sqlalchemy.orm import Session
from modules.user.models import User, Role
from modules.plan.models import Plan
from modules.ai.models import AIPrompt
from sqlalchemy import or_

def get_users(db: Session, query: str = None):
    if query:
        return db.query(User).filter(or_(User.username.ilike(f"%{query}%"), User.email.ilike(f"%{query}%"))).all()
    return db.query(User).all()

def update_user(db: Session, user_id, data):
    db_user = db.query(User).filter(User.id == user_id).first()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_roles(db: Session):
    return db.query(Role).all()

def update_role(db: Session, role_id, data):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_role, key, value)
    db.commit()
    db.refresh(db_role)
    return db_role

def create_plan(db: Session, plan):
    db_plan = Plan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan(db: Session, plan_id, data):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_plan, key, value)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def get_plans(db: Session):
    return db.query(Plan).all()

def create_prompt(db: Session, prompt):
    db_prompt = AIPrompt(**prompt.dict())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

def update_prompt(db: Session, prompt_id, data):
    db_prompt = db.query(AIPrompt).filter(AIPrompt.id == prompt_id).first()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_prompt, key, value)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

def get_prompts(db: Session):
    return db.query(AIPrompt).all()