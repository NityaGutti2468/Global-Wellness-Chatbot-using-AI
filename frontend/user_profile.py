import streamlit as st
from db.db import update_user_profile  # Optional if you want to persist changes

def profile_ui():
    st.markdown("### 👤 Your Profile")
    username = st.text_input("👤 Username", st.session_state.username)
    age_group = st.selectbox("🎂 Age Group", ["Under 18", "18–30", "31–50", "51+"],
                             index=["Under 18", "18–30", "31–50", "51+"].index(st.session_state.age_group))
    language = st.selectbox("🗣️ Language", ["English", "Telugu"],
                            index=["English", "Telugu"].index(st.session_state.language))
    submitted = st.button("💾 Update Profile")

    if submitted:
        update_user_profile(st.session_state.user_id, username, age_group, language)
        st.session_state.username = username
        st.session_state.age_group = age_group
        st.session_state.language = language
        st.success("✅ Profile updated successfully.")