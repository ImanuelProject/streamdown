from pydantic import BaseModel
from typing import Optional

class PreviewRequest(BaseModel):
    url: str

class PreviewResponse(BaseModel):
    is_valid: bool
    title: Optional[str] = None
    thumbnail: Optional[str] = None
    is_playlist: bool = False
    items_count: int = 1
    error_message: Optional[str] = None

class DownloadRequest(BaseModel):
    url: str
    is_playlist: bool = False

class DownloadResponse(BaseModel):
    task_id: str
    message: str

class StatusResponse(BaseModel):
    status: str
    result_path: Optional[str] = None
    error: Optional[str] = None
