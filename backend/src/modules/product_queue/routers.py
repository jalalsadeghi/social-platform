from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.product_queue import schemas, crud
from typing import List
from uuid import UUID

router = APIRouter(prefix="/product-queues", tags=["product-queues"])

@router.post("/", response_model=schemas.ProductQueueOut)
async def create_queue(queue: schemas.ProductQueueCreate, user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await crud.create_product_queue(db, user_id, queue)

@router.get("/{queue_id}", response_model=schemas.ProductQueueOut)
async def read_queue(queue_id: UUID, db: AsyncSession = Depends(get_db)):
    queue = await crud.get_product_queue(db, queue_id)
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    return queue

@router.put("/{queue_id}", response_model=schemas.ProductQueueOut)
async def update_queue(queue_id: UUID, queue: schemas.ProductQueueUpdate, db: AsyncSession = Depends(get_db)):
    updated_queue = await crud.update_product_queue(db, queue_id, queue)
    if not updated_queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    return updated_queue

@router.get("/", response_model=List[schemas.ProductQueueOut])
async def read_queues(user_id: UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_product_queues(db, user_id, skip, limit)
