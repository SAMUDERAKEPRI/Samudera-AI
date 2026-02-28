import streamlit as st
import asyncio
import edge_tts
import os
import subprocess
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri AI Premium", page_icon="🎙️", layout="wide")

# --- CUSTOM CSS UNTUK TAMPILAN MEWAH ---
st.markdown("""
    <style>
    /* Mengubah font dan background */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400;700&display=swap');
    
    .stApp {
        background-color: #0e1117;
    }
    
    /* Header Styling */
    .main-header {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        text-align: center;
        text-shadow: 2px 2px 10px #00d4ff55;
    }
    
    /* Kotak Input dan Area Teks */
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
    }
    
    /* Tombol Produksi - Efek Glow */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #007cf0, #00dfd8);
        color: white;
        border: none;
        padding: 15px 30px;
        font-weight: bold;
        border-radius: 50px;
        width: 100%;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    }
    
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5);
    }
    
    /* Kartu Sidebar */
    .css-163ttbj {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Success Message */
    .stAlert {
        border-radius: 15px;
        background-color: #092540;
        color: #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

LOGO_URL = "https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/logo.png"
BGM_FILE = "news_bgm.mp3"

# DATABASE PELANGGAN
DAFTAR_PELANGGAN = {
    "admin_sk": "sk_pusat_2024",
    "member_pro": "kepri_bangkit"
}

# FUNGSI TTS
async def generate_voice(text, voice_id, output_file):
    communicate = edge_tts.Communicate(text, voice_id, rate="+0%", volume="+0%")
    await communicate.save(output_file)

# --- LOGIN PAGE ---
if "user_authenticated" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        st.image(LOGO_URL, width=180)
        st.markdown("<h2 class='main-header'>SAMUDERA KEPRI AI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#8b949e;'>Premium Voice Production System</p>", unsafe_allow_html=True)
        
        with st.container():
            user_input = st.text_input("Username:")
            pass_input = st.text_input("Password:", type="password")
            if st.button("UNLOCK ACCESS"):
                if user_input in DAFTAR_PELANGGAN and DAFTAR_PELANGGAN[user_input] == pass_input:
                    st.session_state["user_authenticated"] = True
                    st.session_state["username"] = user_input
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
    st.stop()

# --- MAIN INTERFACE ---
st.sidebar.image(LOGO_URL, width=120)
st.sidebar.markdown(f"### 👤 {st.session_state['username'].upper()}")
st.sidebar.markdown("---")
st.sidebar.write("✅ **Status:** Premium Member")
st.sidebar.write("📍 **Region:** Kepulauan Riau")
if st.sidebar.button("Logout"):
    del st.session_state["user_authenticated"]
    st.rerun()

# Konten Utama
st.markdown("<h1 class='main-header'>🎙️ BROADCAST ENGINE PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#8b949e;'>Transformasikan narasi berita menjadi audio profesional dalam hitungan detik.</p>", unsafe_allow_html=True)
st.divider()

# Area Input dengan layout Grid
col_a, col_b = st.columns([2, 1])

with col_a:
    teks_input = st.text_area("✍️ Tulis Narasi Berita Anda di Sini:", height=300, placeholder="Contoh: Tim investigasi Samudera Kepri melaporkan bahwa...")

with col_b:
    st.markdown("### ⚙️ Pengaturan")
    pilihan_suara = st.selectbox("Pilih Penyiar:", [
        ("🧔 Ardi (Pria - Tegas)", "id-ID-ArdiNeural"),
        ("👩 Gadis (Wanita - Jernih)", "id-ID-GadisNeural")
    ], format_func=lambda x: x[0])
    
    pilihan_musik = st.checkbox("🎶 Gunakan Musik Latar", value=True)
    
    st.info("Kualitas Audio: 48kHz Stereo (High Fidelity)")
    
    if st.button("🚀 PRODUKSI SEKARANG"):
        if teks_input:
            with st.spinner("⏳ Sedang memproses audio..."):
                try:
                    voice_temp = "temp_voice.mp3"
                    final_output = f"PRO_AUDIO_{datetime.now().strftime('%H%M%S')}.mp3"
                    
                    asyncio.run(generate_voice(teks_input, pilihan_suara[1], voice_temp))
                    
                    if pilihan_musik and os.path.exists(BGM_FILE):
                        command = [
                            "ffmpeg", "-y", "-i", voice_temp, "-stream_loop", "-1", "-i", BGM_FILE, 
                            "-filter_complex", "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2", 
                            final_output
                        ]
                        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        os.remove(voice_temp)
                    else:
                        os.rename(voice_temp, final_output)

                    st.markdown("---")
                    st.success("✨ Produksi Selesai! Klik tombol di bawah untuk mendengarkan.")
                    st.audio(final_output)
                    with open(final_output, "rb") as f:
                        st.download_button("📥 DOWNLOAD MP3", data=f, file_name=final_output)
                    os.remove(final_output)
                except Exception as e:
                    st.error(f"Teknis Error: {e}")
        else:
            st.warning("Silakan isi teks berita dulu, Pak.")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#30363d;'>© 2024 SamuderaKepri Media Group - AI Division</p>", unsafe_allow_html=True)
