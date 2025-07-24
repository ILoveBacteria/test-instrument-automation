import streamlit as st
import pandas as pd
import time

from adapters.gpib_adapter import PrologixGPIBEthernet
from adapters.pyvisa_adapter import PyVisaAdapter
from devices.hp3458a import HP3458A
from devices.hp53131a import HP53131A



# --- UI Configuration Data ---
HP3458A_FUNCTIONS = {
    'conf_function_DCV': {'mrange': {'type': 'number', 'default': None}, 'nplc': {'type': 'number', 'default': 1}, 'AutoZero': {'type': 'boolean', 'default': True}, 'HiZ': {'type': 'boolean', 'default': False}},
    'conf_function_DCI': {'mrange': {'type': 'number', 'default': None}, 'nplc': {'type': 'number', 'default': 1}, 'AutoZero': {'type': 'boolean', 'default': True}, 'HiZ': {'type': 'boolean', 'default': False}},
    'conf_function_ACV': {'mrange': {'type': 'number', 'default': None}, 'nplc': {'type': 'number', 'default': 1}},
    'conf_function_ACI': {'mrange': {'type': 'number', 'default': None}, 'nplc': {'type': 'number', 'default': 1}},
    'conf_function_OHM2W': {'mrange': {'type': 'number', 'default': None}, 'nplc': {'type': 'number', 'default': 1}, 'AutoZero': {'type': 'boolean', 'default': True}, 'OffsetCompensation': {'type': 'boolean', 'default': False}},
    'conf_function_OHM4W': {'mrange': {'type': 'number', 'default': None}, 'nplc': {'type': 'number', 'default': 1}, 'AutoZero': {'type': 'boolean', 'default': True}, 'OffsetCompensation': {'type': 'boolean', 'default': False}},
    'conf_function_FREQ': {'mrange': {'type': 'text', 'default': 'AUTO'}, 'gate_time': {'type': 'number', 'default': 1.0}},
    'conf_function_ACDCV': {'mrange': {'type': 'number', 'default': None}, 'nplc': {'type': 'number', 'default': 1}, 'ac_bandwidth_low': {'type': 'number', 'default': 20}, 'HiZ': {'type': 'boolean', 'default': False}},
    'conf_function_digitize': {'mode': {'type': 'text', 'default': 'DSDC'}, 'mrange': {'type': 'number', 'default': 10}, 'delay': {'type': 'number', 'default': 0}, 'num_samples': {'type': 'number', 'default': 1024}, 'sample_interval': {'type': 'number', 'default': 100e-9}}
}

# --- Status Panel Helper Functions ---
def get_mock_status(instrument_name):
    """Generates a dictionary of mock status values for a given instrument."""
    if instrument_name == 'HP3458A':
        return {
            'Function': 'DCV', 'Error Occurred': 'No', 'Trigger Source': 'HOLD', 'Arm Source': 'AUTO',
            'Burst Interval': '0.1s', 'Burst Count': 1, 'Range': 'Auto', 'NPLC': 10.0, 'Auto Zero': 'On'
        }
    elif instrument_name == 'HP53131A':
        return {
            'Error Occurred': 'No', 'Measurement': 'Frequency', 'Input Coupling': 'AC', 'Attenuation': '1x',
            'Trigger Level': '1.25 V', 'Slope CH1': 'POS', 'Slope CH2': 'POS', 'Input Mode': 'SEPARATE'
        }
    return {}

def display_status(status_dict):
    """Renders the status dictionary in a grid layout."""
    if not status_dict:
        st.info('Status not available. Click refresh to fetch.')
        return

    st.subheader('Instrument Status')
    cols = st.columns(4)
    col_idx = 0
    for key, value in status_dict.items():
        with cols[col_idx]:
            st.metric(label=key, value=str(value))
        col_idx = (col_idx + 1) % 4
        

# --- Streamlit UI ---
st.set_page_config(layout='wide', page_title='Instrument Control Panel')
st.title('Instrument Control Panel')
st.write("Use the sidebar to connect to an instrument. Navigate to the 'Scenario Builder' page to create test configurations.")

# --- Session State Initialization ---
if 'instrument' not in st.session_state:
    st.session_state.instrument = None
if 'measurement_data' not in st.session_state:
    st.session_state.measurement_data = pd.DataFrame(columns=['Time', 'Measurement'])
if 'totalizer_running' not in st.session_state:
    st.session_state.totalizer_running = False
if 'instrument_status' not in st.session_state:
    st.session_state.instrument_status = None

# --- Sidebar for Connection ---
with st.sidebar:
    st.header('Connection')
    
    if st.session_state.instrument:
        st.success(f'Connected to {st.session_state.instrument.name}')
        if st.button('Disconnect'):
            st.session_state.instrument.adapter.close()
            st.session_state.instrument = None
            st.session_state.measurement_data = pd.DataFrame(columns=['Time', 'Measurement'])
            st.session_state.instrument_status = None
            st.rerun()
    else:
        instrument_type = st.selectbox('Instrument', ['HP3458A', 'HP53131A'])
        connection_type = st.selectbox('Connection Type', ['PyVISA', 'Prologix GPIB-Ethernet'])

        if connection_type == 'PyVISA':
            visa_string = st.text_input('VISA Resource String', 'GPIB0::2::INSTR')
        else:
            prologix_ip = st.text_input('Prologix IP Address', '192.168.1.101')
            gpib_addr = st.number_input('GPIB Address', 1, 30, 2)

        if st.button('Connect'):
            try:
                adapter = None
                if connection_type == 'PyVISA':
                    adapter = PyVisaAdapter(visa_string)
                else:
                    adapter = PrologixGPIBEthernet(prologix_ip, gpib_addr, prologix_read_timeout=0.5, socket_read_timeout=15)

                if instrument_type == 'HP3458A':
                    st.session_state.instrument = HP3458A(name='HP3458A', adapter=adapter)
                else:
                    st.session_state.instrument = HP53131A(name='HP53131A', adapter=adapter)
                
                st.session_state.instrument.setup()
                st.success('Connection successful!')
                # Fetch initial status on connect
                st.session_state.instrument_status = get_mock_status(instrument_type)
                st.rerun()
            except Exception as e:
                st.error(f'Connection failed: {e}')


# --- Main Panel ---
if not st.session_state.instrument:
    st.info('Please connect to an instrument using the sidebar.')
else:
    # --- Status Panel ---
    status_container = st.container()
    with status_container:
        st.markdown('---')
        
        if st.button('Refresh Status'):
            with st.spinner('Refreshing status...'):
                st.session_state.instrument_status = get_mock_status(st.session_state.instrument.name)
                st.rerun()

        display_status(st.session_state.instrument_status)
        st.markdown('---')


    # --- Instrument Specific UI ---
    if isinstance(st.session_state.instrument, HP3458A):
        st.header('HP3458A Digital Multimeter')
        
        with st.expander('Basic Commands', expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Beep', use_container_width=True):
                    st.session_state.instrument.beep()
                    st.toast('Beep!')
                if st.button('Read Temperature', use_container_width=True):
                    temp = st.session_state.instrument.temperature()
                    st.success(f'Internal Temperature: {temp}°C')
            with col2:
                if st.button('Reset Instrument', use_container_width=True):
                    st.session_state.instrument.reset()
                    st.toast('Instrument Reset!')
                if st.button('Check for Errors', use_container_width=True):
                    error = st.session_state.instrument.get_error()
                    st.info(f'Error Status: {error}')

        with st.expander('Function Configuration', expanded=True):
            func_name = st.selectbox('Function', list(HP3458A_FUNCTIONS.keys()))
            params = {}
            param_defs = HP3458A_FUNCTIONS[func_name]
            
            # Create columns for parameters
            cols = st.columns(len(param_defs) if len(param_defs) > 0 else 1)
            
            for i, (p_name, p_def) in enumerate(param_defs.items()):
                with cols[i]:
                    if p_def['type'] == 'number':
                        # Special handling for mrange which can be None for autorange
                        if p_name == 'mrange':
                            if st.toggle('Autorange', value=(p_def['default'] is None), key=f'{func_name}_{p_name}_toggle'):
                                params[p_name] = None
                            else:
                                params[p_name] = st.number_input(p_name, value=1.0, format='%g', key=f'{func_name}_{p_name}')
                        else:
                            params[p_name] = st.number_input(p_name, value=p_def['default'], format='%g', key=f'{func_name}_{p_name}')
                    elif p_def['type'] == 'boolean':
                        params[p_name] = st.checkbox(p_name, value=p_def['default'], key=f'{func_name}_{p_name}')
                    elif p_def['type'] == 'text':
                         params[p_name] = st.text_input(p_name, value=p_def['default'], key=f'{func_name}_{p_name}')

            if st.button('Configure'):
                with st.spinner('Configuring instrument...'):
                    func_to_call = getattr(st.session_state.instrument, func_name)
                    # Filter out None mrange before calling
                    final_params = {k: v for k, v in params.items() if v is not None}
                    func_to_call(**final_params)
                    st.toast(f'Configured for {func_name}')

        with st.expander('Measurement', expanded=True):
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                count = st.number_input('Number of Readings', min_value=1, value=1)
            with m_col2:
                source = st.selectbox('Source', ['HOLD', 'EXT', 'AUTO'])
            with m_col3:
                arm_source = st.selectbox('Arm Source', ['HOLD', 'EXT', 'AUTO'])
            
            interval = st.number_input('Interval (s)', min_value=0.0, value=0.1, format='%g', help='Only used if source is not HOLD')

            if st.button('Start Measurement'):
                with st.spinner('Measuring...'):
                    st.session_state.instrument.reading_configuration(count=count, interval=interval, source=source, arm_source=arm_source)
                    reading = st.session_state.instrument.get_reading()
                    new_data = pd.DataFrame({'Time': [pd.to_datetime(time.time(), unit='s')], 'Measurement': [reading]})
                    st.session_state.measurement_data = pd.concat([st.session_state.measurement_data, new_data], ignore_index=True)
                    st.rerun()

    elif isinstance(st.session_state.instrument, HP53131A):
        # This section remains unchanged
        st.header('HP53131A Universal Counter')
        col1, col2 = st.columns(2)
        with col1:
            with st.expander('Basic Commands', expanded=True):
                if st.button('Reset Instrument'): st.session_state.instrument.reset(); st.toast('Instrument Reset')
                if st.button('Clear Errors'): st.session_state.instrument.clear(); st.toast('Errors Cleared')
                if st.button('Get ID'): st.info(f"Instrument ID: {st.session_state.instrument.id()}")
        with col2:
            with st.expander('Totalizer', expanded=True):
                tot_channel = st.selectbox('Counter Channel', [1, 2], key='tot_ch')
                if not st.session_state.totalizer_running:
                    if st.button('Start Totalizer'):
                        st.session_state.instrument.start_totalize(channel=tot_channel)
                        st.session_state.totalizer_running = True
                        st.rerun()
                else:
                    if st.button('Stop and Read Totalizer'):
                        count = st.session_state.instrument.stop_and_fetch_totalize()
                        st.metric('Total Count', count)
                        st.session_state.totalizer_running = False
                        st.rerun()
        with st.expander('Single Measurement', expanded=True):
            meas_type = st.selectbox('Measurement Type', ['Frequency', 'Period', 'Time Interval'])
            channel = 1
            if meas_type != 'Time Interval':
                channel = st.selectbox('Channel', [1, 2], key='meas_ch')
            if st.button(f'Measure {meas_type}'):
                with st.spinner(f'Measuring {meas_type}...'):
                    reading = None
                    if meas_type == 'Frequency': reading = st.session_state.instrument.measure_frequency(channel=channel)
                    elif meas_type == 'Period': reading = st.session_state.instrument.measure_period(channel=channel)
                    elif meas_type == 'Time Interval': reading = st.session_state.instrument.measure_time_interval()
                    
                    if reading is not None:
                        new_data = pd.DataFrame({'Time': [pd.to_datetime(time.time(), unit='s')], 'Measurement': [reading]})
                        st.session_state.measurement_data = pd.concat([st.session_state.measurement_data, new_data], ignore_index=True)
                        st.rerun()

    # --- Data Display and Plot ---
    st.header('Live Measurements')
    if not st.session_state.measurement_data.empty:
        latest_reading = st.session_state.measurement_data['Measurement'].iloc[-1]
        st.metric('Latest Reading', f'{latest_reading:.9f}')
        st.line_chart(st.session_state.measurement_data.set_index('Time'))
        st.dataframe(st.session_state.measurement_data)
    else:
        st.write('No measurements taken yet.')