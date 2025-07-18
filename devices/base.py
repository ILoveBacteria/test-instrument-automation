from adapters.gpib_adapter import ProtocolAdapter


class Instrument:
    """
    Base class for all instruments.
    """

    def __init__(self, name: str, adapter: ProtocolAdapter):
        self.name = name
        self.adapter = adapter

    def send_command(self, command: str):
        """
        Send a command to the instrument.
        """
        self.adapter.write(command)

    def read_response(self, buffer_size: int = 1024) -> str:
        """
        Read a response from the instrument.
        """
        return self.adapter.read(buffer_size)
    
    def query(self, command: str) -> str:
        """
        Send a command and read the response.
        """
        self.send_command(command)
        return self.read_response()
    
    def setup(self):
        """
        Setup the instrument.
        """
        pass
    
    def error(self) -> str:
        """
        Get the error message from the instrument.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")