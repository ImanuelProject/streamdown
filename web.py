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

# Fungsi untuk load Lottie Animation
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_dj = load_lottieurl("https://lottie.host/626d17e5-182f-41a4-972c-e66699d63c5d/FjC4h9mYjG.json")
lottie_success = load_lottieurl("https://lottie.host/f44b2046-8806-444d-b0f1-41916327386d/E8mZqS8S9i.json")

# 2. CUSTOM CSS (PREMIUM UI/UX)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap');
    
    * { font-family: 'Outfit', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    
    /* Card Style (Glassmorphism) */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Neon Button */
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 700;
        padding: 15px 30px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 4px 15px rgba(0, 210, 255, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 210, 255, 0.5);
        background: linear-gradient(90deg, #3a7bd5 0%, #00d2ff 100%);
    }
    
    /* Custom Input */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    h1, h2, h3 { color: #00d2ff !important; text-shadow: 0 0 10px rgba(0, 210, 255, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR (GLASS UI)
with st.sidebar:
    if lottie_dj:
        st_lottie(lottie_dj, height=150, key="sidebar_dj")
    st.markdown("<h2 style='text-align: center;'>⚙️ CONTROL</h2>", unsafe_allow_html=True)
    
    audio_format = st.selectbox("FORMAT", ["mp3", "wav", "flac"])
    
    st.divider()
    normalize = st.toggle("LOUDNESS NORMALIZATION", value=True)
    trim_silence = st.toggle("AUTO-TRIM SILENCE", value=True)
    
    st.divider()
    st.markdown("### 🔑 SPOTIFY KEYS")
    sp_id = st.text_input("ID", type="password")
    sp_secret = st.text_input("SECRET", type="password")
    
    st.divider()
    playlist_limit = st.number_input("LIMIT", min_value=1, value=50)

# 4. MAIN CONTENT
col_title, col_anim = st.columns([2, 1])
with col_title:
    st.markdown("<h1 style='font-size: 50px;'>STREAMDOWN<br><span style='color: white;'>ULTIMATE</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; opacity: 0.8;'>Engineered for Professional DJs & Music Curators.</p>", unsafe_allow_html=True)

with col_anim:
    if lottie_dj:
        st_lottie(lottie_dj, height=200, key="main_dj")

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🔍 SEARCH", "🔗 URL BATCH", "💚 SPOTIFY"])

# Folder Download Sementara di /tmp (Lebih Stabil untuk Linux/Cloud)
DOWNLOAD_DIR = Path("/tmp/downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def process_download(query, is_search=False, engine="YouTube"):
    # Deteksi jika user paste URL di kotak search
    if is_search and query.startswith("http"):
        final_query = query
        is_search = False
    elif is_search:
        final_query = f"ytsearch1:{query}" if engine == "YouTube" else f"scsearch1:{query}"
    else:
        final_query = query
    
    with st.status(f"⚡ Processing: {query}", expanded=True) as status:
        try:
            cmd = [*main.yt_dlp_cmd(), "--extract-audio", "--audio-format", audio_format, "--audio-quality", "0", 
                   "--output", f"{DOWNLOAD_DIR}/%(title)s.%(ext)s", "--add-metadata", "--embed-thumbnail"]
            
            # Perbaikan Logika Playlist
            if any(x in query.lower() for x in ["playlist", "album", "sets", "list="]):
                cmd.extend(["--playlist-items", f"1-{playlist_limit}"])
            else:
                cmd.append("--no-playlist")
            
            filters = []
            if normalize: filters.append("loudnorm=I=-14:LRA=7:tp=-2")
            if trim_silence: filters.append("silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,silenceremove=stop_periods=1:stop_silence=0.1:stop_threshold=-50dB")
            
            # Tambahkan -threads 1 untuk stabilitas di Cloud
            if filters:
                cmd.extend(["--postprocessor-args", f"ffmpeg:-af {','.join(filters)} -threads 1"])
            else:
                cmd.extend(["--postprocessor-args", "ffmpeg:-threads 1"])
            
            cmd.append(final_query)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                st.error("❌ Detail Error dari Server:")
                st.code(result.stderr) # Menampilkan error asli dari yt-dlp/ffmpeg
                status.update(label="❌ Gagal", state="error")
            else:
                status.update(label=f"✅ {query} Finished", state="complete")
        except Exception as e:
            st.error(f"Error: {e}")

with tab1:
    col_s, col_e = st.columns([3, 1])
    with col_s: s_query = st.text_input("What are we looking for?", placeholder="Artist - Title (Remix)")
    with col_e: s_engine = st.selectbox("SOURCE", ["YouTube", "SoundCloud"])
    if st.button("🔥 HUNT SONG"):
        if s_query: process_download(s_query, is_search=True, engine=s_engine)

with tab2:
    urls = st.text_area("Paste Multiple Links:")
    if st.button("⚡ EXECUTE BATCH"):
        for u in urls.split("\n"):
            if u.strip(): process_download(u.strip())

with tab3:
    sp_url = st.text_input("Paste Spotify Playlist URL:")
    if st.button("❇️ SYNC SPOTIFY"):
        if not sp_id or not sp_secret: st.error("Please provide Spotify Keys in the sidebar!")
        elif sp_url:
            try:
                import spotipy
                from spotipy.oauth2 import SpotifyClientCredentials
                sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=sp_id, client_secret=sp_secret))
                tracks = sp.playlist_items(sp_url)['items']
                for item in tracks:
                    process_download(f"{item['track']['artists'][0]['name']} - {item['track']['name']}", is_search=True)
            except Exception as e: st.error(f"Failed: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# 5. RESULTS AREA
files = list(DOWNLOAD_DIR.glob(f"*.{audio_format}"))
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown(f"### 📦 VAULT")

if files:
    st.markdown(f"**{len(files)} tracks ready for your Rekordbox library!**")
    
    # ZIP BUTTON
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as z:
        for f in files: z.write(f, f.name)
    
    st.download_button("🎁 DOWNLOAD MASTER ZIP", zip_buffer.getvalue(), "streamdown_pro_pack.zip", "application/zip")
    
    # INDIVIDUAL CARDS
    for f_path in files:
        with st.expander(f"🎵 {f_path.name}"):
            st.audio(str(f_path))
            with open(f_path, "rb") as f:
                st.download_button(f"SAVE {f_path.name}", f, file_name=f_path.name, mime=f"audio/{audio_format}")
    
    if st.button("🗑️ CLEAR VAULT"):
        for f in DOWNLOAD_DIR.glob("*"): f.unlink()
        st.rerun()
else:
    st.info("Your vault is currently empty. Start hunting some tracks above! 🎧")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='opacity: 0.5;'>STREAMDOWN v3.0 • Premium DJ Workstation</center>", unsafe_allow_html=True)
