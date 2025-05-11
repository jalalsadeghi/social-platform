# backend/src/modules/admin/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.user.models import User, Role
from modules.plan.models import Plan
from modules.ai.models import AIPrompt
from sqlalchemy import or_
import uuid

async def get_users(db: AsyncSession, query: str = None):
    stmt = select(User)
    if query:
        stmt = stmt.filter(
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
        )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_user(db: AsyncSession, user_id: uuid.UUID, data):
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        return None
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_roles(db: AsyncSession):
    result = await db.execute(select(Role))
    return result.scalars().all()

async def update_role(db: AsyncSession, role_id: uuid.UUID, data):
    result = await db.execute(select(Role).where(Role.id == role_id))
    db_role = result.scalars().first()
    if not db_role:
        return None
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_role, key, value)
    await db.commit()
    await db.refresh(db_role)
    return db_role

async def create_plan(db: AsyncSession, plan):
    db_plan = Plan(**plan.dict())
    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)
    return db_plan

async def update_plan(db: AsyncSession, plan_id: uuid.UUID, data):
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    db_plan = result.scalars().first()
    if not db_plan:
        return None
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    await db.commit()
    await db.refresh(db_plan)
    return db_plan

async def get_plans(db: AsyncSession):
    result = await db.execute(select(Plan))
    return result.scalars().all()

async def create_prompt(db: AsyncSession, prompt):
    db_prompt = AIPrompt(**prompt.dict())
    db.add(db_prompt)
    await db.commit()
    await db.refresh(db_prompt)
    return db_prompt

async def update_prompt(db: AsyncSession, prompt_id: uuid.UUID, data):
    result = await db.execute(select(AIPrompt).where(AIPrompt.id == prompt_id))
    db_prompt = result.scalars().first()
    if not db_prompt:
        return None
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_prompt, key, value)
    await db.commit()
    await db.refresh(db_prompt)
    return db_prompt

async def get_prompts(db: AsyncSession):
    result = await db.execute(select(AIPrompt))
    return result.scalars().all()
