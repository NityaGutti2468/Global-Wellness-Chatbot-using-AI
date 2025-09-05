import streamlit as st
import bcrypt
from db.db import insert_user, validate_user, update_password

def signup_ui():
    st.markdown("### 📝 Create Your Account")
    with st.form("signup_form"):
        username = st.text_input("👤 Username")
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        age_group = st.selectbox("🎂 Age Group", ["Under 18", "18–30", "31–50", "51+"])
        language = st.selectbox("🗣️ Language Preference", ["English", "Telugu"])
        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if username and email and password:
                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                try:
                    insert_user(username, email, hashed_pw, age_group, language)
                    st.success("✅ Account created successfully!")
                    st.session_state.page = "profile"
                    st.session_state.username = username
                    st.session_state.email = email
                    st.session_state.age_group = age_group
                    st.session_state.language = language
                except Exception as e:
                    st.error(f"⚠️ {e}")
            else:
                st.error("⚠️ All fields are required.")

def login_ui():
    st.markdown("### 🔐 Login to Your Account")
    with st.form("login_form"):
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        remember_me = st.checkbox("Remember Me")  # UI only
        submitted = st.form_submit_button("Login")

        if submitted:
            user = validate_user(email)
            if user and bcrypt.checkpw(password.encode(), user[2].encode()):
                st.success("✅ Logged in successfully!")
                set_session(user)
                st.session_state.remember_me = remember_me
            else:
                st.error("⚠️ Invalid credentials.")

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Forgot Password?"):
            st.session_state.page = "forgot"

    st.markdown("""
        <style>
            div.stButton > button:first-child {
                background-color: transparent;
                color: #1f77b4;
                border: none;
                padding: 0;
                font-size: 14px;
                text-decoration: underline;
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

def forgot_password_ui():
    st.markdown("### 🔁 Reset Your Password")
    with st.form("reset_form"):
        email = st.text_input("📧 Enter your registered email")
        new_password = st.text_input("🔑 New Password", type="password")
        confirm_password = st.text_input("🔁 Confirm Password", type="password")
        submitted = st.form_submit_button("Reset Password")

        if submitted:
            if new_password != confirm_password:
                st.error("⚠️ Passwords do not match.")
                return

            user = validate_user(email)
            if user:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                update_password(email, hashed_pw)
                st.success("✅ Password reset successfully. You can now log in.")
                st.session_state.page = "login"
            else:
                st.error("⚠️ No account found with that email.")

def logout():
    for key in ["user_id", "email", "username", "age_group", "language", "page", "remember_me"]:
        st.session_state.pop(key, None)
    st.success("👋 Logged out successfully.")

def set_session(user):
    st.session_state.page = "profile"
    st.session_state.user_id = user[0]
    st.session_state.email = user[1]
    st.session_state.username = user[3]
    st.session_state.age_group = user[4]
    st.session_state.language = user[5]