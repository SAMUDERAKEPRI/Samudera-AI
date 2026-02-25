import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri AI Engine", page_icon="⚓", layout="wide")

# MENGAMBIL API KEY SECARA SENYAP (TIDAK TERLIHAT PENGGUNA)
# Sistem akan mencari di 'Secrets' terlebih dahulu
api_key_otomatis = st.secrets.get("GEMINI_API_KEY", "")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { background-color: #004a99; color: white; border-radius: 8px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚓ SamuderaKepri News Engine")
st.caption("Pusat Kendali Redaksi SamuderaKepri.co.id - Tanjungpinang")

# --- SIDEBAR PENGATURAN ---
with st.sidebar:
    st.header("⚙️ Status Mesin")
    
    # LOGIKA PROTEKSI:
    # Jika API Key ditemukan di Secrets, jangan munculkan kotak input.
    if api_key_otomatis:
        st.success("🔒 Koneksi Terenkripsi (Internal)")
        st.info("Mesin Redaksi Aktif & Aman.")
        api_key = api_key_otomatis
    else:
        # Jika belum ada di Secrets, baru munculkan kotak input (untuk Bapak setting awal)
        api_key = st.text_input("Gemini API Key:", type="password")
        st.warning("Masukkan API Key di Secrets untuk menyembunyikan kotak ini.")

# --- LOGIKA UTAMA ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name.replace('models/', '') for m in genai.list_models() 
                            if 'generateContent' in m.supported_generation_methods]
        
        if available_models:
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                st.subheader("📝 Input Berita")
                selected_model_name = st.selectbox("Pilih Model AI:", available_models)
                model = genai.GenerativeModel(selected_model_name)
                
                teks_mentah = st.text_area("Tempel Rilis/Berita Mentah:", height=300)
                gaya = st.selectbox("Gaya Penulisan:", ["Investigatif & Tajam", "Formal Jurnalistik", "Populer & Ringan"])
                proses = st.button("🚀 Tulis Ulang Berita")

            with col2:
                st.subheader("📰 Hasil Redaksi")
                if proses and teks_mentah:
                    with st.spinner("Mengolah berita..."):
                        prompt = f"Sebagai Editor Senior SamuderaKepri.co.id, tulis ulang teks ini dengan gaya {gaya}: {teks_mentah}"
                        response = model.generate_content(prompt)
                        hasil = response.text
                        st.info(hasil)
                        st.download_button(
                            label="📥 Simpan Berita (.txt)",
                            data=hasil,
                            file_name=f"Berita_SK_{datetime.now().strftime('%d%m%Y')}.txt",
                            mime="text/plain"
                        )
    except Exception as e:
        st.error(f"Sistem Sibuk: Pastikan API Key aktif.")
else:
    st.error("⚠️ Mesin belum dikonfigurasi. Hubungi Editor-in-Chief.")
