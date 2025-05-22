# backend/src/core/dependencies.py
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from modules.user.models import User, Role
from modules.auth.utils import verify_access_token, get_token_from_cookie
from uuid import UUID

# دریافت کاربر فعلی (User)
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user_id = verify_access_token(token.replace("Bearer ", ""))
    
    # حذف تبدیل به UUID در اینجا
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user

# بررسی سطح دسترسی ادمین (Admin)
async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# بررسی سطح دسترسی بر اساس رول‌ها (Dynamic roles)
def has_permission(permission_name: str):
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        permissions = current_user.role.permissions
        if not permissions.get(permission_name, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission: {permission_name}"
            )
        return current_user
    return permission_checker
