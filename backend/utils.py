import streamlit as st

from db import init_db

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
    import streamlit as st
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    init_db()


    