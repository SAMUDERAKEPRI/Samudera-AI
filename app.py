import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri AI Engine", page_icon="⚓", layout="wide")

# URL LOGO (Mengambil langsung dari GitHub Bapak)
# Pastikan nama file di GitHub adalah logo.png
LOGO_URL = "https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/logo.png"

# MENGAMBIL RAHASIA DARI SISTEM
api_key_otomatis = st.secrets.get("GEMINI_API_KEY", "")
password_sistem = st.secrets.get("APP_PASSWORD", "admin123")

# --- FUNGSI LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col2, _ = st.columns([1, 2, 1])
        with col2:
            # MENAMPILKAN LOGO DI HALAMAN LOGIN
            st.image(LOGO_URL, width=250)
            st.title("⚓ Akses Redaksi")
            st.info("Sistem AI Khusus Internal SamuderaKepri.co.id")
            
            pwd = st.text_input("Masukkan Kode Akses:", type="password")
            if st.button("Masuk Ke Sistem"):
                if pwd == password_sistem:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("❌ Kode Akses Salah!")
        return False
    return True

# --- JALANKAN LOGIN ---
if check_password():
    # CSS Custom untuk Branding
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; }
        .stButton>button { background-color: #004a99; color: white; border-radius: 8px; width: 100%; font-weight: bold; }
        .sidebar-logo { display: flex; justify-content: center; margin-bottom: 20px; }
        </style>
        """, unsafe_allow_html=True)

    # HEADER UTAMA DENGAN LOGO
    head_col1, head_col2 = st.columns([1, 4])
    with head_col1:
        st.image(LOGO_URL, width=150)
    with head_col2:
        st.title("SamuderaKepri News Engine")
        st.caption("Pusat Kendali Redaksi - Tanjungpinang, Kepulauan Riau")

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Status")
        st.success("🔒 Koneksi Terenkripsi")
        st.write("Role: Editor-in-Chief")
        if st.button("Keluar Sistem"):
            del st.session_state["password_correct"]
            st.rerun()
        st.divider()
        st.info("Gunakan model Gemini 2.5 Flash untuk hasil investigasi terbaik.")

    # --- LOGIKA UTAMA ---
    if api_key_otomatis:
        try:
            genai.configure(api_key=api_key_otomatis)
            available_models = [m.name.replace('models/', '') for m in genai.list_models() 
                                if 'generateContent' in m.supported_generation_methods]
            
            col1, col2 = st.columns([1, 1], gap="large")
            with col1:
                st.subheader("📝 Input Berita")
                selected_model = st.selectbox("Pilih Model AI:", available_models)
                model = genai.GenerativeModel(selected_model)
                teks_mentah = st.text_area("Tempel Teks Mentah / Rilis:", height=300)
                gaya = st.selectbox("Gaya Penulisan:", ["Investigatif & Tajam", "Formal Jurnalistik", "Populer & Ringan"])
                proses = st.button("🚀 Tulis Ulang Berita")

            with col2:
                st.subheader("📰 Hasil Redaksi")
                if proses and teks_mentah:
                    with st.spinner("Mengolah dengan standar SamuderaKepri..."):
                        prompt = f"Sebagai Editor Senior di SamuderaKepri.co.id, tulis ulang teks ini dengan gaya {gaya}: {teks_mentah}"
                        response = model.generate_content(prompt)
                        st.info(response.text)
                        st.download_button("📥 Simpan Hasil", response.text, f"Berita_SK_{datetime.now().strftime('%d%m%Y')}.txt")
        except Exception as e:
            st.error(f"Sistem sedang sibuk, pastikan API Key aktif.")
    else:
        st.warning("⚠️ Hubungi Admin untuk konfigurasi API Key.")
