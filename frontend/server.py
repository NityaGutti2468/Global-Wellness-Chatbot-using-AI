import streamlit as st
import datetime

# --- Page Config ---
st.set_page_config(page_title="HealthBridge", layout="wide")

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
        body {
            background-color: #f0f8f7;
        }
        .main {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
        }
        h1, h2, h3 {
            color: #2c7873;
        }
        .stButton>button {
            background-color: #2c7873;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stTextInput>div>input, .stDateInput>div>input, .stTimeInput>div>input {
            background-color: #e0f7f4;
            border-radius: 5px;
        }
        .stTextArea>div>textarea {
            background-color: #e0f7f4;
            border-radius: 5px;
        }
        .stRadio>div>label {
            color: #2c7873;
        }
        .stSuccess {
            background-color: #d0f0e0;
            border-left: 5px solid #2c7873;
        }
    </style>
""", unsafe_allow_html=True)

# --- Tabs for Clickable Navigation ---
st.title("🏥 HealthBridge")
st.subheader("Your Health, Your Power")

tabs = st.tabs(["🏠 Home", "🤒 Symptom Checker", "📅 Book Appointment", "📚 Wellness Resources"])

# --- Home Tab ---
with tabs[0]:
    st.markdown("""
        Welcome to **HealthBridge**, a student-friendly healthcare platform designed to support your wellness journey.
        Whether you're feeling under the weather or just need a mental reset, we've got you covered.
    """)
    st.image("https://img.icons8.com/color/96/health-graph.png", caption="Track your health with ease", use_column_width=True)

# --- Symptom Checker Tab ---
with tabs[1]:
    st.markdown("### 🤒 Symptom Checker")
    st.markdown("Describe your symptoms below. Our AI assistant will suggest next steps.")
    symptom_input = st.text_area("What symptoms are you experiencing?")
    if st.button("Check Symptoms"):
        st.success("Based on your input, we recommend rest and hydration. If symptoms persist, consult a doctor.")

# --- Appointment Booking Tab ---
with tabs[2]:
    st.markdown("### 📅 Book an Appointment")
    st.markdown("Choose your preferred date and time to consult a healthcare professional.")
    name = st.text_input("Your Name")
    date = st.date_input("Select Date", min_value=datetime.date.today())
    time = st.time_input("Select Time")
    mode = st.radio("Consultation Mode", ["In-Person", "Telehealth"])
    if st.button("Confirm Booking"):
        st.success(f"✅ Appointment booked for **{name}** on **{date}** at **{time}** via **{mode}**.")

# --- Wellness Resources Tab ---
with tabs[3]:
    st.markdown("### 📚 Wellness Resources")
    st.markdown("Explore curated tips and tools to boost your health and happiness.")
    st.markdown("#### 🧘 Mental Health")
    st.markdown("- Breathing exercises\n- Journaling prompts\n- Stress relief techniques")
    st.markdown("#### 🍎 Nutrition")
    st.markdown("- Balanced meal plans\n- Hydration reminders\n- Smart snacking tips")
    st.markdown("#### 😴 Sleep Hygiene")
    st.markdown("- Sleep tracker apps\n- Bedtime routines\n- Blue light awareness")

# --- Footer ---
st.markdown("---")
st.caption("© 2025 HealthBridge | Designed with care for students everywhere.")