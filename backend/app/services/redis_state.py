import json
from redis import asyncio as redis
from datetime import datetime

async def set_task_status(redis_client: redis.Redis, task_id: str, status: str, progress: float = 0.0, download_url: str = None):
    """Menyimpan status tugas ke Redis."""
    data = {
        "status": status,
        "progress": progress,
        "download_url": download_url,
        "updated_at": str(datetime.now())
    }
    await redis_client.set(f"task:{task_id}", json.dumps(data), ex=86400)
    # Jangan tutup koneksi di sini jika redis_client dikelola oleh pool besar (seperti di worker)

async def get_task_status(redis_client: redis.Redis, task_id: str):
    """Mengambil status tugas dari Redis."""
    try:
        data = await redis_client.get(f"task:{task_id}")
        if data:
            return json.loads(data)
        return None
    finally:
        # Jika ini adalah client sekali pakai (short-lived), pastikan ditutup
        # Namun di FastAPI biasanya kita menggunakan dependency injection yang mengelola ini
        pass
