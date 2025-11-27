import pandas as pd 
from app.data.db import connect_database

def insert_incident(date, incident_type, severity, status, description,reported_by=None):
    """Insert new incident."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO cyber_incidents (date, incident_type, severity, status, description, reported_by) VALUES (?, ?, ?, ?, ?, ?)""", (date , incident_type , severity, status, description, reported_by))
    conn.commit()
    incident_id = cursor.lastrowid
    conn.close()
    return incident_id

def get_all_incidents():
    """Get all incidents as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY id DESC", conn
    )
    conn.close()
    return df
    pass

def update_incident_status(conn, incident_id, new_status):
    """Update the status of an incident."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE cyber_incidents SET status = ? WHERE id = ?""",(new_status,incident_id))
    conn.commit()
    return cursor.rowcount
    pass 

def delete_incident(conn,incident_id):
    """Delete an incident from the database."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        """DELETE FROM cyber_incidents WHERE id = ?""",(incident_id))# TODO: Write DELETE SQL: DELETE FROM cyber_incidents WHERE id = ? # TODO: Execute and commit
    conn.commit()
    return cursor.rowcount # TODO: Return cursor.rowcount
    pass