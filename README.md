# 🎵 STREAMDOWN - Premium Music Downloader (Terminal Edition)

**STREAMDOWN** adalah aplikasi terminal (CLI) premium yang dirancang khusus untuk DJ dan pecinta musik yang ingin membangun library berkualitas tinggi. Mendownload audio dari YouTube & SoundCloud dengan format yang sudah dioptimalkan untuk **Rekordbox**.

## ✨ Fitur Utama
- 🎧 **Rekordbox Ready**: Hasil download berupa MP3 kualitas terbaik (VBR 0 / ~320kbps).
- 🏷️ **Pro Metadata**: Otomatis menyematkan Judul, Artis, Album Art, dan Chapters.
- 📂 **DJ-Friendly Naming**: Format nama file otomatis `Artis - Judul.mp3`.
- 🔄 **Smart Auto-Skip**: Menggunakan sistem *Archive*, lagu yang sudah ada tidak akan didownload ulang.
- 📜 **Playlist Support**: Bisa mendownload seluruh playlist/album dengan opsi limit jumlah lagu.
- 🍏 **Cross-Platform**: Berjalan mulus di **Windows** maupun **macOS**.

## 📋 Persyaratan Sistem
1. **Python 3.8+**
2. **FFmpeg** (Wajib untuk konversi MP3 & Metadata)

## 🚀 Cara Instalasi & Setup

### **Untuk Windows**
1. Taruh file `ffmpeg.exe` dan `ffprobe.exe` langsung di dalam folder project ini.
2. Jalankan di PowerShell:
   ```powershell
   python main.py
   ```

### **Untuk macOS**
1. Instal FFmpeg via Homebrew:
   ```bash
   brew install ffmpeg
   ```
2. Jalankan di Terminal:
   ```bash
   python3 main.py
   ```

## 🎮 Cara Penggunaan

Anda memiliki dua pilihan antarmuka:

### **Opsi A: Versi Terminal (Cepat)**
Jalankan perintah:
```powershell
python main.py
```

### **Opsi B: Versi Web App (Modern)**
1. Instal Streamlit: `pip install streamlit`
2. Jalankan perintah:
   ```powershell
   streamlit run web.py
   ```
3. Browser Anda akan terbuka otomatis menampilkan STREAMDOWN Web.

---
*Dibuat dengan ❤️ untuk komunitas DJ.*
