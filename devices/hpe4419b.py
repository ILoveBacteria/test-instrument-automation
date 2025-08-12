import time

from pymeasure.instruments import Instrument


class HPE4419B(Instrument):
    """
    Driver for the Agilent/HP E4419B Power Meter.
    
    This class provides methods for configuring, calibrating, and performing
    power measurements on one or two channels.
    """
    
    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, 'Hewlett-Packard HPE4419B', **kwargs)
    
    def setup(self):
        """
        Initializes the power meter to a known state for remote programming.
        This performs a reset, clears the status registers, and presets the system.
        """
        super().setup()
        self.reset()
        self.clear_status()
        self.write('SYST:PRES')
        
    def id(self) -> str:
        """Queries the instrument's identification string."""
        return self.ask('*IDN?')

    def reset(self):
        """Resets the instrument to its factory default state."""
        self.write('*RST')
        
    def clear_status(self):
        """Clears all event registers and the error queue."""
        self.write('*CLS')

    def error(self) -> str:
        """
        Queries the oldest error from the error queue.
        Returns '0,"No error"' if the queue is empty.
        
        SCPI Command: SYSTem:ERRor?
        """
        return self.ask('SYST:ERR?')

    def _wait_for_opc(self, timeout_sec: int = 30):
        """
        Waits for a pending operation to complete by polling the Service
        Request Queue (SRQ) for the Operation Complete (OPC) bit.
        
        This requires the adapter to have a `query_srq()` method.
        """
        start_time = time.time()
        # *OPC command enables the OPC bit in the Standard Event Status Register
        # to be set when all pending operations are finished.
        self.write('*OPC')
        while not self.adapter.query_srq():
            if time.time() - start_time > timeout_sec:
                raise TimeoutError("Timeout waiting for operation to complete.")
            time.sleep(0.1)
        # Clear status registers after a successful wait to prepare for the next operation
        self.clear_status()

    def _execute_and_fetch(self, channel: int) -> float:
        """
        Private helper to initiate, wait for, and fetch a single measurement result
        after the instrument has been configured.
        """
        # Enable the Operation Complete bit (bit 0, weight 1)
        self.write('*ESE 1')
        # Enable the Standard Event summary bit (bit 5, weight 32) to generate an SRQ
        self.write('*SRE 32')
        # Initiate the measurement on the specified channel
        self.initiate_measurement(channel)
        # Wait for the measurement to finish using SRQ
        self._wait_for_opc()
        # Fetch the result from the appropriate window (assuming 1-to-1 mapping)
        response = self.fetch_measurement(window=channel)
        return float(response)

    # --- Configuration Functions ---

    def configure_window(self, window: int, channel: int):
        """
        Assigns a sensor channel to a display window.
        """
        if window not in [1, 2]:
            raise ValueError("Window must be 1 or 2.")
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self.write(f'CALC{window}:MATH "(SENS{channel})"')

    def set_continuous_measurement(self, channel: int, enabled: bool):
        """
        Enables or disables continuous triggering for a channel.
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self.write(f'INIT{channel}:CONT {int(enabled)}')

    def set_measurement_units(self, window: int, unit: str):
        """
        Sets the measurement units for a display window.
        """
        if window not in [1, 2]:
            raise ValueError("Window must be 1 or 2.")
        unit_upper = unit.upper()
        if unit_upper not in ['W', 'DBM']:
            raise ValueError("Unit must be 'W' or 'DBM'.")
        self.write(f'UNIT{window}:POW {unit_upper}')

    # --- Calibration Functions ---

    def zero_channel(self, channel: int, wait_for_completion: bool = True):
        """
        Performs a zeroing operation on the specified channel.
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self.write(f'CAL{channel}:ZERO:AUTO ONCE')
        if wait_for_completion:
            # Setup status registers to wait for the operation to complete
            self.write('*ESE 1') # Enable Operation Complete bit
            self.write('*SRE 32') # Enable SRQ from Event Status bit
            self._wait_for_opc()

    def calibrate_channel(self, channel: int, wait_for_completion: bool = True):
        """
        Performs a calibration on the specified channel using the 1mW reference.
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self.write(f'CAL{channel}:AUTO ONCE')
        if wait_for_completion:
            self.write('*ESE 1')
            self.write('*SRE 32')
            self._wait_for_opc()

    def full_calibration_channel(self, channel: int) -> bool:
        """
        Performs a full zero and calibration sequence on the specified channel.
        This is a blocking query and waits for completion internally.
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        response = self.ask(f'CAL{channel}:ALL?')
        return int(response.strip()) == 0

    # --- Measurement and Data Fetching ---

    def initiate_measurement(self, channel: int):
        """
        Arms the trigger system for the specified channel, preparing it for a measurement.
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self.write(f'INIT{channel}:IMM')

    def fetch_measurement(self, window: int) -> float:
        """
        Fetches the result of the last completed measurement for a given window.
        """
        if window not in [1, 2]:
            raise ValueError("Window must be 1 or 2.")
        response = self.ask(f'FETC{window}?')
        return float(response)

    def get_measurement(self, window: int) -> float:
        """
        A convenient high-level function to configure, trigger, and read a single power measurement.
        
        Args:
            window (int): The window to measure (1 or 2). Assumes the window is
                          already configured to the desired channel.

        Returns:
            float: The measured power value.
        """
        if window not in [1, 2]:
            raise ValueError("Window must be 1 or 2.")
        # The channel is inferred from the window number for this high-level function
        return self._execute_and_fetch(channel=window)