# backend/src/modules/platform/instagram_bot/services/secure_credentials.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.user.models import SocialAccount
from ..utils.security import encrypt, decrypt

async def store_social_credentials(
        db: AsyncSession, 
        user_id: UUID, 
        platform: str,
        lang: str,
        identifier: str, 
        credentials: dict, 
        is_oauth: bool,
        ):
    encrypted_creds = {key: encrypt(value) for key, value in credentials.items()}
    account = SocialAccount(
        user_id=user_id,
        platform=platform,
        lang=lang,
        account_identifier=identifier,
        credentials=encrypted_creds,
        is_oauth=is_oauth,
    )
    db.add(account)
    await db.commit()


async def get_social_credentials(user_id: str, db: AsyncSession, skip: int = 0, limit: int = 100):

    query = select(SocialAccount)

    if user_id:
        query = query.where(SocialAccount.user_id == user_id) 
    else:
        query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    social_accounts = result.scalars().all()

    decrypted_creds_list = []
    for account in social_accounts:
        credentials = account.credentials or {}
        decrypted_creds = {
            "id": account.id,
            "platform": account.platform.value if account.platform else None,
            "account_identifier": account.account_identifier,
            "lang": account.lang.value if account.lang else None,
            "username": decrypt(credentials.get('username', '')),
            "password": decrypt(credentials.get('password', ''))
        }

        decrypted_creds_list.append(decrypted_creds)

    return decrypted_creds_list


async def store_cookies(db: AsyncSession, user_id: UUID, platform: str, cookies: list):
    account = (await db.execute(
        select(SocialAccount).filter_by(user_id=user_id, platform=platform)
    )).scalars().first()
    if account:
        account.cookies = cookies
        await db.commit()

async def get_cookies(db: AsyncSession, user_id: UUID, platform: str):
    account = (await db.execute(
        select(SocialAccount).filter_by(user_id=user_id, platform=platform)
    )).scalars().first()
    return account.cookies if account and account.cookies else None
