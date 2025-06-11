# src/modules/product/models.py
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from sqlalchemy import Table
import enum

class QueueStatusProduct(enum.Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    posted = "posted"
    failed = "failed"

# product_social_accounts = Table(
#     "product_social_accounts",
#     Base.metadata,
#     Column("product_id", UUID(as_uuid=True), ForeignKey("product.id", ondelete="CASCADE"), primary_key=True),
#     Column("social_account_id", UUID(as_uuid=True), ForeignKey("social_accounts.id", ondelete="CASCADE"), primary_key=True)
# )

class Product(Base):
    __tablename__ = 'product'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    product_url = Column(String, nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    ai_content = Column(Text, nullable=True)
    status = Column(Enum(QueueStatusProduct), default=QueueStatusProduct.pending, index=True)
    priority = Column(Integer, default=0)
    scheduled_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # platform = relationship("Platform", secondary=product_social_accounts, lazy="selectin")
    user = relationship("User", backref="products", lazy="selectin")
    media = relationship("Media", cascade="all, delete-orphan", back_populates="product", lazy="selectin")
    instagram_stats = relationship("InstagramStats", cascade="all, delete-orphan", back_populates="product", lazy="selectin", uselist=False) 

class Media(Base):
    __tablename__ = 'media'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    media_url = Column(String, nullable=False)
    media_type = Column(Enum('image', 'video', name='media_type_enum'), nullable=False)
    local_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="media", lazy="selectin")

class InstagramStats(Base):
    __tablename__ = 'instagram_stats'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('product.id', ondelete='CASCADE'), unique=True, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    last_checked_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="instagram_stats", lazy="selectin")


