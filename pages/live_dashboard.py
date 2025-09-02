import streamlit as st
import redis
import json
import time

st.set_page_config(layout='wide', page_title='Live Monitoring Dashboard')

# --- Session State Initialization ---
if 'device_data' not in st.session_state:
    # Start with an empty dictionary. Devices will be added dynamically as data arrives.
    st.session_state.device_data = {}
if 'execution_log' not in st.session_state:
    st.session_state.execution_log = []
if 'redis_client' not in st.session_state:
    st.session_state.redis_client = None
if 'pubsub' not in st.session_state:
    st.session_state.pubsub = None

# --- Helper Functions ---
def format_log_message(msg):
    """Formats a log message with a simpler text-based format."""
    action = msg.get('action', '')
    msg_type = msg.get('type', '') # Keep it lowercase as per user example
    name = msg.get('name', '')
    status = msg.get('status', '')

    log_string = f"{action} {msg_type}: {name}"

    if status == 'PASS':
        return f"{log_string} - **:green[{status}]**"
    elif status == 'FAIL':
        return f"{log_string} - **:red[{status}]**"
    
    return log_string # For start/end actions without a final status

# --- UI Layout ---
st.sidebar.header("Redis Connection")
redis_host = st.sidebar.text_input("Host", "localhost")
redis_port = st.sidebar.number_input("Port", 6379)
redis_channel = st.sidebar.text_input("Channel", "robot_events")

if st.sidebar.button("Connect and Start Listening"):
    try:
        # Clear state on new connection attempt
        st.session_state.device_data = {}
        st.session_state.execution_log = ["--- Listening for new test runs ---"]
        
        r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        r.ping()
        st.session_state.redis_client = r
        st.session_state.pubsub = st.session_state.redis_client.pubsub()
        st.session_state.pubsub.subscribe(redis_channel)
        st.sidebar.success(f"Subscribed to channel '{redis_channel}'")
        st.rerun()

    except Exception as e:
        st.sidebar.error(f"Failed to connect to Redis: {e}")
        st.session_state.redis_client = None
        st.session_state.pubsub = None

if st.sidebar.button("Stop Listening"):
    if st.session_state.pubsub:
        st.session_state.pubsub.unsubscribe()
        st.session_state.pubsub.close()
    st.session_state.redis_client = None
    st.session_state.pubsub = None
    st.sidebar.info("Stopped listening.")


# --- Main Page Layout ---
main_area, right_sidebar = st.columns([3, 1])

with main_area:
    st.header("Device Status")

    # This section now handles the case where no devices have been discovered yet
    if not st.session_state.device_data:
        st.info("Waiting for first measurement data to populate devices...")

    # --- Dynamic Row/Column Logic ---
    COLS_PER_ROW = 3 # Max number of devices per row
    # Sort to maintain a consistent order
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
if not st.session_state.pubsub:
    main_area.info("Connect to a Redis server using the sidebar to see live data.")
else:
    while True:
        # Update UI with current state for existing devices
        for device_name, placeholder in placeholders.items():
            if device_name in st.session_state.device_data:
                data = st.session_state.device_data[device_name]
                with placeholder.container(border=True):
                    if data['status'] == 'ERROR':
                        st.error(f"**{device_name}**")
                        st.metric("Last Measurement", data['measurement'], delta="Error Detected", delta_color="inverse")
                    else:
                        st.success(f"**{device_name}**")
                        st.metric("Last Measurement", data['measurement'])
        
        with right_sidebar:
            log_placeholder.markdown("\n\n".join(st.session_state.execution_log[::-1]), unsafe_allow_html=True)

        # Process new message from Redis
        message = st.session_state.pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
        if message:
            msg_data = json.loads(message['data'])
            msg_type = msg_data.get('type')

            if msg_type == 'data':
                owner = msg_data.get('owner')
                
                # DYNAMIC DEVICE ADDITION LOGIC
                if owner and owner not in st.session_state.device_data:
                    st.session_state.device_data[owner] = {'measurement': 'N/A', 'status': 'OK'}
                    st.rerun() # Rerun the script to redraw UI with the new device box

                if owner in st.session_state.device_data:
                    st.session_state.device_data[owner]['measurement'] = msg_data.get('data')

            elif msg_type in ['suite', 'keyword']:
                if msg_type == 'suite' and msg_data.get('action') == 'start':
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
