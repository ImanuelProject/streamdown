import streamlit as st
import main
from pathlib import Path
import os
import subprocess
import zipfile
import io
import json
import requests
from streamlit_lottie import st_lottie

# 1. KONFIGURASI HALAMAN & TEMA
st.set_page_config(page_title="STREAMDOWN ULTIMATE", page_icon="💎", layout="wide")

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_dj = load_lottieurl("https://lottie.host/626d17e5-182f-41a4-972c-e66699d63c5d/FjC4h9mYjG.json")

# CUSTOM CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap');
    * { font-family: 'Outfit', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
    .glass-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 25px; margin-bottom: 20px; }
    .stButton>button { background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); border: none; border-radius: 15px; color: white; font-weight: 700; height: 3.5em; text-transform: uppercase; letter-spacing: 2px; }
    h1, h2, h3 { color: #00d2ff !important; text-shadow: 0 0 10px rgba(0, 210, 255, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    if lottie_dj: st_lottie(lottie_dj, height=150, key="sidebar_dj")
    st.markdown("<h2 style='text-align: center;'>⚙️ CONTROL</h2>", unsafe_allow_html=True)
    audio_format = st.selectbox("FORMAT", ["mp3", "wav", "flac"])
    st.divider()
    st.markdown("### 🔑 SPOTIFY KEYS")
    sp_id = st.text_input("ID", type="password")
    sp_secret = st.text_input("SECRET", type="password")
    playlist_limit = st.number_input("PLAYLIST LIMIT", min_value=1, value=50, help="Maksimal lagu yang diambil dari satu playlist")

# MAIN CONTENT
col_t, col_a = st.columns([2, 1])
with col_t:
    st.markdown("<h1 style='font-size: 50px;'>STREAMDOWN<br><span style='color: white;'>ULTIMATE</span></h1>", unsafe_allow_html=True)
with col_a:
    if lottie_dj: st_lottie(lottie_dj, height=150, key="main_dj")

# Folder Download di /tmp agar stabil
DOWNLOAD_DIR = Path("/tmp/downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def process_download(query, is_search=False, engine="YouTube", is_playlist_mode=False):
    if is_search and query.startswith("http"):
        final_query = query
        is_search = False
    elif is_search:
        final_query = f"ytsearch1:{query}" if engine == "YouTube" else f"scsearch1:{query}"
    else:
        final_query = query
    
    with st.status(f"⚡ Processing: {query}", expanded=is_search) as status:
        try:
            cmd = [*main.yt_dlp_cmd(), "--extract-audio", "--audio-format", audio_format, "--audio-quality", "0", 
                   "--output", f"{DOWNLOAD_DIR}/%(title)s.%(ext)s", "--restrict-filenames",
                   "--add-metadata", "--embed-thumbnail",
                   "--concurrent-fragments", "5"] # Download 1 lagu pakai 5 jalur
            
            # Logika Playlist Otomatis
            if is_playlist_mode or any(x in query.lower() for x in ["playlist", "album", "sets", "list="]):
                cmd.extend(["--playlist-items", f"1-{playlist_limit}"])
            else:
                cmd.append("--no-playlist")
            
            cmd.append(final_query)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                st.error("Error Log:")
                st.code(result.stderr)
                status.update(label="❌ Failed", state="error")
                return False
            
            status.update(label=f"✅ Done!", state="complete")
            return True
        except Exception as e:
            st.error(f"Error: {e}")
            return False

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🔍 SEARCH SINGLE", "📜 PLAYLIST / ALBUM", "💚 SPOTIFY SYNC"])

with tab1:
    col_s, col_e = st.columns([3, 1])
    with col_s: s_query = st.text_input("Find One Song:", placeholder="Artist - Title")
    with col_e: s_engine = st.selectbox("SOURCE", ["YouTube", "SoundCloud"])
    if st.button("🔥 HUNT SONG"):
        if s_query:
            for f in DOWNLOAD_DIR.glob("*"): f.unlink()
            process_download(s_query, is_search=True, engine=s_engine)

with tab2:
    p_url = st.text_input("Paste Playlist / Album / Set URL:", placeholder="Link YouTube Playlist atau SoundCloud Set")
    if st.button("⚡ DOWNLOAD ALL FROM PLAYLIST"):
        if p_url:
            for f in DOWNLOAD_DIR.glob("*"): f.unlink()
            process_download(p_url, is_playlist_mode=True)
            st.success("Playlist processing finished! Check the vault below.")

with tab3:
    sp_url = st.text_input("Spotify Playlist URL:")
    if st.button("❇️ SYNC SPOTIFY"):
        if not sp_id or not sp_secret: st.error("Provide Keys in sidebar!")
        elif sp_url:
            for f in DOWNLOAD_DIR.glob("*"): f.unlink()
            try:
                import spotipy
                from spotipy.oauth2 import SpotifyClientCredentials
                sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=sp_id, client_secret=sp_secret))
                tracks = sp.playlist_items(sp_url)['items']
                progress_bar = st.progress(0)
                for i, item in enumerate(tracks):
                    process_download(f"{item['track']['artists'][0]['name']} - {item['track']['name']}", is_search=True)
                    progress_bar.progress((i + 1) / len(tracks))
            except Exception as e: st.error(f"Failed: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# RESULTS AREA
files = list(DOWNLOAD_DIR.glob(f"*.{audio_format}"))
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown(f"### 📦 VAULT")
if files:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as z:
        for f in files: z.write(f, f.name)
    st.download_button("🎁 DOWNLOAD MASTER ZIP", zip_buffer.getvalue(), "streamdown_pack.zip", "application/zip")
    
    with st.expander("Show/Preview Individual Tracks"):
        for f_path in files:
            st.write(f"🎵 {f_path.name}")
            st.audio(str(f_path))
            with open(f_path, "rb") as f:
                st.download_button(f"SAVE {f_path.name[:20]}...", f, file_name=f_path.name, mime=f"audio/{audio_format}", key=f_path.name)
    if st.button("🗑️ CLEAR VAULT"):
        for f in DOWNLOAD_DIR.glob("*"): f.unlink()
        st.rerun()
else:
    st.info("Vault is empty. Hunt some tracks or playlists! 🎧")
st.markdown('</div>', unsafe_allow_html=True)
