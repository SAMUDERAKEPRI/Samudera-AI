import streamlit as st
import asyncio
import edge_tts
import os
import subprocess
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri Cinematic Voice", page_icon="🎙️", layout="wide")
LOGO_URL = "https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/logo.png"
BGM_FILE = "news_bgm.mp3"

# AMBIL PASSWORD
password_sistem = st.secrets.get("APP_PASSWORD", "admin123")

async def generate_voice(text, voice_name, output_file):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_file)

# --- SISTEM LOGIN ---
if "password_correct" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, width=250)
        st.title("🎙️ Redaksi Cinematic Voice")
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
st.title("⚓ SamuderaKepri Voice Pro + BGM")
st.caption("Narator Berita Investigasi dengan Musik Latar Dramatis")
st.divider()

teks_input = st.text_area("Masukkan Narasi Berita:", height=250)
pilihan_musik = st.checkbox("Tambahkan Musik Latar Dramatis", value=True)

if st.button("🚀 PRODUKSI AUDIO CINEMATIC"):
    if teks_input:
        with st.spinner("Sedang meramu suara narator dan musik latar..."):
            try:
                voice_temp = "temp_voice.mp3"
                final_output = f"BERITA_SK_{datetime.now().strftime('%H%M%S')}.mp3"
                
                # 1. Buat Suara Ardi
                asyncio.run(generate_voice(teks_input, "id-ID-ArdiNeural", voice_temp))
                
                # 2. Gabungkan dengan Musik Latar (Langsung lewat server FFmpeg)
                if pilihan_musik and os.path.exists(BGM_FILE):
                    # Rumus untuk mengecilkan volume musik (15%) dan menyamakan durasinya dengan suara narator
                    command = [
                        "ffmpeg", "-y", 
                        "-i", voice_temp, 
                        "-stream_loop", "-1", "-i", BGM_FILE, 
                        "-filter_complex", "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2", 
                        final_output
                    ]
                    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    os.remove(voice_temp) # Bersihkan file sementara
                else:
                    os.rename(voice_temp, final_output)
                    if pilihan_musik:
                        st.warning("⚠️ File news_bgm.mp3 belum ada. Suara diproses tanpa musik.")

                # 3. Tampilkan Hasil
                if os.path.exists(final_output):
                    st.success("✅ Produksi Selesai!")
                    st.audio(final_output)
                    
                    with open(final_output, "rb") as f:
                        st.download_button("📥 Unduh Hasil Produksi", data=f, file_name=final_output, mime="audio/mp3")
                    
                    os.remove(final_output)
                else:
                    st.error("Gagal menggabungkan audio. Sistem sedang sibuk.")

            except Exception as e:
                st.error(f"Terjadi kesalahan teknis: {str(e)}")
    else:
        st.warning("Isi teks beritanya dulu, Pak.")
