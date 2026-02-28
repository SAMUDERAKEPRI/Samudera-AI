import streamlit as st
import os
import subprocess
import requests
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri Voice VIP", page_icon="🎙️", layout="wide")
LOGO_URL = "https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/logo.png"
BGM_FILE = "news_bgm.mp3"

# AMBIL SECRETS
password_sistem = st.secrets.get("APP_PASSWORD", "admin123")
eleven_api_key = st.secrets.get("ELEVENLABS_API_KEY", "")

# --- SISTEM LOGIN ---
if "password_correct" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, width=250)
        st.title("🎙️ Redaksi Voice VIP")
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
st.title("⚓ SamuderaKepri Human Voice Engine")
st.caption("Penyiar Berita Investigasi Hyper-Realistic - Khusus Tanjungpinang")
st.divider()

if not eleven_api_key:
    st.error("⚠️ ELEVENLABS_API_KEY belum ditemukan di Secrets Streamlit.")
    st.stop()

teks_input = st.text_area("Masukkan Narasi Berita:", height=250)

col1, col2 = st.columns(2)
with col1:
    # ID Suara Pria Tegas di ElevenLabs
    # cVOUjw03p17q2lS6hN83 = "Callum" (Tegas, Serius, Berwibawa)
    # pNInz6obpgDQGcFmaJgB = "Adam" (Jernih, Narator Profesional)
    pilihan_suara = st.selectbox("Karakter Suara:", [
        ("Pria Berwibawa & Investigatif", "cVOUjw03p17q2lS6hN83"),
        ("Pria Narator Profesional", "pNInz6obpgDQGcFmaJgB")
    ], format_func=lambda x: x[0])
with col2:
    pilihan_musik = st.checkbox("Gabungkan dengan Musik Latar (BGM)", value=True)

if st.button("🚀 PRODUKSI SUARA MANUSIA ASLI"):
    if teks_input:
        with st.spinner("Memanggil penyiar berita..."):
            try:
                voice_temp = "temp_voice.mp3"
                final_output = f"BERITA_SK_{datetime.now().strftime('%H%M%S')}.mp3"
                
                # 1. Panggil API ElevenLabs
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{pilihan_suara[1]}"
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": eleven_api_key
                }
                data = {
                    "text": teks_input,
                    "model_id": "eleven_multilingual_v2", # Model ini fasih bahasa Indonesia
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
                }
                
                response = requests.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    with open(voice_temp, "wb") as f:
                        f.write(response.content)
                        
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
                    st.success("✅ Penyiar selesai membacakan berita!")
                    st.audio(final_output)
                    with open(final_output, "rb") as f:
                        st.download_button("📥 Unduh Hasil Produksi", data=f, file_name=final_output, mime="audio/mp3")
                    os.remove(final_output)
                else:
                    st.error(f"Gagal memanggil API: {response.text}")

            except Exception as e:
                st.error(f"Terjadi kesalahan teknis: {str(e)}")
    else:
        st.warning("Isi teks beritanya dulu, Pak.")
