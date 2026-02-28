import streamlit as st
import asyncio
import edge_tts
import os
from datetime import datetime
from pydub import AudioSegment # Library pengolah audio

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri Cinematic Voice", page_icon="🎙️", layout="wide")
LOGO_URL = "https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/logo.png"
BGM_FILE = "news_bgm.mp3" # File musik yang Bapak upload ke GitHub

# AMBIL PASSWORD DARI SECRETS
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
        with st.spinner("Sedang meramu suara dan musik..."):
            try:
                # 1. Generate Suara Ardi (Tanpa Musik dulu)
                voice_temp = "temp_voice.mp3"
                asyncio.run(generate_voice(teks_input, "id-ID-ArdiNeural", voice_temp))
                
                final_output = f"BERITA_SK_{datetime.now().strftime('%H%M%S')}.mp3"

                if pilihan_musik and os.path.exists(BGM_FILE):
                    # 2. Proses Penggabungan dengan Pydub
                    voice_audio = AudioSegment.from_file(voice_temp)
                    bgm_audio = AudioSegment.from_file(BGM_FILE)
                    
                    # Kecilkan suara musik agar tidak menabrak suara narator (-20dB)
                    bgm_audio = bgm_audio - 20 
                    
                    # Jika musik lebih pendek, loop musiknya. Jika musik panjang, potong.
                    combined = voice_audio.overlay(bgm_audio, loop=True)
                    
                    # Simpan hasil akhir
                    combined.export(final_output, format="mp3")
                    os.remove(voice_temp) # Hapus file sementara
                else:
                    os.rename(voice_temp, final_output)
                    if pilihan_musik: st.warning("File news_bgm.mp3 tidak ditemukan, suara tanpa musik.")

                st.success("✅ Produksi Selesai!")
                st.audio(final_output)
                
                with open(final_output, "rb") as f:
                    st.download_button("📥 Unduh Hasil Produksi", data=f, file_name=final_output, mime="audio/mp3")
                
                os.remove(final_output)

            except Exception as e:
                st.error(f"Gagal memproses: {str(e)}")
    else:
        st.warning("Isi teks beritanya dulu, Pak.")

st.divider()
st.markdown("<p style='text-align: center; color: #888;'>Inovasi Digital SamuderaKepri.co.id</p>", unsafe_allow_html=True)
