# backend/src/modules/product/routers.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from modules.product import crud, schemas
from core.database import get_db
from core.dependencies import get_current_user
from .scraper import scrape_and_extract

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[schemas.ProductOut])
async def read_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    products = await crud.get_products(db, user_id=current_user.id, skip=skip, limit=limit)
    return products

@router.get("/{product_id}", response_model=schemas.ProductOut)
async def read_product(
    product_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    product = await crud.get_product(db, product_id, user_id=current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=schemas.ProductOut)
async def create_product(
    product: schemas.ProductCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_product(db, product, user_id=current_user.id)

@router.put("/{product_id}", response_model=schemas.ProductOut)
async def update_product(
    product_id: UUID,
    product_update: schemas.ProductUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    product = await crud.update_product(db, product_id, product_update, user_id=current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or Unauthorized")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_product(db, product_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found or Unauthorized")
    return {"detail": "Product deleted successfully"}

@router.post("/scrape/")
async def scrape_product(
    url: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    base_url = str(request.base_url).rstrip('/')
    try:
        result = await scrape_and_extract(url, base_url)
        return result
    except Exception as e:
        print(f"Scraping error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
