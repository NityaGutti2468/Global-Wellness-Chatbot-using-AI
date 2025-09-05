import streamlit as st
from db.db import get_all_users, delete_user_by_email

def is_admin():
    return st.session_state.get("email") == "nityagutti273541@gmail.com"

def admin_ui():
    if not is_admin():
        st.error("⚠️ Access denied.")
        return

    st.markdown("### 🛠️ Admin Panel: Manage Users")
    users_df = get_all_users()
    st.dataframe(users_df)

    selected_email = st.selectbox("📧 Select user to delete", users_df["email"].tolist())
    if st.button("Delete User"):
        delete_user_by_email(selected_email)
        st.success(f"✅ User {selected_email} deleted.")