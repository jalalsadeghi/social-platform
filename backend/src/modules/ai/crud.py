# backend/src/modules/ai/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.ai.models import AIPrompt, Language
from modules.ai.schemas import PromptCreate, PromptUpdate
from uuid import UUID
from typing import List

async def create_prompt(db: AsyncSession, prompt: PromptCreate, user_id=UUID):
    db_prompt = AIPrompt(**prompt.dict(), user_id=user_id)
    db.add(db_prompt)
    await db.commit()
    await db.refresh(db_prompt)
    return db_prompt

async def get_prompts(db: AsyncSession, user_id: UUID, skip=0, limit=30):
    result = await db.execute(select(AIPrompt).where(AIPrompt.user_id == user_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_prompt(db: AsyncSession, prompt_id: UUID, user_id: UUID):
    result = await db.execute(select(AIPrompt).where(AIPrompt.id == prompt_id, AIPrompt.user_id == user_id))
    return result.scalars().first()

async def update_prompt(db: AsyncSession, prompt_id: UUID, user_id: UUID, data: PromptUpdate):
    result = await db.execute(select(AIPrompt).where(AIPrompt.id == prompt_id, AIPrompt.user_id == user_id))
    db_prompt = result.scalars().first()
    
    if not db_prompt:
        return None
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_prompt, key, value)
    
    await db.commit()
    await db.refresh(db_prompt)
    return db_prompt

async def delete_prompt(db: AsyncSession, prompt_id: UUID, user_id: UUID):
    db_product = await get_prompt(db, prompt_id, user_id)
    if db_product:
        await db.delete(db_product)
        await db.commit()
        return True
    return False
