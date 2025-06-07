# backend/src/modules/ai/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.ai import schemas, crud
from core.dependencies import get_current_user
from typing import List
from uuid import UUID

router = APIRouter(prefix="/ai-prompts", tags=["AI Prompts"])

@router.post("/", response_model=schemas.PromptOut)
async def create_prompt(
    prompt: schemas.PromptCreate, 
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)):
    try:
        result = await crud.create_prompt(db, prompt, user_id=current_user.id)
        print("Created prompt:", result.id)
        return result
    except Exception as e:
        print("Error creating prompt:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[schemas.PromptOut])
async def read_prompts(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)):

    return await crud.get_prompts(db, current_user.id)

@router.get("/{prompt_id}", response_model=List[schemas.PromptOut])
async def read_prompts_by_id(
    prompt_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ):

    return await crud.get_prompts_by_id(db, prompt_id, current_user.id)

@router.put("/{prompt_id}", response_model=schemas.PromptOut)
async def update_prompt(
    prompt_id: UUID, 
    prompt: schemas.PromptUpdate, 
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated_prompt = await crud.update_prompt(db, prompt_id, current_user.id, prompt)
    if not updated_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt
