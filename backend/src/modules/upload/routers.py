# backend/src/modules/upload/routers.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from uuid import uuid4
import shutil
import os
from core.config import settings

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIRECTORY = settings.UPLOAD_DIRECTORY

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

ALLOWED_CONTENT_TYPES = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'image/jpg': 'jpg',
    'image/avif': 'avif',
    'image/webp': 'webp',
    'image/svg+xml': 'svg',
    'video/mp4': 'mp4',
    'video/quicktime': 'mov'
}

@router.post("/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    content_type = file.content_type

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    file_extension = ALLOWED_CONTENT_TYPES[content_type]
    file_name = f"{uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # base_url = str(request.base_url).rstrip('/')
    file_url = f"{UPLOAD_DIRECTORY}/{file_name}"

    return JSONResponse(content={"url": file_url, "local_path": file_path})
