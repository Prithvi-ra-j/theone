"""Add missing columns to moodlog table for demo/prototype.
Run: python tools/fix_moodlog_columns.py
"""
from app.db.session import engine
from sqlalchemy import text

ALTERS = [
    "ALTER TABLE IF EXISTS moodlog ADD COLUMN IF NOT EXISTS primary_emotion VARCHAR(50);",
    "ALTER TABLE IF EXISTS moodlog ADD COLUMN IF NOT EXISTS secondary_emotions VARCHAR(255);",
    "ALTER TABLE IF EXISTS moodlog ADD COLUMN IF NOT EXISTS entry_method VARCHAR(20) DEFAULT 'manual' NOT NULL;",
    "ALTER TABLE IF EXISTS moodlog ADD COLUMN IF NOT EXISTS log_time TIME;",
    "ALTER TABLE IF EXISTS moodlog ADD COLUMN IF NOT EXISTS is_private BOOLEAN DEFAULT TRUE NOT NULL;"
]

def main():
    with engine.begin() as conn:
        for stmt in ALTERS:
            print(f"Applying: {stmt}")
            conn.execute(text(stmt))
    print("All moodlog columns ensured.")

if __name__ == "__main__":
    main()
