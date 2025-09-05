import streamlit as st
from utils import init_session, translations

def start_ui():
    init_session()
    st.set_page_config(page_title="Wellness Assistant", page_icon="🌿", layout="centered")

    # Language selector
    lang = st.sidebar.selectbox("🌐 Language", ["en", "te"])
    st.session_state.lang = lang
    t = translations[lang]

    # Background color
    st.markdown("""
    <style>
        .stApp { background-color: #f0f8ff; }
        .title { text-align: center; font-size: 36px; margin-top: 20px; color: #2e8b57; }
        .subtitle { text-align: center; font-size: 18px; color: #4682b4; }
        button[data-testid="baseButton"] {
            padding: 12px 30px;
            font-size: 16px;
            border-radius: 10px;
            margin-top: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown(f"<div class='title'>🌿 {t['title']}</div>", unsafe_allow_html=True)

    # Image
    st.markdown(f"""
    <div style='text-align: center;'>
        <img src='assets/welcome_image.png' width='250' style='border-radius: 12px;'>
        <p class='subtitle'>{t['greeting']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(t["login"], use_container_width=True):
            st.session_state.page = "login"
    with col2:
        if st.button(t["signup"], use_container_width=True):
            st.session_state.page = "signup"