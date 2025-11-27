from pathlib import Path
import sqlite3

DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)

def connect_database(db_path=DB_PATH):
    """Return a connection to the SQLite database."""
    return sqlite3.connect(str(db_path))

# 🔥 THIS PART ACTUALLY CREATES THE DATABASE FILE
conn = connect_database()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS test_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

conn.commit()
conn.close()

print("Database created at:", DB_PATH.resolve())

