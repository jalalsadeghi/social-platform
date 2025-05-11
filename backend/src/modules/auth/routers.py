# modules/auth/routers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.auth import oauth, utils, schemas, crud
from modules.user.models import User
from core.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.Token)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await crud.create_user(db, user)
    await db.commit()
    await db.refresh(user)

    access_token = utils.create_access_token(data={"sub": str(user.id)})
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=schemas.Token)
async def login(user: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await crud.authenticate_user(db, user.email, user.password)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = utils.create_access_token(data={"sub": str(db_user.id)})
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/instagram/callback", response_model=schemas.Token)
async def instagram_auth_callback(code: str, db: AsyncSession = Depends(get_db)):
    insta_data = await oauth.get_instagram_user(code)
    oauth_user = schemas.OAuthUser(
        email=f"{insta_data['user_id']}@instagram.com",
        username=insta_data['username'],
        full_name=insta_data['username'],
        profile_picture=""
    )

    user = await crud.get_or_create_user(db, oauth_user)
    await db.commit()
    await db.refresh(user)

    access_token = utils.create_access_token(data={"sub": str(user.id)})
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/google/callback", response_model=schemas.Token)
async def google_auth_callback(code: str, db: AsyncSession = Depends(get_db)):
    google_data = await oauth.get_google_user(code)
    oauth_user = schemas.OAuthUser(
        email=google_data['email'],
        username=google_data['email'].split('@')[0],
        full_name=google_data.get('name'),
        profile_picture=google_data.get('picture')
    )

    user = await crud.get_or_create_user(db, oauth_user)
    await db.commit()
    await db.refresh(user)

    access_token = utils.create_access_token(data={"sub": str(user.id)})
    return schemas.Token(access_token=access_token, token_type="bearer")