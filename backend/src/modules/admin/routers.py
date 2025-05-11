# routers.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from modules.admin import schemas, crud

router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    db = get_db()
    try:
        yield db
    finally:
        db.close()

# User Management
@router.get("/users", response_model=List[schemas.UserOut])
def read_users(query: str = None, db: Session = Depends(get_db)):
    return crud.get_users(db, query)

@router.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id, data: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(db, user_id, data)

# Role Management
@router.get("/roles", response_model=List[schemas.RoleOut])
def read_roles(db: Session = Depends(get_db)):
    return crud.get_roles(db)

@router.put("/roles/{role_id}", response_model=schemas.RoleOut)
def update_role(role_id, data: schemas.RoleUpdate, db: Session = Depends(get_db)):
    return crud.update_role(db, role_id, data)

# Plan Management
@router.post("/plans", response_model=schemas.PlanOut)
def create_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    return crud.create_plan(db, plan)

@router.put("/plans/{plan_id}", response_model=schemas.PlanOut)
def update_plan(plan_id, data: schemas.PlanUpdate, db: Session = Depends(get_db)):
    return crud.update_plan(db, plan_id, data)

# AI Prompt Management
@router.post("/prompts", response_model=schemas.PromptOut)
def create_prompt(prompt: schemas.PromptCreate, db: Session = Depends(get_db)):
    return crud.create_prompt(db, prompt)

@router.put("/prompts/{prompt_id}", response_model=schemas.PromptOut)
def update_prompt(prompt_id, data: schemas.PromptUpdate, db: Session = Depends(get_db)):
    return crud.update_prompt(db, prompt_id, data)