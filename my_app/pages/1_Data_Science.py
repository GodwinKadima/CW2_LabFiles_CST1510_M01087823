import os 
import sys
import streamlit as st 
import pandas as pd
import plotly.express as px
from datetime import datetime 

# --- CRITICAL PATH SETUP FOR MODULE IMPORTS ---
# 1. Get the directory of the current script (e.g., /.../my_app/pages/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. Go up two levels to reach the project root directory (../../)
project_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))

# 3. Add the project root to sys.path so Python can find modules like 'app.data.datasets'
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    import app.data.datasets as datasets_crud 
    st.sidebar.success("CRUD module loaded successfully.")
except Exception as e:
    # If this fails, the app still runs on CSV data, but CRUD won't work
    st.sidebar.error(f"Failed to import CRUD module: {e}")


# --- CSV FILE PATH DEFINITION ---

def get_data_path(filename):
    """Calculates the absolute path to the data file."""
    return os.path.join(project_root, "DATA", filename)

# Using the datasets metadata file as requested
CSV_FILE_PATH = get_data_path("datasets_metadata_1000.csv")


# --- DATA LOADING AND SESSION STATE INITIALIZATION ---

@st.cache_data
def load_initial_datasets():
    """Reads data from the CSV file for initial state, or creates dummy data on fail."""
    try:
        datasets_df = pd.read_csv(CSV_FILE_PATH, index_col=False)
        datasets_df.columns = datasets_df.columns.str.lower()
        
        if 'timestamp' in datasets_df.columns:
            datasets_df['timestamp'] = pd.to_datetime(datasets_df['timestamp'], errors='coerce')
        
        st.sidebar.success(f"Initial load: {len(datasets_df)} datasets from CSV.")
        return datasets_df
        
    except FileNotFoundError:
        st.sidebar.error(f"Error: CSV file not found at '{CSV_FILE_PATH}'. Dashboard running on MOCK data.")
        # Generate mock data if file is missing
        data = {
            'id': [101, 102, 103, 104, 105, 106],
            'title': ["User Log", "Network Flow", "Email Headers", "Firewall Logs", "Endpoint Alerts", "Threat Intel"],
            'severity': ["High", "Critical", "Medium", "Low", "Critical", "Medium"],
            'status': ["Open", "In Progress", "Open", "Closed", "Open", "In Progress"],
            'timestamp': [
                datetime(2025, 11, 20), datetime(2025, 11, 25), datetime(2025, 11, 28),
                datetime(2025, 11, 15), datetime(2025, 11, 29), datetime(2025, 11, 22)
            ]
        }
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return pd.DataFrame()

# Initialize the DataFrame in Streamlit's session state if it doesn't exist
if 'datasets_df' not in st.session_state:
    st.session_state['datasets_df'] = load_initial_datasets()

# --- HELPER FUNCTION FOR DATA MANAGEMENT FORMS ---
def get_dataset_row(df, dataset_id):
    """Retrieves a single dataset row (Series) by ID, or None if not found."""
    if dataset_id is None:
        return None
    
    filtered_df = df[df['id'] == dataset_id]
    
    if not filtered_df.empty:
        # Return the first matching row as a Pandas Series
        return filtered_df.iloc[0]
    return None

# --- CRUD FUNCTIONALITY (Operating on session state for now) ---

def handle_add_dataset(new_data):
    """Handles the 'Create' operation."""
    current_df = st.session_state['datasets_df']
    
    new_id = current_df['id'].max() + 1 if not current_df.empty and 'id' in current_df.columns else 1
    
    new_row = pd.DataFrame([{
        'id': new_id,
        'title': new_data['title'],
        'severity': new_data['severity'],
        'status': 'Open',
        'timestamp': datetime.now(),
    }])
    
    # Use pd.concat for reliable DataFrame appending
    st.session_state['datasets_df'] = pd.concat([new_row, current_df], ignore_index=True)
    st.success(f"Dataset '{new_data['title']}' added successfully (in memory).")

def handle_update_dataset(dataset_id, updated_data):
    """Handles the 'Update' operation."""
    current_df = st.session_state['datasets_df']
    if 'id' not in current_df.columns:
        st.error("Cannot update: 'id' column is missing.")
        return

    # Find the index of the row to update
    idx_to_update = current_df[current_df['id'] == dataset_id].index
    
    if not idx_to_update.empty:
        # Update fields in the session state DataFrame using .loc
        for key, value in updated_data.items():
            st.session_state['datasets_df'].loc[idx_to_update, key] = value
        st.success(f"Dataset ID {dataset_id} updated successfully (in memory).")
    else:
        st.error(f"Dataset ID {dataset_id} not found for update.")

def handle_delete_dataset(dataset_id):
    """Handles the 'Delete' operation."""
    current_df = st.session_state['datasets_df']
    if 'id' not in current_df.columns:
        st.error("Cannot delete: 'id' column is missing.")
        return

    # Filter out the row with the given ID
    rows_before = len(current_df)
    st.session_state['datasets_df'] = current_df[current_df['id'] != dataset_id].reset_index(drop=True)
    
    rows_after = len(st.session_state['datasets_df'])

    if rows_before > rows_after:
        st.success(f"Dataset ID {dataset_id} deleted successfully (in memory).")
    else:
        st.error(f"Dataset ID {dataset_id} not found for deletion.")


# --- STREAMLIT PAGE FUNCTIONS ---

def display_dashboard(df):
    """Renders the main dashboard metrics and charts."""
    st.title("🛡️ Datasets Dashboard Overview")

    if df.empty:
        st.info("No datasets to display.")
        return
        
    col1, col2, col3 = st.columns(3)
    
    total_datasets = len(df)
    open_datasets = df[df['status'] == 'Open'].shape[0] if 'status' in df.columns else 0
    critical_datasets = df[df['severity'] == 'Critical'].shape[0] if 'severity' in df.columns else 0

    col1.metric("Total Datasets", total_datasets)
    col2.metric("Open Datasets", open_datasets)
    col3.metric("Critical Datasets", critical_datasets)

    st.markdown("---")

    st.header("Datasets Analysis")
    chart_col1, chart_col2 = st.columns(2)

    if 'severity' in df.columns:
        severity_counts = df['severity'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        fig_severity = px.pie(
            severity_counts, 
            values='Count', 
            names='Severity', 
            title='Datasets by Severity',
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        chart_col1.plotly_chart(fig_severity, use_container_width=True)

    if 'status' in df.columns:
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_status = px.bar(
            status_counts, 
            x='Status', 
            y='Count', 
            title='Datasets by Status',
            color='Status',
            color_discrete_map={'Open': '#EF4444', 'In Progress': '#F59E0B', 'Closed': '#10B981'},
        )
        chart_col2.plotly_chart(fig_status, use_container_width=True)

    st.markdown("---")

    st.header("All Datasets Data (R-ead)")
    if 'timestamp' in df.columns:
        df = df.sort_values(by='timestamp', ascending=False)
        
    st.dataframe(df, use_container_width=True, height=350)


def display_crud_form(df):
    """Renders the Add Dataset (Create), Update, and Delete forms using tabs."""
    st.title("🗂️ Dataset Management (Create, Read, Update, Delete)")
    
    can_manage = 'id' in df.columns

    create_tab, update_tab, delete_tab = st.tabs(["➕ Create New", "✏️ Update Existing", "🗑️ Delete Dataset"])
    
    # --- CREATE TAB ---
    with create_tab:
        st.subheader("Add New Dataset")
        
        with st.form("add_dataset_form", clear_on_submit=True):
            
            new_title = st.text_input("Dataset Title", max_chars=100)
            new_severity = st.selectbox("Severity Level", ['Low', 'Medium', 'High', 'Critical'])
            
            submitted = st.form_submit_button("Submit New Dataset")
            
            if submitted:
                if new_title:
                    new_data = {
                        'title': new_title,
                        'severity': new_severity
                    }
                    handle_add_dataset(new_data)
                else:
                    st.error("Please enter a title for the dataset.")

    # --- UPDATE TAB ---
    with update_tab:
        if can_manage and not df.empty:
            st.subheader("Update Dataset Details")
            
            dataset_ids = df['id'].sort_values().tolist()
            
            default_index = 0 if dataset_ids else None 
            
            selected_update_id = st.selectbox("Select Dataset ID to Update", dataset_ids, index=default_index, key='update_id_select')
            
            if selected_update_id is not None:
                current_data = get_dataset_row(df, selected_update_id)
                
                if current_data is not None:
                    with st.form("update_dataset_form"):
                        # Safely access fields using .get() to prevent KeyError
                        current_title = current_data.get('title', 'Title Missing')
                        current_severity = current_data.get('severity', 'Medium')
                        current_status = current_data.get('status', 'Open')
                        
                        st.caption(f"Editing Dataset ID: **{selected_update_id}** - Current Title: **{current_title}**")
                        
                        upd_title = st.text_input("New Title", value=current_title, max_chars=100)
                        
                        severity_options = ['Low', 'Medium', 'High', 'Critical']
                        status_options = ['Open', 'In Progress', 'Closed']
                        
                        upd_severity = st.selectbox(
                            "New Severity Level", 
                            severity_options, 
                            index=severity_options.index(current_severity) if current_severity in severity_options else 0
                        )
                        upd_status = st.selectbox(
                            "New Status", 
                            status_options, 
                            index=status_options.index(current_status) if current_status in status_options else 0
                        )
                        
                        update_submitted = st.form_submit_button("Apply Update", type="primary")
                        
                        if update_submitted:
                            updated_data = {
                                'title': upd_title,
                                'severity': upd_severity,
                                'status': upd_status
                            }
                            handle_update_dataset(selected_update_id, updated_data)
                else:
                     st.info(f"Dataset ID {selected_update_id} not found in current data.")
            else:
                st.info("No datasets available to update.")
        elif not can_manage:
            st.warning("Cannot manage data: 'id' column is missing in the initial dataset.")
        else:
            st.info("No datasets available to update.")
        
    # --- DELETE TAB ---
    with delete_tab:
        if can_manage and not df.empty:
            st.subheader("Delete Dataset")
            
            delete_ids = df['id'].sort_values().tolist()
            
            default_delete_index = 0 if delete_ids else None 
            
            selected_delete_id = st.selectbox("Select Dataset ID to Delete", delete_ids, index=default_delete_index, key='delete_id_select')

            if selected_delete_id is not None:
                st.warning(f"Are you sure you want to delete Dataset ID: **{selected_delete_id}**? This cannot be undone.")

                if st.button("Confirm Delete", type="primary"):
                    handle_delete_dataset(selected_delete_id)
            else:
                st.info("No dataset selected for deletion.")
        elif not can_manage:
            st.warning("Cannot manage data: 'id' column is missing in the initial dataset.")
        else:
            st.info("No datasets available to delete.")


    st.markdown("---")
    
    st.subheader("Current Datasets List (Live View)")
    st.dataframe(df, use_container_width=True)


# --- MAIN APPLICATION LOGIC ---

st.set_page_config(layout="wide")

page = st.sidebar.radio("Navigate Views", ["Dashboard Overview", "Add/Manage Datasets"])
st.sidebar.markdown("---")
st.sidebar.caption(f"Data source file: `{CSV_FILE_PATH}`")


if page == "Dashboard Overview":
    display_dashboard(st.session_state['datasets_df'])
elif page == "Add/Manage Datasets":
    display_crud_form(st.session_state['datasets_df'])