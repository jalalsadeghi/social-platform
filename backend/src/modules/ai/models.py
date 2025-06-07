# src/modules/ai/models.py
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.sql import func
import enum

class Language(enum.Enum):
    English = "English"
    German = "German"
    Persian = "Persian"

class PromptType(enum.Enum):
    caption_prompt = "caption_prompt"
    comment_prompt = "comment_prompt"

class PromptSample(enum.Enum):
    English = (
        "Based on information gathered from the internet and provided to you, write an optimized and up-to-date text.\n"
        "Make sure to include the latest facts, statistics, trends, and unique, engaging insights obtained through internet research about the video's topic, so that the content you produce is credible, scientific, practical, and up-to-date.\n"
        "The tone of the narratives is always friendly, warm, optimistic, with a touch of humor, and engaging, written in a natural, conversational style.\n"
        "The narratives are crafted to build trust and connection with the audience.\n"
        "When writing the text, pay close attention to the provided internet-sourced information to ensure accuracy and freshness.\n"
        "Write only the original text and do not write any sentences or explanations before or after the text."
    )

    German = (
        "Schreiben Sie den Text optimiert und aktuell auf Grundlage der Informationen, die aus dem Internet gesammelt und Ihnen zur Verfügung gestellt wurden.\n"
        "Nutzen Sie in Ihrem Text unbedingt die neuesten Fakten, Statistiken, Trends sowie besondere und interessante Informationen, die Sie durch Ihre Internetrecherche zum Thema des Videos erhalten haben,\n"
        "damit der produzierte Inhalt glaubwürdig, wissenschaftlich, praktisch und aktuell ist.\n"
        "Der Ton der Erzählungen ist stets freundlich, herzlich, optimistisch, mit einer Prise Humor versehen und fesselnd, und wird in einem natürlichen, gesprächigen Stil verfasst.\n"
        "Die Erzählungen werden mit dem Ziel geschrieben, Vertrauen aufzubauen und eine Verbindung zum Publikum herzustellen.\n"
        "Achten Sie beim Schreiben stets auf die Aktualität und Genauigkeit der Informationen aus dem Internet.\n"
        "Schreiben Sie nur den Originaltext und schreiben Sie keine Sätze oder Erklärungen vor oder nach dem Text."
    )

    Persian = (
        "بر اساس اطلاعاتی که از اینترنت جمع آوری شده و در اختیارت قرار داده شده است، متن را بهینه و به روز می‌نویسی.\n"
        "حتماً در متن خود از جدیدترین فکت‌ها، آمارها، ترندها و نکات خاص و جذابی که از جستجوهای اینترنتی درباره موضوع ویدئو به دست می‌آوری استفاده کن تا محتوای تولیدی معتبر، علمی، کاربردی و به‌روز باشد.\n"
        "لحن روایت‌ها همیشه دوستانه، صمیمی، خوش‌بینانه، با کمی شوخ‌طبعی و جذاب بوده و به صورت مکالمه‌ای طبیعی نوشته می‌شود.\n"
        "روایت‌ها با هدف ایجاد اعتماد و ارتباط با مخاطب نوشته می‌شوند.\n"
        "در هنگام نوشتن متن به اطلاعاتی که از اینترنت دریافت شده توجه کن و مطلب را به روز بنویس."
    )
    
class AIPrompt(Base):
    __tablename__ = 'ai_prompts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    prompt_name = Column(String, unique=True, nullable=False)
    prompt_content = Column(Text, default=PromptSample.English ,nullable=False)
    language = Column(Enum(Language), default=Language.English, index=True)
    expertise = Column(String, unique=True, nullable=False)
    promt_type = Column(Enum(PromptType), default=PromptType.caption_prompt, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="ai_prompts", lazy="joined")
    social_accounts = relationship("SocialAccount", back_populates="ai_prompts", lazy="selectin")
