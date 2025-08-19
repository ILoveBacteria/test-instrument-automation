import logging

from devices import HP3458A


logger = logging.getLogger(__name__)


class HP3458ALibrary:
    """
    Robot Framework library wrapper for controlling the HP 3458A Multimeter.
    Provides keywords for configuration, measurement, and device utilities.
    """
    def __init__(self):
        self.device = None

    # ------------------ CONNECTION ------------------
    def open_connection(self, resource, **kwargs):
        """
        Opens connection to the HP3458A.
        Example:
        | Open Connection | GPIB0::2::INSTR |
        """
        self.device = HP3458A(resource, **kwargs)
        logger.info(f"Connected to HP3458A at {resource}")
        self.device.setup()

    def close_connection(self):
        """
        Closes the instrument connection.
        """
        if self.device:
            self.device.adapter.connection.close()
            self.device = None
            logger.info("Connection closed from HP3458A.")

    # --- Identification & System Status ---

    def get_id(self) -> str:
        """Returns the device identification string."""
        return self.device.id

    def get_temperature(self) -> float:
        """Returns the internal device temperature (°C)."""
        return self.device.temperature

    def reset_device(self):
        """Resets the device to default state."""
        self.device.reset()

    def setup_device(self):
        """Performs basic setup (END ALWAYS, TRIG HOLD)."""
        self.device.setup()

    def beep(self):
        """Beeps the device."""
        self.device.beep()

    def get_error(self) -> str:
        """Reads the last error string from the device."""
        return self.device.error()

    def display_message(self, message: str):
        """Displays a message on the device screen (≤75 chars)."""
        self.device.display(message)

    # --- Basic Reading ---

    def get_reading(self, trig: bool = True):
        """
        Triggers a single reading and returns the value.
        Returns a list if multiple readings are returned.
        """
        return self.device.get_reading(trig)

    # --- Configuration Controls ---

    def set_auto_zero(self, state: str):
        """Sets Auto Zero ON or OFF."""
        self.device.auto_zero = state.upper()

    def set_high_impedance(self, state: str):
        """Sets High Impedance ON or OFF (DC Voltage only)."""
        self.device.high_impedance = state.upper()

    def set_offset_compensation(self, state: str):
        """Sets Offset Compensation ON or OFF (Resistance only)."""
        self.device.offset_compensation = state.upper()

    def set_low_pass_filter(self, state: str):
        """Sets Low Pass Filter ON or OFF."""
        self.device.low_pass_filter = state.upper()

    def set_trigger_source(self, source: str):
        """Sets Trigger Source (SGL, EXT, HOLD)."""
        self.device.trigger_source = source.upper()

    def set_arm_source(self, source: str):
        """Sets Arm Source (AUTO, SGL, EXT, HOLD)."""
        self.device.arm_source = source.upper()

    def set_burst_interval(self, interval: float):
        """Sets burst interval between readings (seconds)."""
        self.device.burst_interval = interval

    def set_measurement_range(self, value: str):
        """Sets measurement range (float or 'AUTO')."""
        self.device.measurement_range = value

    def set_nplc(self, nplc: float):
        """Sets integration time in power line cycles (NPLC)."""
        self.device.nplc = nplc

    # --- Measurement Configurations ---

    def configure_dcv(self, mrange=None, nplc=1, autozero=True, hiz=False):
        """Configures the device for DC Voltage measurement."""
        self.device.conf_function_DCV(mrange, nplc, autozero, hiz)

    def configure_dci(self, mrange=None, nplc=1, autozero=True, hiz=False):
        """Configures the device for DC Current measurement."""
        self.device.conf_function_DCI(mrange, nplc, autozero, hiz)

    def configure_acv(self, mrange=None, nplc=1):
        """Configures the device for AC Voltage measurement."""
        self.device.conf_function_ACV(mrange, nplc)

    def configure_aci(self, mrange=None, nplc=1):
        """Configures the device for AC Current measurement."""
        self.device.conf_function_ACI(mrange, nplc)

    def configure_ohm2w(self, mrange=None, nplc=1, autozero=True, offset_comp=False):
        """Configures the device for 2-Wire Resistance measurement."""
        self.device.conf_function_OHM2W(mrange, nplc, autozero, offset_comp)

    def configure_ohm4w(self, mrange=None, nplc=1, autozero=True, offset_comp=False):
        """Configures the device for 4-Wire Resistance measurement."""
        self.device.conf_function_OHM4W(mrange, nplc, autozero, offset_comp)

    def configure_frequency(self, mrange="AUTO", gate_time=1.0):
        """Configures the device for Frequency measurement."""
        self.device.conf_function_FREQ(mrange, gate_time)

    def configure_acdcv(self, mrange=None, nplc=1, ac_bandwidth_low=20, hiz=False):
        """Configures the device for combined AC+DC Voltage measurement."""
        self.device.conf_function_ACDCV(mrange, nplc, ac_bandwidth_low, hiz)

    def configure_digitize(self, mode="DSDC", mrange=10, delay=0,
                           num_samples=1024, sample_interval=100e-9):
        """Configures the device for high-speed digitizing mode."""
        self.device.conf_function_digitize(mode, mrange, delay, num_samples, sample_interval)
