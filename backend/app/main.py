from fastapi import FastAPI
from app.api import endpoints

app = FastAPI(
    title="Streamdown API",
    description="Backend API for streamdown music downloader",
    version="0.1.0",
)

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
