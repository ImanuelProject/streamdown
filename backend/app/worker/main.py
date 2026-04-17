from arq import worker
from arq.connections import RedisSettings
from app.core.config import settings
import asyncio

async def download_task(ctx, url: str):
    # Placeholder for actual download logic
    print(f"Downloading {url}")
    await asyncio.sleep(2)
    return {"status": "success", "url": url}

class WorkerSettings:
    functions = [download_task]
    # Parse redis url
    # e.g. redis://redis:6379/0
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

if __name__ == '__main__':
    worker.run_worker(WorkerSettings)
