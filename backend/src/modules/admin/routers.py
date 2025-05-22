# backend/src/modules/admin/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.admin import schemas, crud
from core.dependencies import get_current_admin
from typing import List
from uuid import UUID

router = APIRouter(prefix="/admin", tags=["admin"])

# User Management
@router.get("/users", response_model=List[schemas.UserOut])
async def read_users(query: str = None, db: AsyncSession = Depends(get_db)):
    return await crud.get_users(db, query)

@router.put("/users/{user_id}", response_model=schemas.UserOut)
async def update_user(user_id: UUID, data: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Role Management
@router.get("/roles", response_model=List[schemas.RoleOut])
async def read_roles(db: AsyncSession = Depends(get_db)):
    return await crud.get_roles(db)

@router.post("/roles", response_model=schemas.RoleOut)
async def create_role(role: schemas.RoleCreate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    existing_roles = await crud.get_roles(db)
    if any(r.name == role.name for r in existing_roles):
        raise HTTPException(status_code=400, detail="Role already exists")
    return await crud.create_role(db, role)

@router.put("/roles/{role_id}", response_model=schemas.RoleOut)
async def update_role(role_id: UUID, data: schemas.RoleUpdate, db: AsyncSession = Depends(get_db)):
    role = await crud.update_role(db, role_id, data)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

# Plan Management
@router.post("/plans", response_model=schemas.PlanOut)
async def create_plan(plan: schemas.PlanCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_plan(db, plan)

@router.put("/plans/{plan_id}", response_model=schemas.PlanOut)
async def update_plan(plan_id: UUID, data: schemas.PlanUpdate, db: AsyncSession = Depends(get_db)):
    plan = await crud.update_plan(db, plan_id, data)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

# AI Prompt Management
@router.post("/prompts", response_model=schemas.PromptOut)
async def create_prompt(prompt: schemas.PromptCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_prompt(db, prompt)

@router.put("/prompts/{prompt_id}", response_model=schemas.PromptOut)
async def update_prompt(prompt_id: UUID, data: schemas.PromptUpdate, db: AsyncSession = Depends(get_db)):
    prompt = await crud.update_prompt(db, prompt_id, data)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt
