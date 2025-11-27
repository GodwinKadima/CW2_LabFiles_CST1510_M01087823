import pandas as pd 
from app.data.db import connect_database

def insert_datasets (date, datasets_type, severity, status, description, reported_by=None):
    """Insert new datasets"""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO cyber_datasets(date, datasets_type, severity, status,decsription, reported_by) VALUES(?, ?, ?, ?, ?, ?)""",(date, datasets_type, severity, status, description, reported_by))
    conn.commit()
    datasets_id = cursor.lastrowid
    conn.close
    return datasets_id

def get_all_datasets(conn):
    """Retrieve all datasets from the database"""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_datasets",conn
    )
    conn.close
    return df

def update_datasets_status(conn,datasets_id, new_status):
    """Update the status of datasets"""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("UPDATE cyber_incidents SET status = ? WHERE id = ?",(new_status,datasets_id))
    conn.commit
    return cursor.rowcount
    pass

def delete_datasets(conn, datasets_id):
    """Delete a datasets from the database"""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cyber_incidents WHERE id = ?",(datasets_id))
    conn.commit
    return cursor.rowcount
