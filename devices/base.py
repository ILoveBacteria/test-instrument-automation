class TerminationMixin:
    def __init__(self, *args, **kwargs):
        default_values = {'read_termination': '\n', 'write_termination': '\n'}
        for key, value in default_values.items():
            if key not in kwargs:
                kwargs[key] = value
        super().__init__(*args, **kwargs)
