# 🎵 STREAMDOWN - Premium Music Downloader

**STREAMDOWN** adalah aplikasi berbasis terminal (CLI) yang memungkinkan Anda mendownload audio berkualitas tinggi (MP3 320kbps) dari YouTube dan SoundCloud dengan mudah. Aplikasi ini secara otomatis menyematkan metadata (judul, artis) dan thumbnail ke dalam file audio.

## ✨ Fitur Utama
- 🚀 **High Speed Download**: Menggunakan engine `yt-dlp` yang sangat cepat.
- 🎧 **High Quality Audio**: Konversi otomatis ke format MP3 kualitas terbaik.
- 🖼️ **Auto Metadata**: Menyematkan gambar album dan informasi lagu secara otomatis.
- 📂 **Auto Organize**: Hasil download tersimpan rapi di folder `Music/Streamdown`.
- 🛠️ **Smart Dependency**: Deteksi otomatis FFmpeg di folder lokal maupun PATH.

## 📋 Persyaratan Sistem
1. **Python 3.7+**
2. **FFmpeg** (Diperlukan untuk konversi audio)

## 🚀 Cara Instalasi (Setup)

### Langkah 1: Clone atau Download Project
Pastikan Anda berada di folder project `streamdown`.

### Langkah 2: Instalasi Library Python
Jalankan perintah berikut di terminal/PowerShell:
```powershell
pip install yt-dlp
```

### Langkah 3: Setup FFmpeg (Penting!)
FFmpeg diperlukan agar aplikasi bisa merubah video menjadi MP3.
1. Download FFmpeg dari [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip).
2. Extract file `.zip` tersebut.
3. Masuk ke folder `bin`, cari file **`ffmpeg.exe`**.
4. Copy dan Paste file **`ffmpeg.exe`** tersebut langsung ke dalam folder project ini (`D:\Data Joni\streamdown`).

## 🎮 Cara Penggunaan
Cukup jalankan file `main.py` menggunakan Python:

```powershell
python main.py
```

1. Pilih menu **1** untuk mendownload.
2. Masukkan URL lagu dari YouTube atau SoundCloud.
3. Tunggu hingga proses selesai.
4. Cek folder **Music/Streamdown** di komputer Anda.

## 🛠️ Troubleshooting
Jika muncul pesan `FFmpeg tidak ditemukan`:
- Pastikan file `ffmpeg.exe` ada di folder yang sama dengan `main.py`.
- Atau pastikan folder `bin` FFmpeg sudah terdaftar di **Environment Variables (PATH)** Windows Anda.

---
*Dibuat dengan ❤️ untuk pecinta musik.*
