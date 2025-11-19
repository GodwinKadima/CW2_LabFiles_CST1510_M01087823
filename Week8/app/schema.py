import sqlite3
import pandas as pd
import bcrypt
from pathlib import Path

def create_user_table(conn):
    """Create users table."""
    cursor = conn.cursor() 
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGRER PRIMARY KEY AUTOINCREMENT,username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,role TEXT DEFAULT 'user')""")

def create_all_tables(conn):
    """Create all tables."""
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)