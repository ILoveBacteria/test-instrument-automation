class ProtocolAdapter:
    """
    Base class for protocol adapters.
    This class defines the interface for the protocol adapter.
    """
    
    def __init__(self, address: int):
        """
        Initialize the protocol adapter with the given address.

        Args:
            address (int): The address of the device to communicate with.
        """
        self.address = address
        
    def write(self, command: str) -> None:
        """
        Write a command to the device.
        This method should be implemented by subclasses to send a command to the device.

        Args:
            command (str): The command to send to the device.
        """
        pass

    def read(self, buffer_size: int = 1024) -> str:
        """
        Read a response from the device.
        This method should be implemented by subclasses to read a response from the device.

        Args:
            buffer_size (int, optional): The number of bytes to read from the device. Defaults to 1024.

        Returns:
            str: The response from the device.
        """
        pass

    def ask(self, command: str, buffer_size: int = 1024) -> str:
        """
        Send a command to the device and read the response.

        Args:
            command (str): The command to send to the device.
            buffer_size (int, optional): The number of bytes to read from the device. Defaults to 1024.

        Returns:
            str: The response from the device.
        """
        self.write(command)
        return self.read(buffer_size)