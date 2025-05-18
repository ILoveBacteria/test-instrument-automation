import time

from schema.scenario import Scenario
from devices.base import Instrument
from core.exceptions import ScenarioExecutionError


class ScenarioExecutor:
    """
    Executes a parsed and validated scenario on a target instrument.

    Attributes:
        scenario (Scenario): The test scenario to execute.
        instrument: The device object (e.g., HP3458A) with callable methods.
    """

    def __init__(self, scenario: Scenario, instrument: Instrument):
        self.scenario = scenario
        self.instrument = instrument
        
    def execute(self):
        """
        Executes the scenario step by step.

        Raises:
            ScenarioExecutionError: If the scenario execution fails.
        """
        for step in self.scenario.steps:
            try:
                # Log the step execution
                print(f'Executing step: {step}')
                step.execute(self.instrument)
            except Exception as e:
                raise ScenarioExecutionError(f'Failed to execute step: {step}') from e  
