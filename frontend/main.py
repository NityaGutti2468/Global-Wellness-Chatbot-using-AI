import streamlit as st
from start import start_ui
from auth import login_ui, signup_ui
from user_profile import profile_ui
from auth import forgot_password_ui
from utils import init_session

from admin import admin_ui
init_session()

if st.session_state.page == "home":
    start_ui()
elif st.session_state.page == "login":
    login_ui()
elif st.session_state.page == "signup":
    signup_ui()
elif st.session_state.page == "profile":
    profile_ui()
elif st.session_state.page == "admin":
    admin_ui()
elif st.session_state.page == "forgot":
    forgot_password_ui()

from admin import is_admin

# Sidebar navigation for admin
if is_admin():
    if st.sidebar.button("🛠️ Admin Panel"):
        st.session_state.page = "admin"




