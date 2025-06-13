from core.database import Base

# از همه ماژول‌ها مدل‌ها را اینجا وارد کنید
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
from modules.content.models import Content, MusicFile

__all__ = [
    "Product", "Media", "InstagramStats",
    "User", "Role",
    "Plan", "Subscription",
    "InstagramIntegration", "InstagramActionLog",
    "InstagramBotReport",
    "Post", "Comment",
    "PerformanceReport",
    "Payment",
    "AppLog",
    "AIPrompt",
    "Platform",
    "Content", "MusicFile"
]
