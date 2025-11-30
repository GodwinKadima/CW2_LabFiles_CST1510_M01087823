import os 
import sys
import streamlit as st 
import pandas as pd
import plotly.express as px
from datetime import datetime 

# --- CRITICAL: DEFINE YOUR CSV FILE PATH ---
# !!! IMPORTANT: REPLACE "YOUR_CSV_FILE_PATH_HERE.csv" with the actual file path !!!
# Example: CSV_FILE_PATH = "../data/incidents_log.csv" 
#          (Use '../' if your data folder is at the project root level)
CSV_FILE_PATH = "./Data/cyber_incidents_1000.csv"
# ---------------------------------------------

# --- FIX: Add the project root to the system path to enable potential imports ---
# This block ensures Python can find any modules in your 'app' folder if needed later
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
sys.path.append(project_root)

# --- Custom Function to Read Data from CSV ---

@st.cache_data
def get_incidents_from_csv():
    """Reads data from the CSV file. If the file is not found, it creates dummy data."""
    try:
        # 1. Read the actual CSV file using the path you defined above
        # The index_col is set to False to prevent issues if your CSV lacks an index column
        incidents_df = pd.read_csv(CSV_FILE_PATH, index_col=False)
        
        # 2. Basic cleanup and type conversion 
        if 'timestamp' in incidents_df.columns:
            # Convert timestamp column to datetime objects
            incidents_df['timestamp'] = pd.to_datetime(incidents_df['timestamp'], errors='coerce')
        
        st.sidebar.success(f"Loaded {len(incidents_df)} incidents from CSV.")
        return incidents_df
        
    except FileNotFoundError:
        st.sidebar.error(f"Error: CSV file not found at '{CSV_FILE_PATH}'. Dashboard running on MOCK data.")
        
        # 3. If file not found, generate mock data for demonstration
        data = {
            'id': [101, 102, 103, 104, 105, 106],
            'title': ["Phishing Campaign", "Server Breach", "DDoS Attack", "Misconfiguration", "Insider Threat", "Patching Failure"],
            'severity': ["High", "Critical", "Medium", "Low", "Critical", "Medium"],
            'status': ["Open", "In Progress", "Open", "Closed", "Open", "In Progress"],
            'timestamp': [
                datetime(2025, 11, 20), datetime(2025, 11, 25), datetime(2025, 11, 28),
                datetime(2025, 11, 15), datetime(2025, 11, 29), datetime(2025, 11, 22)
            ]
        }
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error reading CSV file. Check columns names (e.g., severity, status): {e}")
        return pd.DataFrame()


# --- Streamlit App Initialization ---

st.set_page_config(layout="wide")
st.title("🛡️ Cyber incidents Dashboard (CSV Data Source)")

# READ: Load all incidents from CSV
incidents_df = get_incidents_from_csv()

if not incidents_df.empty:
    
    # --- Metrics Section ---
    col1, col2, col3 = st.columns(3)
    
    total_incidents = len(incidents_df)
    # Check if columns exist before filtering
    open_incidents = incidents_df[incidents_df['status'] == 'Open'].shape[0] if 'status' in incidents_df.columns else 0
    critical_incidents = incidents_df[incidents_df['severity'] == 'Critical'].shape[0] if 'severity' in incidents_df.columns else 0

    col1.metric("Total Incidents", total_incidents)
    col2.metric("Open Incidents", open_incidents)
    col3.metric("Critical Incidents", critical_incidents)

    st.markdown("---")

    # --- Charts Section ---
    st.header("Incident Analysis")
    chart_col1, chart_col2 = st.columns(2)

    if 'severity' in incidents_df.columns:
        # Chart 1: Incidents by Severity
        severity_counts = incidents_df['severity'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        fig_severity = px.pie(
            severity_counts, 
            values='Count', 
            names='Severity', 
            title='Incidents by Severity',
            color_discrete_sequence=px.colors.sequential.Plasma_r # Use a nice color sequence
        )
        chart_col1.plotly_chart(fig_severity, use_container_width=True)
    else:
        chart_col1.warning("Cannot plot Severity: 'severity' column missing.")

    if 'status' in incidents_df.columns:
        # Chart 2: Incidents by Status
        status_counts = incidents_df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_status = px.bar(
            status_counts, 
            x='Status', 
            y='Count', 
            title='Incidents by Status',
            color='Status',
            color_discrete_map={'Open': '#EF4444', 'In Progress': '#F59E0B', 'Closed': '#10B981'},
        )
        chart_col2.plotly_chart(fig_status, use_container_width=True)
    else:
        chart_col2.warning("Cannot plot Status: 'status' column missing.")


    st.markdown("---")

    # --- Data Table Section ---
    st.header("All Incidents Data")
    # Sort by timestamp, if it exists, to show most recent incidents first
    if 'timestamp' in incidents_df.columns:
        incidents_df = incidents_df.sort_values(by='timestamp', ascending=False)
        
    st.dataframe(incidents_df, use_container_width=True, height=350)
    

# --- Form Logic Removed (CSV is read-only) ---
st.sidebar.header("Data Source")
st.sidebar.info("This dashboard is running in **Read-Only (CSV) mode**.")
st.sidebar.caption("If you need to input new incidents, please switch back to the database setup.")