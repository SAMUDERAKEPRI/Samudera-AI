import streamlit as st
import asyncio
import edge_tts
import os
import subprocess
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri AI - Premium Voice", page_icon="💰", layout="wide")
LOGO_URL = "https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/logo.png"
BGM_FILE = "news_bgm.mp3"

# --- DATABASE KODE AKSES (SIMULASI PELANGGAN) ---
# Di sini Bapak bisa menambah atau menghapus user yang sudah bayar langganan
DAFTAR_PELANGGAN = {
    "admin_sk": "sk_pusat_2024",       # Password Bapak (Admin)
    "member_pro": "kepri_bangkit",     # Contoh User Berbayar 1
    "user_test": "coba_ai"             # Contoh User Berbayar 2
}

# --- FUNGSI GENERATE SUARA ---
async def generate_voice(text, voice_id, output_file):
    communicate = edge_tts.Communicate(text, voice_id, rate="+0%", volume="+0%")
    await communicate.save(output_file)

# --- SISTEM LOGIN MULTI-USER ---
if "user_authenticated" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, width=220)
        st.title("⚓ SamuderaKepri AI Login")
        st.info("Silakan masukkan Kode Akses Berlangganan Anda.")
        
        user_input = st.text_input("Username / ID Pelanggan:")
        pass_input = st.text_input("Kode Akses (Password):", type="password")
        
        if st.button("Masuk Ke Sistem"):
            if user_input in DAFTAR_PELANGGAN and DAFTAR_PELANGGAN[user_input] == pass_input:
                st.session_state["user_authenticated"] = True
                st.session_state["username"] = user_input
                st.success(f"Selamat Datang, {user_input}!")
                st.rerun()
            else:
                st.error("ID atau Kode Akses Salah/Sudah Kedaluwarsa. Hubungi Admin SamuderaKepri.")
    st.stop()

# --- TAMPILAN UTAMA (SETELAH LOGIN) ---
st.sidebar.image(LOGO_URL, width=100)
st.sidebar.title("Panel Pelanggan")
st.sidebar.write(f"Logged in as: **{st.session_state['username']}**")
if st.sidebar.button("Log Out"):
    del st.session_state["user_authenticated"]
    st.rerun()

st.title("🎙️ SamuderaKepri Broadcast Engine")
st.caption("Mesin Narasi Berita Otomatis untuk Konten Kreator & Media")
st.divider()

# AREA INPUT
teks_input = st.text_area("Masukkan Narasi Berita Anda (Maksimal 5000 karakter):", height=200)

col1, col2 = st.columns(2)
with col1:
    pilihan_suara = st.selectbox("Pilih Karakter Suara:", [
        ("🧔 Ardi (Pria - Tegas)", "id-ID-ArdiNeural"),
        ("👩 Gadis (Wanita - Profesional)", "id-ID-GadisNeural")
    ], format_func=lambda x: x[0])
with col2:
    pilihan_musik = st.checkbox("Gunakan Musik Latar Khas SamuderaKepri", value=True)

# PROSES PRODUKSI
if st.button("🚀 PRODUKSI AUDIO SEKARANG"):
    if teks_input:
        with st.spinner("Sedang meramu audio kualitas studio..."):
            try:
                voice_temp = "temp_voice.mp3"
                final_output = f"HASIL_AI_{st.session_state['username']}_{datetime.now().strftime('%H%M%S')}.mp3"
                
                # 1. Generate Voice
                asyncio.run(generate_voice(teks_input, pilihan_suara[1], voice_temp))
                
                # 2. Gabungkan BGM
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

                # 3. Hasil
                st.success("✅ File Audio Berhasil Dibuat!")
                st.audio(final_output)
                with open(final_output, "rb") as f:
                    st.download_button("📥 Unduh File MP3", data=f, file_name=final_output)
                os.remove(final_output)

            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Silakan masukkan teks narasi terlebih dahulu.")
