# src/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_recycle=1800,
    pool_timeout=30,
    echo=False
)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session

# from modules.product.models import Product, Media, InstagramStats
from modules.user.models import User, Role
from modules.plan.models import Plan, Subscription
# from modules.platform.instagram.models import InstagramIntegration, InstagramActionLog
from modules.platform.instagram_bot.models import InstagramBotReport
from modules.post.models import Post, Comment
from modules.reports.models import PerformanceReport
from modules.payment.models import Payment
from modules.logs.models import AppLog
from modules.ai.models import AIPrompt
from modules.platform.models import Platform


