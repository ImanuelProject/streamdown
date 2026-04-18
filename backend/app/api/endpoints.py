import os
import uuid
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from app.schemas.audio import PreviewRequest, PreviewResponse, DownloadRequest, DownloadResponse, StatusResponse
from app.services.downloader import get_video_info
from app.services.redis_state import set_task_status, get_task_status
from redis.asyncio import Redis
from app.core.config import settings

router = APIRouter()

@router.post("/preview", response_model=PreviewResponse)
async def preview_url(request: PreviewRequest):
    try:
        info = get_video_info(request.url)
        return PreviewResponse(
            is_valid=True,
            title=info.get("title"),
            thumbnail=info.get("thumbnail"),
            is_playlist=info.get("is_playlist", False),
            items_count=info.get("items_count", 1)
        )
    except Exception as e:
        return PreviewResponse(is_valid=False, error_message=str(e))

@router.post("/download", response_model=DownloadResponse)
async def start_download(request: DownloadRequest, req: Request):
    task_id = str(uuid.uuid4())
    
    # 1. Daftarkan tugas ke antrean ARQ (Background Worker)
    arq_pool = req.app.state.arq_pool
    await arq_pool.enqueue_job("execute_download", request.url, request.is_playlist, task_id)
    
    # 2. Inisialisasi status pertama ke Redis menjadi QUEUED
    redis_client = Redis.from_url(settings.REDIS_URL)
    await set_task_status(redis_client, task_id, "QUEUED")
    await redis_client.aclose()
    
    return DownloadResponse(
        task_id=task_id,
        message="Download telah dimasukkan ke dalam antrean (Queue)"
    )

@router.get("/status/{task_id}", response_model=StatusResponse)
async def get_status(task_id: str):
    redis_client = Redis.from_url(settings.REDIS_URL)
    status_data = await get_task_status(redis_client, task_id)
    await redis_client.aclose()
    
    if not status_data:
        raise HTTPException(status_code=404, detail="Task ID tidak ditemukan")
        
    return StatusResponse(**status_data)

@router.get("/stream/{task_id}")
async def stream_file(task_id: str):
    redis_client = Redis.from_url(settings.REDIS_URL)
    status_data = await get_task_status(redis_client, task_id)
    await redis_client.aclose()
    
    if not status_data or status_data.get("status") != "COMPLETED":
        raise HTTPException(status_code=400, detail="File belum selesai diproses")
        
    file_path = status_data.get("result_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File tidak ditemukan di sistem")
        
    filename = os.path.basename(file_path)
    return FileResponse(file_path, filename=filename)
