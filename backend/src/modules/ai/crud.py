# backend/src/modules/ai/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.ai.models import AIPrompt, AIContent
from modules.ai.schemas import PromptCreate, PromptUpdate
import uuid

async def create_prompt(db: AsyncSession, prompt: PromptCreate):
    db_prompt = AIPrompt(**prompt.dict())
    db.add(db_prompt)
    await db.commit()
    await db.refresh(db_prompt)
    return db_prompt

async def get_prompts(db: AsyncSession):
    result = await db.execute(select(AIPrompt))
    return result.scalars().all()

async def update_prompt(db: AsyncSession, prompt_id: uuid.UUID, data: PromptUpdate):
    result = await db.execute(select(AIPrompt).where(AIPrompt.id == prompt_id))
    db_prompt = result.scalars().first()
    if not db_prompt:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_prompt, key, value)
    await db.commit()
    await db.refresh(db_prompt)
    return db_prompt
    