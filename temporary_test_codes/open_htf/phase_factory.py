from typing import Callable

import openhtf as htf
from openhtf.util import units

from devices import Instrument


def phase_factory(step_config: dict, instrument: Instrument) -> Callable:
    """
    Generate an OpenHTF test phase function from a step configuration and instrument.

    Args:
        step_config (dict): Dictionary specifying the test step, including function name, parameters, and optional measurement details.
        instrument (Instrument): The instrument instance to execute the step on.

    Returns:
        Callable: An OpenHTF-compatible test phase function, optionally decorated with measurement configuration.
    """
    def dynamic_phase(test):
        """The actual phase logic that will be executed."""
        # Get the instrument function name and parameters from the config.
        func_name = step_config['function']
        params = step_config.get('params', {})

        # Get the corresponding method from our instrument plug.
        instrument_method = getattr(instrument, func_name)

        # Execute the instrument method.
        result = instrument_method(**params)
        print(f"PHASE '{step_config['comment']}': Executed '{func_name}', got result: {result}")

        # If this step includes a measurement, record it.
        if 'measurement' in step_config:
            measurement_name = step_config['measurement']['name']
            test.measurements[measurement_name] = result

    # Set a descriptive name for the phase function for better logging.
    dynamic_phase.name = step_config.get('comment', step_config['function'])

    # If the step defines a measurement, dynamically create and attach it.
    if 'measurement' in step_config:
        meas_config = step_config['measurement']
        measurement = htf.Measurement(meas_config['name'])

        # Dynamically set units if specified.
        if 'units' in meas_config:
            unit_name = meas_config['units']
            # getattr is a safe way to get the unit type from the units module.
            if hasattr(units, unit_name):
                measurement.with_units(getattr(units, unit_name))
            else:
                print(f"Warning: Unit '{unit_name}' not found.")

        # Dynamically add validators.
        if 'validators' in meas_config:
            for validator_conf in meas_config['validators']:
                if validator_conf['type'] == 'in_range':
                    measurement.in_range(
                        minimum=validator_conf.get('min'),
                        maximum=validator_conf.get('max')
                    )
                elif validator_conf['type'] == 'equals':
                    measurement.equals(validator_conf['value'])
                # Add more 'elif' blocks for other validators you need.

        # Apply the fully configured measurement to our phase function.
        return htf.measures(measurement)(dynamic_phase)

    # If no measurement, return the phase as is.
    return dynamic_phase
