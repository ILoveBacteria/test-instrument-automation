from schema.step import Step


class Scenario:
    """Structured representation of a test scenario."""

    def __init__(self, data: dict):
        self.device = data['device']
        self.name = data['name']
        self.address = data['address']
        self.steps = [Step.from_dict(step) for step in data['steps']]

    def __repr__(self):
        return f'Scenario {self.name} with {len(self.steps)} steps'
    
    def validate(self):
        """
        Validate the scenario steps.
        
        Raises:
            ValueError: If any step is invalid.
        """
        for step in self.steps:
            step.validate()