-- ===============================
-- Create Tables
-- ===============================

-- First aid information
CREATE TABLE IF NOT EXISTS first_aid (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    situation TEXT NOT NULL,
    steps TEXT NOT NULL
);

-- Store user details
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    username TEXT NOT NULL
);

-- Store chatbot conversation history
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Store wellness tips
CREATE TABLE IF NOT EXISTS wellness_tips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    tip TEXT NOT NULL
);

-- Store emergency contacts
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    type TEXT CHECK(type IN ('hospital','ambulance','police','fire')) NOT NULL
);

-- Symptoms and advice
CREATE TABLE IF NOT EXISTS symptoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptom TEXT NOT NULL,
    possible_condition TEXT,
    advice TEXT
);



-- Response templates for chatbot
CREATE TABLE IF NOT EXISTS response_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent TEXT NOT NULL,
    template TEXT NOT NULL
);

CREATE TABLE kb_entries (
    id TEXT PRIMARY KEY,
    intent TEXT NOT NULL,
    entity TEXT NOT NULL,
    response TEXT NOT NULL,
    source TEXT
);

-- ===============================
-- Insert Sample Data
-- ===============================

-- Symptoms
INSERT INTO symptoms (symptom, possible_condition, advice) VALUES
('Headache', 'Stress / Dehydration', 'Drink water, take rest, avoid screen time'),
('Fever', 'Viral Infection', 'Take paracetamol, stay hydrated, consult doctor if >102°F'),
('Cough', 'Cold / Allergy', 'Drink warm fluids, avoid cold drinks, use honey'),
('Stomach Pain', 'Indigestion / Gas', 'Eat light food, drink water, consult doctor if persistent'),
('Stress', 'Workload / Anxiety', 'Practice meditation, take breaks, talk to someone');

-- Wellness Tips
INSERT INTO wellness_tips (category, tip) VALUES
('Fitness', 'Do 30 minutes of exercise daily'),
('Diet', 'Eat fruits and vegetables regularly'),
('Mental Health', 'Practice mindfulness and meditation'),
('Sleep', 'Aim for 7-8 hours of quality sleep'),
('Hydration', 'Drink at least 2-3 liters of water per day');

-- First Aid
INSERT INTO first_aid (situation, steps) VALUES
('Burn', 'Cool the burn under running water for 10 minutes, cover with clean cloth, avoid ice'),
('Cut', 'Clean with water, apply antiseptic, cover with bandage'),
('Nosebleed', 'Lean forward, pinch nose for 10 minutes, apply cold compress'),
('Sprain', 'Rest, ice, compress, elevate (RICE method)'),
('Fainting', 'Lay person flat, raise legs, loosen tight clothing');

-- Emergency Contacts
INSERT INTO emergency_contacts (name, phone, type) VALUES
('City Hospital', '9876543210', 'hospital'),
('Rapid Ambulance', '1122334455', 'ambulance'),
('Local Police Station', '100', 'police'),
('Fire Department', '101', 'fire');

