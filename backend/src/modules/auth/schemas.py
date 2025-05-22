# modules/auth/schemas.py
from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str

class OAuthUser(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RoleOut(BaseModel):
    name: str
    permissions: Dict[str, Dict[str, bool]]

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    full_name: Optional[str]
    profile_picture: Optional[str]
    role: RoleOut

    class Config:
        from_attributes = True