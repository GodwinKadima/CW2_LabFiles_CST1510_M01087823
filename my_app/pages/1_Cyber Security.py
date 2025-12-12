import os 
import sys
import streamlit as st 
import pandas as pd
import plotly.express as px
from datetime import datetime 
from openai import OpenAI
import requests
import json
import time




# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

# If logged in, show dashboard content
st.title("📊 Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")

# --- CRITICAL PATH SETUP ---
# Determine the project root to correctly locate the data folder
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))

# This is often needed for Streamlit app structures to find internal modules
if project_root not in sys.path:
    sys.path.append(project_root)

# Attempt to import an external CRUD module (if it exists)
try:
    # Changed 'datasets_crud' to 'incidents_crud'
    import app.data.incidents as incidents_crud 
    st.sidebar.success("External CRUD module loaded successfully.")
except Exception:
    st.sidebar.caption("CRUD functionality is simulated in memory for this demo.")


# --- CSV FILE PATH DEFINITION ---

def get_data_path(filename):
    """Calculates the absolute path to the data file."""
    return os.path.join(project_root, "DATA", filename)

CSV_FILE_PATH = get_data_path("cyber_incidents_1000.csv")


# --- DATA LOADING AND SESSION STATE INITIALIZATION ---

@st.cache_data
def load_initial_incidents():
    """Reads data from the CSV file for initial state, or creates dummy data on fail."""
    try:
        incidents_df = pd.read_csv(CSV_FILE_PATH, index_col=False)
        incidents_df.columns = incidents_df.columns.str.lower()
        
        if 'timestamp' in incidents_df.columns:
            incidents_df['timestamp'] = pd.to_datetime(incidents_df['timestamp'], errors='coerce')
        
        st.sidebar.success(f"Initial load: {len(incidents_df)} incidents from CSV.")
        return incidents_df
        
    except FileNotFoundError:
        st.sidebar.error(f"Error: CSV file not found at '{CSV_FILE_PATH}'. Running on MOCK data.")
        # Generate mock data if file is missing
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
        st.error(f"Error reading CSV file: {e}")
        return pd.DataFrame()

# Initialize the DataFrame in Streamlit's session state if it doesn't exist
if 'incidents_df' not in st.session_state:
    st.session_state['incidents_df'] = load_initial_incidents()

# --- HELPER FUNCTION FOR DATA MANAGEMENT FORMS ---
def get_incident_row(df, incident_id):
    """Retrieves a single incident row (Series) by ID, or None if not found."""
    if incident_id is None:
        return None
    
    filtered_df = df[df['id'] == incident_id]
    
    if not filtered_df.empty:
        return filtered_df.iloc[0]
    return None

# --- CRUD FUNCTIONALITY (Operating on session state in memory) ---

def handle_add_incident(new_data):
    """Handles the 'Create' operation."""
    current_df = st.session_state['incidents_df']
    
    # Calculate a new unique ID
    new_id = current_df['id'].max() + 1 if not current_df.empty and 'id' in current_df.columns else 1000
    
    new_row = pd.DataFrame([{
        'id': new_id,
        'title': new_data['title'],
        'severity': new_data['severity'],
        'status': 'Open',
        'timestamp': datetime.now(),
    }])
    
    # Use pd.concat for reliable DataFrame appending, placing new incident at the top
    st.session_state['incidents_df'] = pd.concat([new_row, current_df], ignore_index=True)
    st.success(f"Incident '{new_data['title']}' added successfully (in memory). ID: {new_id}")

def handle_update_incident(incident_id, updated_data):
    """Handles the 'Update' operation."""
    current_df = st.session_state['incidents_df']
    if 'id' not in current_df.columns:
        st.error("Cannot update: 'id' column is missing.")
        return

    # Find the index of the row to update
    idx_to_update = current_df[current_df['id'] == incident_id].index
    
    if not idx_to_update.empty:
        # Update fields in the session state DataFrame using .loc
        for key, value in updated_data.items():
            st.session_state['incidents_df'].loc[idx_to_update, key] = value
        st.success(f"Incident ID {incident_id} updated successfully (in memory).")
    else:
        st.error(f"Incident ID {incident_id} not found for update.")

def handle_delete_incident(incident_id):
    """Handles the 'Delete' operation."""
    current_df = st.session_state['incidents_df']
    if 'id' not in current_df.columns:
        st.error("Cannot delete: 'id' column is missing.")
        return

    # Filter out the row with the given ID
    rows_before = len(current_df)
    st.session_state['incidents_df'] = current_df[current_df['id'] != incident_id].reset_index(drop=True)
    
    rows_after = len(st.session_state['incidents_df'])

    if rows_before > rows_after:
        st.success(f"Incident ID {incident_id} deleted successfully (in memory).")
    else:
        st.error(f"Incident ID {incident_id} not found for deletion.")


# --- STREAMLIT PAGE FUNCTIONS ---

def display_dashboard(df):
    """Renders the main dashboard metrics and charts."""
    st.title("Cyber Incidents Dashboard Overview")

    if df.empty:
        st.info("No incidents to display.")
        return
        
    col1, col2, col3 = st.columns(3)
    
    total_incidents = len(df)
    open_incidents = df[df['status'] == 'Open'].shape[0] if 'status' in df.columns else 0
    critical_incidents = df[df['severity'] == 'Critical'].shape[0] if 'severity' in df.columns else 0

    col1.metric("Total Incidents", total_incidents)
    col2.metric("Open Incidents", open_incidents)
    col3.metric("Critical Incidents", critical_incidents)

    st.markdown("---")

    st.header("Incident Analysis")
    chart_col1, chart_col2 = st.columns(2)

    if 'severity' in df.columns:
        severity_counts = df['severity'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        fig_severity = px.pie(
            severity_counts, 
            values='Count', 
            names='Severity', 
            title='Incidents by Severity',
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
            title='Incidents by Status',
            color='Status',
            color_discrete_map={'Open': '#EF4444', 'In Progress': '#F59E0B', 'Closed': '#10B981'},
        )
        chart_col2.plotly_chart(fig_status, use_container_width=True)

    st.markdown("---")

    st.header("All Incidents Data (Read)")
    if 'timestamp' in df.columns:
        df = df.sort_values(by='timestamp', ascending=False)
        
    st.dataframe(df, use_container_width=True, height=350)


def display_crud_form(df):
    """Renders the Add Incident (Create), Update, and Delete forms using tabs."""
    st.title("Incident Management (Create, Update, Delete)")
    
    can_manage = 'id' in df.columns

    create_tab, update_tab, delete_tab = st.tabs(["➕ Create New", "✏️ Update Existing", "🗑️ Delete Incident"])
    
    # --- CREATE TAB ---
    with create_tab:
        st.subheader("Add New Incident")
        
        with st.form("add_incident_form", clear_on_submit=True):
            
            new_title = st.text_input("Incident Title", max_chars=100)
            new_severity = st.selectbox("Severity Level", ['Low', 'Medium', 'High', 'Critical'])
            
            submitted = st.form_submit_button("Submit New Incident", type="primary")
            
            if submitted:
                if new_title:
                    new_data = {
                        'title': new_title,
                        'severity': new_severity
                    }
                    handle_add_incident(new_data)
                else:
                    st.error("Please enter a title for the incident.")

    # --- UPDATE TAB ---
    with update_tab:
        if can_manage and not df.empty:
            st.subheader("Update Incident Details")
            
            incident_ids = df['id'].sort_values().tolist()
            
            # Select the ID to update
            selected_update_id = st.selectbox("Select Incident ID to Update", incident_ids, key='update_id_select')
            
            if selected_update_id is not None:
                current_data = get_incident_row(df, selected_update_id)
                
                if current_data is not None:
                    with st.form("update_incident_form"):
                        # Safely access fields using .get()
                        current_title = current_data.get('title', 'Title Missing')
                        current_severity = current_data.get('severity', 'Medium')
                        current_status = current_data.get('status', 'Open')
                        
                        st.caption(f"Editing Incident ID: **{selected_update_id}** - Current Title: **{current_title}**")
                        
                        upd_title = st.text_input("New Title", value=current_title, max_chars=100)
                        
                        severity_options = ['Low', 'Medium', 'High', 'Critical']
                        status_options = ['Open', 'In Progress', 'Closed']
                        
                        # Set initial index for select boxes
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
                            handle_update_incident(selected_update_id, updated_data)
                else:
                     st.info(f"Incident ID {selected_update_id} not found in current data.")
            else:
                st.info("No incidents available to update.")
        else:
            st.info("No incidents available to update or 'id' column is missing.")
        
    # --- DELETE TAB ---
    with delete_tab:
        if can_manage and not df.empty:
            st.subheader("Delete Incident")
            
            delete_ids = df['id'].sort_values().tolist()
            
            # Select the ID to delete
            selected_delete_id = st.selectbox("Select Incident ID to Delete", delete_ids, key='delete_id_select')

            if selected_delete_id is not None:
                st.warning(f"Are you sure you want to delete Incident ID: **{selected_delete_id}**? This cannot be undone.")

                if st.button("Confirm Delete", type="primary"):
                    handle_delete_incident(selected_delete_id)
            else:
                st.info("No incident selected for deletion.")
        else:
            st.info("No incidents available to delete or 'id' column is missing.")


    st.markdown("---")
    
    st.subheader("Current Incidents List (Live View)")
    # Sort the table to show newest incidents first for better visibility of CRUD operations
    if 'timestamp' in df.columns:
        df = df.sort_values(by='timestamp', ascending=False)
    st.dataframe(df, use_container_width=True)


# --- MAIN APPLICATION LOGIC ---

st.set_page_config(layout="wide")

# Use sidebar radio button to switch between views
page = st.sidebar.radio("Navigate Views", ["Dashboard Overview", "Incident Management (CRUD)"])
st.sidebar.markdown("---")
st.sidebar.caption(f"Data source file: `{CSV_FILE_PATH}`")


if page == "Dashboard Overview":
    # Pass the DataFrame from session state
    display_dashboard(st.session_state['incidents_df'])
elif page == "Incident Management (CRUD)":
    # Pass the DataFrame from session state
    display_crud_form(st.session_state['incidents_df'])


API_KEY = "" 

# NEW: Use the correct OpenAI API URL
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# NEW: Define the OpenAI model you want to use
OPENAI_MODEL = "gpt-4.1-mini" 

MAX_RETRIES = 3
SYSTEM_INSTRUCTION = "You are a Data Science Specialist"

# --- Security Check: Ensure User is Logged In ---
# If the user hasn't logged in, they can't see the chat.
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access the AI Chat.")
    st.stop() 

st.title(f"Welcome, {st.session_state.username}!")
st.subheader("Simple AI Coding Assistant")

# --- Initialize Chat History ---
# Conversation history is stored in Streamlit's session state.
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add an initial greeting message
    st.session_state.messages.append({"role": "assistant", "content": "Hello! Ask me anything about coding or websites! I'll keep the answers simple and fun. 🚀"})

# --- API Call Logic ---
def get_ai_response(prompt, history):
    """Sends the user's prompt and chat history to the OpenAI API."""
    
    # Format the Streamlit history into the structure the OpenAI API expects
    contents = []
    # Note: OpenAI uses 'assistant' for the model's role, which matches Streamlit, 
    # but the history messages need to be built explicitly.
    for msg in history:
        # The history includes roles 'user' and 'assistant'
        contents.append({
            "role": msg["role"], 
            "content": msg["content"]
        })
        
    # Append the current user prompt
    contents.append({
        "role": "user", 
        "content": prompt
    })

    # The payload structure for OpenAI is different from Gemini
    payload_data = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            *contents # The full conversation history plus the system instruction
        ]
    }

    # Use the requests library to communicate with the API
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                OPENAI_API_URL, # *** CHANGED API URL HERE ***
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {API_KEY}' # *** ADDED AUTHORIZATION HEADER ***
                }, 
                data=json.dumps(payload_data)
            )
            response.raise_for_status() 
            
            result = response.json()
            
            # Extract the generated text from the structured JSON response
            # NOTE: OpenAI uses 'message.content' inside 'choices[0]'
            generated_text = result.get('choices', [{}])[0].get('message', {}).get('content')
            
            return generated_text if generated_text else "I couldn't generate a clear response for that request."
            
        except requests.exceptions.RequestException as e:
            # Check for specific authentication errors (e.g., 401 Unauthorized)
            if response.status_code == 401:
                return "Authentication Error: The API Key is invalid or expired. Please check your key."
            
            st.error(f"Connection Error: {e}")
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time) 
            else:
                return "Failed to get a response after several tries. Check your connection or API status."
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            return "An internal error occurred."


# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input Handler ---
if prompt := st.chat_input("Ask me a coding question..."):
    # 1. Add and display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get AI response and display it
    with st.chat_message("assistant"):
        with st.spinner("AI is thinking..."):
            # Send the prompt and the history 
            assistant_response = get_ai_response(prompt, st.session_state.messages) 
            st.markdown(assistant_response)

    # 3. Add AI response to session state
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})