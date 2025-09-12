import streamlit as st
import redis
import json
import time
import os
from pathlib import Path
import subprocess

from robots.parser import MyTestSuite


# --- Page Configuration ---
st.set_page_config(layout='wide', page_title='Test Runner & Dashboard')

# --- Session State Initialization for entire page ---
if 'view' not in st.session_state:
    st.session_state.view = 'explorer'  # Can be 'explorer' or 'dashboard'

# Explorer-specific state
if 'folder_path' not in st.session_state:
    st.session_state.folder_path = ''
if 'robot_files' not in st.session_state:
    st.session_state.robot_files = []
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None
if 'test_process' not in st.session_state:
    st.session_state.test_process = None

# Dashboard-specific state
if 'device_data' not in st.session_state:
    st.session_state.device_data = {}
if 'execution_log' not in st.session_state:
    st.session_state.execution_log = []
if 'redis_client' not in st.session_state:
    st.session_state.redis_client = None
if 'pubsub' not in st.session_state:
    st.session_state.pubsub = None

# --- Helper Functions ---

def find_robot_files(folder):
    """Recursively finds all .robot files in a given folder."""
    try:
        path = Path(folder)
        if not path.is_dir():
            st.error(f'Error: "{folder}" is not a valid directory.')
            return []
        files = sorted(list(path.rglob('*.robot')))
        if not files:
            st.warning(f'No ".robot" files found in the specified directory.')
        return files
    except Exception as e:
        st.error(f"An error occurred while scanning the folder: {e}")
        return []

def format_log_message(msg):
    """Formats a log message with a simpler text-based format."""
    action = msg.get('action', '')
    msg_type = msg.get('type', '')
    name = msg.get('name', '')
    status = msg.get('status', '')
    log_string = f"{action} {msg_type}: {name}"
    if status == 'PASS':
        return f"{log_string} - **:green[{status}]**"
    elif status == 'FAIL':
        return f"{log_string} - **:red[{status}]**"
    return log_string

def render_test_suite_overview(file_path):
    """Parse a Robot Framework file and render its test cases and keywords as expandable cards."""
    suite = MyTestSuite.from_file(str(file_path))
    if suite.libraries:
        libs = ', '.join(suite.libraries)
        st.markdown(f"**Libraries Used:** {libs}")
    for tc in suite.testcases:
        with st.expander(f"Test Case: {tc.name} (Line {tc.lineno})", expanded=False):
            if tc.documentation:
                st.markdown(f"**Documentation:** {tc.documentation}")
            if not tc.keywords:
                st.info("No keywords found.")
            else:
                for kw in tc.keywords:
                    st.markdown(f"- **{kw.name}** (Line {kw.lineno})")

# --- UI Rendering Functions ---

def render_explorer_view():
    """Renders the UI for finding and running Robot Framework files."""
    st.title('🤖 Robot Test Runner')
    st.write("Enter the absolute path to a folder containing your test suites to get started.")

    folder_input = st.text_input(
        "Test Suite Folder Path",
        value=st.session_state.folder_path,
        placeholder="e.g., C:/Users/YourUser/Documents/robot-tests"
    )

    if st.button("Scan Folder"):
        st.session_state.folder_path = folder_input
        st.session_state.robot_files = find_robot_files(folder_input)
        st.session_state.selected_file = None

    # --- Sidebar for File Navigation ---
    st.sidebar.header("Test Suites")
    if not st.session_state.robot_files:
        st.sidebar.info("Scan a folder to see test files.")
    else:
        file_display_names = [f.name for f in st.session_state.robot_files]
        selected_display_name = st.sidebar.radio("Select a file to run:", options=file_display_names)
        for f in st.session_state.robot_files:
            if f.name == selected_display_name:
                st.session_state.selected_file = f
                break

    # --- Main Area for File Content and Run Button ---
    if st.session_state.selected_file:
        st.subheader(f"Viewing: `{os.path.relpath(st.session_state.selected_file, st.session_state.folder_path)}`")
        
        # Run button is placed above the code view
        if st.button(f"▶️ Run Test: {st.session_state.selected_file.name}", type="primary"):
            try:
                # 1. Start the robot process
                command = ["robot", str(st.session_state.selected_file)]
                st.session_state.test_process = subprocess.Popen(command)
                st.toast(f"Started process for: {st.session_state.selected_file.name}")

                # 2. Connect to Redis automatically
                r = redis.Redis(host='localhost', port=6379, decode_responses=True)
                r.ping()
                st.session_state.redis_client = r
                st.session_state.pubsub = st.session_state.redis_client.pubsub()
                st.session_state.pubsub.subscribe('robot_events')
                
                # 3. Switch to the dashboard view
                st.session_state.view = 'dashboard'
                st.rerun()

            except FileNotFoundError:
                st.error("Error: 'robot' command not found. Is Robot Framework installed and in your system's PATH?")
            except redis.exceptions.ConnectionError as e:
                 st.error(f"Could not connect to Redis to monitor the test. Is it running? Error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

        # Display file content
        try:
            content = st.session_state.selected_file.read_text(encoding='utf-8')
            st.code(content, language='robotframework', line_numbers=True)
            # Render parsed test suite overview below code
            render_test_suite_overview(st.session_state.selected_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("Select a file from the sidebar to view its content and run the test.")


def render_dashboard_view():
    """Renders the live monitoring dashboard."""
    # --- Sidebar Controls for Dashboard ---
    st.sidebar.header("Test Control")
    if st.sidebar.button("⬅️ Run Another Test"):
        if st.session_state.pubsub:
            st.session_state.pubsub.unsubscribe()
            st.session_state.pubsub.close()
        st.session_state.redis_client = None
        st.session_state.pubsub = None
        st.session_state.view = 'explorer'
        st.rerun()

    # --- Main Page Layout ---
    main_area, right_sidebar = st.columns([3, 1])

    with main_area:
        st.header("Device Status")
        if not st.session_state.device_data:
            st.info("Waiting for first measurement data from test run...")

        COLS_PER_ROW = 3
        device_names = sorted(list(st.session_state.device_data.keys()))
        placeholders = {}
        device_chunks = [device_names[i:i + COLS_PER_ROW] for i in range(0, len(device_names), COLS_PER_ROW)]

        for chunk in device_chunks:
            device_cols = st.columns(len(chunk))
            for i, device_name in enumerate(chunk):
                with device_cols[i]:
                    placeholders[device_name] = st.empty()

    with right_sidebar:
        st.header("Test Execution Log")
        log_placeholder = st.empty()

    # --- Main Loop ---
    while True:
        # Update UI with current state
        for device_name, placeholder in placeholders.items():
            if device_name in st.session_state.device_data:
                device_info = st.session_state.device_data[device_name]
                with placeholder.container(border=True):
                    # Display device header with status color
                    if device_info['status'] == 'ERROR':
                        st.error(f"**{device_name}**")
                    else:
                        st.success(f"**{device_name}**")

                    channels = device_info.get('channels', [])
                    if not channels:
                        st.text("No measurements received yet.")
                    else:
                        for i, channel in enumerate(channels):
                            # Only show channel number if there's more than one
                            if len(channels) > 1:
                                st.text(f"Channel {i + 1}")
                            
                            if not channel:
                                st.text("No measurements for this channel.")
                                continue

                            # Create columns for measurements within a channel if there are multiple
                            num_measurements = len(channel)
                            metric_cols = st.columns(num_measurements) if num_measurements > 1 else [st]
                                
                            for j, measurement in enumerate(channel):
                                col = metric_cols[j] if num_measurements > 1 else st
                                metric_label = (measurement.get('value_type') or 'Measurement').title()
                                metric_value = f"{measurement.get('value', 'N/A')} {measurement.get('value_unit', '')}".strip()
                                col.caption(metric_label)
                                col.text(metric_value)
        
        with right_sidebar:
            log_placeholder.markdown("\n\n".join(st.session_state.execution_log[::-1]), unsafe_allow_html=True)

        # Process new message from Redis
        message = st.session_state.pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
        if message:
            msg_data = json.loads(message['data'])
            msg_type = msg_data.get('type')

            if msg_type == 'data':
                owner = msg_data.get('owner')
                if owner and owner not in st.session_state.device_data:
                    # Initialize new device with the correct structure
                    st.session_state.device_data[owner] = {'status': 'OK', 'channels': []}
                    st.rerun()
                
                if owner in st.session_state.device_data:
                    # Store the entire list of channels and their measurements
                    st.session_state.device_data[owner]['channels'] = msg_data.get('data', [])

            elif msg_type in ['suite', 'keyword']:
                if msg_type == 'suite' and msg_data.get('action') == 'start':
                    st.session_state.execution_log = ["--- Listening for new test runs ---"]
                    for device in st.session_state.device_data.values():
                        device['status'] = 'OK'
                if msg_data.get('status') == 'FAIL':
                    name = msg_data.get('name', '').upper()
                    for device_name in st.session_state.device_data:
                        if device_name.upper() in name:
                            st.session_state.device_data[device_name]['status'] = 'ERROR'
                log_entry = format_log_message(msg_data)
                st.session_state.execution_log.append(log_entry)
        
        time.sleep(0.1)


# --- Main Controller ---
if st.session_state.view == 'explorer':
    render_explorer_view()
else:
    render_dashboard_view()
