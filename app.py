import streamlit as st
import google.generativeai as genai
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from gtts import gTTS  # INI YANG TADI TERLUPA, PAK!
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri AI Engine", page_icon="⚓", layout="wide")
LOGO_URL = "https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/logo.png"

# AMBIL RAHASIA DARI SISTEM (STREAMS SECRETS)
api_key_otomatis = st.secrets.get("GEMINI_API_KEY", "")
password_sistem = st.secrets.get("APP_PASSWORD", "admin123")
wp_url = st.secrets.get("WP_URL", "")
wp_user = st.secrets.get("WP_USER", "")
wp_app_pwd = st.secrets.get("WP_APP_PWD", "")

# --- FUNGSI LOGIN ---
if "password_correct" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, width=250)
        st.title("⚓ Akses Redaksi")
        pwd = st.text_input("Kode Akses:", type="password")
        if st.button("Masuk"):
            if pwd == password_sistem:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Kode Salah!")
    st.stop()

# --- HEADER UTAMA ---
head_col1, head_col2 = st.columns([1, 5])
with head_col1:
    st.image(LOGO_URL, width=120)
with head_col2:
    st.title("SamuderaKepri News Engine")
    st.caption("Pusat Kendali Redaksi & Voice Generator - Tanjungpinang, Kepri")

# --- LOGIKA UTAMA ---
if api_key_otomatis:
    try:
        genai.configure(api_key=api_key_otomatis)
        available_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.subheader("📝 Olah Berita")
            model_pilihan = st.selectbox("Pilih Model AI:", available_models)
            teks_mentah = st.text_area("Tempel Teks Mentah / Rilis:", height=250)
            gaya = st.selectbox("Gaya Penulisan:", ["Investigatif & Tajam", "Formal Jurnalistik", "Populer & Ringan"])
            
            if st.button("🚀 Proses Sekarang"):
                if teks_mentah:
                    with st.spinner("Sedang mengolah data..."):
                        model = genai.GenerativeModel(model_pilihan)
                        prompt = f"Sebagai Editor Senior SamuderaKepri, tulis ulang teks ini menjadi berita profesional (Berikan Judul di baris pertama) dengan gaya {gaya}: {teks_mentah}"
                        response = model.generate_content(prompt)
                        st.session_state['hasil_berita'] = response.text
                else:
                    st.warning("Masukkan teks dulu, Pak.")

        with col2:
            st.subheader("📰 Hasil & Fitur Lanjutan")
            if 'hasil_berita' in st.session_state:
                hasil = st.session_state['hasil_berita']
                st.text_area("Cek Hasil Redaksi:", hasil, height=250)
                
                # --- TAB FITUR ---
                tab_wp, tab_tts = st.tabs(["🌐 Kirim ke Website", "🔊 Buat Suara (TTS)"])
                
                with tab_wp:
                    judul_wp = st.text_input("Judul untuk Website:")
                    if st.button("Kirim ke Draf WordPress"):
                        if judul_wp and wp_url:
                            # Logika kirim WP
                            endpoint = f"{wp_url}/wp-json/wp/v2/posts"
                            res = requests.post(endpoint, json={'title': judul_wp, 'content': hasil, 'status': 'draft'}, auth=HTTPBasicAuth(wp_user, wp_app_pwd))
                            if res.status_code == 201: st.success("✅ Berhasil masuk Draf Website!")
                            else: st.error(f"Gagal! Cek konfigurasi WP Bapak.")
                
                with tab_tts:
                    if st.button("🎙️ Ubah Menjadi Suara"):
                        with st.spinner("Sedang mengisi suara narasi..."):
                            tts = gTTS(text=hasil, lang='id')
                            tts.save("berita_audio.mp3")
                            st.audio("berita_audio.mp3")
                            with open("berita_audio.mp3", "rb") as file:
                                st.download_button("📥 Unduh Audio (MP3)", data=file, file_name=f"Audio_SK_{datetime.now().strftime('%d%m')}.mp3")

    except Exception as e:
        st.error(f"Terjadi kendala: {str(e)}")
