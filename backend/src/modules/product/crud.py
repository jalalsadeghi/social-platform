# src/product/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from .models import Product, Media
from .schemas import ProductCreate, ProductUpdate
import uuid
from uuid import UUID

async def get_products(db: AsyncSession, user_id: uuid.UUID, skip=0, limit=30):
    result = await db.execute(select(Product).where(Product.user_id == user_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_product(db: AsyncSession, product_id: uuid.UUID, user_id: uuid.UUID):
    result = await db.execute(select(Product).where(Product.id == product_id, Product.user_id == user_id))
    return result.scalars().first()

async def create_product(db: AsyncSession, product: ProductCreate, user_id: uuid.UUID):
    product_data = product.dict(exclude={"media"})
    if product_data.get("product_url"):
        product_data["product_url"] = str(product_data["product_url"])

    db_product = Product(**product_data, user_id=user_id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    for media_item in product.media:
        media_data = media_item.dict()
        media_data["media_url"] = str(media_data["media_url"]) 
        db_media = Media(**media_data, product_id=db_product.id)
        db.add(db_media)

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

async def update_product(db: AsyncSession, product_id: UUID, product_update: ProductUpdate, user_id: UUID):
    db_product = await get_product(db, product_id, user_id)
    if not db_product:
        return None

    update_data = product_update.dict(exclude_unset=True, exclude={"media"})

    if "product_url" in update_data:
        update_data["product_url"] = str(update_data["product_url"])

    for key, value in update_data.items():
        setattr(db_product, key, value)

    if product_update.media is not None:
        await db.execute(delete(Media).where(Media.product_id == db_product.id))

        media_instances = [
            Media(
                media_url=str(item.media_url), 
                media_type=item.media_type,
                product_id=db_product.id
            ) 
            for item in product_update.media
        ]
        db.add_all(media_instances)

    await db.commit()
    await db.refresh(db_product)
    return db_product

