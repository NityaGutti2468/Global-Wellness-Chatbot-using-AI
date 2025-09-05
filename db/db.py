import sqlite3
import pandas as pd

DB_PATH = "users.db"

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