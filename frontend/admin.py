import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.append(os.path.abspath("../db"))

from db.db import (
    get_all_users, delete_user_by_email,
    get_all_tips, add_tip, update_tip, delete_tip,
    get_all_symptoms, add_symptom, update_symptom, delete_symptom,
    get_all_first_aid, add_first_aid, update_first_aid, delete_first_aid,
    get_symptom_query_stats, get_tip_usage_stats, get_user_activity, get_connection
)

def is_admin():
    return st.session_state.get("email") == "nityagutti273541@gmail.com"

def admin_ui():
    if not is_admin():
        st.error("⚠️ Access denied.")
        return

    st.set_page_config(page_title="HealthBot Admin", layout="wide")
    st.title("🛠️ HealthBot Admin Panel")

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📚 Knowledge Base", "📈 Analytics"])

    with tab1:
        st.subheader("📌 System Overview")

        # === Metrics ===
        users_df = get_all_users()
        total_users = users_df.shape[0]

        msg_df = pd.read_sql("SELECT COUNT(*) as total FROM chat_history", get_connection())
        total_queries = int(msg_df["total"].iloc[0])

        topics_count = len(get_all_tips()) + len(get_all_symptoms()) + len(get_all_first_aid())

        feedback_df = pd.read_sql("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive
            FROM feedback
        """, get_connection())

        total_feedback = int(feedback_df["total"].iloc[0]) or 0
        positive_raw = feedback_df["positive"].iloc[0]
        positive_feedback = int(positive_raw) if positive_raw is not None else 0
        negative_feedback = total_feedback - positive_feedback

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Users", total_users)
        col2.metric("Queries Handled", total_queries)
        col3.metric("Health Topics", topics_count)
        col4.metric("Positive Feedback", f"{(positive_feedback / total_feedback * 100):.0f}%" if total_feedback > 0 else "N/A")

        st.markdown("---")
        st.subheader("📈 Query Trends Over Time")

        query_trend_df = pd.read_sql("""
            SELECT strftime('%w', created_at) AS weekday, COUNT(*) AS queries
            FROM chat_history
            GROUP BY weekday
            ORDER BY weekday
        """, get_connection())

        weekday_map = {
            "0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed",
            "4": "Thu", "5": "Fri", "6": "Sat"
        }
        query_trend_df["Day"] = query_trend_df["weekday"].map(weekday_map)
        query_trend_df = query_trend_df[["Day", "queries"]].set_index("Day")
        st.line_chart(query_trend_df)
        
        st.markdown("---")
        st.subheader("📊 Most Queried Intents")

        intent_df = pd.read_sql("""
           SELECT intent, COUNT(*) AS count
           FROM query_logs
           GROUP BY intent
           ORDER BY count DESC
        """, get_connection())

        if intent_df.empty:
            st.info("No intent data available.")
        else:
            st.dataframe(intent_df)
            st.bar_chart(intent_df.set_index("intent"))

        st.markdown("---")
        st.subheader("📊 Message Distribution by Day")

        volume_df = pd.read_sql("""
            SELECT strftime('%w', created_at) AS weekday, COUNT(*) AS messages
            FROM chat_history
            GROUP BY weekday
            ORDER BY weekday
        """, get_connection())

        volume_df["Day"] = volume_df["weekday"].map(weekday_map)
        volume_df = volume_df[["Day", "messages"]]

        fig = px.pie(
            volume_df,
            names="Day",
            values="messages",
            title="Message Distribution by Day",
            color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692"],
            hole=0.4
        )
        fig.update_traces(textinfo="percent+label", pull=[0.05]*len(volume_df))
        fig.update_layout(
            showlegend=True,
            legend_title_text="Day",
            title_font_size=20,
            margin=dict(t=50, b=20, l=0, r=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🗣️ Recent Feedback Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Feedback", total_feedback)
        col2.metric("👍 Positive", f"{positive_feedback} ({(positive_feedback / total_feedback * 100):.0f}%)" if total_feedback > 0 else "0")
        col3.metric("👎 Negative", f"{negative_feedback} ({(negative_feedback / total_feedback * 100):.0f}%)" if total_feedback > 0 else "0")

        st.markdown("---")
        st.subheader("💬 Recent Comments")

        comments_df = pd.read_sql("""
            SELECT sentiment, comment, timestamp
            FROM feedback
            WHERE comment IS NOT NULL AND TRIM(comment) != ''
            ORDER BY timestamp DESC
            LIMIT 5
        """, get_connection())

        if comments_df.empty:
            st.info("No comments submitted yet.")
        else:
            for _, row in comments_df.iterrows():
                icon = "👍" if row["sentiment"] == "positive" else "👎"
                st.markdown(f"{icon} **Comment:** {row['comment']}")
                st.markdown(f"🕒 *{row['timestamp']}*")
                st.markdown("---")

        st.markdown("---")
        st.subheader("❌ Failed Queries (Unresolved)")

        failed_df = pd.read_sql("""
           SELECT query, intent, confidence, timestamp
           FROM query_logs
           WHERE resolved = 0
           ORDER BY timestamp DESC
           LIMIT 50
        """, get_connection())

        if failed_df.empty:
            st.info("No unresolved queries found.")
        else:
            st.dataframe(failed_df)

    # === Knowledge Base Management ===
    with tab2:
        st.subheader("👥 Manage Users")
        users_df = get_all_users()
        st.dataframe(users_df)
        selected_email = st.selectbox("📧 Select user to delete", users_df["email"].tolist())
        if st.button("Delete User"):
            delete_user_by_email(selected_email)
            st.success(f"✅ User {selected_email} deleted.")

        st.markdown("---")
        st.subheader("💡 Manage Wellness Tips")
        tips_df = get_all_tips()
        st.dataframe(tips_df)

        with st.expander("➕ Add New Tip"):
            category = st.text_input("Category")
            tip = st.text_area("Tip")
            if st.button("Add Tip"):
                add_tip(category, tip)
                st.success("✅ Tip added.")

        with st.expander("✏️ Update Tip"):
            tip_id = st.number_input("Tip ID", min_value=1)
            new_tip = st.text_area("New Tip")
            if st.button("Update Tip"):
                update_tip(tip_id, new_tip)
                st.success("✅ Tip updated.")

        with st.expander("🗑️ Delete Tip"):
            tip_id_del = st.number_input("Tip ID to delete", min_value=1)
            if st.button("Delete Tip"):
                delete_tip(tip_id_del)
                st.success("✅ Tip deleted.")

        st.markdown("---")
        st.subheader("🩺 Manage Symptoms")
        symptoms_df = get_all_symptoms()
        st.dataframe(symptoms_df)

        with st.expander("➕ Add Symptom"):
            symptom = st.text_input("Symptom")
            condition = st.text_input("Possible Condition")
            advice = st.text_area("Advice")
            if st.button("Add Symptom"):
                add_symptom(symptom, condition, advice)
                st.success("✅ Symptom added.")

        with st.expander("✏️ Update Symptom"):
            symptom_id = st.number_input("Symptom ID", min_value=1)
            new_advice = st.text_area("New Advice")
            if st.button("Update Symptom"):
                update_symptom(symptom_id, new_advice)
                st.success("✅ Symptom updated.")

        with st.expander("🗑️ Delete Symptom"):
            symptom_id_del = st.number_input("Symptom ID to delete", min_value=1)
            if st.button("Delete Symptom"):
                delete_symptom(symptom_id_del)
                st.success("✅ Symptom deleted.")

        st.markdown("---")
        st.subheader("🆘 Manage First Aid")
        aid_df = get_all_first_aid()
        st.dataframe(aid_df)

        with st.expander("➕ Add First Aid"):
            situation = st.text_input("Situation")
            steps = st.text_area("Steps")
            if st.button("Add First Aid"):
                add_first_aid(situation, steps)
                st.success("✅ First aid added.")

        with st.expander("✏️ Update First Aid"):
            aid_id = st.number_input("First Aid ID", min_value=1)
            new_steps = st.text_area("New Steps")
            if st.button("Update First Aid"):
                update_first_aid(aid_id, new_steps)
                st.success("✅ First aid updated.")

        with st.expander("🗑️ Delete First Aid"):
            aid_id_del = st.number_input("First Aid ID to delete", min_value=1)
            if st.button("Delete First Aid"):
                delete_first_aid(aid_id_del)
                st.success("✅ First aid deleted.")

    # === Analytics ===
    with tab3:
        st.subheader("📌 System Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Symptoms Queried", get_symptom_query_stats().shape[0])
        col2.metric("Wellness Tips Used", get_tip_usage_stats().shape[0])
        col3.metric("Active Users", get_user_activity().shape[0])

        st.markdown("---")
        st.subheader("🩺 Most Queried Symptoms")
        symptom_df = get_symptom_query_stats()
        if not symptom_df.empty:
            st.dataframe(symptom_df)
            st.bar_chart(symptom_df.set_index("symptom"))
        else:
            st.warning("No symptom query data available.")

        st.markdown("---")
        st.subheader("💡 Most Used Wellness Tips")
        tip_df = get_tip_usage_stats()
        if not tip_df.empty and "count" in tip_df.columns:
            st.dataframe(tip_df)
            fig = px.pie(
                tip_df,
                names="tip",
                values="count",
                title="Wellness Tip Usage",
                color="tip",
                color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96", "#AB63FA"],
                hole=0.4  # donut-style chart
            )
            fig.update_traces(textinfo="percent+label", pull=[0.05]*len(tip_df))
            fig.update_layout(
                showlegend=True,
                legend_title_text="Tip",
                title_font_size=20,
                margin=dict(t=50, b=20, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No tip usage data available.")
