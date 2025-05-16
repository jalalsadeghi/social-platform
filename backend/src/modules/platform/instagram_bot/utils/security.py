# backend/src/modules/platform/instagram_bot/utils/security.py
from core.config import settings
from cryptography.fernet import Fernet

fernet = Fernet(settings.SECRET_KEY.encode())

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
