import pandas as pd 
from app.data.db import connect_database

def insert_tickets (date, tickets_type, severity, status, description, reported_by=None):
    """Insert new tickets"""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO cyber_tickets(date, tickets_type, severity, status,decsription, reported_by) VALUES(?, ?, ?, ?, ?, ?)""",(date, tickets_type, severity, status, description, reported_by))
    conn.commit()
    tickets_id = cursor.lastrowid
    conn.close
    return tickets_id

def get_all_tickets(conn):
    """Retrieve all tickets from the database"""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_tickets",conn
    )
    conn.close
    return df

def update_tickets_status(conn,tickets_id, new_status):
    """Update the status of datasets"""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("UPDATE cyber_tickets SET status = ? WHERE id = ?",(new_status,tickets_id))
    conn.commit
    return cursor.rowcount
    pass

def delete_datasets(conn, tickets_id):
    """Delete a datasets from the database"""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cyber_tickets WHERE id = ?",(tickets_id))
    conn.commit
    return cursor.rowcount
