import streamlit as st

from db import init_db

translations = {
    "en": {
        "title": "Wellness Assistant",
        "greeting": "Hello! Track your wellness, reflect on your habits, and grow mindfully.",
        "login": "🔐 LOGIN",
        "signup": "📝 SIGNUP"
    },
    "te": {
        "title": "వెల్నెస్ అసిస్టెంట్",
        "greeting": "హలో! మీ ఆరోగ్యాన్ని ట్రాక్ చేయండి, అలవాట్లను పరిశీలించండి, మరియు మానసికంగా ఎదగండి.",
        "login": "🔐 లాగిన్",
        "signup": "📝 సైన్ అప్"
    }
}

def init_session():
    import streamlit as st
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    init_db()