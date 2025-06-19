# core/sync_database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

SYNC_DATABASE_URL = settings.SYNC_DATABASE_URL  # مثلا "postgresql://user:pass@host/db"

engine_sync = create_engine(SYNC_DATABASE_URL)
SyncSession = sessionmaker(bind=engine_sync, autocommit=False, autoflush=False)

from modules.product.models import Product, Media, InstagramStats
from modules.user.models import User, Role
from modules.plan.models import Plan, Subscription
from modules.platform.instagram.models import InstagramIntegration, InstagramActionLog
from modules.platform.instagram_bot.models import InstagramBotReport
from modules.post.models import Post, Comment
from modules.reports.models import PerformanceReport
from modules.payment.models import Payment
from modules.logs.models import AppLog
from modules.ai.models import AIPrompt
from modules.platform.models import Platform
from modules.content.models import Content, MusicFile, ContentPlatform