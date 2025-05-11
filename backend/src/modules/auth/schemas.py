# modules/auth/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

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