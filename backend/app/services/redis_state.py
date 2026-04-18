import json
from redis import asyncio as redis

async def set_task_status(redis_client: redis.Redis, task_id: str, status: str, result_path: str = None, error: str = None, progress: float = 0):
    data = {
        "status": status,
        "result_path": result_path,
        "error": error,
        "progress": progress
    }
    # Expire in 24 hours (86400 seconds)
    await redis_client.set(f"task:{task_id}", json.dumps(data), ex=86400)

async def get_task_status(redis_client: redis.Redis, task_id: str) -> dict:
    data = await redis_client.get(f"task:{task_id}")
    if data:
        return json.loads(data)
    return None
