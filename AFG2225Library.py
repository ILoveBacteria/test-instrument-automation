import logging

from devices import AFG2225
from robot_library import BaseLibrary, publish_result, measure


logger = logging.getLogger(__name__)


class AFG2225Library(BaseLibrary):
    """
    Robot Framework Library for controlling GW Instek AFG-2225 Function Generator.
    Provides high-level keywords to configure channels, frequency, amplitude, etc.
    """
    NAME = 'Function Generator'
    
    def __init__(self):
        super().__init__()
        self.device = None

    # ------------------ CONNECTION ------------------
    def open_connection(self, resource, **kwargs):
        """
        Opens connection to the AFG2225.
        Example:
        | Open Connection | ASRL5::INSTR |
        """
        self.device = AFG2225(resource, **kwargs)
        logger.info(f"Connected to AFG2225 at {resource}")
        self.device.setup()

    def close_connection(self):
        """
        Closes the instrument connection.
        """
        if self.device:
            self.device.adapter.connection.close()
            self.device = None
            logger.info("Connection closed from AFG2225.")

    # ------------------ CHANNEL CONTROL ------------------
    def set_channel_shape(self, channel, shape):
        """Sets waveform shape: sine, square, ramp, pulse, noise, user."""
        getattr(self.device, f"ch{channel}").shape = shape

    def get_channel_shape(self, channel):
        """Returns current waveform shape of a channel."""
        return getattr(self.device, f"ch{channel}").shape

    def set_channel_frequency(self, channel, freq):
        """Sets channel frequency in Hz."""
        getattr(self.device, f"ch{channel}").frequency = float(freq)

    @publish_result
    @measure('frequency', 'Hz')
    def get_channel_frequency(self, channel):
        """Returns channel frequency in Hz."""
        return getattr(self.device, f"ch{channel}").frequency

    def set_channel_amplitude(self, channel, amplitude):
        """Sets channel amplitude in Vpp."""
        getattr(self.device, f"ch{channel}").amplitude = float(amplitude)

    def get_channel_amplitude(self, channel):
        """Returns channel amplitude in Vpp."""
        return getattr(self.device, f"ch{channel}").amplitude

    def set_channel_offset(self, channel, offset):
        """Sets DC offset in volts."""
        getattr(self.device, f"ch{channel}").offset = float(offset)

    def get_channel_offset(self, channel):
        """Returns DC offset in volts."""
        return getattr(self.device, f"ch{channel}").offset

    def set_channel_phase(self, channel, phase):
        """Sets phase in degrees."""
        getattr(self.device, f"ch{channel}").phase = float(phase)

    def get_channel_phase(self, channel):
        """Returns channel phase in degrees."""
        return getattr(self.device, f"ch{channel}").phase

    def enable_channel_output(self, channel):
        """Turns ON channel output."""
        getattr(self.device, f"ch{channel}").output_enabled = True

    def disable_channel_output(self, channel):
        """Turns OFF channel output."""
        getattr(self.device, f"ch{channel}").output_enabled = False

    def is_channel_output_enabled(self, channel):
        """Checks if channel output is ON."""
        return getattr(self.device, f"ch{channel}").output_enabled

    def set_channel_load(self, channel, load):
        """Sets output load: '50ohm' or 'highZ'."""
        getattr(self.device, f"ch{channel}").load = load

    def get_channel_load(self, channel):
        """Returns channel load."""
        return getattr(self.device, f"ch{channel}").load

    def set_channel_duty_cycle(self, channel, duty):
        """Sets duty cycle (%) for square wave."""
        getattr(self.device, f"ch{channel}").duty_cycle = float(duty)

    def get_channel_duty_cycle(self, channel):
        """Returns duty cycle (%) for square wave."""
        return getattr(self.device, f"ch{channel}").duty_cycle

    def set_channel_ramp_symmetry(self, channel, symmetry):
        """Sets ramp symmetry (%) for ramp waveforms."""
        getattr(self.device, f"ch{channel}").ramp_symmetry = float(symmetry)

    def get_channel_ramp_symmetry(self, channel):
        """Returns ramp symmetry (%) for ramp waveforms."""
        return getattr(self.device, f"ch{channel}").ramp_symmetry

    # ------------------ INSTRUMENT LEVEL ------------------
    def reset_instrument(self):
        """Resets AFG2225 to defaults."""
        self.device.reset()

    def sync_phase(self):
        """Synchronizes phase between CH1 and CH2."""
        self.device.sync_phase()

    def set_remote_mode(self):
        """Locks front panel (remote mode)."""
        self.device.remote_mode()

    def set_local_mode(self):
        """Unlocks front panel (local mode)."""
        self.device.local_mode()

    def get_error(self):
        """Returns next error message from the instrument."""
        return self.device.error
