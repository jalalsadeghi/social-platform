# modules/auth/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.user.models import User, Role
from modules.auth.schemas import OAuthUser, UserCreate
import uuid
from modules.auth.utils import get_password_hash, verify_password


async def get_or_create_user(db: AsyncSession, oauth_user: OAuthUser):
    result = await db.execute(select(User).where(User.email == oauth_user.email))
    user = result.scalars().first()

    if user:
        return user

    result = await db.execute(select(Role).where(Role.name == "user"))
    default_role = result.scalars().first()

    user = User(
        id=uuid.uuid4(),
        username=oauth_user.username,
        email=oauth_user.email,
        full_name=oauth_user.full_name,
        profile_picture=oauth_user.profile_picture,
        hashed_password="",
        role_id=default_role.id
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)

    result = await db.execute(select(Role).where(Role.name == "user"))
    default_role = result.scalars().first()

    db_user = User(
        id=uuid.uuid4(),
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role_id=default_role.id
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user or not verify_password(password, user.hashed_password):
        return None

    return user