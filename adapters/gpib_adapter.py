import socket
from typing import Literal


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
        self.connect()

    def connect(self) -> None:
        """
        Connect to the Prologix GPIB-Ethernet controller and perform initial setup.
        """
        self.socket.connect((self.host, self.PORT))
        self._setup()
        self.set_address(self.address)

    def close(self) -> None:
        """
        Close the connection to the Prologix GPIB-Ethernet controller.
        """
        self.socket.close()

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
        return self._recv(buffer_size)

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

    def _recv(self, byte_num: int = 1024) -> str:
        """
        Receive data from the Prologix GPIB-Ethernet controller.

        Args:
            byte_num (int, optional): The number of bytes to read.

        Returns:
            str: The received data as a string.
        """
        value = self.socket.recv(byte_num)
        return value.decode('ascii').strip()

    def _setup(self) -> None:
        """
        Perform initial setup for the Prologix GPIB-Ethernet controller.
        """
        self.set_mode('controller')
        self.set_auto_read(False)
        self.set_read_timeout(self.prologix_read_timeout)
        self.set_eos('crlf')
        self.set_eoi(True)
        
    def set_address(self, primary: int, secondary: int = None) -> None:
        """
        Set the primary (and optionally secondary) GPIB address.
        
        Args:
            primary (int): The primary GPIB address (0-30).
            secondary (int, optional): The secondary GPIB address (0-15). Defaults to None.
        """
        if secondary is not None:
            self._send(f'++addr {primary} {secondary + 96}')
        else:
            self._send(f'++addr {primary}')

    def get_address(self) -> str:
        """
        Get the currently selected GPIB address.
        
        Returns:
            str: The currently selected GPIB address.
        """
        self._send('++addr')
        return self._recv(64)

    def set_mode(self, mode: Literal['controller', 'device']) -> None:
        """
        Set Prologix mode to 'controller' or 'device'.
        
        Args:
            mode (str): The mode to set ('controller' or 'device').
        """
        mode_map = {'controller': 1, 'device': 0}
        if mode not in mode_map:
            raise ValueError('mode must be controller or device')
        self._send(f'++mode {mode_map[mode]}')

    def get_mode(self) -> Literal['controller', 'device']:
        """
        Get the current Prologix mode (controller/device).
        
        Returns:
            str: The current mode ('controller' or 'device').
        """
        self._send('++mode')
        mode_map = {0: 'device', 1: 'controller'}
        return mode_map[int(self._recv(64))]

    def set_auto_read(self, enabled: bool) -> None:
        """
        Enable or disable auto-read mode (++auto).
        
        Args:
            enabled (bool): True to enable auto-read, False to disable.
        """
        self._send(f'++auto {1 if enabled else 0}')

    def is_auto_read(self) -> bool:
        """
        Get the current auto-read setting.
        
        Returns:
            bool: True if auto-read is enabled, False otherwise.
        """
        self._send('++auto')
        return self._recv(8) == '1'

    def set_read_timeout(self, seconds: float) -> None:
        """
        Set read timeout in seconds (converted to ms).
        
        Args:
            seconds (float): The read timeout in seconds.
        """
        timeout_ms = int(seconds * 1000)
        self._send(f'++read_tmo_ms {timeout_ms}')

    def get_read_timeout(self) -> str:
        """
        Get the current Prologix read timeout (in ms).
        
        Returns:
            str: The current read timeout in milliseconds.
        """
        self._send('++read_tmo_ms')
        return self._recv(64)

    def set_eoi(self, enabled: bool) -> None:
        """
        Enable or disable EOI (End Or Identify).
        
        Args:
            enabled (bool): True to enable EOI, False to disable.
        """
        self._send(f'++eoi {1 if enabled else 0}')

    def get_eoi(self) -> bool:
        """
        Get the current EOI setting.
        
        Returns:
            bool: True if EOI is enabled, False otherwise.
        """
        self._send('++eoi')
        return self._recv(8) == '1'

    def set_eos(self, mode: Literal['crlf', 'cr', 'lf', 'none']) -> None:
        """
        Set the EOS (End Of String) mode.
        
        Args:
            mode (str): The EOS mode to set ('crlf', 'cr', 'lf', 'none').

        Raises:
            ValueError: If the mode is not one of the valid options.
        """
        eos_modes = {'crlf': 0, 'cr': 1, 'lf': 2, 'none': 3}
        if mode not in eos_modes:
            raise ValueError('Invalid EOS mode. Choose from: crlf, cr, lf, none.')
        self._send(f'++eos {eos_modes[mode]}')

    def get_eos(self) -> Literal['crlf', 'cr', 'lf', 'none']:
        """
        Get the current EOS setting.
        
        Returns:
            str: The current EOS mode ('crlf', 'cr', 'lf', 'none').
        """
        self._send('++eos')
        eos_map = {0: 'crlf', 1: 'cr', 2: 'lf', 3: 'none'}
        return eos_map[int(self._recv(64))]
    
    def set_eot(self, enabled: bool) -> None:
        """
        Enable or disable EOT (End Of Transmission) after read.
        
        Args:
            enabled (bool): True to enable EOT, False to disable.
        """
        self._send(f'++eot_enable {1 if enabled else 0}')

    def set_eot_char(self, ascii_code: int) -> None:
        """
        Set the EOT character (ASCII code).
        
        Args:
            ascii_code (int): The ASCII code for the EOT character (0-255).
        """
        self._send(f'++eot_char {ascii_code}')

    def send_ifc(self) -> None:
        """Send Interface Clear (IFC) signal on the GPIB bus."""
        self._send('++ifc')

    def device_clear(self) -> None:
        """Send device clear (DCL) to the currently addressed GPIB device."""
        self._send('++clr')

    def disable_local(self) -> None:
        """Disable local keyboard on the instrument (++llo)."""
        self._send('++llo')

    def enable_local(self) -> None:
        """Enable local keyboard and front panel (++loc)."""
        self._send('++loc')

    def listen_only_mode(self, enabled: bool) -> None:
        """
        Enable or disable listen-only mode (++lon).
        
        Args:
            enabled (bool): True to enable listen-only mode, False to disable.
        """
        self._send(f'++lon {1 if enabled else 0}')

    def reset_controller(self) -> None:
        """Reset the Prologix controller (++rst)."""
        self._send('++rst')

    def get_version(self) -> str:
        """
        Get firmware version of the Prologix adapter (++ver).
        
        Returns:
            str: The firmware version of the Prologix adapter.
        """
        self._send('++ver')
        return self._recv(64)

    def get_help(self) -> str:
        """
        Get help text showing supported commands (++help).
        
        Returns:
            str: The help text showing supported commands.
        """
        self._send('++help')
        return self._recv(256)

    def query_srq(self) -> bool:
        """
        Check if SRQ (Service Request) is active (++srq).
        
        Returns:
            bool: True if SRQ is active, False otherwise.
        """
        self._send('++srq')
        return self._recv(8) == '1'

    def serial_poll(self, pad: int = None, sad: int = None) -> str:
        """
        Perform serial poll on the device. Optionally provide PAD and SAD.
        
        Args:
            pad (int, optional): The primary address of the device to poll.
            sad (int, optional): The secondary address of the device to poll.
        """
        if pad is not None:
            cmd = f'++spoll {pad}' + (f' {sad + 96}' if sad is not None else '')
        else:
            cmd = '++spoll'
        self._send(cmd)
        return self._recv(64)

    def set_status_byte(self, value: int) -> None:
        """Set the adapter's internal status byte (++status)."""
        self._send(f'++status {value}')

    def get_status_byte(self) -> str:
        """Read the current status byte (++status)."""
        self._send('++status')
        return self._recv(64)

    def trigger(self, *addresses: int) -> None:
        """Send GPIB trigger to one or more devices (++trg)."""
        if addresses:
            self._send('++trg ' + ' '.join(map(str, addresses)))
        else:
            self._send('++trg')

    def read_until(self, mode: str = 'eoi', char_code: int = None) -> str:
        """
        Read from device until EOI or specific byte.
        - mode: 'eoi' (default) or 'char'
        - char_code: ASCII byte to end reading on (if mode='char')
        """
        if mode == 'eoi':
            self._send('++read eoi')
        elif char_code is not None:
            self._send(f'++read {char_code}')
        else:
            self._send('++read')
        return self._recv(1024)
