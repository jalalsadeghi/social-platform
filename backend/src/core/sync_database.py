# core/sync_database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

SYNC_DATABASE_URL = settings.SYNC_DATABASE_URL  # مثلا "postgresql://user:pass@host/db"

engine_sync = create_engine(SYNC_DATABASE_URL)
SyncSession = sessionmaker(bind=engine_sync, autocommit=False, autoflush=False)
