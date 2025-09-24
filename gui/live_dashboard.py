import json
import os

import streamlit as st
import redis
import requests

# from robots.parser import MyTestSuite


# --- Page Configuration ---
st.set_page_config(layout='wide', page_title='Test Runner & Dashboard')

# --- Session State Initialization for entire page ---
if 'view' not in st.session_state:
    st.session_state.view = 'explorer'  # Can be 'explorer' or 'dashboard'

# Explorer-specific state
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
if 'progress' not in st.session_state:
    st.session_state.progress = 0.0

# --- Helper Functions ---

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
    return
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

def start_robot_test_api(file_obj):
    """Send the selected .robot file to the API server via POST request."""
    api_url = os.environ.get('ROBOT_API_URL', 'http://localhost')
    api_port = os.environ.get('ROBOT_API_PORT', '5000')
    url = f"{api_url}:{api_port}/run-test"
    files = {'robot_file': (file_obj.name, file_obj, 'text/plain')}
    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            st.toast("Test started via API server.")
            return True, response.json()
        else:
            error_msg = response.json().get('error', 'Unknown error')
            st.error(f"API Error: {error_msg}")
            return False, response.json()
    except Exception as e:
        st.error(f"Failed to contact API server: {e}")
        return False, {'error': str(e)}

# --- UI Rendering Functions ---

def connect_to_redis():
    """Establishes a connection to Redis and sets up pub/sub."""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        st.session_state.redis_client = r
        st.session_state.pubsub = st.session_state.redis_client.pubsub()
        st.session_state.pubsub.subscribe('robot_events')
        return True
    except redis.exceptions.ConnectionError as e:
        st.error(f"Could not connect to Redis. Is it running? Error: {e}")
        return False

def render_explorer_view():
    """Renders the UI for selecting and running Robot Framework files."""
    st.title('🤖 Robot Test Runner')
    st.write("Select one or more Robot Framework test files from disk to get started.")

    uploaded_files = st.file_uploader(
        "Choose Robot Framework file(s)",
        type=["robot"],
        accept_multiple_files=True
    )

    # Sidebar for file navigation
    st.sidebar.header("Test Suites")
    if not uploaded_files:
        st.sidebar.info("Upload one or more .robot files to see test files.")
        st.session_state.selected_file = None
    else:
        file_display_names = [f.name for f in uploaded_files]
        selected_display_name = st.sidebar.radio("Select a file to run:", options=file_display_names)
        for f in uploaded_files:
            if f.name == selected_display_name:
                st.session_state.selected_file = f
                break

    # Main Area for File Content and Run Button
    if st.session_state.selected_file:
        st.subheader(f"Viewing: `{st.session_state.selected_file.name}`")
        if st.button(f"▶️ Run Test: {st.session_state.selected_file.name}", type="primary"):
            success, result = start_robot_test_api(st.session_state.selected_file)
            if success:
                connect_to_redis()
                st.session_state.view = 'dashboard'
                st.rerun()
        # Display file content
        try:
            content = st.session_state.selected_file.read().decode('utf-8')
            st.code(content, language='robotframework', line_numbers=True)
            # Optionally render parsed test suite overview
            # render_test_suite_overview(st.session_state.selected_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("Select a file from the sidebar to view its content and run the test.")
        
def process_new_redis_message():
    message = st.session_state.pubsub.get_message(ignore_subscribe_messages=True, timeout=60)
    if not message:
        return
    msg_data = json.loads(message['data'])
    msg_type = msg_data.get('type')

    if msg_type == 'data':
        owner = msg_data.get('owner')
        if not owner:
            return
        st.session_state.device_data[owner] = msg_data
        st.rerun()

    elif msg_type in ['suite', 'keyword', 'test']:
        if msg_type == 'suite' and msg_data.get('action') == 'start':
            st.session_state.execution_log = ["--- Listening for new test runs ---"]
        log_entry = format_log_message(msg_data)
        st.session_state.execution_log.append(log_entry)
        st.session_state.progress = msg_data.get('progress', 0)


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
    # Priority window selector
    all_priorities = sorted(set(
        device.get('priority', 0)
        for device in st.session_state.device_data.values()
    ))
    if 'selected_priority' not in st.session_state:
        st.session_state.selected_priority = all_priorities[0] if all_priorities else 0
    # Render priority buttons inline
    for prio in all_priorities:
        if st.button(f'Window {prio}', key=f'window_{prio}'):
            st.session_state.selected_priority = prio

    main_area, right_sidebar = st.columns([3, 1])

    with main_area:
        st.header(f"Device Status (Window {st.session_state.selected_priority})")
        # Only show devices with selected priority
        filtered_devices = {
            k: v for k, v in st.session_state.device_data.items()
            if v.get('priority', 0) == st.session_state.selected_priority
        }
        if not filtered_devices:
            st.info("No devices in this window.")

        COLS_PER_ROW = 3
        device_names = sorted(list(filtered_devices.keys()))
        placeholders = {}
        device_chunks = [device_names[i:i + COLS_PER_ROW] for i in range(0, len(device_names), COLS_PER_ROW)]

        for chunk in device_chunks:
            device_cols = st.columns(len(chunk))
            for i, device_name in enumerate(chunk):
                with device_cols[i]:
                    placeholders[device_name] = st.empty()

    with right_sidebar:
        st.header("Test Execution Log")
        # progress bar
        progress_bar = st.progress(0)
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

                    channels = device_info.get('data', [])
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
            progress_bar.progress(st.session_state.progress)
            log_placeholder.markdown("\n\n".join(st.session_state.execution_log[::-1]), unsafe_allow_html=True)

        # Process new message from Redis
        process_new_redis_message()


# --- Main Controller ---
if st.session_state.view == 'explorer':
    render_explorer_view()
else:
    render_dashboard_view()
