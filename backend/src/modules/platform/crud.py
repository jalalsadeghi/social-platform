# background/src/modules/platform/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.future import select
from .models import Platform
from .schemas import PlatformUpdate
from core.security import encrypt, decrypt
from uuid import UUID
import json


def parse_netscape_cookies(cookie_str: str):
    cookies = []
    for line in cookie_str.strip().split("\n"):
        if line.startswith('#') or not line.strip():
            continue
        domain, _, path, secure, expires, name, value = line.strip().split("\t")
        cookies.append({
            "domain": domain,
            "path": path,
            "name": name,
            "value": value,
            "secure": secure.lower() == "true",
            "expires": int(expires)
        })
    return cookies


async def create_platform(
        db: AsyncSession, 
        user_id: UUID, 
        platform: str,
        identifier: str, 
        credentials: dict, 
        cookies:str,
        is_oauth: bool,
        ):
    encrypted_creds = {key: encrypt(value) for key, value in credentials.items()}
    cookie_list = parse_netscape_cookies(cookies)
    account = Platform(
        user_id=user_id,
        platform=platform,
        account_identifier=identifier,
        credentials=encrypted_creds,
        cookies=cookie_list,
        is_oauth=is_oauth,
    )
    db.add(account)
    await db.commit()

async def get_platforms(user_id: UUID, db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(Platform).where(Platform.user_id == user_id).offset(skip).limit(limit)

    result = await db.execute(query)
    platforms = result.scalars().all()

    decrypted_creds_list = []
    for platform in platforms:
        credentials = platform.credentials or {}
        decrypted_creds = {
            "id": platform.id,
            "user_id": platform.user_id,
            "platform": platform.platform,
            "account_identifier": platform.account_identifier,
            "username": decrypt(credentials.get('username', '')),
            "password": decrypt(credentials.get('password', '')),
            "cookies": json.dumps(platform.cookies) if platform.cookies else None,
            "updated_at": platform.updated_at,
            "created_at": platform.created_at
        }
        decrypted_creds_list.append(decrypted_creds)

    return decrypted_creds_list


async def get_platform(db: AsyncSession, platform_id: UUID, user_id: UUID):
    result = await db.execute(
        select(Platform).where(Platform.id == platform_id, Platform.user_id == user_id)
    )
    platform = result.scalars().first()

    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found."
        )

    credentials = platform.credentials or {}

    decrypted_creds = {
        "id": platform.id,
        "user_id": platform.user_id,
        "platform": platform.platform.value,  # حتماً باید مقدار Enum را برگردانید
        "account_identifier": platform.account_identifier,
        "username": decrypt(credentials.get('username', '')),
        "password": decrypt(credentials.get('password', '')),
        "cookies": json.dumps(platform.cookies) if platform.cookies else None,
        "updated_at": platform.updated_at,
        "created_at": platform.created_at
    }

    return decrypted_creds

async def update_platforms(db: AsyncSession, platforms_id: UUID, user_id: UUID, data: PlatformUpdate):
    result = await db.execute(
        select(Platform).where(
            Platform.id == platforms_id,
            Platform.user_id == user_id
        )
    )
    db_platform = result.scalars().first()

    if not db_platform:
        return None

    credentials = db_platform.credentials or {}

    update_data = data.dict(exclude_unset=True)

    if 'password' in update_data and update_data['password']:
        credentials['password'] = encrypt(update_data['password'])

    if 'cookies' in update_data:
        cookies_str = json.loads(update_data['cookies'])
        cookie_list = parse_netscape_cookies(cookies_str)
        db_platform.cookies = cookie_list

    if 'platform' in update_data:
        db_platform.platform = update_data['platform']

    db_platform.credentials = credentials

    await db.commit()
    await db.refresh(db_platform)

    response_data = {
        "id": db_platform.id,
        "user_id": db_platform.user_id,
        "platform": db_platform.platform,
        "account_identifier": db_platform.account_identifier,
        "username": decrypt(credentials.get('username', '')),
        "password": decrypt(credentials.get('password', '')),
        "cookies": json.dumps(db_platform.cookies),
        "created_at": db_platform.created_at,
        "updated_at": db_platform.updated_at
    }

    return response_data



async def delete_platform(db: AsyncSession, platform_id: UUID, user_id: UUID):
    result = await db.execute(select(Platform).where(Platform.id == platform_id, Platform.user_id == user_id))
    db_platform = result.scalars().first()
    if db_platform:
        await db.delete(db_platform)
        await db.commit()
        return True
    return False
