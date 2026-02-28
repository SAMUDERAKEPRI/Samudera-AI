import streamlit as st
import asyncio
import edge_tts
import os
import subprocess
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri Voice Pro", page_icon="🎙️", layout="wide")
LOGO_URL = "https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/logo.png"
BGM_FILE = "news_bgm.mp3"

# AMBIL PASSWORD DARI SECRETS (Tidak butuh API Key Suara lagi!)
password_sistem = st.secrets.get("APP_PASSWORD", "admin123")

# --- FUNGSI GENERATE SUARA MICROSOFT AZURE ---
async def generate_voice(text, voice_id, output_file):
    # Menggunakan rate +0% (normal) dan volume normal
    communicate = edge_tts.Communicate(text, voice_id, rate="+0%", volume="+0%")
    await communicate.save(output_file)

# --- SISTEM LOGIN ---
if "password_correct" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, width=250)
        st.title("🎙️ Redaksi Voice Pro")
        pwd = st.text_input("Kode Akses:", type="password")
        if st.button("Masuk"):
            if pwd == password_sistem:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Kode Salah!")
    st.stop()

# --- TAMPILAN UTAMA ---
st.image(LOGO_URL, width=120)
st.title("⚓ SamuderaKepri Broadcast Engine")
st.caption("Mesin Penyiar Berita AI (Powered by Microsoft Azure Neural - 100% Gratis)")
st.divider()

teks_input = st.text_area("Masukkan Narasi Berita:", height=250)

col1, col2 = st.columns(2)
with col1:
    # Tersedia Suara Pria (Ardi) dan Wanita (Gadis) dari Microsoft
    pilihan_suara = st.selectbox("Pilih Penyiar Studio:", [
        ("🧔 Ardi (Pria - Tegas & Berwibawa)", "id-ID-ArdiNeural"),
        ("👩 Gadis (Wanita - Profesional & Jelas)", "id-ID-GadisNeural")
    ], format_func=lambda x: x[0])
with col2:
    pilihan_musik = st.checkbox("Gabungkan dengan Musik Latar (BGM)", value=True)

if st.button("🚀 PRODUKSI SUARA SIARAN"):
    if teks_input:
        with st.spinner("Memproses suara penyiar Microsoft Neural..."):
            try:
                voice_temp = "temp_voice.mp3"
                final_output = f"BERITA_SK_{datetime.now().strftime('%H%M%S')}.mp3"
                
                # 1. Panggil sistem Microsoft Edge TTS (Gratis)
                asyncio.run(generate_voice(teks_input, pilihan_suara[1], voice_temp))
                
                # 2. Gabungkan Musik
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

                # 3. Tampilkan Audio
                if os.path.exists(final_output):
                    st.success("✅ Produksi Selesai! Tidak ada pemotongan kuota.")
                    st.audio(final_output)
                    with open(final_output, "rb") as f:
                        st.download_button("📥 Unduh Hasil Produksi", data=f, file_name=final_output, mime="audio/mp3")
                    os.remove(final_output)
                else:
                    st.error("Gagal menggabungkan audio.")

            except Exception as e:
                st.error(f"Terjadi kesalahan teknis: {str(e)}")
    else:
        st.warning("Isi teks beritanya dulu, Pak.")
