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
    """Ekstrak metadata dari Spotify secara instan menggunakan OEmbed API."""
    try:
        import urllib.request
        import json
        
        # OEmbed API adalah cara tercepat untuk mendapatkan metadata publik (Thumbnail & Title)
        oembed_url = f"https://open.spotify.com/oembed?url={url}"
        
        with urllib.request.urlopen(oembed_url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            # Judul biasanya formatnya: "Song Name by Artist Name"
            title = data.get("title", "Unknown Spotify Track")
            thumbnail = data.get("thumbnail_url")
            
            # OEmbed tidak memberitahu jumlah lagu jika playlist, 
            # jadi kita tetap gunakan logika deteksi sederhana
            is_playlist = is_spotify_playlist(url)
            
            return {
                "title": title,
                "thumbnail": thumbnail,
                "is_playlist": is_playlist,
                "items_count": 0 if is_playlist else 1 # 0 berarti 'Banyak' untuk playlist
            }
            
    except Exception as e:
        # Fallback ke spotdl jika OEmbed gagal (misal: URL tidak didukung OEmbed)
        return _get_spotify_info_fallback(url)

def _get_spotify_info_fallback(url: str) -> dict:
    """Fallback menggunakan spotdl jika OEmbed tidak tersedia."""
    try:
        save_path = f"/tmp/spotdl_{hash(url)}.spotdl"
        if os.path.exists(save_path):
            os.remove(save_path)
            
        result = subprocess.run(
            ["spotdl", "save", url, "--save-file", save_path],
            capture_output=True, text=True, timeout=30
        )
        
        if not os.path.exists(save_path):
            raise Exception("Spotdl gagal mengambil metadata")
            
        with open(save_path, "r", encoding="utf-8") as f:
            tracks = json.load(f)
        
        os.remove(save_path)
        is_playlist = is_spotify_playlist(url) or len(tracks) > 1
        
        return {
            "title": tracks[0].get("name", "Unknown") if not is_playlist else "Spotify Playlist",
            "thumbnail": tracks[0].get("cover_url"),
            "is_playlist": is_playlist,
            "items_count": len(tracks)
        }
    except Exception as e:
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
    Download Spotify menggunakan spotipy (untuk daftar lagu) + yt-dlp (untuk audio).
    Ini menjamin lagu terpisah-pisah meskipun dalam album/playlist.
    """
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    import os

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    # 1. Ambil daftar lagu (Search Queries)
    queries = []
    album_name = "Spotify Download"
    
    try:
        if client_id and client_secret:
            print("DEBUG: Menggunakan kredensial Spotify untuk mengambil daftar lagu...", flush=True)
            auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
            sp = spotipy.Spotify(auth_manager=auth_manager)
            
            if "track" in url:
                track = sp.track(url)
                queries.append(f"{track['artists'][0]['name']} - {track['name']}")
            elif "album" in url:
                results = sp.album_tracks(url)
                album_name = sp.album(url)['name']
                for item in results['items']:
                    queries.append(f"{item['artists'][0]['name']} - {item['name']}")
            elif "playlist" in url:
                results = sp.playlist_tracks(url)
                album_name = sp.playlist(url)['name']
                for item in results['items']:
                    track = item['track']
                    queries.append(f"{track['artists'][0]['name']} - {track['name']}")
        else:
            # Fallback jika tidak ada kredensial (Hanya satu lagu dari OEmbed)
            print("DEBUG: Tanpa kredensial, fallback ke OEmbed (Hanya 1 lagu)...", flush=True)
            info = _get_spotify_info(url)
            queries.append(info['title'])
    except Exception as e:
        print(f"DEBUG ERROR: Gagal mengambil daftar lagu via Spotipy: {e}", flush=True)
        # Final fallback
        info = _get_spotify_info(url)
        queries.append(info['title'])

    # 2. Download tiap lagu satu per satu
    def ydl_hook(d):
        if progress_callback and d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','').strip()
            try:
                progress_callback(float(p))
            except: pass

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f"{output_path}/%(title)s.%(ext)s",
        'progress_hooks': [ydl_hook],
        'quiet': True,
        'no_warnings': True,
    }

    print(f"DEBUG: Memulai unduhan {len(queries)} lagu secara terpisah...", flush=True)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, q in enumerate(queries):
            print(f"DEBUG: Mengunduh ({i+1}/{len(queries)}): {q}", flush=True)
            try:
                ydl.download([f"ytsearch1:{q} official audio"])
            except Exception as e:
                print(f"DEBUG ERROR: Gagal mengunduh {q}: {e}", flush=True)
                
    print(f"DEBUG: Semua proses selesai!", flush=True)
