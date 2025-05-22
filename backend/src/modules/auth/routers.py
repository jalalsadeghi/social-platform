# modules/auth/routers.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.responses import RedirectResponse
from modules.auth.oauth import get_instagram_user
from modules.auth import oauth, utils, schemas, crud
from modules.auth.utils import get_token_from_cookie, verify_access_token
from modules.user.models import User
from core.database import get_db
from datetime import timedelta
from modules.auth.utils import create_access_token
from core.config import settings
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/auth/register", response_model=schemas.Token)
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

@router.post("/login")
async def login(user: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await crud.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(db_user.id), "username": db_user.username, "email": db_user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response = JSONResponse(content={
        "user": {
            "id": str(db_user.id),
            "username": db_user.username,
            "email": db_user.email,
        },
        "message": "Login successful"
    })

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # همچنان امن
        secure=True,
        samesite='strict',
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response

@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Successfully logged out"})
    response.delete_cookie("access_token", path="/", secure=True, httponly=True, samesite='strict')
    return response

@router.get("/me", response_model=schemas.UserOut)
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    token = get_token_from_cookie(request)
    user_id = verify_access_token(token)

    result = await db.execute(
        select(User).options(joinedload(User.role)).where(User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user

@router.get("/instagram/callback", response_model=schemas.Token)
async def instagram_auth_callback(code: str, db: AsyncSession = Depends(get_db)):
    insta_data = await get_instagram_user(code)
    oauth_user = schemas.OAuthUser(
        email=f"{insta_data['instagram_user_id']}@instagram.com",
        username=insta_data['username'],
        full_name=insta_data['username'],
        profile_picture=""
    )

    user = await crud.get_or_create_user(db, oauth_user)
    await db.commit()
    await db.refresh(user)

    access_token = crud.create_access_token(data={"sub": str(user.id)})

    frontend_redirect_url = f"{settings.FRONTEND_URL}/instagram-success?token={access_token}"
    
    return RedirectResponse(frontend_redirect_url)


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
