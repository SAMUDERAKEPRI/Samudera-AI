import streamlit as st
import asyncio
import edge_tts
import os
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri Voice Pro", page_icon="🎙️", layout="wide")
LOGO_URL = "https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/logo.png"

# AMBIL PASSWORD DARI SECRETS
password_sistem = st.secrets.get("APP_PASSWORD", "admin123")

# --- FUNGSI GENERATE SUARA (ASYNC) ---
async def generate_voice(text, voice_name, output_file):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_file)

# --- SISTEM LOGIN ---
if "password_correct" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, width=250)
        st.title("🎙️ Redaksi Voice Pro")
        st.info("Sistem Narator Otomatis SamuderaKepri.co.id")
        pwd = st.text_input("Kode Akses:", type="password")
        if st.button("Masuk"):
            if pwd == password_sistem:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Kode Salah!")
    st.stop()

# --- TAMPILAN UTAMA ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .stButton>button { background-color: #004a99; color: white; border-radius: 8px; font-weight: bold; height: 3.5em; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

col_logo, col_text = st.columns([1, 5])
with col_logo:
    st.image(LOGO_URL, width=120)
with col_text:
    st.title("⚓ SamuderaKepri Voice Pro")
    st.caption("Narator Berita Pria Tegas - Khusus Redaksi Tanjungpinang")

st.divider()

# INPUT TEKS
st.subheader("📝 Masukkan Teks Berita/Puisi")
teks_input = st.text_area("Tempel teks Bapak di sini (Maksimal 5000 karakter untuk hasil terbaik):", height=300)

col1, col2 = st.columns(2)
with col1:
    # Kita kunci di suara Ardi (Pria Tegas)
    st.write("**Karakter Suara:** 🧔 Ardi (Pria - Berwibawa)")
    voice_id = "id-ID-ArdiNeural" 
with col2:
    pitch = st.slider("Tingkat Kewibawaan (Pitch):", -10, 10, 0)
    # Penyesuaian Pitch di edge-tts menggunakan format string
    pitch_str = f"{pitch:+}Hz"

if st.button("🔊 GENERATE SUARA NEWS ANCHOR"):
    if teks_input:
        with st.spinner("Sedang memproses suara pria tegas..."):
            try:
                output_filename = f"News_SK_{datetime.now().strftime('%H%M%S')}.mp3"
                
                # Menjalankan fungsi async di dalam Streamlit
                asyncio.run(generate_voice(teks_input, voice_id, output_filename))
                
                st.success("✅ Suara Berita Berhasil Dibuat!")
                st.audio(output_filename)
                
                with open(output_filename, "rb") as f:
                    st.download_button(
                        label="📥 Unduh Audio MP3 untuk YouTube/Web",
                        data=f,
                        file_name=output_filename,
                        mime="audio/mp3"
                    )
                
                # Bersihkan file
                os.remove(output_filename)
            except Exception as e:
                st.error(f"Gagal memproses: {str(e)}")
    else:
        st.warning("Silakan isi teks beritanya dulu, Pak Ronny.")

st.divider()
st.markdown("<p style='text-align: center; color: #888;'>Properti Digital SamuderaKepri.co.id</p>", unsafe_allow_html=True)
