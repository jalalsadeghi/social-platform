# backend/src/modules/ai/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.ai.models import AIPrompt
from modules.ai.schemas import PromptCreate, PromptUpdate
from uuid import UUID

async def create_prompt(db: AsyncSession, prompt: PromptCreate, user_id=UUID):
    db_prompt = AIPrompt(**prompt.dict(), user_id=user_id)
    db.add(db_prompt)
    await db.commit()
    await db.refresh(db_prompt)
    return db_prompt

async def get_prompts(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(AIPrompt).where(AIPrompt.user_id == user_id))
    return result.scalars().all()

async def get_prompts_by_id(db: AsyncSession, prompt_id: UUID, user_id: UUID):
    result = await db.execute(select(AIPrompt).where(AIPrompt.id == prompt_id, AIPrompt.user_id == user_id))
    return result.scalars().all()

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
    