# src/modules/product/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from datetime import datetime, timezone
from .models import Product, Media, QueueStatus
from .schemas import ProductCreate, ProductUpdate
from modules.platform.models import Platform
import uuid
from uuid import UUID
from typing import Optional

async def get_products(db: AsyncSession, user_id: uuid.UUID, skip=0, limit=30):
    result = await db.execute(select(Product).where(Product.user_id == user_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_product(db: AsyncSession, product_id: uuid.UUID, user_id: uuid.UUID):
    result = await db.execute(select(Product).where(Product.id == product_id, Product.user_id == user_id))
    return result.scalars().first()

async def print(product: ProductCreate):
    # product_data = product.dict(exclude={"media"})
    print(f"print product_data: {product.media}")
    return product.media

async def create_product(db: AsyncSession, product: ProductCreate, user_id: uuid.UUID):
    product_data = product.dict(exclude={"media", "social_account_ids"})
    db_product = Product(**product_data, user_id=user_id)
    
    # Fetch social accounts
    if product.social_account_ids:
        social_accounts = (await db.execute(
            select(Platform).where(Platform.id.in_(product.social_account_ids), Platform.user_id == user_id)
        )).scalars().all()
        db_product.social_accounts = social_accounts

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    
    # Handle media
    for media_item in product.media:
        db_media = Media(**media_item.dict(), product_id=db_product.id)
        db.add(db_media)

    await db.commit()
    await db.refresh(db_product)
    return db_product

async def update_product(db: AsyncSession, product_id: UUID, product_update: ProductUpdate, user_id: UUID):
    db_product = await get_product(db, product_id, user_id)
    if not db_product:
        return None

    update_data = product_update.dict(exclude_unset=True, exclude={"media", "social_account_ids"})

    for key, value in update_data.items():
        setattr(db_product, key, value)

    if product_update.social_account_ids is not None:
        social_accounts = (await db.execute(
            select(Platform).where(Platform.id.in_(product_update.social_account_ids), Platform.user_id == user_id)
        )).scalars().all()
        db_product.social_accounts = social_accounts

    await db.commit()
    await db.refresh(db_product)
    return db_product

async def delete_product(db: AsyncSession, product_id: uuid.UUID, user_id: uuid.UUID):
    db_product = await get_product(db, product_id, user_id)
    if db_product:
        await db.delete(db_product)
        await db.commit()
        return True
    return False

async def get_scheduled_products(db: AsyncSession, user_id: uuid.UUID, limit: int = 10):
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Product)
        .where(Product.user_id == user_id)
        .where(Product.status == QueueStatus.ready)
        .where(Product.scheduled_time <= now)
        .order_by(Product.priority.desc(), Product.scheduled_time.asc())
        .limit(limit)
    )
    return result.scalars().all()

async def update_product_status(db: AsyncSession, product_id: UUID, user_id: UUID, status: QueueStatus):
    db_product = await get_product(db, product_id, user_id)
    if not db_product:
        return None
    
    db_product.status = status
    await db.commit()
    await db.refresh(db_product)
    return db_product
