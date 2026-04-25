import streamlit as st
import main
from pathlib import Path
import os
import subprocess

# Konfigurasi Halaman
st.set_page_config(page_title="STREAMDOWN PRO", page_icon="🎧", layout="wide")

# CSS Kustom untuk Tampilan Pro DJ
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-weight: bold; font-size: 18px; }
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #ff4b4b, #ff7b7b); color: white; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Settings Pro")
    audio_format = st.selectbox("Format Audio:", ["mp3", "wav", "flac"])
    quality = st.select_slider("Kualitas Audio:", options=["LDR", "Standard", "High", "Ultra (Pro)"], value="Ultra (Pro)")
    st.divider()
    playlist_limit = st.number_input("Limit Playlist (Item):", min_value=1, value=50)
    st.info("💡 Tip: Gunakan WAV/FLAC jika Anda ingin kualitas lossless tanpa kompresi.")

st.title("🎧 STREAMDOWN PRO")
st.caption("The Ultimate Music Discovery & Downloader for DJs")

tab1, tab2 = st.tabs(["🔍 Search & Download", "🔗 Direct URL / Batch"])

# Folder Download Sementara
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Fungsi Helper Download
def process_download(query, is_search=False):
    # Bersihkan folder lama
    for f in DOWNLOAD_DIR.glob("*"): 
        if f.is_file(): f.unlink()
    
    # Jika search, tambahkan prefix ytsearch
    final_query = f"ytsearch1:{query}" if is_search else query
    
    with st.status(f"Sedang memproses: {query}...", expanded=True) as status:
        try:
            # Kita modifikasi sedikit parameter cmd secara dinamis
            # (Untuk kemudahan, kita panggil yt-dlp langsung di sini agar fleksibel dengan format)
            cmd = [
                *main.yt_dlp_cmd(),
                "--extract-audio",
                "--audio-format", audio_format,
                "--audio-quality", "0",
                "--output", f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
                "--no-playlist" if not is_playlist else "--playlist-items", f"1-{playlist_limit}",
                "--add-metadata", "--embed-thumbnail",
                final_query
            ]
            
            subprocess.run(cmd, check=True)
            status.update(label="✅ Selesai!", state="complete")
            
            # Tampilkan Preview & Download
            files = list(DOWNLOAD_DIR.glob(f"*.{audio_format}"))
            if files:
                for file_path in files:
                    st.write(f"🎵 **{file_path.name}**")
                    st.audio(str(file_path)) # PREVIEW PLAYER
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"💾 Download {file_path.name}",
                            data=f,
                            file_name=file_path.name,
                            mime=f"audio/{audio_format}"
                        )
                st.balloons()
            else:
                st.error("File tidak ditemukan.")
        except Exception as e:
            st.error(f"Error: {e}")

# TAB 1: SEARCH
with tab1:
    search_query = st.text_input("Cari judul lagu, artis, atau remix:", placeholder="Contoh: Raingurl Ekany Remix")
    if st.button("CARI & DOWNLOAD"):
        if search_query:
            is_playlist = False
            process_download(search_query, is_search=True)

# TAB 2: DIRECT URL / BATCH
with tab2:
    urls = st.text_area("Masukkan URL (Satu link per baris untuk Batch Download):", placeholder="https://youtube.com/...\nhttps://soundcloud.com/...")
    if st.button("PROSES SEMUA LINK"):
        if urls:
            url_list = [u.strip() for u in urls.split("\n") if u.strip()]
            for single_url in url_list:
                is_playlist = any(x in single_url.lower() for x in ["playlist", "album", "sets", "list="])
                process_download(single_url)
        else:
            st.warning("Masukkan link dulu!")

st.divider()
st.markdown("<center><small>STREAMDOWN v2.0 Pro • Built for DJs</small></center>", unsafe_allow_html=True)
