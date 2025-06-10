# backend/src/modules/ai/routers.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.ai import schemas, crud
from .models import Language, PromptSample, PromptType
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
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    prompts = await crud.get_prompts(db, user_id=current_user.id, skip=skip, limit=limit)
    return prompts if prompts else []
    

@router.get("/{prompt_id}", response_model=schemas.PromptOut)
async def read_prompts(
    prompt_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prompt = await crud.get_prompt(db, prompt_id, user_id=current_user.id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

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

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_prompt(db, prompt_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found or Unauthorized")
    return {"detail": "Prompt deleted successfully"}


@router.get("/language/", response_model=List[schemas.LanguageBase])
async def read_language():
    languages = [{"name": lang.name, "value": lang.value} for lang in Language]
    return languages

@router.get("/parompt_sample/", response_model=List[schemas.PromptSampleBase])
async def read_parompt_sample():
    prompts = [{"name": prompt.name, "value": prompt.value} for prompt in PromptSample]
    return prompts
