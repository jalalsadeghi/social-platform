# backend/src/modules/user/schemas.py
from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime
from typing import Optional

# Base User Schema
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role_id: UUID4
    plan_id: Optional[UUID4] = None

class UserUpdate(UserBase):
    full_name: Optional[str] = None
    role_id: Optional[UUID4] = None
    plan_id: Optional[UUID4] = None

class UserInDB(UserBase):
    id: UUID4
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



