# backend/src/modules/ai/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.ai.models import AIPrompt
from modules.ai.schemas import PromptCreate, PromptUpdate
from uuid import UUID
from typing import List
from openai import OpenAI
from core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
openai_model = settings.OPENAI_MODEL

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
    db_platform = await get_prompt(db, prompt_id, user_id)
    if db_platform:
        await db.delete(db_platform)
        await db.commit()
        return True
    return False

async def generate_ai_content(messages: list, openai_model: str, int_max_tokens: int = 1500):
    """Generate content from AI based on provided messages. Adapts parameters based on model capabilities."""

    restricted_models = {
        "gpt-4o-mini-search-preview",
    }

    request_args = {
        "model": openai_model,
        "messages": messages
    }

    if openai_model not in restricted_models:
        request_args.update({
            "temperature": 0.3,
            "max_tokens": int_max_tokens
        })

    try:
        ai_response = client.chat.completions.create(**request_args)
        return ai_response.choices[0].message.content if ai_response.choices else ""
    except Exception as e:
        print(f"[AI Error] {e}")
        return ""

