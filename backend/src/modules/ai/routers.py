# backend/src/modules/ai/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.ai import schemas, crud
from typing import List
from uuid import UUID

router = APIRouter(prefix="/ai-prompts", tags=["AI Prompts"])

@router.post("/", response_model=schemas.PromptOut)
async def create_prompt(prompt: schemas.PromptCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_prompt(db, prompt)

@router.get("/", response_model=List[schemas.PromptOut])
async def read_prompts(db: AsyncSession = Depends(get_db)):
    return await crud.get_prompts(db)

@router.put("/{prompt_id}", response_model=schemas.PromptOut)
async def update_prompt(prompt_id: UUID, prompt: schemas.PromptUpdate, db: AsyncSession = Depends(get_db)):
    updated_prompt = await crud.update_prompt(db, prompt_id, prompt)
    if not updated_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt
