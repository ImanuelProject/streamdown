import streamlit as st
import main
from pathlib import Path
import os
import shutil

# Konfigurasi Halaman
st.set_page_config(page_title="STREAMDOWN Cloud", page_icon="🎵", layout="centered")

# CSS Kustom
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff4b4b; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎵 STREAMDOWN")
st.caption("Music Downloader for Rekordbox (Cloud Version)")

# Inisialisasi System
if 'ffmpeg_checked' not in st.session_state:
    main.check_system()
    st.session_state.ffmpeg_checked = True

# Tentukan folder download sementara di server
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

url = st.text_input("Masukkan URL YouTube atau SoundCloud:", placeholder="https://...")

# Deteksi Playlist
is_playlist = any(x in url.lower() for x in ["playlist", "album", "sets", "list="])
items = None
if is_playlist:
    limit_toggle = st.checkbox("Batasi jumlah lagu?")
    if limit_toggle:
        items = st.number_input("Berapa lagu?", min_value=1, value=10, step=1)

if st.button("PROSES DOWNLOAD"):
    if url:
        with st.status("Sedang diproses oleh server...", expanded=True) as status:
            try:
                # Bersihkan folder download sebelumnya agar tidak penuh
                for f in DOWNLOAD_DIR.glob("*"):
                    if f.is_file(): f.unlink()
                
                # Jalankan download ke folder sementara di server
                main.download_audio(url, str(DOWNLOAD_DIR), items=items)
                
                status.update(label="✅ Berhasil Diproses!", state="complete")
                st.success("Lagu sudah siap didownload ke perangkat Anda!")
                
                # Cari file yang baru didownload
                downloaded_files = list(DOWNLOAD_DIR.glob("*.mp3")) + list(DOWNLOAD_DIR.glob("*.m4a"))
                
                if downloaded_files:
                    for file_path in downloaded_files:
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label=f"💾 SIMPAN KE PERANGKAT: {file_path.name}",
                                data=f,
                                file_name=file_path.name,
                                mime="audio/mpeg"
                            )
                    st.balloons()
                else:
                    st.warning("File tidak ditemukan. Coba lagi.")
                    
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Masukkan URL dulu!")

st.divider()
st.info("💡 Petunjuk: Setelah proses selesai, klik tombol 'SIMPAN KE PERANGKAT' untuk mendownload file ke Mac/HP Anda.")
