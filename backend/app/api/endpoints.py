from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DownloadRequest(BaseModel):
    url: str

@router.post("/download")
async def start_download(request: DownloadRequest):
    # This will later dispatch to ARQ worker
    return {"message": "Download task queued", "url": request.url}
