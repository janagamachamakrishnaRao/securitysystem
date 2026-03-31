import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "security.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_type TEXT,
    visitor_name TEXT,
    purpose TEXT,
    in_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    out_time DATETIME
)
""")

conn.commit()
conn.close()

print("Database created successfully at:", DB_PATH)
