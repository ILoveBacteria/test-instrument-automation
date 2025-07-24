import pyvisa
from typing import Optional

from adapters.base import ProtocolAdapter


class PyVisaAdapter(ProtocolAdapter):
    """
    A protocol adapter that uses the PyVISA library to provide
    an abstraction layer over different communication interfaces.
    """
    
    _rm: Optional[pyvisa.ResourceManager] = None
    
    def __init__(self, visa_resource_string: str, read_timeout: int = 10000, **kwargs):
        """
        Initialize the PyVISA adapter.

        Args:
            visa_resource_string (str): The VISA resource string (e.g., 'GPIB0::15::INSTR').
            read_timeout (int): Read timeout in milliseconds.
        """
        # The resource string contains all address-like info.
        super().__init__(address=visa_resource_string)
        
        # Use a shared ResourceManager for efficiency
        if PyVisaAdapter._rm is None:
            PyVisaAdapter._rm = pyvisa.ResourceManager()
            
        self.instrument = self._rm.open_resource(self.address, **kwargs)
        self.instrument.timeout = read_timeout

    def write(self, command: str) -> None:
        """
        Write a command to the device.
        """
        self.instrument.write(command)

    def read(self, buffer_size: int = 1024) -> str:
        """
        Read a response from the device.
        Note: buffer_size is often not needed for read() in PyVISA.
        """
        return self.instrument.read()

    def ask(self, command: str) -> str:
        """
        Send a command and read the response.
        """
        return self.instrument.ask(command)
        
    def close(self):
        """
        Close the connection to the instrument.
        """
        self.instrument.close()
