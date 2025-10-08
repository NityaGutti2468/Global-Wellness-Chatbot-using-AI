import sqlite3
import json
import re
import sys
from thefuzz import fuzz
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from deep_translator import GoogleTranslator

# === Load Model ===
model_path = "./models/wellness-intent"
model = BertForSequenceClassification.from_pretrained(model_path, local_files_only=True)
tokenizer = BertTokenizer.from_pretrained(model_path, local_files_only=True)
clf = pipeline("text-classification", model=model, tokenizer=tokenizer)

# === Constants ===
DISCLAIMER = (
    "\n\n---\n\n"
    "⚠ Disclaimer: This is general wellness guidance, not a substitute for professional care.\n"
    "Please consult a healthcare provider for diagnosis or treatment."
)

URGENT_DISCLAIMER = (
    "\n\n---\n\n"
    "⚠ URGENT: If you're experiencing a medical emergency, contact your local emergency services immediately."
)

UNSAFE_PHRASES = [
    "skip medication", "drink bleach", "self harm", "end my life",
    "how to overdose", "stop taking insulin", "hurt myself"
]

INTENT_MAP = {
    "greet": "greet",
    "greeting": "greet",
    "goodbye": "goodbye",
    "chitchat": "chitchat",
    "general_query": "ask_disease_info",
    "symptom": "ask_disease_info",
    "first_aid": "ask_first_aid",
    "inform_symptom": "ask_disease_info",
    "wellness_tip": "ask_prevention",
    "ask_wellness_tips": "ask_prevention",
    "ask_disease_info": "ask_disease_info",
    "ask_prevention": "ask_prevention",
    "emergency_help": "emergency_help",
    "ask_diet": "ask_diet",
    "ask_exercise": "ask_exercise",
    "ask_sleep": "ask_sleep",
    "ask_hygiene": "ask_hygiene",
    "ask_mental_health": "ask_mental_health",
    "ask_productivity": "ask_productivity"
}

# === DB Connection ===
def get_connection():
    return sqlite3.connect("db/wellness.db")

# === Helpers ===
def normalize(text):
    return (text or "").lower().strip(" ?.!").replace('"', "").replace("'", "")

def detect_language(text):
    return "hi" if re.search(r"[^\x00-\x7F]", text) else "en"

def translate_hi_to_en(text):
    return GoogleTranslator(source="hi", target="en").translate(text)

def translate_en_to_hi(text):
    return GoogleTranslator(source="en", target="hi").translate(text)

def violates_guardrails(user_input):
    text = user_input.lower()
    return any(phrase in text for phrase in UNSAFE_PHRASES)

def get_disclaimer(intent):
    no_disclaimer_intents = ["greet", "goodbye", "chitchat"]
    urgent_intents = ["emergency_help", "ask_first_aid", "ask_disease_info"]
    if intent in no_disclaimer_intents:
        return ""
    if intent in urgent_intents:
        return URGENT_DISCLAIMER
    return DISCLAIMER

def log_unmatched_query(query, intent, confidence):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            intent TEXT,
            confidence REAL,
            resolved INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        INSERT INTO query_logs (query, intent, confidence, resolved)
        VALUES (?, ?, ?, ?)
    """, (query, intent, confidence, 0))
    conn.commit()
    conn.close()

# === Fuzzy Matching from kb_entries ===
def get_kb_response(user_input, intent, tokens):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT entity, response FROM kb_entries WHERE intent = ?", (intent,))
    rows = cursor.fetchall()
    conn.close()

    user_input_norm = normalize(user_input)
    best_score, best_response, matched_entity = 0, None, None

    for entity_json, response in rows:
        try:
            entity_list = json.loads(entity_json)
        except:
            entity_list = [entity_json]

        for raw_entity in entity_list:
            entity_norm = normalize(raw_entity)

            if entity_norm in tokens or any(token == entity_norm for token in tokens):
                print(f"[Exact match: {raw_entity}]")
                return response

            if entity_norm in user_input_norm:
                score = fuzz.partial_ratio(entity_norm, user_input_norm) + 20
            else:
                score = fuzz.partial_ratio(entity_norm, user_input_norm)

            if score > best_score:
                best_score = score
                best_response = response
                matched_entity = raw_entity

    if best_score >= 70:
        print(f"[Fuzzy match: {matched_entity}, Score: {best_score}]")
        return best_response
    return None

# === Emergency Contacts ===
def get_emergency_contacts(contact_type, lang="en"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, phone FROM emergency_contacts WHERE type = ?", (contact_type,))
    results = cursor.fetchall()
    conn.close()

    if results:
        contacts = "\n".join([f"{name}: {phone}" for name, phone in results])
        message = f"{contacts}\n{DISCLAIMER}"
    else:
        message = f"No emergency contacts found.\n{DISCLAIMER}"

    return translate_en_to_hi(message) if lang == "hi" else message

# === Core Response Logic ===
def get_bot_response(user_input):
    lang = detect_language(user_input)
    translated_input = translate_hi_to_en(user_input) if lang == "hi" else user_input
    user_input_norm = normalize(translated_input)
    tokens = user_input_norm.split()

    greeting_phrases = ["hi", "hello", "hey", "hii", "heyy", "helloo", "good morning", "good afternoon", "good evening"]
    if any(fuzz.ratio(user_input_norm, phrase) > 80 for phrase in greeting_phrases):
        intent = "greet"
        score = 1.0
    else:
        result = clf(translated_input)[0]
        intent = result["label"]
        score = result["score"]

    print(f"[Intent: {intent}, Confidence: {score:.2f}]")
    intent = INTENT_MAP.get(intent, intent)

    if score < 0.5:
        log_unmatched_query(translated_input, intent, score)
        fallback = "🤖 I'm not sure I understood that. Could you rephrase?"
        return translate_en_to_hi(fallback) if lang == "hi" else fallback

    if violates_guardrails(user_input):
        warning = (
            "⚠️ That sounds unsafe. Please consult a medical professional or emergency service immediately.\n"
            + get_emergency_contacts("mental_health", lang)
        )
        return warning

    conn = get_connection()
    cursor = conn.cursor()

    if intent == "ask_disease_info":
        cursor.execute("SELECT symptom, possible_condition, advice FROM symptoms")
        rows = cursor.fetchall()
        for symptom, condition, advice in rows:
            if normalize(symptom) in tokens or normalize(symptom) in user_input_norm:
                conn.close()
                response = f"🩺 Possible condition: {condition}\n💡 Advice: {advice}{get_disclaimer(intent)}"
                return translate_en_to_hi(response) if lang == "hi" else response

    elif intent == "ask_first_aid":
        cursor.execute("SELECT situation, steps FROM first_aid")
        rows = cursor.fetchall()
        for situation, steps in rows:
            if normalize(situation) in tokens or normalize(situation) in user_input_norm:
                conn.close()
                response = f"🆘 First Aid Steps: {steps}{get_disclaimer(intent)}"
                return translate_en_to_hi(response) if lang == "hi" else response

    elif intent == "ask_prevention":
        cursor.execute("SELECT tip FROM wellness_tips ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        if result:
            response = f"💡 Wellness Tip: {result[0]}{get_disclaimer(intent)}"
            return translate_en_to_hi(response) if lang == "hi" else response

    conn.close()

    kb_match = get_kb_response(translated_input, intent, tokens)
    if kb_match:
        response = kb_match + get_disclaimer(intent)
        return translate_en_to_hi(response) if lang == "hi" else response

    log_unmatched_query(translated_input, intent, score)
    fallback = "🤖 Sorry, I don't have a response for that yet. Could you rephrase or try a different query?"
    return translate_en_to_hi(fallback) if lang == "hi" else fallback

# === CLI Demo ===
if __name__ == "__main__":
    print("🧠 Wellness Chatbot (CLI Demo)")
    print("Type 'exit' to quit.\n")
    print("Ask me about symptoms, first aid, wellness tips, or emergency contacts.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Take care! 👋")
            break

        reply = get_bot_response(user_input)
        print(f"Bot: {reply}\n")
