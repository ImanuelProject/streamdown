from arq.connections import RedisSettings
from app.core.config import settings
from app.worker.tasks import execute_download

class WorkerSettings:
    functions = [execute_download]
    # Konfigurasi koneksi Redis dari app.core.config
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
