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
"Write a clear, up-to-date, and engaging script based on the information collected from the internet and provided to you. \
Be sure to include the latest facts, statistics, trends, and unique insights relevant to the video's topic to make the content informative, credible, and appealing. \
The tone should always be friendly, conversational, upbeat, and slightly humorous—creating a natural and relatable narrative style. \
The goal is not only to inform but also to build a sense of trust and emotional connection with the audience, while actively encouraging interaction (such as asking for opinions or prompting them to share their experiences). \
If the video’s length allows, include a short question or thought-provoking comment at the end of the script to spark curiosity and increase engagement (e.g., “Would you buy this?” or “What do you think?”). \
Only write the script itself—no extra explanations or additional text outside the narration."
    )

    German = (
"Erstellen Sie einen klaren, aktuellen und ansprechenden Text auf Grundlage der bereitgestellten Informationen aus dem Internet. \
Integrieren Sie unbedingt die neuesten Fakten, Statistiken, Trends und besondere, spannende Erkenntnisse zum Thema des Videos, um den Inhalt glaubwürdig, informativ und relevant zu gestalten. \
Der Erzählstil sollte stets freundlich, locker, optimistisch und mit einer Prise Humor versehen sein, so entsteht eine natürliche, gesprächige Atmosphäre. \
Ziel der Erzählung ist es nicht nur zu informieren, sondern auch Vertrauen aufzubauen und eine emotionale Verbindung zum Publikum herzustellen, und gleichzeitig aktiv zur Interaktion anzuregen (z.B. durch Fragen oder Einladungen, eigene Erfahrungen zu teilen). \
Wenn die Videolänge es zulässt, fügen Sie am Ende eine kurze Frage oder einen neugierig machenden Kommentar ein, um die Aufmerksamkeit zu steigern und mehr Reaktionen zu fördern (z.B.: „Würdet ihr das kaufen?“ oder „Was denkt ihr?“). \
Schreiben Sie ausschließlich den Text der Erzählung, keine Erklärungen oder zusätzlichen Hinweise davor oder danach."
    )

    Persian = (
"بر اساس اطلاعات به‌روز و معتبر جمع‌آوری‌شده از اینترنت، متنی بهینه و هماهنگ با موضوع ویدئو تهیه کن. \
در متن خود حتماً از جدیدترین فکت‌ها، آمارها، ترندها و نکات خاص و جذابی که از جستجوهای آنلاین درباره محصول یا موضوع ویدئو به دست می‌آوری استفاده کن تا محتوا هم علمی و کاربردی باشد و هم برای مخاطب جذاب و قابل اعتماد. \
لحن روایت باید همیشه صمیمی، دوستانه، خوش‌بینانه و کمی شوخ‌طبعانه باشد، طوری که حس یک گفت‌و‌گوی طبیعی و بی‌واسطه با مخاطب را القا کند. \
هدف روایت، علاوه بر اطلاع‌رسانی، ایجاد حس نزدیکی و دعوت به تعامل فعال با مخاطب است، مثلاً از او خواسته شود تجربه‌اش را بگوید، نظرش را بنویسد یا سوالی کوتاه در ذهنش شکل بگیرد. \
در پایان متن، اگر زمان اجازه می‌دهد، یک سوال ساده یا جمله‌ای تحریک‌کننده کنجکاوی قرار بده\
(مثل: به نظرتون این ارزش خرید داره؟ یا شما بین این و مدل قبلی کدومو انتخاب می‌کنید؟) تا مخاطب بیشتر با محتوا درگیر شود و تمایل به کامنت گذاشتن یا لایک کردن داشته باشد."
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