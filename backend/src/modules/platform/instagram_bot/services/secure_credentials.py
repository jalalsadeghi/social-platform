# # backend/src/modules/platform/instagram_bot/services/secure_credentials.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.user.models import SocialAccount
from ..utils.security import encrypt, decrypt

async def store_social_credentials(db: AsyncSession, user_id: UUID, platform: str, identifier: str, credentials: dict, is_oauth: bool):
    encrypted_creds = {key: encrypt(value) for key, value in credentials.items()}

    account = SocialAccount(
        user_id=user_id,
        platform=platform,
        account_identifier=identifier,
        credentials=encrypted_creds,
        is_oauth=is_oauth
    )
    db.add(account)
    await db.commit()

async def get_social_credentials(db: AsyncSession, user_id: UUID, platform: str):
    result = await db.execute(select(SocialAccount).filter_by(user_id=user_id, platform=platform))
    account = result.scalars().first()
    if not account:
        raise ValueError("Credentials not found.")

    decrypted_creds = {key: decrypt(value) for key, value in account.credentials.items()}
    return decrypted_creds
