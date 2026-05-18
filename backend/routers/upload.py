import uuid
import os
import asyncio
import aiofiles

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from config import get_settings
from pipeline_executor import execute_pipeline, jobs

router = APIRouter()
settings = get_settings()

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json", ".parquet"}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB


@router.post("/upload")
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    job_id = str(uuid.uuid4())
    file_path = os.path.join(settings.DATA_DIR, f"{job_id}{ext}")

    # Stream write to disk
    async with aiofiles.open(file_path, "wb") as out:
        while chunk := await file.read(1024 * 64):
            await out.write(chunk)

    # Launch pipeline in background
    background_tasks.add_task(execute_pipeline, job_id, file_path)

    return JSONResponse(
        status_code=202,
        content={
            "job_id": job_id,
            "message": "Dataset uploaded. Pipeline started.",
            "filename": file.filename,
        },
    )
