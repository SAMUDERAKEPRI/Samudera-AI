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

# --- FUNGSI MENGAMBIL DAFTAR SUARA DARI ELEVENLABS ---
@st.cache_data(ttl=3600)
def get_elevenlabs_voices(api_key):
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices = response.json().get("voices", [])
        return {v["name"]: v["voice_id"] for v in voices}
    return {}

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

# Tarik otomatis daftar suara penyiar
daftar_suara_asli = get_elevenlabs_voices(eleven_api_key)

if not daftar_suara_asli:
    st.error("Gagal terhubung ke ElevenLabs. Pastikan API Key sudah benar.")
    st.stop()

teks_input = st.text_area("Masukkan Narasi Berita:", height=250)

col1, col2 = st.columns(2)
with col1:
    # Dropdown otomatis dari nama-nama penyiar asli ElevenLabs
    pilihan_nama = st.selectbox("Pilih Penyiar (Otomatis dari ElevenLabs):", list(daftar_suara_asli.keys()))
    id_suara_terpilih = daftar_suara_asli[pilihan_nama]
with col2:
    pilihan_musik = st.checkbox("Gabungkan dengan Musik Latar (BGM)", value=True)

if st.button("🚀 PRODUKSI SUARA MANUSIA ASLI"):
    if teks_input:
        with st.spinner(f"Memanggil {pilihan_nama} untuk siaran berita..."):
            try:
                voice_temp = "temp_voice.mp3"
                final_output = f"BERITA_SK_{datetime.now().strftime('%H%M%S')}.mp3"
                
                # 1. Panggil API ElevenLabs dengan ID Suara yang valid
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{id_suara_terpilih}"
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": eleven_api_key
                }
                data = {
                    "text": teks_input,
                    "model_id": "eleven_multilingual_v2", 
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
                }
                
                response = requests.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    with open(voice_temp, "wb") as f:
                        f.write(response.content)
                        
                    # 2. Gabungkan Musik Latar
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
                    st.success(f"✅ Siaran oleh {pilihan_nama} selesai diproses!")
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
