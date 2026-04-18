import asyncio
import os
import shutil
from redis.asyncio import Redis
from app.core.config import settings
from app.services.downloader import download_single, download_playlist
from app.services.redis_state import set_task_status

async def execute_download(ctx, url: str, is_playlist: bool, task_id: str):
    """
    Fungsi latar belakang (Background Job) yang dieksekusi oleh ARQ Worker.
    Fungsi ini bersifat asinkronus (async) tapi menjalankan fungsi yt-dlp secara threadpool.
    """
    redis_client = Redis.from_url(settings.REDIS_URL)
    
    # Path diletakkan di ./data yang tersambung via volume Docker
    output_dir = f"/data/{task_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        await set_task_status(redis_client, task_id, "DOWNLOADING")
        
        loop = asyncio.get_event_loop()
        
        if is_playlist:
            # Mengunduh secara sinkron di latar belakang
            await loop.run_in_executor(None, download_playlist, url, output_dir)
            await set_task_status(redis_client, task_id, "ZIPPING")
            
            # Membungkus folder menjadi ZIP
            zip_path_base = f"/data/{task_id}_playlist"
            await loop.run_in_executor(None, shutil.make_archive, zip_path_base, 'zip', output_dir)
            
            # Membersihkan folder berisi kumpulan .mp3 mentah untuk menghemat memori
            shutil.rmtree(output_dir)
            
            await set_task_status(redis_client, task_id, "COMPLETED", result_path=f"{zip_path_base}.zip")
        else:
            await loop.run_in_executor(None, download_single, url, output_dir)
            
            # Mencari lokasi file hasil unduhan
            files = os.listdir(output_dir)
            if files:
                file_path = f"{output_dir}/{files[0]}"
                await set_task_status(redis_client, task_id, "COMPLETED", result_path=file_path)
            else:
                raise Exception("File MP3 tidak ditemukan setelah proses diunduh.")
                
    except Exception as e:
        await set_task_status(redis_client, task_id, "FAILED", error=str(e))
    finally:
        await redis_client.aclose()
