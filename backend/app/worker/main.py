from arq.connections import RedisSettings
from app.core.config import settings
from app.worker.tasks import execute_download

class WorkerSettings:
    functions = [execute_download]
    # Konfigurasi koneksi Redis dari app.core.config
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    # Menaikkan timeout menjadi 1 jam (3600 detik) untuk menangani playlist besar
    job_timeout = 3600
