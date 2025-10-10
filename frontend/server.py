import streamlit as st
import sys, os

# Inject project root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if not os.path.exists("db/db.db"):
    import backend.init_db
# === Imports ===
from start import start_ui
from auth import login_ui, signup_ui, forgot_password_ui, logout
from user_profile import profile_ui
from admin import admin_ui, is_admin
from analytics import analytics_ui
from utils import init_session
from backend.bot_core import get_bot_response
from db.db import log_chat, get_connection

# === Initialize session ===
init_session()

# === Feedback Functions ===
def save_feedback(message_id: int, sentiment: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (message_id, sentiment, timestamp)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (message_id, sentiment))
    conn.commit()

def feedback_ui(message_id: int):
    #st.markdown("#### 🙋 Was this response helpful?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("👍 ", key=f"yes_{message_id}"):
            save_feedback(message_id, "positive")
            st.success("Thanks for your feedback!")

    with col2:
        if st.button("👎 ", key=f"no_{message_id}"):
            save_feedback(message_id, "negative")
            st.info("We'll use this to improve future responses.")

    comment = st.text_input("💬 Optional comment", key=f"comment_{message_id}")
    if comment:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE feedback SET comment = ? WHERE message_id = ?
        """, (comment, message_id))
        conn.commit()
        st.success("Comment saved!")


# === Sidebar Navigation ===
if st.session_state.get("user_id"):
    st.sidebar.title("📌 Navigation")

    if "page" not in st.session_state:
        st.session_state.page = "chatbot"

    if st.sidebar.button("🚪 Logout"):
        logout()
    if st.sidebar.button("💬 Chatbot"):
        st.session_state.page = "chatbot"
    if st.sidebar.button("👤 Profile"):
        st.session_state.page = "profile"

    if is_admin():
        if st.sidebar.button("🛠️ Show Admin Tools"):
            st.session_state.show_admin_tools = True

        if st.session_state.get("show_admin_tools"):
            st.sidebar.markdown("---")
            st.sidebar.title("🛠️ Admin Tools")
            st.session_state.page = "admin"
            

# === Page Routing ===
if st.session_state.page == "home":
    start_ui()

elif st.session_state.page == "login":
    login_ui()

elif st.session_state.page == "signup":
    signup_ui()

elif st.session_state.page == "forgot":
    forgot_password_ui()

elif st.session_state.page == "profile":
    profile_ui()

elif st.session_state.page == "admin":
    admin_ui()

elif st.session_state.page == "analytics":
    analytics_ui()

elif st.session_state.page == "chatbot":
    if st.session_state.get("user_id"):
        st.title("🧠 Wellness Chatbot")
        st.markdown("Ask me about symptoms, first aid, wellness tips, or emergency contacts.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_input = st.chat_input("Type your message here...")

        if user_input:
            bot_reply = get_bot_response(user_input)

            # Save to DB and get message_id
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (user_id, message, response)
                VALUES (?, ?, ?)
            """, (st.session_state.user_id, user_input, bot_reply))
            conn.commit()
            message_id = cursor.lastrowid

            # Store both message and feedback trigger
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("Bot", bot_reply, message_id))

        for item in st.session_state.chat_history:
            if item[0] == "You":
                st.markdown(f"**👤 You:** {item[1]}")
            elif item[0] == "Bot":
                st.markdown(f"**🤖 Bot:** {item[1]}")

                # Skip feedback for greetings or fallback replies
                if len(item) > 2:
                    bot_text = item[1].lower()
                    skip_phrases = [
                        "hi", "hello", "hey", "good morning", "good evening", "greetings",
                        "sorry, i don't have a response", "could you rephrase", "try a different query"
                    ]
                    if not any(phrase in bot_text for phrase in skip_phrases):
                        feedback_ui(item[2])

            st.markdown("---")
    else:
        st.warning("🔐 Please log in to access the chatbot.")
