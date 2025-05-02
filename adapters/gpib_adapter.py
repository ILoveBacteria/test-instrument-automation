import socket


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

    def query(self, command: str, buffer_size: int = 1024) -> str:
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


class PrologixGPIBEthernet(ProtocolAdapter):
    """
    A protocol adapter for Prologix GPIB-Ethernet devices.

    This class provides an interface to communicate with instruments
    over GPIB using a Prologix GPIB-Ethernet controller.
    """

    PORT = 1234

    def __init__(self, host: str, address: int, prologix_read_timeout: float = 1.0, socket_read_timeout: float = 1.0):
        """
        Initialize the Prologix GPIB-Ethernet adapter.

        Args:
            host (str): The hostname or IP address of the Prologix GPIB-Ethernet controller.
            address (int): The GPIB address of the device to communicate with.
            prologix_read_timeout (float, optional): Timeout for Prologix read operations in seconds. Defaults to 1.0.
            socket_read_timeout (float, optional): Timeout for socket read operations in seconds. Defaults to 1.0.

        Raises:
            ValueError: If the Prologix read timeout is greater than the socket read timeout,
                        or if the Prologix read timeout is outside the range [0.001, 3] seconds.
        """
        super().__init__(address)
        self.host = host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.prologix_read_timeout = prologix_read_timeout
        self.socket_read_timeout = socket_read_timeout

        if self.prologix_read_timeout > self.socket_read_timeout:
            raise ValueError('Prologix read timeout must be less than socket read timeout')
        if self.prologix_read_timeout < 0.001 or self.prologix_read_timeout > 3:
            raise ValueError('Timeout must be >= 1ms and <= 3s')

        self.socket.settimeout(self.socket_read_timeout)

    def connect(self) -> None:
        """
        Connect to the Prologix GPIB-Ethernet controller and perform initial setup.
        """
        self.socket.connect((self.host, self.PORT))
        self._setup()
        self.select(self.address)

    def close(self) -> None:
        """
        Close the connection to the Prologix GPIB-Ethernet controller.
        """
        self.socket.close()

    def select(self, addr: int) -> None:
        """
        Select the GPIB address of the device to communicate with.

        Args:
            addr (int): The GPIB address to select.
        """
        self._send(f'++addr {int(addr)}')

    def write(self, command: str) -> None:
        """
        Write a command to the device.

        Args:
            command (str): The command to send to the device.
        """
        self._send(command)

    def read(self, buffer_size: int = 1024) -> str:
        """
        Read a response from the device.

        Args:
            buffer_size (int, optional): The number of bytes to read from the device. Defaults to 1024.

        Returns:
            str: The response from the device.
        """
        self._send('++read eoi')
        return self._recv(buffer_size).strip()

    def query(self, command: str, buffer_size: int = 1024) -> str:
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

    def _send(self, value: str) -> None:
        """
        Send a command or data to the Prologix GPIB-Ethernet controller.

        Args:
            value (str): The command or data to send.
        """
        encoded_value = f'{value}\n'.encode('ascii')
        self.socket.send(encoded_value)

    def _recv(self, byte_num: int) -> str:
        """
        Receive data from the Prologix GPIB-Ethernet controller.

        Args:
            byte_num (int): The number of bytes to read.

        Returns:
            str: The received data as a string.
        """
        value = self.socket.recv(byte_num)
        return value.decode('ascii')

    def _setup(self) -> None:
        """
        Perform initial setup for the Prologix GPIB-Ethernet controller.
        """
        self._send('++mode 1')  # Set to controller mode
        self._send('++auto 0')  # Disable auto-read
        self._send(f'++read_tmo_ms {int(self.prologix_read_timeout * 1000)}')  # Set read timeout
        self._send('++eos 0')  # Set end-of-string to none
        self._send('++eoi 1')  # Enable EOI (End-Or-Identify)