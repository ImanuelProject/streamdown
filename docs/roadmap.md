l# 🗺️ Streamdown Development Roadmap

Dokumen ini memuat peta jalan (roadmap) pengembangan platform Streamdown. Sesuai dengan arsitektur yang sudah kita buat, fokus pengembangan akan dilakukan secara bertahap dimulai dari **Backend (Core Logic & API)** terlebih dahulu, lalu disusul oleh **Frontend (UI & Integrasi)**.

## 🔄 User Flow (Berdasarkan Diagram)
1. User masuk ke **Landing Page**
2. User menambahkan URL tunggal (*single music*) atau banyak lagu (*multiple music/playlist*).
3. User menekan **Button Review** untuk pratinjau (mengekstrak metadata tanpa mengunduh).
4. Jika **True** (valid), lanjut ke **Button Download**. Jika **False**, kembali ke tahap masukkan URL.
5. Menghasilkan `.mp3` tunggal atau `.zip` untuk beberapa lagu.
6. Tersimpan ke *Local Storage* pengguna.

---

## 🏗️ Phase 1: Backend Core (Downloader Engine & Preview)
Fokus utama di fase ini adalah membangun mesin pengunduh inti menggunakan pustaka Python (`yt-dlp` & `spotdl`).

*   [x] **Service Preview/Review**: Menggunakan opsi khusus `yt-dlp` untuk mengekstrak metadata secara cepat (Judul, Thumbnail, apakah ini *single* lagu atau *playlist* multi lagu) tanpa mendownload audionya.
*   [x] **Service Single Downloader**: Fungsi `download_single` untuk mengunduh murni dari YouTube/Spotify dan menyimpannya menjadi file `.mp3`.
*   [x] **Service Multiple Downloader (ZIP)**: Fungsi `download_playlist` yang dapat mengunduh beberapa lagu sekaligus dan mengompresinya (*packaging*) ke dalam satu arsip `.zip`.

## ⚙️ Phase 2: Backend Queue Management (ARQ & Redis)
Karena proses kompresi ZIP atau konversi audio MP3 memakan waktu, tugas ini dikerjakan di latar belakang (*background worker*).

*   [x] **Task Definition**: Mendefinisikan fungsi ARQ di `backend/app/worker/tasks.py` yang akan memanggil fungsi-fungsi *downloader* dari Phase 1.
*   [x] **Job State Management**: Menyimpan status unduhan di Redis (misal: `QUEUED`, `DOWNLOADING`, `ZIPPING`, `COMPLETED`, `FAILED`).
*   [x] **Cleanup Routine**: Membuat logika untuk menghapus otomatis file `.mp3` dan `.zip` sementara dari server setelah diunduh pengguna ke penyimpanan lokal mereka.

## 🌐 Phase 3: Backend API (FastAPI)
Membuat titik masuk API (*Endpoints*) yang merepresentasikan *flowchart* antarmuka pengguna.

*   [x] **Endpoint Review**: `POST /api/v1/preview` - Menerima URL, dan mengembalikan hasil fungsi *Preview/Review* (True/False) dengan metadata lagu.
*   [x] **Endpoint Download**: `POST /api/v1/download` - Menerima URL yang sudah divalidasi, mendaftarkan tugas ke ARQ Queue, lalu mengembalikan ID antrean.
*   [x] **Endpoint Status & Streaming**: `GET /api/v1/stream/{task_id}` - Menyediakan file `.mp3` atau `.zip` akhir (*StreamingResponse*) ke klien untuk diunduh.

---

## 🎨 Phase 4: Frontend UI (React + Tailwind v4)
*   [x] **Landing Page**: Membuat form masukan URL yang jernih dan bersih.
*   [x] **Review Card**: Membuat tampilan validasi sebelum *download* yang menampilkan judul dan detail lagu/playlist (merespons 'True/False' dari tahap Review).
*   [x] **Button Review & Download**: Membuat dua *state* tombol (*Button Review* dan *Button Download*) yang selaras dengan *flowchart* yang telah disepakati.

## 🔗 Phase 5: Frontend Integration & Polish
*   [x] Menggabungkan semua tahap agar pengguna dapat merasakan alur: *Paste URL -> Review -> Klik Download -> Loading/Polling -> Menerima File MP3/ZIP*.
