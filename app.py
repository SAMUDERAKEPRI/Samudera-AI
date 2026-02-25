import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri AI Engine", page_icon="⚓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { background-color: #004a99; color: white; border-radius: 8px; width: 100%; font-weight: bold; }
    .download-btn>button { background-color: #28a745 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚓ SamuderaKepri News Engine")
st.caption("Pusat Kendali Redaksi SamuderaKepri.co.id - Tanjungpinang")

# --- SIDEBAR PENGATURAN ---
with st.sidebar:
    st.header("⚙️ Pengaturan")
    api_key = st.text_input("Gemini API Key:", type="password")
    st.divider()
    st.info("Gunakan API Key untuk mengaktifkan fitur investigasi cerdas.")

# --- LOGIKA APLIKASI ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Deteksi otomatis model yang aktif
        available_models = [m.name.replace('models/', '') for m in genai.list_models() 
                            if 'generateContent' in m.supported_generation_methods]
        
        if available_models:
            st.success(f"✅ Terhubung! Ditemukan {len(available_models)} model aktif.")
            
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                st.subheader("📝 Input Berita")
                selected_model_name = st.selectbox("Pilih Model AI:", available_models, index=0)
                model = genai.GenerativeModel(selected_model_name)
                
                teks_mentah = st.text_area("Tempel Rilis/Berita Mentah:", height=300)
                gaya = st.selectbox("Gaya Penulisan:", ["Investigatif & Tajam", "Formal Jurnalistik", "Populer & Ringan"])
                
                proses = st.button("🚀 Tulis Ulang Berita")

            with col2:
                st.subheader("📰 Hasil Redaksi")
                if proses and teks_mentah:
                    with st.spinner("Editor AI sedang mengolah data..."):
                        prompt = f"""
                        Anda adalah Editor Senior SamuderaKepri.co.id. 
                        Tulis ulang teks berikut dengan gaya {gaya}. 
                        Gunakan struktur piramida terbalik, tajam dalam menganalisis data, 
                        dan pastikan konteks wilayah Kepulauan Riau akurat.
                        
                        Teks: {teks_mentah}
                        """
                        response = model.generate_content(prompt)
                        hasil_berita = response.text
                        
                        # Tampilan Hasil
                        st.info(hasil_berita)
                        
                        st.divider()
                        
                        # FITUR BARU: TOMBOL UNDUH
                        waktu_sekarang = datetime.now().strftime("%d%m%Y_%H%M")
                        nama_file = f"Berita_SamuderaKepri_{waktu_sekarang}.txt"
                        
                        st.download_button(
                            label="📥 Simpan Berita ke Komputer (.txt)",
                            data=hasil_berita,
                            file_name=nama_file,
                            mime="text/plain",
                            help="Klik untuk mengunduh hasil berita dalam format teks."
                        )
                elif proses:
                    st.warning("Silakan isi teks mentahnya dulu, Pak.")
        else:
            st.error("❌ Tidak ada model yang aktif di akun ini.")
            
    except Exception as e:
        st.error(f"Terjadi Kesalahan: {str(e)}")
else:
    st.warning("⚠️ Masukkan API Key di sidebar untuk menyalakan mesin.")