import streamlit as st
import pandas as pd
import time

from adapters.gpib_adapter import PrologixGPIBEthernet
from adapters.pyvisa_adapter import PyVisaAdapter
from devices.hp3458a import HP3458A
from devices.hp53131a import HP53131A


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

# --- Sidebar for Connection ---
with st.sidebar:
    st.header('Connection')
    
    if st.session_state.instrument:
        st.success(f'Connected to {st.session_state.instrument.name}')
        if st.button('Disconnect'):
            st.session_state.instrument.adapter.close()
            st.session_state.instrument = None
            st.session_state.measurement_data = pd.DataFrame(columns=['Time', 'Measurement'])
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
                st.rerun()
            except Exception as e:
                st.error(f'Connection failed: {e}')


# --- Main Panel ---
if not st.session_state.instrument:
    st.info('Please connect to an instrument using the sidebar.')
else:
    # --- Instrument Specific UI ---
    if isinstance(st.session_state.instrument, HP3458A):
        st.header('HP3458A Digital Multimeter')
        
        col1, col2 = st.columns(2)
        with col1:
            with st.expander('Basic Commands', expanded=True):
                if st.button('Beep'):
                    st.session_state.instrument.beep()
                    st.toast('Beep!')
                if st.button('Reset Instrument'):
                    st.session_state.instrument.reset()
                    st.toast('Instrument Reset')
                if st.button('Read Temperature'):
                    temp = st.session_state.instrument.temperature()
                    st.metric('Internal Temperature', f'{temp}°C')
                if st.button('Check for Errors'):
                    error = st.session_state.instrument.get_error()
                    st.info(f'Error Status: {error}')

        with col2:
            with st.expander('Measurement Configuration', expanded=True):
                func = st.selectbox('Function', ['DCV', 'ACV', 'OHM2W'])
                nplc = st.number_input('NPLC (Power Line Cycles)', 0.001, 100.0, 1.0, 0.1)
                autorange = st.toggle('Autorange', True)
                mrange = st.number_input('Manual Range', value=1.0, disabled=autorange)
                
                if st.button('Configure and Measure'):
                    with st.spinner('Measuring...'):
                        if func == 'DCV':
                            st.session_state.instrument.conf_function_DCV(mrange=None if autorange else mrange, nplc=nplc)
                        elif func == 'ACV':
                            st.session_state.instrument.conf_function_ACV(mrange=None if autorange else mrange, nplc=nplc)
                        elif func == 'OHM2W':
                            st.session_state.instrument.conf_function_OHM2W(mrange=None if autorange else mrange, nplc=nplc)
                        
                        reading = st.session_state.instrument.get_reading()
                        
                        new_data = pd.DataFrame({'Time': [pd.to_datetime(time.time(), unit='s')], 'Measurement': [reading]})
                        st.session_state.measurement_data = pd.concat([st.session_state.measurement_data, new_data], ignore_index=True)

    elif isinstance(st.session_state.instrument, HP53131A):
        st.header('HP53131A Universal Counter')
        
        col1, col2 = st.columns(2)
        with col1:
            with st.expander('Basic Commands', expanded=True):
                if st.button('Reset Instrument'):
                    st.session_state.instrument.reset()
                    st.toast('Instrument Reset')
                if st.button('Clear Errors'):
                    st.session_state.instrument.clear()
                    st.toast('Errors Cleared')
                if st.button('Get ID'):
                    idn = st.session_state.instrument.id()
                    st.info(f'Instrument ID: {idn}')
        
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
            
            if meas_type != 'Time Interval':
                channel = st.selectbox('Channel', [1, 2], key='meas_ch')
            
            if st.button(f'Measure {meas_type}'):
                with st.spinner(f'Measuring {meas_type}...'):
                    reading = None
                    if meas_type == 'Frequency':
                        reading = st.session_state.instrument.measure_frequency(channel=channel)
                    elif meas_type == 'Period':
                        reading = st.session_state.instrument.measure_period(channel=channel)
                    elif meas_type == 'Time Interval':
                        reading = st.session_state.instrument.measure_time_interval()
                    
                    if reading is not None:
                        new_data = pd.DataFrame({'Time': [pd.to_datetime(time.time(), unit='s')], 'Measurement': [reading]})
                        st.session_state.measurement_data = pd.concat([st.session_state.measurement_data, new_data], ignore_index=True)


    # --- Data Display and Plot ---
    st.header('Live Measurements')
    if not st.session_state.measurement_data.empty:
        latest_reading = st.session_state.measurement_data['Measurement'].iloc[-1]
        st.metric('Latest Reading', f'{latest_reading:.9f}')
        
        st.line_chart(st.session_state.measurement_data.set_index('Time'))
        
        st.dataframe(st.session_state.measurement_data)
    else:
        st.write('No measurements taken yet.')
