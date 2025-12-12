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

# --- CRITICAL: DEFINE YOUR CSV FILE PATH ---

def get_data_path(filename):
    """Calculates the absolute path to the data file."""
    # Get the directory of the current script (e.g., /.../my_app/pages/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels to reach the project root directory (../../)
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
    # Combine root, DATA folder (using correct capitalization), and filename 
    return os.path.join(project_root, "DATA", filename)

# Use the function to get the correct path (Consistent with tickets theme)
CSV_FILE_PATH = get_data_path("it_tickets_1000.csv")
# ---------------------------------------------

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

# --- Custom Function to Read Data from CSV ---

@st.cache_data
def get_tickets_from_csv():
    """Reads data from the CSV file. If the file is not found, it creates dummy data."""
    try:
        # 1. Read the actual CSV file using the calculated path
        tickets_df = pd.read_csv(CSV_FILE_PATH, index_col=False)
        
        # 2. Basic cleanup and type conversion 
        if 'timestamp' in tickets_df.columns:
            # Convert timestamp column to datetime objects
            tickets_df['timestamp'] = pd.to_datetime(tickets_df['timestamp'], errors='coerce')
        
        st.sidebar.success(f"Loaded {len(tickets_df)} tickets from CSV.")
        return tickets_df
        
    except FileNotFoundError:
        st.sidebar.error(f"Error: CSV file not found at '{CSV_FILE_PATH}'. Dashboard running on MOCK data.")
        
        # 3. If file not found, generate mock data for demonstration
        data = {
            'id': [1001, 1002, 1003, 1004, 1005, 1006],
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

# --- INITIALIZATION (Use session state for CRUD) ---

if 'tickets_df' not in st.session_state:
    st.session_state['tickets_df'] = get_tickets_from_csv()

# --- HELPER FUNCTIONS FOR CRUD OPERATIONS (In-memory) ---

def get_ticket_row(df, ticket_id):
    """Retrieves a single ticket row (Series) by ID, or None if not found."""
    if ticket_id is None:
        return None
    filtered_df = df[df['id'] == ticket_id]
    if not filtered_df.empty:
        return filtered_df.iloc[0]
    return None

def handle_add_ticket(new_data):
    """Handles the 'Create' operation."""
    current_df = st.session_state['tickets_df']
    
    # Calculate a new unique ID
    new_id = current_df['id'].max() + 1 if not current_df.empty and 'id' in current_df.columns else 1000
    
    new_row = pd.DataFrame([{
        'id': new_id,
        'title': new_data['title'],
        'severity': new_data['severity'],
        'status': 'Open',
        'timestamp': datetime.now(),
    }])
    
    # Prepend the new ticket
    st.session_state['tickets_df'] = pd.concat([new_row, current_df], ignore_index=True)
    st.success(f"Ticket '{new_data['title']}' added successfully (in memory). ID: {new_id}")

def handle_update_ticket(ticket_id, updated_data):
    """Handles the 'Update' operation."""
    current_df = st.session_state['tickets_df']
    if 'id' not in current_df.columns:
        st.error("Cannot update: 'id' column is missing.")
        return

    idx_to_update = current_df[current_df['id'] == ticket_id].index
    
    if not idx_to_update.empty:
        for key, value in updated_data.items():
            st.session_state['tickets_df'].loc[idx_to_update, key] = value
        st.success(f"Ticket ID {ticket_id} updated successfully (in memory).")
    else:
        st.error(f"Ticket ID {ticket_id} not found for update.")

def handle_delete_ticket(ticket_id):
    """Handles the 'Delete' operation."""
    current_df = st.session_state['tickets_df']
    if 'id' not in current_df.columns:
        st.error("Cannot delete: 'id' column is missing.")
        return

    rows_before = len(current_df)
    st.session_state['tickets_df'] = current_df[current_df['id'] != ticket_id].reset_index(drop=True)
    rows_after = len(st.session_state['tickets_df'])

    if rows_before > rows_after:
        st.success(f"Ticket ID {ticket_id} deleted successfully (in memory).")
    else:
        st.error(f"Ticket ID {ticket_id} not found for deletion.")


# --- STREAMLIT PAGE FUNCTIONS ---

def display_dashboard(df):
    """Renders the main dashboard metrics and charts."""
    st.title("Tickets Dashboard Overview")

    if df.empty:
        st.info("No tickets to display.")
        return
        
    # --- Metrics Section (Consistent with tickets) ---
    col1, col2, col3 = st.columns(3)
    
    total_tickets = len(df)
    open_tickets = df[df['status'] == 'Open'].shape[0] if 'status' in df.columns else 0
    critical_tickets = df[df['severity'] == 'Critical'].shape[0] if 'severity' in df.columns else 0

    col1.metric("Total Tickets", total_tickets)
    col2.metric("Open Tickets", open_tickets)
    col3.metric("Critical Tickets", critical_tickets)

    st.markdown("---")

    # --- Charts Section (Consistent with tickets) ---
    st.header("Ticket Analysis")
    chart_col1, chart_col2 = st.columns(2)

    if 'severity' in df.columns:
        severity_counts = df['severity'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        fig_severity = px.pie(
            severity_counts, 
            values='Count', 
            names='Severity', 
            title='Tickets by Severity',
            color_discrete_sequence=px.colors.sequential.Plasma_r 
        )
        chart_col1.plotly_chart(fig_severity, use_container_width=True)
    else:
        chart_col1.warning("Cannot plot Severity: 'severity' column missing.")

    if 'status' in df.columns:
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_status = px.bar(
            status_counts, 
            x='Status', 
            y='Count', 
            title='Tickets by Status',
            color='Status',
            color_discrete_map={'Open': '#EF4444', 'In Progress': '#F59E0B', 'Closed': '#10B981'},
        )
        chart_col2.plotly_chart(fig_status, use_container_width=True)
    else:
        chart_col2.warning("Cannot plot Status: 'status' column missing.")

    st.markdown("---")

    # --- Data Table Section ---
    st.header("All Tickets Data")
    if 'timestamp' in df.columns:
        df = df.sort_values(by='timestamp', ascending=False)
    st.dataframe(df, use_container_width=True, height=350)


def display_crud_form(df):
    """Renders the Add Ticket (Create), Update, and Delete forms using tabs."""
    st.title("Ticket Management (Create, Update, Delete)")
    
    can_manage = 'id' in df.columns

    create_tab, update_tab, delete_tab = st.tabs(["➕ Create New", "✏️ Update Existing", "🗑️ Delete Ticket"])
    
    # --- CREATE TAB ---
    with create_tab:
        st.subheader("Add New Ticket")
        
        with st.form("add_ticket_form", clear_on_submit=True):
            
            new_title = st.text_input("Ticket Title", max_chars=100)
            new_severity = st.selectbox("Severity Level", ['Low', 'Medium', 'High', 'Critical'])
            
            submitted = st.form_submit_button("Submit New Ticket", type="primary")
            
            if submitted:
                if new_title:
                    new_data = {
                        'title': new_title,
                        'severity': new_severity
                    }
                    handle_add_ticket(new_data)
                else:
                    st.error("Please enter a title for the ticket.")

    # --- UPDATE TAB ---
    with update_tab:
        if can_manage and not df.empty:
            st.subheader("Update Ticket Details")
            
            ticket_ids = df['id'].sort_values().tolist()
            
            # Select the ID to update
            selected_update_id = st.selectbox("Select Ticket ID to Update", ticket_ids, key='update_id_select')
            
            if selected_update_id is not None:
                current_data = get_ticket_row(df, selected_update_id)
                
                if current_data is not None:
                    with st.form("update_ticket_form"):
                        # Safely access fields using .get()
                        current_title = current_data.get('title', 'Title Missing')
                        current_severity = current_data.get('severity', 'Medium')
                        current_status = current_data.get('status', 'Open')
                        
                        st.caption(f"Editing Ticket ID: **{selected_update_id}** - Current Title: **{current_title}**")
                        
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
                            handle_update_ticket(selected_update_id, updated_data)
                else:
                     st.info(f"Ticket ID {selected_update_id} not found in current data.")
            else:
                st.info("No tickets available to update.")
        else:
            st.info("No tickets available to update or 'id' column is missing.")
        
    # --- DELETE TAB ---
    with delete_tab:
        if can_manage and not df.empty:
            st.subheader("Delete Ticket")
            
            delete_ids = df['id'].sort_values().tolist()
            
            # Select the ID to delete
            selected_delete_id = st.selectbox("Select Ticket ID to Delete", delete_ids, key='delete_id_select')

            if selected_delete_id is not None:
                st.warning(f"Are you sure you want to delete Ticket ID: **{selected_delete_id}**? This cannot be undone.")

                if st.button("Confirm Delete", type="primary"):
                    handle_delete_ticket(selected_delete_id)
            else:
                st.info("No ticket selected for deletion.")
        else:
            st.info("No tickets available to delete or 'id' column is missing.")


    st.markdown("---")
    
    st.subheader("Current Tickets List (Live View)")
    # Sort the table to show newest tickets first for better visibility of CRUD operations
    if 'timestamp' in df.columns:
        df = df.sort_values(by='timestamp', ascending=False)
    st.dataframe(df, use_container_width=True)


# --- MAIN APPLICATION LOGIC ---

st.set_page_config(layout="wide")

# Use sidebar radio button to switch between views
page = st.sidebar.radio("Navigate Views", ["Dashboard Overview", "Ticket Management (CRUD)"])
st.sidebar.markdown("---")
st.sidebar.caption(f"Data source file: `{CSV_FILE_PATH}`")


if page == "Dashboard Overview":
    # Pass the DataFrame from session state
    display_dashboard(st.session_state['tickets_df'])
elif page == "Ticket Management (CRUD)":
    # Pass the DataFrame from session state
    display_crud_form(st.session_state['tickets_df'])


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