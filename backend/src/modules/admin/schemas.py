# backend/src/modules/admin/schemas.py
from pydantic import BaseModel, UUID4, EmailStr
from typing import Optional

class UserOut(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    full_name: Optional[str]
    role_id: UUID4

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    full_name: Optional[str]
    role_id: Optional[UUID4]

class RoleOut(BaseModel):
    id: UUID4
    name: str
    permissions: dict

class RoleUpdate(BaseModel):
    name: Optional[str]
    permissions: Optional[dict]

class PlanOut(BaseModel):
    id: UUID4
    name: str
    price: float
    features: dict

class PlanCreate(BaseModel):
    name: str
    price: float
    features: dict

class PlanUpdate(BaseModel):
    name: Optional[str]
    price: Optional[float]
    features: Optional[dict]

class PromptOut(BaseModel):
    id: UUID4
    prompt_name: str
    prompt_content: str
    prompt_type: str

class PromptCreate(BaseModel):
    prompt_name: str
    prompt_content: str
    prompt_type: str

class PromptUpdate(BaseModel):
    prompt_name: Optional[str]
    prompt_content: Optional[str]
    prompt_type: Optional[str]
