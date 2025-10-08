# backend/save_queries.py

queries = """-- Sample Queries for Wellness Chatbot DB

-- 1. Check all tables in the database
.tables

-- 2. See structure of a table (example: symptoms)
.schema symptoms

-- 3. View all first aid steps
SELECT * FROM first_aid;

-- 4. Find advice for a specific symptom (example: Fever)
SELECT possible_condition, advice 
FROM symptoms 
WHERE symptom = 'Fever';

-- 5. Get random wellness tip
SELECT tip 
FROM wellness_tips 
ORDER BY RANDOM() 
LIMIT 1;

-- 6. Check emergency contacts (example: hospitals)
SELECT name, phone 
FROM emergency_contacts 
WHERE type = 'hospital';

-- 7. See recent chat history (last 5 messages)
SELECT message, response, created_at 
FROM chat_history 
ORDER BY created_at DESC 
LIMIT 5;

-- 8. Find all wellness tips under “Mental Health”
SELECT tip 
FROM wellness_tips 
WHERE category = 'Mental Health';

-- 9. Insert new symptom (example for demo)
INSERT INTO symptoms (symptom, possible_condition, advice) 
VALUES ('Back Pain', 'Muscle strain', 'Do stretching, use hot compress, rest properly');

-- 10. Delete chat history (cleanup for demo)
DELETE FROM chat_history;
"""

file_path = "db/sample_queries.sql"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(queries)

print("✅ Sample queries saved at:", file_path)