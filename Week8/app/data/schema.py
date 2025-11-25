import bcrypt
from pathlib import Path


def create_user_table(conn):
    """Create users table."""
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS datasets_metadata (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()


def create_cyber_incidents_table(conn):
    """Create cyber_incidents table."""
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS cyber_incidents (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT , incident_type, severity TEXT, status TEXT, description TEXT, reported_by TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()


def create_datasets_metadata_table(conn):
    """Create datasets_metadata table."""
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS datasets_metadata (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT , datasets_type,severity TEXT, status TEXT, description TEXT, reported_by TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()


def create_it_tickets_table(conn):
    """Create it_tickets table."""
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tickets_table (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, tickets_type,severity TEXT, status TEXT, description TEXT, reported_by TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()


def create_all_tables(conn):
    """Create all tables."""
    create_user_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)