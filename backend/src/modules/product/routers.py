# src/modules/product/routers.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from modules.product import crud, schemas
from core.database import get_db
from modules.auth.utils import verify_access_token
from fastapi import Request

router = APIRouter(prefix="/products", tags=["products"])

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_id = verify_access_token(token.replace("Bearer ", ""))
    return user_id

@router.get("/", response_model=List[schemas.ProductOut])
async def read_products(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user(request)
    products = await crud.get_products(db, user_id=user_id, skip=skip, limit=limit)
    return products

@router.get("/{product_id}", response_model=schemas.ProductOut)
async def read_product(product_id: UUID, request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user(request)
    product = await crud.get_product(db, product_id, user_id=user_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=schemas.ProductOut)
async def create_product(
    product: schemas.ProductCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user(request)
    return await crud.create_product(db, product, user_id=user_id)

@router.put("/{product_id}", response_model=schemas.ProductOut)
async def update_product(
    product_id: UUID,
    product_update: schemas.ProductUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user(request)
    product = await crud.update_product(db, product_id, product_update, user_id=user_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or Unauthorized")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: UUID, request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user(request)
    success = await crud.delete_product(db, product_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found or Unauthorized")
    return {"detail": "Product deleted successfully"}
