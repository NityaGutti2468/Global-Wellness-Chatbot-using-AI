import sqlite3
import json
import os

def initialize_db():
    with open("db/wellness.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()

    conn = sqlite3.connect("db/wellness.db")
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    print("✅ Database initialized from wellness.sql")

    # === Add JSON ingestion below ===

    # Load disease_symptom_map.json
    with open("db/assets/disease_symptom_map.json", "r", encoding="utf-8") as f:
        symptom_data = json.load(f)

    for entry in symptom_data:
        disease = entry["disease"]
        for symptom in entry["symptoms"]:
            cursor.execute('''
                INSERT OR IGNORE INTO disease_symptoms (disease, symptom)
                VALUES (?, ?)
            ''', (disease, symptom))

    # Load health_kb.json
    with open("db/assets/health_kb.json", "r", encoding="utf-8") as f:
        kb_data = json.load(f)

    for entry in kb_data:
        disease = entry["disease"]
        symptoms = ', '.join(entry["symptoms"])
        first_aid = entry.get("first_aid", "Not available")
        prevention = entry.get("prevention", "Not available")

        cursor.execute('''
            REPLACE INTO disease_knowledge (disease, symptoms, first_aid, prevention)
            VALUES (?, ?, ?, ?)
        ''', (disease, symptoms, first_aid, prevention))

    conn.commit()
    conn.close()
    print("✅ JSON data loaded into SQLite")

if __name__ == "__main__":
    initialize_db()