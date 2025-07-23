from typing import Callable

import openhtf as htf
from openhtf.util import units


def phase_factory(function: Callable, comment: str = None, params: dict = None, measurement_config: dict = None) -> Callable:
    """
    Generate an OpenHTF test phase function from a step configuration and instrument.

    Args:
        step_config (dict): Dictionary specifying the test step, including function name, parameters, and optional measurement details.
        instrument (Instrument): The instrument instance to execute the step on.

    Returns:
        Callable: An OpenHTF-compatible test phase function, optionally decorated with measurement configuration.
    """
    if comment is None:
        comment = function.__name__
    if params is None:
        params = {}

    def dynamic_phase(test):
        """The actual phase logic that will be executed."""
        result = function(**params)
        print(f"PHASE '{comment}': Executed '{function.__name__}', got result: {result}")

        # If this step includes a measurement, record it.
        if measurement_config:
            measurement_name = measurement_config['name']
            test.measurements[measurement_name] = result

    # Set a descriptive name for the phase function for better logging.
    dynamic_phase.name = comment

    # If the step defines a measurement, dynamically create and attach it.
    if measurement_config:
        measurement = htf.Measurement(measurement_config['name'])

        # Dynamically set units if specified.
        if 'units' in measurement_config:
            unit_name = measurement_config['units']
            # getattr is a safe way to get the unit type from the units module.
            if hasattr(units, unit_name):
                measurement.with_units(getattr(units, unit_name))
            else:
                print(f"Warning: Unit '{unit_name}' not found.")

        # Dynamically add validators.
        if 'validators' in measurement_config:
            for validator_conf in measurement_config['validators']:
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
