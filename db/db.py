import sqlite3
import pandas as pd
import os

DB_PATH = os.path.abspath("db/wellness.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                username TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                age_group TEXT,
                language TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

def insert_user(username, email, password, age_group, language):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password, username) VALUES (?, ?, ?)", (email, password, username))
        user_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO profiles (user_id, username, age_group, language)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, age_group, language))

def validate_user(email):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT users.id, users.email, users.password,
                   profiles.username, profiles.age_group, profiles.language
            FROM users
            JOIN profiles ON users.id = profiles.user_id
            WHERE users.email = ?
        """, (email,))
        return cursor.fetchone()

def update_user_profile(user_id, username, age_group, language):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE profiles
            SET username = ?, age_group = ?, language = ?
            WHERE user_id = ?
        """, (username, age_group, language, user_id))

def delete_user_by_email(email):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if user:
            user_id = user[0]
            cursor.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

def get_all_users():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT users.email, profiles.username, profiles.age_group, profiles.language
            FROM users
            JOIN profiles ON users.id = profiles.user_id
        """, conn)

def update_password(email, new_hashed_pw):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET password = ?
            WHERE email = ?
        """, (new_hashed_pw, email))




def log_chat(user_id, message, response):
    conn = sqlite3.connect("db/wellness.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (user_id, message, response)
        VALUES (?, ?, ?)
    """, (user_id, message, response))
    conn.commit()
    conn.close()


def get_all_tips():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM wellness_tips", conn)

def add_tip(category, tip):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO wellness_tips (category, tip) VALUES (?, ?)", (category, tip))

def update_tip(tip_id, new_tip):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE wellness_tips SET tip = ? WHERE id = ?", (new_tip, tip_id))

def delete_tip(tip_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM wellness_tips WHERE id = ?", (tip_id,))


def get_all_symptoms():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM symptoms", conn)

def add_symptom(symptom, condition, advice):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO symptoms (symptom, possible_condition, advice) VALUES (?, ?, ?)", (symptom, condition, advice))

def update_symptom(symptom_id, new_advice):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE symptoms SET advice = ? WHERE id = ?", (new_advice, symptom_id))

def delete_symptom(symptom_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM symptoms WHERE id = ?", (symptom_id,))


def get_all_first_aid():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM first_aid", conn)

def add_first_aid(situation, steps):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO first_aid (situation, steps) VALUES (?, ?)", (situation, steps))

def update_first_aid(aid_id, new_steps):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE first_aid SET steps = ? WHERE id = ?", (new_steps, aid_id))

def delete_first_aid(aid_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM first_aid WHERE id = ?", (aid_id,))


def get_symptom_query_stats():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT symptom, COUNT(*) as count
            FROM symptoms
            JOIN chat_history ON chat_history.message LIKE '%' || symptoms.symptom || '%'
            GROUP BY symptom
            ORDER BY count DESC
        """, conn)

def get_tip_usage_stats():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT tip, COUNT(*) as count
            FROM wellness_tips
            JOIN chat_history ON chat_history.response LIKE '%' || wellness_tips.tip || '%'
            GROUP BY tip
            ORDER BY count DESC
        """, conn)

def get_user_activity():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT users.email, COUNT(chat_history.id) as messages, MAX(chat_history.created_at) as last_active
            FROM users
            JOIN chat_history ON users.id = chat_history.user_id
            GROUP BY users.email
            ORDER BY messages DESC
        """, conn)