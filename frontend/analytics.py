import streamlit as st
import pandas as pd
import plotly.express as px
from db.db import (
    get_symptom_query_stats, get_tip_usage_stats, get_user_activity, get_connection
)

def is_admin():
    return st.session_state.get("email") == "nityagutti273541@gmail.com"

def analytics_ui():
    if not is_admin():
        st.error("⚠️ Access denied.")
        return

    st.title("📊 Admin Analytics Dashboard")

    # === Summary Metrics ===
    st.subheader("📌 System Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Symptoms Queried", get_symptom_query_stats().shape[0])
    with col2:
        st.metric("Wellness Tips Used", get_tip_usage_stats().shape[0])
    with col3:
        st.metric("Active Users", get_user_activity().shape[0])

    st.markdown("---")

    # === Symptom Queries ===
    st.subheader("🩺 Most Queried Symptoms")
    symptom_df = get_symptom_query_stats()
    if not symptom_df.empty:
        st.dataframe(symptom_df)
        st.bar_chart(symptom_df.set_index("symptom"))
    else:
        st.warning("No symptom query data available.")

    st.markdown("---")

    # === Tip Usage ===
    st.subheader("💡 Most Used Wellness Tips")
    tip_df = get_tip_usage_stats()
    if not tip_df.empty and "count" in tip_df.columns:
        st.dataframe(tip_df)
        fig = px.pie(tip_df, names="tip", values="count", title="Wellness Tip Usage")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No tip usage data available.")

    st.markdown("---")

    # === User Activity ===
    st.subheader("👥 User Activity")
    user_df = get_user_activity()
    if not user_df.empty:
        st.dataframe(user_df)
    else:
        st.warning("No user activity data available.")

    st.markdown("---")

    # === Daily Message Volume ===
    st.subheader("📈 Daily Message Volume")
    msg_df = pd.read_sql("""
        SELECT DATE(created_at) as date, COUNT(*) as messages
        FROM chat_history
        GROUP BY DATE(created_at)
        ORDER BY date
    """, get_connection())

    if not msg_df.empty:
        st.line_chart(msg_df.set_index("date"))
    else:
        st.warning("No message volume data available.")