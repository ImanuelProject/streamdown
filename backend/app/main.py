from fastapi import FastAPI
from contextlib import asynccontextmanager
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings
from app.api import endpoints

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Membuat koneksi tunggal (Connection Pool) untuk Redis
    # arq.create_pool secara otomatis mendukung operasi Redis standar
    app.state.arq_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    yield
    # Menutup semua koneksi saat aplikasi dimatikan
    await app.state.arq_pool.close()

app = FastAPI(
    title="Streamdown API",
    description="Backend API for streamdown music downloader",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
