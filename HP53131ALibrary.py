import logging

from devices import HP53131A
from robot_library import BaseLibrary, publish_result, measure


logger = logging.getLogger(__name__)


class HP53131ALibrary(BaseLibrary):
    """
    Robot Framework library wrapper for controlling the HP 53131A Universal Counter.
    Provides high-level keywords that map to the HP53131A class methods.
    """
    NAME = 'Counter'
    
    def __init__(self):
        super().__init__()
        self.device = None

    # ------------------ CONNECTION ------------------
    def open_connection(self, resource, **kwargs):
        """
        Opens connection to the HP53131A.
        Example:
        | Open Connection | GPIB0::3::INSTR |
        """
        self.device = HP53131A(resource, **kwargs)
        logger.info(f"Connected to HP53131A at {resource}")
        self.device.setup()

    def close_connection(self):
        """
        Closes the instrument connection.
        """
        if self.device:
            self.device.adapter.connection.close()
            self.device = None
            logger.info("Connection closed from HP53131A.")

    # --- Identification and Status ---

    def get_id(self) -> str:
        """Returns the device identification string."""
        return self.device.id()

    def reset_device(self):
        """Resets the device to factory defaults."""
        self.device.reset()

    def clear_status(self):
        """Clears status and error registers."""
        self.device.clear()

    def get_error(self) -> str:
        """Queries the last error from the device."""
        return self.device.error()

    # --- Configuration ---

    def configure_channel(self, channel: int, coupling: str = 'AC',
                          slope: str = 'POS', attenuation: int = 1,
                          trigger_level: float = 0):
        """
        Configures input channel settings.

        Args:
            channel: 1 or 2
            coupling: 'AC' or 'DC'
            slope: 'POS' or 'NEG'
            attenuation: 1 or 10
            trigger_level: float in Volts
        """
        self.device.measurement_configuration(channel, coupling, slope,
                                                  attenuation, trigger_level)

    def set_trigger_level(self, channel: int, level: float):
        """Sets the trigger level (Volts) for the given channel."""
        self.device._set_trigger_level_volts(channel, level)

    def get_trigger_level(self, channel: int) -> float:
        """Returns the trigger level (Volts) for the given channel."""
        return self.device.get_trigger_level_volts(channel)

    # --- Measurements ---

    @measure('frequency', 'Hz')
    def measure_frequency(self, channel: int, expected_value: str = 'DEF', resolution: str = 'DEF'):
        """Configures frequency measurement on a channel."""
        self.device.measure_frequency(channel, expected_value, resolution)

    @measure('frequency', 'Hz')
    def measure_frequency_gated(self, gate_time: float, channel: int = 1):
        """Configures gated frequency measurement."""
        self.device.measure_frequency_gated(channel, gate_time)

    @measure('period', 's')
    def measure_period(self, channel: int, expected_value: str = 'DEF', resolution: str = 'DEF'):
        """Configures period measurement on a channel."""
        self.device.measure_period(channel, expected_value, resolution)

    @measure('interval', 's')
    def measure_time_interval(self):
        """Configures time interval measurement (Ch1 start, Ch2 stop)."""
        self.device.measure_time_interval()

    # --- Initiate / Fetch ---

    def initiate_measurement(self):
        """Initiates measurement on the device."""
        self.device.initiate()

    def fetch_result(self) -> float:
        """Fetches the last measurement result."""
        return self.device.fetch()

    def wait_and_fetch_result(self, timeout: int = 10) -> float:
        """Waits for measurement completion and fetches the result."""
        return self.device.wait_and_fetch(timeout)

    @publish_result
    def initiate_wait_and_fetch(self, timeout: int = 10) -> float:
        """Initiates measurement, waits, and fetches the result."""
        return self.device.initiate_wait_fetch(timeout)

    def fetch_average_result(self) -> float:
        """Fetches an averaged measurement result."""
        return self.device.fetch_average()

    # --- Totalizer ---

    def measure_totalize(self):
        """Configures continuous totalizer measurement."""
        self.device.measure_totalize()

    def measure_totalize_timed(self, gate_time: float):
        """Configures timed totalizer measurement."""
        self.device.measure_totalize_timed(gate_time)

    def stop_measurement(self):
        """Stops current measurement / totalizer."""
        self.device.stop()
