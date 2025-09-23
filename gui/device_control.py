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
HP53131A_FUNCTIONS = {
    'measure_frequency': {'channel': {'type': 'number', 'default': 1}, 'expected_value': {'type': 'text', 'default': 'DEF'}, 'resolution': {'type': 'text', 'default': 'DEF'}},
    'measure_frequency_gated': {'gate_time': {'type': 'number', 'default': 1.0}, 'channel': {'type': 'number', 'default': 1}},
    'measure_period': {'channel': {'type': 'number', 'default': 1}, 'expected_value': {'type': 'text', 'default': 'DEF'}, 'resolution': {'type': 'text', 'default': 'DEF'}},
    'measure_time_interval': {},
    'measure_period_average': {'channel': {'type': 'number', 'default': 1}, 'num_averages': {'type': 'number', 'default': 10}},
    'measure_time_interval_average': {'num_averages': {'type': 'number', 'default': 10}},
    'measure_totalize': {},
    'measure_totalize_timed': {'gate_time': {'type': 'number', 'default': 1.0}}
}

# --- Status Panel Helper Functions ---
def get_mock_status(instrument_name):
    if instrument_name == 'HP3458A':
        return {'Function': 'DCV', 'Error Occurred': 'No', 'Trigger Source': 'HOLD', 'Arm Source': 'AUTO', 'Burst Interval': '0.1s', 'Burst Count': 1, 'Range': 'Auto', 'NPLC': 10.0, 'Auto Zero': 'On'}
    elif instrument_name == 'HP53131A':
        return {'Error Occurred': 'No', 'Measurement': 'Frequency', 'Input Coupling': 'AC', 'Attenuation': '1x', 'Trigger Level': '1.25 V', 'Slope CH1': 'POS', 'Slope CH2': 'POS', 'Input Mode': 'SEPARATE'}
    return {}

def display_status(status_dict):
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
        
# --- UI Helper ---
def create_param_widgets(func_name, param_defs):
    params = {}
    cols = st.columns(len(param_defs)) if param_defs else [st]
    for i, (p_name, p_def) in enumerate(param_defs.items()):
        with cols[i]:
            if p_def['type'] == 'number':
                if p_name == 'mrange':
                    if st.toggle('Autorange', value=(p_def['default'] is None), key=f'{func_name}_{p_name}_toggle'):
                        params[p_name] = None
                    else:
                        params[p_name] = st.number_input(p_name, value=1.0, format='%g', key=f'{func_name}_{p_name}')
                else:
                    params[p_name] = st.number_input(p_name, value=float(p_def['default']), format='%g', key=f'{func_name}_{p_name}')
            elif p_def['type'] == 'boolean':
                params[p_name] = st.checkbox(p_name, value=p_def['default'], key=f'{func_name}_{p_name}')
            elif p_def['type'] == 'text':
                params[p_name] = st.text_input(p_name, value=p_def['default'], key=f'{func_name}_{p_name}')
    return params

# --- Streamlit UI ---
st.set_page_config(layout='wide', page_title='Instrument Control Panel')
st.title('Instrument Control Panel')
st.write("Use the sidebar to connect to an instrument. Navigate to the 'Scenario Builder' page to create test configurations.")

# --- Session State Initialization ---
if 'instrument' not in st.session_state:
    st.session_state.instrument = None
if 'measurement_data' not in st.session_state:
    st.session_state.measurement_data = pd.DataFrame(columns=['Time', 'Measurement'])
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
                st.session_state.instrument_status = get_mock_status(instrument_type)
                st.rerun()
            except Exception as e:
                st.error(f'Connection failed: {e}')

# --- Main Panel ---
if not st.session_state.instrument:
    st.info('Please connect to an instrument using the sidebar.')
else:
    # Status Panel
    with st.container():
        st.markdown('---')
        if st.button('Refresh Status'):
            with st.spinner('Refreshing status...'):
                st.session_state.instrument_status = get_mock_status(st.session_state.instrument.name)
                st.rerun()
        display_status(st.session_state.instrument_status)
        st.markdown('---')

    # Instrument Specific UI
    if isinstance(st.session_state.instrument, HP3458A):
        st.header('HP3458A Digital Multimeter')
        with st.expander('Basic Commands', expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Beep', use_container_width=True): st.session_state.instrument.beep(); st.toast('Beep!')
                if st.button('Read Temperature', use_container_width=True): st.success(f"Internal Temperature: {st.session_state.instrument.temperature()}°C")
            with col2:
                if st.button('Reset Instrument', use_container_width=True): st.session_state.instrument.reset(); st.toast('Instrument Reset!')
                if st.button('Check for Errors', use_container_width=True): st.info(f"Error Status: {st.session_state.instrument.get_error()}")
        with st.expander('Function Configuration', expanded=True):
            func_name = st.selectbox('Function', list(HP3458A_FUNCTIONS.keys()))
            params = create_param_widgets(func_name, HP3458A_FUNCTIONS[func_name])
            if st.button('Configure'):
                with st.spinner('Configuring instrument...'):
                    func_to_call = getattr(st.session_state.instrument, func_name)
                    final_params = {k: v for k, v in params.items() if v is not None}
                    func_to_call(**final_params)
                    st.toast(f'Configured for {func_name}')
        with st.expander('Measurement', expanded=True):
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1: count = st.number_input('Number of Readings', min_value=1, value=1)
            with m_col2: source = st.selectbox('Source', ['HOLD', 'EXT', 'AUTO'])
            with m_col3: arm_source = st.selectbox('Arm Source', ['HOLD', 'EXT', 'AUTO'])
            interval = st.number_input('Interval (s)', min_value=0.0, value=0.1, format='%g', help='Only used if source is not HOLD')
            if st.button('Start Measurement'):
                with st.spinner('Measuring...'):
                    st.session_state.instrument.reading_configuration(count=count, interval=interval, source=source, arm_source=arm_source)
                    reading = st.session_state.instrument.get_reading()
                    new_data = pd.DataFrame({'Time': [pd.to_datetime(time.time(), unit='s')], 'Measurement': [reading]})
                    st.session_state.measurement_data = pd.concat([st.session_state.measurement_data, new_data], ignore_index=True)
                    st.rerun()

    elif isinstance(st.session_state.instrument, HP53131A):
        st.header('HP53131A Universal Counter')
        with st.expander('Measurement Configuration', expanded=True):
            func_name = st.selectbox('Function', list(HP53131A_FUNCTIONS.keys()))
            params = create_param_widgets(func_name, HP53131A_FUNCTIONS[func_name])
            if st.button(f'Configure {func_name}'):
                with st.spinner('Configuring instrument...'):
                    func_to_call = getattr(st.session_state.instrument, func_name)
                    func_to_call(**params)
                    st.toast(f'Configured for {func_name}')
        
        col1, col2 = st.columns(2)
        with col1:
            with st.expander('Channel 1 Configuration'):
                ch1_coupling = st.selectbox('Coupling', ['DC', 'AC'], key='ch1_coupling')
                ch1_slope = st.selectbox('Slope', ['POS', 'NEG'], key='ch1_slope')
                ch1_atten = st.selectbox('Attenuation', [1, 10], key='ch1_atten')
                ch1_trig = st.number_input('Trigger Level (V)', value=0.0, format='%g', key='ch1_trig')
                if st.button('Configure Channel 1'):
                    st.session_state.instrument.measurement_configuration(channel=1, coupling=ch1_coupling, slope=ch1_slope, attenuation_x=ch1_atten, trigger_level=ch1_trig)
                    st.toast('Channel 1 Configured')
        with col2:
            with st.expander('Channel 2 Configuration'):
                ch2_coupling = st.selectbox('Coupling', ['DC', 'AC'], key='ch2_coupling')
                ch2_slope = st.selectbox('Slope', ['POS', 'NEG'], key='ch2_slope')
                ch2_atten = st.selectbox('Attenuation', [1, 10], key='ch2_atten')
                ch2_trig = st.number_input('Trigger Level (V)', value=0.0, format='%g', key='ch2_trig')
                if st.button('Configure Channel 2'):
                    st.session_state.instrument.measurement_configuration(channel=2, coupling=ch2_coupling, slope=ch2_slope, attenuation_x=ch2_atten, trigger_level=ch2_trig)
                    st.toast('Channel 2 Configured')
                
                mode = st.selectbox('Time Interval Input Mode', ['SEPARATE', 'COMMON'], key='ti_mode')
                if st.button('Set Input Mode'):
                    st.session_state.instrument._set_time_interval_input_mode(mode)
                    st.toast(f'Input mode set to {mode}')

        with st.expander('Initiate & Read', expanded=True):
            timeout = st.number_input('Timeout (s)', min_value=1, value=10)
            r_col1, r_col2, r_col3 = st.columns(3)
            with r_col1:
                if st.button('Initiate', use_container_width=True): st.session_state.instrument.initiate(); st.toast('Initiated')
                if st.button('Fetch', use_container_width=True):
                    reading = st.session_state.instrument.fetch()
                    st.success(f'Fetched: {reading}')
                    st.session_state.measurement_data = pd.concat([st.session_state.measurement_data, pd.DataFrame({'Time': [pd.to_datetime(time.time(), unit='s')], 'Measurement': [reading]})], ignore_index=True)
            with r_col2:
                if st.button('Stop', use_container_width=True): st.session_state.instrument.stop(); st.toast('Stopped')
                if st.button('Wait & Fetch', use_container_width=True):
                    reading = st.session_state.instrument.wait_and_fetch(timeout_sec=timeout)
                    st.success(f'Fetched: {reading}')
                    st.session_state.measurement_data = pd.concat([st.session_state.measurement_data, pd.DataFrame({'Time': [pd.to_datetime(time.time(), unit='s')], 'Measurement': [reading]})], ignore_index=True)
            with r_col3:
                if st.button('Initiate, Wait & Fetch', use_container_width=True):
                    reading = st.session_state.instrument.initiate_wait_fetch(timeout_sec=timeout)
                    st.success(f'Fetched: {reading}')
                    st.session_state.measurement_data = pd.concat([st.session_state.measurement_data, pd.DataFrame({'Time': [pd.to_datetime(time.time(), unit='s')], 'Measurement': [reading]})], ignore_index=True)
        
        with st.expander('Basic Commands'):
            if st.button('Reset Instrument'): st.session_state.instrument.reset(); st.toast('Instrument Reset')
            if st.button('Clear Errors'): st.session_state.instrument.clear(); st.toast('Errors Cleared')
            if st.button('Get ID'): st.info(f"Instrument ID: {st.session_state.instrument.id()}")

    # Data Display and Plot
    st.header('Live Measurements')
    if not st.session_state.measurement_data.empty:
        latest_reading = st.session_state.measurement_data['Measurement'].iloc[-1]
        st.metric('Latest Reading', f'{latest_reading:.9f}')
        st.line_chart(st.session_state.measurement_data.set_index('Time'))
        st.dataframe(st.session_state.measurement_data)
    else:
        st.write('No measurements taken yet.')