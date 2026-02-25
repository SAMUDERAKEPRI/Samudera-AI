import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- KONFIGURASI ---
st.set_page_config(page_title="SamuderaKepri AI Engine", page_icon="⚓", layout="wide")

# Mengambil API Key dari Secrets secara otomatis
# Jika tidak ada di Secrets, baru minta input manual
api_key_secret = st.secrets.get("GEMINI_API_KEY", "")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { background-color: #004a99; color: white; border-radius: 8px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚓ SamuderaKepri News Engine")
st.caption("Pusat Kendali Redaksi SamuderaKepri.co.id - Tanjungpinang")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Pengaturan")
    # Jika API Key sudah ada di Secrets, kolom ini akan terisi otomatis
    api_key = st.text_input("Gemini API Key:", type="password", value=api_key_secret)
    st.divider()
    st.info("Mesin ini siap mengolah rilis menjadi berita investigatif yang tajam.")

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
                # Pilih Gemini 2.5 Flash jika tersedia di list
                selected_model_name = st.selectbox("Pilih Model AI:", available_models)
                model = genai.GenerativeModel(selected_model_name)
                
                teks_mentah = st.text_area("Tempel Rilis/Berita Mentah:", height=300)
                gaya = st.selectbox("Gaya Penulisan:", ["Investigatif & Tajam", "Formal Jurnalistik", "Populer & Ringan"])
                proses = st.button("🚀 Tulis Ulang Berita")

            with col2:
                st.subheader("📰 Hasil Redaksi")
                if proses and teks_mentah:
                    with st.spinner("Memproses..."):
                        prompt = f"Sebagai Editor Senior SamuderaKepri.co.id, tulis ulang teks ini dengan gaya {gaya}: {teks_mentah}"
                        response = model.generate_content(prompt)
                        hasil = response.text
                        st.info(hasil)
                        
                        # Tombol Unduh
                        st.download_button(
                            label="📥 Simpan Berita (.txt)",
                            data=hasil,
                            file_name=f"Berita_SK_{datetime.now().strftime('%d%m%Y')}.txt",
                            mime="text/plain"
                        )
    except Exception as e:
        st.error(f"Kendala: {str(e)}")
else:
    st.warning("⚠️ Masukkan API Key di sidebar atau simpan di Secrets.")
