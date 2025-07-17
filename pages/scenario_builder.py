import streamlit as st
import yaml


# --- Instrument Function Definitions ---
# This metadata is used to dynamically generate the UI for parameters.
INSTRUMENT_FUNCTIONS = {
    'HP3458A': {
        'conf_function_dcv': {
            'mrange': {'type': 'number', 'default': 10.0},
            'nplc': {'type': 'number', 'default': 1.0},
            'AutoZero': {'type': 'boolean', 'default': True},
            'HiZ': {'type': 'boolean', 'default': True}
        },
        'get_reading': {},
        'beep': {},
        'temperature': {},
        'get_error': {},
        'reset': {}
    },
    'HP53131A': {
        'measure_frequency': {
            'channel': {'type': 'number', 'default': 1},
        },
        'measure_period': {
            'channel': {'type': 'number', 'default': 1},
        },
        'measure_time_interval': {},
        'start_totalize': {
            'channel': {'type': 'number', 'default': 1},
        },
        'stop_and_fetch_totalize': {},
        'reset': {},
        'clear': {}
    }
}

# --- Helper Functions ---
def get_default_step(device_type):
    """Returns a dictionary representing a default step."""
    return {
        'comment': 'New Step',
        'function': list(INSTRUMENT_FUNCTIONS[device_type].keys())[0],
        'params': {},
        'add_measurement': False,
        'measurement': {
            'name': 'measurement_name',
            'units': 'VOLT',
            'validators': []
        }
    }

def get_default_validator():
    """Returns a dictionary representing a default validator."""
    return {'type': 'in_range', 'min': 0, 'max': 1}

# --- UI Rendering ---
st.set_page_config(layout='wide', page_title='Scenario Builder')
st.title('YAML Scenario Builder')

# Initialize session state for steps if it doesn't exist
if 'steps' not in st.session_state:
    st.session_state.steps = []

# --- Global Configuration ---
st.header('Global Configuration')
col1, col2, col3 = st.columns(3)
with col1:
    device_type = st.selectbox('Device', ['HP3458A', 'HP53131A'], key='device_type')
with col2:
    scenario_name = st.text_input('Scenario Name', 'hp3458_test', key='scenario_name')
with col3:
    device_address = st.number_input('Device Address', 1, 30, 2, key='device_address')

# --- Steps Configuration ---
st.header('Test Steps')

# Add a new step
if st.button('Add Step'):
    st.session_state.steps.append(get_default_step(device_type))

# Display and configure each step
for i, step in enumerate(st.session_state.steps):
    with st.expander(f"Step {i+1}: {step.get('comment', 'New Step')}", expanded=True):
        st.subheader(f'Step {i+1}')
        
        # --- Basic Step Info ---
        step['comment'] = st.text_input('Comment', step.get('comment', ''), key=f'comment_{i}')
        
        # --- Function and Parameters ---
        available_functions = list(INSTRUMENT_FUNCTIONS.get(device_type, {}).keys())
        # Ensure the currently selected function is valid for the device
        current_function_index = available_functions.index(step['function']) if step['function'] in available_functions else 0
        step['function'] = st.selectbox('Function', available_functions, index=current_function_index, key=f'function_{i}')
        
        st.write('Parameters:')
        function_params = INSTRUMENT_FUNCTIONS.get(device_type, {}).get(step['function'], {})
        step['params'] = {} # Reset params for the selected function
        for param_name, param_attrs in function_params.items():
            if param_attrs['type'] == 'number':
                step['params'][param_name] = st.number_input(param_name, value=param_attrs['default'], key=f'param_{i}_{param_name}')
            elif param_attrs['type'] == 'boolean':
                step['params'][param_name] = st.checkbox(param_name, value=param_attrs['default'], key=f'param_{i}_{param_name}')

        # --- Measurement Block ---
        step['add_measurement'] = st.checkbox('Add Measurement Block', value=step.get('add_measurement', False), key=f'add_meas_{i}')
        if step['add_measurement']:
            meas = step['measurement']
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                meas['name'] = st.text_input('Measurement Name', meas.get('name', ''), key=f'meas_name_{i}')
            with m_col2:
                meas['units'] = st.text_input('Units', meas.get('units', ''), key=f'meas_units_{i}')

            st.write('Validators:')
            if st.button('Add Validator', key=f'add_validator_{i}'):
                meas['validators'].append(get_default_validator())

            for j, validator in enumerate(meas['validators']):
                v_col1, v_col2, v_col3, v_col4 = st.columns([2,2,2,1])
                with v_col1:
                    validator['type'] = st.selectbox('Type', ['in_range', 'equals'], key=f'val_type_{i}_{j}')
                if validator['type'] == 'in_range':
                    with v_col2:
                        validator['min'] = st.number_input('Min', value=float(validator.get('min', 0)), key=f'val_min_{i}_{j}')
                    with v_col3:
                        validator['max'] = st.number_input('Max', value=float(validator.get('max', 1)), key=f'val_max_{i}_{j}')
                elif validator['type'] == 'equals':
                     with v_col2:
                        validator['value'] = st.number_input('Value', value=float(validator.get('value', 0)), key=f'val_equals_{i}_{j}')
                with v_col4:
                     if st.button('✖', key=f'remove_validator_{i}_{j}'):
                        meas['validators'].pop(j)
                        st.rerun()


        # --- Remove Step Button ---
        if st.button('Remove Step', key=f'remove_step_{i}'):
            st.session_state.steps.pop(i)
            st.rerun()
        st.markdown('---')


# --- Generate YAML ---
st.header('Generated YAML')
if st.button('Generate YAML Configuration'):
    final_config = {
        'device': device_type,
        'name': scenario_name,
        'address': device_address,
        'steps': []
    }

    for step_data in st.session_state.steps:
        step_entry = {
            'comment': step_data['comment'],
            'function': step_data['function'],
            'params': step_data['params']
        }
        if step_data['add_measurement']:
            meas_entry = {
                'name': step_data['measurement']['name'],
                'units': step_data['measurement']['units'],
                'validators': []
            }
            for val in step_data['measurement']['validators']:
                validator_entry = {'type': val['type']}
                if val['type'] == 'in_range':
                    validator_entry['min'] = val['min']
                    validator_entry['max'] = val['max']
                elif val['type'] == 'equals':
                    validator_entry['value'] = val['value']
                meas_entry['validators'].append(validator_entry)
            step_entry['measurement'] = meas_entry
        final_config['steps'].append(step_entry)

    yaml_output = yaml.dump(final_config, sort_keys=False, indent=2)
    
    st.session_state.yaml_output = yaml_output

if 'yaml_output' in st.session_state:
    st.code(st.session_state.yaml_output, language='yaml')
    st.download_button(
        label='Download YAML File',
        data=st.session_state.yaml_output,
        file_name=f'{scenario_name}.yaml',
        mime='text/yaml'
    )

