import streamlit as st
import google.generativeai as genai
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

# --- KONFIGURASI ---
st.set_page_config(page_title="SamuderaKepri AI Engine", page_icon="⚓", layout="wide")
LOGO_URL = "https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/logo.png"

# AMBIL RAHASIA
api_key_otomatis = st.secrets.get("GEMINI_API_KEY", "")
password_sistem = st.secrets.get("APP_PASSWORD", "admin123")
wp_url = st.secrets.get("WP_URL", "")
wp_user = st.secrets.get("WP_USER", "")
wp_app_pwd = st.secrets.get("WP_APP_PWD", "")

# --- FUNGSI POST KE WORDPRESS ---
def kirim_ke_wordpress(title, content):
    endpoint = f"{wp_url}/wp-json/wp/v2/posts"
    post_data = {
        'title': title,
        'content': content,
        'status': 'draft' # Masuk sebagai draf agar bisa diperiksa dulu
    }
    response = requests.post(
        endpoint, 
        json=post_data, 
        auth=HTTPBasicAuth(wp_user, wp_app_pwd)
    )
    return response

# --- SISTEM LOGIN (Sama seperti sebelumnya) ---
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
                st.error("Salah!")
    st.stop()

# --- DASHBOARD UTAMA ---
st.image(LOGO_URL, width=120)
st.title("SamuderaKepri News Engine")
st.caption("Pusat Kendali Redaksi - Terkoneksi ke Website")

if api_key_otomatis:
    try:
        genai.configure(api_key=api_key_otomatis)
        available_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.subheader("📝 Olah Berita")
            model_pilihan = st.selectbox("Pilih Model:", available_models)
            teks_mentah = st.text_area("Teks Mentah:", height=250)
            gaya = st.selectbox("Gaya:", ["Investigatif & Tajam", "Formal", "Populer"])
            
            if st.button("🚀 Proses Sekarang"):
                if teks_mentah:
                    with st.spinner("Sedang menulis..."):
                        model = genai.GenerativeModel(model_pilihan)
                        prompt = f"Sebagai Editor Senior SamuderaKepri, tulis ulang teks ini menjadi berita profesional (Berikan Judul di baris pertama) dengan gaya {gaya}: {teks_mentah}"
                        response = model.generate_content(prompt)
                        st.session_state['hasil_berita'] = response.text
                else:
                    st.warning("Isi teksnya dulu, Pak.")

        with col2:
            st.subheader("📰 Hasil & Publikasi")
            if 'hasil_berita' in st.session_state:
                hasil = st.session_state['hasil_berita']
                st.text_area("Cek Hasil:", hasil, height=300)
                
                # Form pengiriman ke WP
                judul_wp = st.text_input("Konfirmasi Judul untuk Website:")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🌐 Kirim ke Draf WordPress"):
                        if judul_wp:
                            res = kirim_ke_wordpress(judul_wp, hasil)
                            if res.status_code == 201:
                                st.success("✅ Berhasil masuk ke Draf Website!")
                            else:
                                st.error(f"Gagal! Error: {res.status_code}")
                        else:
                            st.warning("Isi judul dulu untuk WP, Pak.")
                with col_btn2:
                    st.download_button("📥 Simpan ke PC", hasil, f"Berita_{datetime.now().strftime('%d%m')}.txt")

    except Exception as e:
        st.error(f"Sistem Error: {str(e)}")
        from gtts import gTTS
import os

# --- BAGIAN TTS DI DALAM KOLOM HASIL REDAKSI ---
st.subheader("🔊 Konversi ke Suara (TTS)")
if 'hasil_berita' in st.session_state:
    audio_text = st.session_state['hasil_berita']
    
    # Pilihan Bahasa (Indonesia secara default)
    if st.button("Generate Suara Narasi"):
        with st.spinner("Sedang mengisi suara..."):
            tts = gTTS(text=audio_text, lang='id')
            tts.save("berita_audio.mp3")
            
            # Putar Audio di Streamlit
            audio_file = open("berita_audio.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
            
            # Tombol Unduh Audio
            st.download_button(
                label="📥 Unduh Audio Berita",
                data=audio_bytes,
                file_name=f"Audio_SK_{datetime.now().strftime('%d%m%Y')}.mp3",
                mime="audio/mp3"
            )

