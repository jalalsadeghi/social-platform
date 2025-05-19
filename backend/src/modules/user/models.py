# backend/src/modules/user/models.py
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from core.database import Base
from modules.plan.models import Plan


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    permissions = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="role", lazy="selectin")


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('plans.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    role = relationship("Role", back_populates="users", lazy="joined")
    plan = relationship("Plan", back_populates="users", lazy="joined")
    subscriptions = relationship("Subscription", back_populates="user", lazy="selectin")
    social_accounts = relationship("SocialAccount", back_populates="user", lazy="selectin")


class SocialAccount(Base):
    __tablename__ = 'social_accounts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    platform = Column(String, nullable=False, index=True)
    account_identifier = Column(String, nullable=False)
    credentials = Column(JSONB, nullable=True)
    cookies = Column(JSONB, nullable=True)
    is_oauth = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="social_accounts", lazy="joined")