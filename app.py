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
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400;700&display=swap');
    
    .stApp { background-color: #0e1117; }
    
    .main-header {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        text-align: center;
        text-shadow: 2px 2px 10px #00d4ff55;
    }

    /* Styling Kotak Info Langganan */
    .promo-box {
        background: linear-gradient(45deg, #161b22, #0d1117);
        border: 1px dashed #00d4ff;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 20px;
    }

    .wa-button {
        background-color: #25d366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }

    div.stButton > button:first-child {
        background: linear-gradient(45deg, #007cf0, #00dfd8);
        color: white; border: none; padding: 12px;
        font-weight: bold; border-radius: 50px; width: 100%;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
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
        
        with st.container():
            user_input = st.text_input("Username:")
            pass_input = st.text_input("Password:", type="password")
            if st.button("UNLOCK ACCESS"):
                if user_input in DAFTAR_PELANGGAN and DAFTAR_PELANGGAN[user_input] == pass_input:
                    st.session_state["user_authenticated"] = True
                    st.session_state["username"] = user_input
                    st.rerun()
                else:
                    st.error("Gagal Login. Pastikan Username & Password Benar.")

        # INFO LANGGANAN UNTUK PENGUNJUNG BARU
        st.markdown(f"""
            <div class="promo-box">
                <p style="color: #8b949e; margin-bottom: 5px;">Belum punya akses? Miliki akun Premium sekarang!</p>
                <p style="color: #00d4ff; font-weight: bold; margin-bottom: 5px;">📧 admin@samuderakepri.co.id</p>
                <a href="https://wa.me/6281276520021?text=Halo%20Admin%20SamuderaKepri,%20saya%20tertarik%20berlangganan%20AI%20Voice%20Premium" class="wa-button">
                    💬 Chat WA: 0812 7652 0021
                </a>
            </div>
        """, unsafe_allow_html=True)
    st.stop()

# --- MAIN INTERFACE (SETELAH LOGIN) ---
st.sidebar.image(LOGO_URL, width=120)
st.sidebar.markdown(f"### 👤 {st.session_state['username'].upper()}")
st.sidebar.write("✅ **Status:** Premium Member")
st.sidebar.markdown("---")

# Info Admin di Sidebar
st.sidebar.info("Bantuan & Perpanjangan:")
st.sidebar.write("📧 admin@samuderakepri.co.id")
st.sidebar.write("📞 0812 7652 0021")

if st.sidebar.button("Logout"):
    del st.session_state["user_authenticated"]
    st.rerun()

# Konten Utama
st.markdown("<h1 class='main-header'>🎙️ BROADCAST ENGINE PRO</h1>", unsafe_allow_html=True)
st.divider()

col_a, col_b = st.columns([2, 1])
with col_a:
    teks_input = st.text_area("✍️ Tulis Narasi Berita Anda:", height=300)

with col_b:
    st.markdown("### ⚙️ Pengaturan")
    pilihan_suara = st.selectbox("Pilih Penyiar:", [
        ("🧔 Ardi (Pria - Tegas)", "id-ID-ArdiNeural"),
        ("👩 Gadis (Wanita - Jernih)", "id-ID-GadisNeural")
    ], format_func=lambda x: x[0])
    pilihan_musik = st.checkbox("🎶 Gunakan Musik Latar", value=True)
    
    if st.button("🚀 PRODUKSI SEKARANG"):
        if teks_input:
            with st.spinner("⏳ Memproses audio..."):
                try:
                    voice_temp = "temp_voice.mp3"
                    final_output = f"PRO_AUDIO_{datetime.now().strftime('%H%M%S')}.mp3"
                    asyncio.run(generate_voice(teks_input, pilihan_suara[1], voice_temp))
                    
                    if pilihan_musik and os.path.exists(BGM_FILE):
                        command = ["ffmpeg", "-y", "-i", voice_temp, "-stream_loop", "-1", "-i", BGM_FILE, "-filter_complex", "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2", final_output]
                        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        os.remove(voice_temp)
                    else:
                        os.rename(voice_temp, final_output)

                    st.success("✨ Selesai!")
                    st.audio(final_output)
                    with open(final_output, "rb") as f:
                        st.download_button("📥 DOWNLOAD MP3", data=f, file_name=final_output)
                    os.remove(final_output)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Isi teks dulu, Pak.")

st.markdown("<p style='text-align:center; color:#30363d; margin-top:50px;'>© 2024 SamuderaKepri Media Group</p>", unsafe_allow_html=True)
# --- KODE PEMBERSIH TAMPILAN (PASTE DI PALING BAWAH) ---
st.markdown("""
    <style>
    /* Sembunyikan Header (Logo Github, tombol Deploy, dsb) */
    header {visibility: hidden !important;}
    
    /* Sembunyikan Footer (Made with Streamlit) */
    footer {visibility: hidden !important;}
    
    /* Sembunyikan Dekorasi Garis Berwarna di paling atas */
    [data-testid="stDecoration"] {display: none !important;}
    
    /* Sembunyikan Menu Hamburger (Titik tiga di pojok kanan) */
    #MainMenu {visibility: hidden !important;}
    
    /* Hilangkan jarak kosong berlebih di bagian atas layar */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Sembunyikan elemen 'Manage app' yang terkadang muncul di pojok kanan bawah */
    .stAppToolbar {display: none !important;}
    </style>
""", unsafe_allow_html=True)
