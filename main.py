#!/usr/bin/env python3
"""
🎵 STREAMDOWN - Premium Terminal Music Downloader
YouTube & SoundCloud → High Quality MP3
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

# ─── UI Styles ────────────────────────────────────────────────────
class Style:
    PURPLE = "\033[95m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

def log_ok(msg):
    try: print(f"{Style.GREEN} ✔ {Style.RESET} {msg}")
    except: print(f"[OK] {msg}")

def log_warn(msg):
    try: print(f"{Style.YELLOW} ⚠ {Style.RESET} {msg}")
    except: print(f"[!] {msg}")

def log_err(msg):
    try: print(f"{Style.RED} ✘ {Style.RESET} {msg}")
    except: print(f"[X] {msg}")

def log_info(msg):
    try: print(f"{Style.CYAN} ℹ {Style.RESET} {msg}")
    except: print(f"[i] {msg}")

def print_banner():
    try:
        print(f"{Style.PURPLE}{Style.BOLD}")
        print("  ███████╗████████╗██████╗ ███████╗ █████╗ ███╗   ███╗")
        print("  ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗████╗ ████║")
        print("  ███████╗   ██║   ██████╔╝█████╗  ███████║██╔████╔██║")
        print("  ╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║")
        print("  ███████║   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║")
        print(f"{Style.RESET}{Style.CYAN}  Premium Music Downloader • YouTube & SoundCloud{Style.RESET}\n")
    except UnicodeEncodeError:
        # Fallback jika terminal tidak support karakter blok (biasanya di .exe)
        print("\n--- STREAMDOWN - Premium Music Downloader ---\n")

# ─── Dependency Management ────────────────────────────────────────
FFMPEG_LOCATION = None
FFMPEG_AVAILABLE = False

def yt_dlp_cmd():
    return [sys.executable, "-m", "yt_dlp"]

def can_run_binary(command):
    try:
        subprocess.run(
            command,
            capture_output=True,
            check=True,
            text=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False

def find_ffmpeg():
    # 0. Check PyInstaller temporary folder (Jika dibundel jadi .exe)
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
        ext = ".exe" if os.name == "nt" else ""
        if (Path(bundle_dir) / f"ffmpeg{ext}").exists():
            return bundle_dir

    # 1. Check System PATH (Terbaik untuk Mac via Homebrew)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return str(Path(system_ffmpeg).parent)

    # 2. Check local paths
    ext = ".exe" if os.name == "nt" else ""
    local_candidates = [
        Path.cwd(),
        Path.cwd() / "ffmpeg" / "bin",
        Path.cwd() / "ffmpeg",
    ]
    for directory in local_candidates:
        ffmpeg_exe = directory / f"ffmpeg{ext}"
        ffprobe_exe = directory / f"ffprobe{ext}"
        if ffmpeg_exe.exists() and ffprobe_exe.exists():
            return str(directory)

    return None

def check_system():
    global FFMPEG_LOCATION, FFMPEG_AVAILABLE
    print_banner()
    log_info("Memeriksa dependensi...")

    # Check yt-dlp
    try:
        subprocess.run(yt_dlp_cmd() + ["--version"], capture_output=True, check=True)
        log_ok("yt-dlp siap.")
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        log_warn("Menginstall yt-dlp...")
        subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"], check=True)
        log_ok("yt-dlp terinstal.")

    # Check FFmpeg
    found_dir = find_ffmpeg()
    if found_dir:
        ext = ".exe" if os.name == "nt" else ""
        ffmpeg_exe = str(Path(found_dir) / f"ffmpeg{ext}")
        ffprobe_exe = str(Path(found_dir) / f"ffprobe{ext}")
        
        if can_run_binary([ffmpeg_exe, "-version"]) and can_run_binary([ffprobe_exe, "-version"]):
            FFMPEG_LOCATION = found_dir
            FFMPEG_AVAILABLE = True
            log_ok(f"FFmpeg siap di: {FFMPEG_LOCATION}")
        else:
            FFMPEG_AVAILABLE = False
            log_warn("FFmpeg ditemukan tapi tidak bisa dijalankan.")
    else:
        FFMPEG_AVAILABLE = False
        log_warn("FFmpeg tidak ditemukan. Silakan instal via Homebrew (Mac) atau taruh di folder project.")

# ─── Downloader Logic ─────────────────────────────────────────────
def download_audio(url, output_path, items=None):
    if not FFMPEG_AVAILABLE:
        log_warn("Peringatan: FFmpeg tidak aktif. File mungkin tidak support Rekordbox!")
    
    log_info(f"Memulai download: {url}")

    # Template nama file: "Artis - Judul.mp3" (Sangat disukai DJ agar rapi)
    cmd = [
        *yt_dlp_cmd(), 
        "--output", f"{output_path}/%(artist,uploader)s - %(title)s.%(ext)s",
        "--no-mtime", # Agar file date adalah waktu download, memudahkan sorting 'Date Added'
        "--download-archive", f"{output_path}/archive.txt", # CATATAN: Skip lagu yang sudah pernah didownload
        "--no-overwrites" # Jangan timpa file jika sudah ada di folder
    ]

    # Fitur Playlist Limit
    if items:
        cmd.extend(["--playlist-items", f"1-{items}"])

    if FFMPEG_AVAILABLE and FFMPEG_LOCATION:
        cmd.extend(
            [
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "--ffmpeg-location", FFMPEG_LOCATION,
                "--add-metadata",
                "--embed-thumbnail",
                "--embed-chapters", # Berguna untuk melihat struktur lagu (Intro/Drop) di beberapa player
                "--metadata-from-title", "%(artist)s - %(title)s", # Coba ekstrak artis dari judul
            ]
        )
    else:
        # Fall back to the source audio file when FFmpeg cannot run.
        cmd.extend(["--format", "bestaudio/best"])

    cmd.append(url)
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n{Style.GREEN}{Style.BOLD}✔ SELESAI!{Style.RESET} Lagu siap di-import ke Rekordbox.")
    except subprocess.CalledProcessError:
        log_err("Gagal mendownload. Pastikan URL benar.")
    except OSError as exc:
        log_err(f"Gagal menjalankan downloader: {exc}")

# ─── Main Menu ────────────────────────────────────────────────────
def main():
    check_system()
    music_dir = Path.home() / "Music" / "Streamdown"
    music_dir.mkdir(parents=True, exist_ok=True)

    while True:
        print(f"\n{Style.BOLD}[ MENU ]{Style.RESET}")
        print("1. Download Lagu/Playlist (YouTube/SoundCloud)")
        print("2. Keluar")
        
        choice = input(f"\nPilih [1-2]: ").strip()
        
        if choice == "1":
            url = input(f"Masukkan URL: ").strip()
            if url:
                # Deteksi playlist yang lebih kuat (YouTube 'list=' dan SoundCloud '/sets/')
                is_playlist = any(x in url.lower() for x in ["playlist", "album", "sets", "list="])
                
                if is_playlist:
                    limit = input(f"Playlist/Set terdeteksi. Berapa lagu mau didownload? (Kosongkan untuk semua): ").strip()
                    items = int(limit) if limit.isdigit() else None
                else:
                    items = None
                
                download_audio(url, str(music_dir), items=items)
        elif choice == "2":
            print(f"{Style.PURPLE}Sampai jumpa!{Style.RESET}")
            break
        else:
            log_warn("Pilihan tidak valid.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
