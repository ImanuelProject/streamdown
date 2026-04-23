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

def log_ok(msg):    print(f"{Style.GREEN} ✔ {Style.RESET} {msg}")
def log_warn(msg):  print(f"{Style.YELLOW} ⚠ {Style.RESET} {msg}")
def log_err(msg):   print(f"{Style.RED} ✘ {Style.RESET} {msg}")
def log_info(msg):  print(f"{Style.CYAN} ℹ {Style.RESET} {msg}")

def print_banner():
    print(f"{Style.PURPLE}{Style.BOLD}")
    print("  ███████╗████████╗██████╗ ███████╗ █████╗ ███╗   ███╗")
    print("  ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗████╗ ████║")
    print("  ███████╗   ██║   ██████╔╝█████╗  ███████║██╔████╔██║")
    print("  ╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║")
    print("  ███████║   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║")
    print(f"{Style.RESET}{Style.CYAN}  Premium Music Downloader • YouTube & SoundCloud{Style.RESET}\n")

# ─── Dependency Management ────────────────────────────────────────
FFMPEG_EXE = "ffmpeg"

def find_ffmpeg():
    global FFMPEG_EXE
    # 1. Check System PATH
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    
    # 2. Check Local Directory
    local_ffmpeg = Path.cwd() / "ffmpeg.exe"
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    
    # 3. Check Downloads Folder (Auto-Fix)
    downloads = Path.home() / "Downloads"
    for exe in downloads.rglob("ffmpeg.exe"):
        log_info(f"Ditemukan ffmpeg.exe di Downloads: {exe.parent}")
        return str(exe)
        
    return None

def check_system():
    global FFMPEG_EXE
    print_banner()
    log_info("Memeriksa dependensi...")

    # Check yt-dlp
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        log_ok("yt-dlp siap.")
    except:
        log_warn("Menginstall yt-dlp...")
        subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"], check=True)
        log_ok("yt-dlp terinstal.")

    # Check FFmpeg
    found = find_ffmpeg()
    if found:
        FFMPEG_EXE = found
        log_ok(f"FFmpeg siap ({'System' if found=='ffmpeg' else 'Local/Found'})")
    else:
        log_err("FFmpeg tidak ditemukan!")
        print(f"\n{Style.YELLOW}Solusi Cepat:{Style.RESET}")
        print("1. Download zip dari: https://github.com/BtbN/FFmpeg-Builds/releases")
        print("2. Ambil 'ffmpeg.exe' dari dalam folder 'bin'.")
        print(f"3. Letakkan di folder ini: {os.getcwd()}\n")
        sys.exit(1)

# ─── Downloader Logic ─────────────────────────────────────────────
def download_audio(url, output_path):
    log_info(f"Memulai download: {url}")
    
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--ffmpeg-location", FFMPEG_EXE,
        "--output", f"{output_path}/%(title)s.%(ext)s",
        "--add-metadata",
        "--embed-thumbnail",
        url
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n{Style.GREEN}{Style.BOLD}✔ BERHASIL!{Style.RESET} Cek folder Music Anda.")
    except subprocess.CalledProcessError:
        log_err("Gagal mendownload. Pastikan URL benar.")

# ─── Main Menu ────────────────────────────────────────────────────
def main():
    check_system()
    music_dir = Path.home() / "Music" / "Streamdown"
    music_dir.mkdir(parents=True, exist_ok=True)

    while True:
        print(f"\n{Style.BOLD}[ MENU ]{Style.RESET}")
        print("1. Download Lagu (YouTube/SoundCloud)")
        print("2. Keluar")
        
        choice = input(f"\nPilih [1-2]: ").strip()
        
        if choice == "1":
            url = input(f"Masukkan URL: ").strip()
            if url:
                download_audio(url, str(music_dir))
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
