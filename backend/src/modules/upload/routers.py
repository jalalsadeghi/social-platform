from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from uuid import uuid4
import shutil
import os

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIRECTORY = "uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@router.post("/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    allowed_extensions = ['png', 'jpg', 'jpeg', 'avif', 'mp4', 'mov']
    file_extension = file.filename.split(".")[-1]

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    file_name = f"{uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    base_url = str(request.base_url).rstrip('/')
    file_url = f"{base_url}/{UPLOAD_DIRECTORY}/{file_name}"

    return JSONResponse(content={"url": file_url})
