from core.exceptions import ScenarioExecutionError
from devices.base import Instrument


class Step:
    """Represents a single test step."""

    def __init__(self, data: dict):
        self.data = data
        self.comment = data.get('comment')

    def __repr__(self):
        return f'Step {self.data}'
        
    def validate(self):
        """
        Validates the step data against the schema.
        
        Raises:
            ValueError: If the step data is invalid.
        """
        condition = ('command' in self.data,
                     'function' in self.data,
                     'read' in self.data)
        if sum(condition) != 1:
            raise ValueError('Step must have exactly one of command, function, or read')
        
    def execute(self, instrument: Instrument, context: dict):
        """
        Executes the step on the given instrument.
        
        Args:
            instrument: The device object (e.g., HP3458A) with callable methods.
            context (dict): Stores variables, outputs, etc. during execution.
        
        Raises:
            ScenarioExecutionError: If the step execution fails.
        """
        raise NotImplementedError('Subclasses must implement execute method')

    @staticmethod
    def from_dict(data: dict) -> 'Step':
        """Factory method to create the correct Step subclass."""
        
        if 'command' in data:
            return CommandStep.from_dict(data)
        elif 'function' in data:
            return FunctionStep.from_dict(data)
        elif 'read' in data:
            return ReadStep.from_dict(data)
        else:
            raise ValueError('Unknown step type')
        
        
class CommandStep(Step):
    def __init__(self, data):
        super().__init__(data)
        self.command = data.get('command')
        
    @staticmethod
    def from_dict(data: dict) -> 'CommandStep':
        return CommandStep(data)
    
    def execute(self, instrument: Instrument, context: dict):
        try:
            instrument.send_command(self.command)
        except Exception as e:
            raise ScenarioExecutionError(f'Command {self.command} execution failed: {e}')


class FunctionStep(Step):
    def __init__(self, data):
        super().__init__(data)
        self.function = data['function']
    
    @staticmethod    
    def from_dict(data: dict) -> 'FunctionStep':
        """Factory method to create the correct FunctionStep subclass."""
        
        function = data['function']
        if function == 'measure_voltage':
            return MeasureVoltage.from_dict(data)
        else:
            raise ValueError(f'Unknown function type: {function}')


class ReadStep(Step):
    def __init__(self, data):
        super().__init__(data)
        self.read = data['read']
        self.print = data.get('print')
        self.save_to_file = data.get('save_to_file')

    @staticmethod
    def from_dict(data: dict) -> 'ReadStep':
        return ReadStep(data)


class MeasureVoltage(FunctionStep):
    def __init__(self, data):
        super().__init__(data)
        self.reading_times = data.get('reading_times')
        self.interval = data.get('interval')

    def validate(self):
        super().validate()
        if self.reading_times < 1:
            raise ValueError('reading_times must be >= 1')
        
    @staticmethod
    def from_dict(data: dict) -> 'MeasureVoltage':
        return MeasureVoltage(data)
