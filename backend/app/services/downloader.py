import yt_dlp
import subprocess
import json
import os
import re

def is_spotify_url(url: str) -> bool:
    """Cek apakah URL berasal dari Spotify."""
    return "spotify.com" in url or "open.spotify.com" in url

def is_spotify_playlist(url: str) -> bool:
    """Cek apakah URL Spotify adalah playlist atau album."""
    return "/playlist/" in url or "/album/" in url

# ========================================
# PREVIEW / REVIEW FUNCTIONS
# ========================================

def get_video_info(url: str) -> dict:
    """
    Extract metadata without downloading audio.
    Used for the Review phase (button review).
    Mendukung YouTube dan Spotify.
    """
    if is_spotify_url(url):
        return _get_spotify_info(url)
    else:
        return _get_youtube_info(url)

def _get_youtube_info(url: str) -> dict:
    """Ekstrak metadata dari YouTube menggunakan yt-dlp."""
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                entries = list(info['entries'])
                return {
                    "title": info.get('title', 'Unknown Playlist'),
                    "thumbnail": None, 
                    "is_playlist": True,
                    "items_count": len(entries)
                }
            else:
                return {
                    "title": info.get('title', 'Unknown Title'),
                    "thumbnail": info.get('thumbnail'),
                    "is_playlist": False,
                    "items_count": 1
                }
        except Exception as e:
            raise Exception(f"Gagal mengambil data dari YouTube: {str(e)}")

def _get_spotify_info(url: str) -> dict:
    """Ekstrak metadata dari Spotify menggunakan spotdl v4.x."""
    try:
        save_path = f"/tmp/spotdl_{hash(url)}.spotdl"
        
        # Hapus file lama jika ada
        if os.path.exists(save_path):
            os.remove(save_path)
        
        # Spotdl 4.x syntax: spotdl save [url] --save-file [path]
        result = subprocess.run(
            ["spotdl", "save", url, "--save-file", save_path],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Gagal menjalankan spotdl"
            if "rate/request limit" in error_msg.lower():
                raise Exception("Spotify API rate limit tercapai. Silakan coba lagi nanti atau gunakan URL YouTube.")
            raise Exception(f"Spotdl error: {error_msg.splitlines()[-1] if error_msg.splitlines() else error_msg}")
        
        if not os.path.exists(save_path):
            raise Exception("Spotdl tidak menghasilkan file metadata")
        
        with open(save_path, "r", encoding="utf-8") as f:
            tracks = json.load(f)
        
        # Bersihkan file sementara
        os.remove(save_path)
        
        if not tracks:
            raise Exception("Tidak ada lagu yang ditemukan dari tautan Spotify ini")
        
        is_playlist = is_spotify_playlist(url) or len(tracks) > 1
        
        if is_playlist:
            # Cari info playlist dari meta jika memungkinkan
            title = "Spotify Playlist"
            if tracks[0].get("list_name"):
                title = tracks[0]["list_name"]
            
            return {
                "title": f"{title} ({len(tracks)} lagu)",
                "thumbnail": tracks[0].get("cover_url") if tracks else None,
                "is_playlist": True,
                "items_count": len(tracks)
            }
        else:
            track = tracks[0]
            artists = ", ".join(track.get("artists", ["Unknown Artist"]))
            return {
                "title": f"{artists} - {track.get('name', 'Unknown Title')}",
                "thumbnail": track.get("cover_url"),
                "is_playlist": False,
                "items_count": 1
            }
    except subprocess.TimeoutExpired:
        raise Exception("Waktu habis saat mengambil data dari Spotify (60 detik)")
    except Exception as e:
        if "rate limit" in str(e).lower():
            raise e
        raise Exception(f"Gagal mengambil data dari Spotify: {str(e)}")


# ========================================
# DOWNLOAD FUNCTIONS
# ========================================

def download_single(url: str, output_path: str, progress_callback=None):
    """Download single audio as MP3. Mendukung YouTube & Spotify."""
    if is_spotify_url(url):
        _download_spotify(url, output_path, progress_callback)
    else:
        _download_youtube_single(url, output_path, progress_callback)

def download_playlist(url: str, output_path: str, progress_callback=None):
    """Download playlist/album as MP3. Mendukung YouTube & Spotify."""
    if is_spotify_url(url):
        _download_spotify(url, output_path, progress_callback)
    else:
        _download_youtube_playlist(url, output_path, progress_callback)

def _download_youtube_single(url: str, output_path: str, progress_callback=None):
    """Download single audio dari YouTube menggunakan yt-dlp."""
    def ydl_hook(d):
        if progress_callback and d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','').strip()
            try:
                progress_callback(float(p))
            except:
                pass

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'progress_hooks': [ydl_hook],
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def _download_youtube_playlist(url: str, output_path: str, progress_callback=None):
    """Download playlist dari YouTube menggunakan yt-dlp."""
    def ydl_hook(d):
        if progress_callback and d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','').strip()
            try:
                progress_callback(float(p))
            except:
                pass

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(playlist_index)s - %(title)s.%(ext)s',
        'progress_hooks': [ydl_hook],
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def _download_spotify(url: str, output_path: str, progress_callback=None):
    """
    Download audio dari Spotify menggunakan spotdl v4.x.
    """
    process = subprocess.Popen(
        [
            "spotdl", "download", url,
            "--output", f"{output_path}/{{title}} - {{artists}}.{{output-ext}}",
            "--format", "mp3",
            "--bitrate", "192k",
            "--log-level", "INFO"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:
        if progress_callback:
            match = re.search(r"(\d+)%", line)
            if match:
                try:
                    progress_callback(float(match.group(1)))
                except:
                    pass
    
    process.wait()
    if process.returncode != 0:
        raise Exception(f"Download Spotify gagal dengan kode {process.returncode}")
