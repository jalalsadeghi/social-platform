# backend/tests/test_auth.py

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.database import Base, get_db
from src.main import app
import os

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
TestingSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # ایجاد پایگاه داده
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # حذف پایگاه داده
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_register_and_login_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword123"
        }

        response = await ac.post("/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        login_data = {
            "email": "testuser@example.com",
            "password": "securepassword123"
        }

        response = await ac.post("/auth/login", json=login_data)
        assert response.status_code == 200
        login_response_data = response.json()
        assert "access_token" in login_response_data
        assert login_response_data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_with_wrong_credentials():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        wrong_login_data = {
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }

        response = await ac.post("/auth/login", json=wrong_login_data)
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
