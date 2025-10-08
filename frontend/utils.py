import sys, os
import streamlit as st

# Inject project root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from db.db import get_connection, init_db

translations = {
    "en": {
        "title": "Wellness Assistant",
        "greeting": "Hello! Track your wellness, reflect on your habits, and grow mindfully.",
        "login": "🔐 LOGIN",
        "signup": "📝 SIGNUP"
    },
    "hi": {
        "title": "वेलनेस सहायक",
        "greeting": "नमस्ते! अपनी सेहत पर नज़र रखें, अपनी आदतों पर विचार करें, और मानसिक रूप से आगे बढ़ें।",
        "login": "🔐 लॉगिन",
        "signup": "📝 साइन अप"

    }
}

def init_session():
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    init_db()
