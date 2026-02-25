import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SamuderaKepri AI Engine", page_icon="⚓", layout="wide")

# MENGAMBIL RAHASIA DARI SISTEM
api_key_otomatis = st.secrets.get("GEMINI_API_KEY", "")
password_sistem = st.secrets.get("APP_PASSWORD", "admin123") # Default jika lupa setting

# --- FUNGSI LOGIN ---
def check_password():
    """Mengembalikan True jika pengguna memasukkan password yang benar."""
    def password_entered():
        if st.session_state["password"] == password_sistem:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Hapus password dari state agar aman
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Tampilan Login
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://raw.githubusercontent.com/SAMUDERAKEPRI/Samudera-AI/main/icon.png", width=100) # Jika ada logo
            st.title("⚓ Akses Terbatas")
            st.info("Silakan masukkan kode akses Redaksi SamuderaKepri.co.id")
            st.text_input("Password:", type="password", on_change=password_entered, key="password")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ Password Salah. Akses Ditolak.")
        return False
    return True

# --- JALANKAN LOGIN ---
if check_password():
    # CSS Custom
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
        st.header("⚙️ Status Mesin")
        st.success("🔒 Koneksi Terenkripsi")
        if st.button("Log Out"):
            del st.session_state["password_correct"]
            st.rerun()
        st.divider()
        st.write(f"User: Admin Redaksi")

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
                teks_mentah = st.text_area("Tempel Teks Mentah:", height=300)
                gaya = st.selectbox("Gaya Penulisan:", ["Investigatif & Tajam", "Formal", "Populer"])
                proses = st.button("🚀 Tulis Ulang Berita")

            with col2:
                st.subheader("📰 Hasil Redaksi")
                if proses and teks_mentah:
                    with st.spinner("Mengolah berita..."):
                        prompt = f"Sebagai Editor Senior SamuderaKepri, tulis ulang teks ini dengan gaya {gaya}: {teks_mentah}"
                        response = model.generate_content(prompt)
                        st.info(response.text)
                        st.download_button("📥 Unduh Berita", response.text, f"Berita_SK_{datetime.now().strftime('%d%m%Y')}.txt")
        except Exception as e:
            st.error(f"Terjadi kendala teknis. Pastikan API Key aktif.")
    else:
        st.warning("⚠️ Konfigurasi API Key belum ditemukan di Secrets.")
