import yt_dlp

def get_video_info(url: str) -> dict:
    """
    Extract metadata without downloading audio.
    Used for the Review phase (button review).
    """
    ydl_opts = {
        'extract_flat': True, # Do not download, just extract metadata
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            
            # Check if it's a playlist
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
            raise Exception(f"Gagal mengambil data dari URL: {str(e)}")

def download_single(url: str, output_path: str):
    """
    Download single audio as MP3.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_playlist(url: str, output_path: str):
    """
    Download playlist items.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
