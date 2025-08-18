import logging
from pymeasure.instruments import Instrument, Channel, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pyvisa.constants import Parity, StopBits

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AFG2225Channel(Channel):
    """
    Represents a single channel of the GW Instek AFG-2225 Function Generator.
    """

    # Mappings for shape and load properties
    SHAPES = {
        'sine': 'SIN', 'square': 'SQU', 'ramp': 'RAMP',
        'pulse': 'PULS', 'noise': 'NOIS', 'user': 'USER'
    }
    LOADS = {'50ohm': 'DEF', 'highZ': 'INF'}

    shape = Instrument.control(
        "SOURce{ch}:FUNCtion?", "SOURce{ch}:FUNCtion %s",
        """Controls the waveform shape (function) of the channel.""",
        validator=strict_discrete_set,
        values=SHAPES,
        map_values=True
    )

    frequency = Instrument.control(
        "SOURce{ch}:FREQuency?", "SOURce{ch}:FREQuency %e",
        """Controls the frequency of the waveform in Hz.""",
        validator=strict_range,
        values=[1e-6, 25e6]
    )

    amplitude = Instrument.control(
        "SOURce{ch}:AMPlitude?", "SOURce{ch}:AMPlitude %f",
        """Controls the peak-to-peak amplitude in Volts (Vpp).""",
        validator=strict_range,
        values=[0.001, 10.0]
    )

    offset = Instrument.control(
        "SOURce{ch}:DCOffset?", "SOURce{ch}:DCOffset %f",
        """Controls the DC offset in Volts."""
    )

    phase = Instrument.control(
        "SOURce{ch}:PHASe?", "SOURce{ch}:PHASe %f",
        """Controls the phase shift in degrees.""",
        validator=strict_range,
        values=[-360, 360]
    )

    output_enabled = Instrument.control(
        "OUTPut{ch}?", "OUTPut{ch} %s",
        """Controls whether the channel output is ON (True) or OFF (False).""",
        validator=strict_discrete_set,
        values=[True, False],
        get_process=lambda v: True if int(v) == 1 else False,
        set_process=lambda v: 'ON' if bool(v) else 'OFF'
    )

    load = Instrument.control(
        "OUTPut{ch}:LOAD?", "OUTPut{ch}:LOAD %s",
        """Controls the output load impedance ('50ohm' or 'highZ').""",
        validator=strict_discrete_set,
        values=LOADS,
        map_values=True
    )

    duty_cycle = Instrument.control(
        "SOURce{ch}:SQUare:DCYCle?", "SOURce{ch}:SQUare:DCYCle %f",
        """Controls the duty cycle for Square waveforms in percent (1 to 99).""",
        validator=strict_range,
        values=[1.0, 99.0]
    )

    ramp_symmetry = Instrument.control(
        "SOURce{ch}:RAMP:SYMMetry?", "SOURce{ch}:RAMP:SYMMetry %f",
        """Controls the symmetry for Ramp waveforms in percent (0 to 100).""",
        validator=strict_range,
        values=[0, 100]
    )


class AFG2225(SCPIMixin, Instrument):
    """
    Represents the GW Instek AFG-2225 Arbitrary Function Generator
    and provides a high-level interface for interacting with the instrument.
    """

    ch1 = Instrument.ChannelCreator(AFG2225Channel, 1)
    ch2 = Instrument.ChannelCreator(AFG2225Channel, 2)

    def __init__(self, adapter, name="GW Instek AFG-2225", **kwargs):
        """
        Initializes the function generator.
        :param adapter: VISA resource string for the instrument.
        :param kwargs: Keyword arguments for the Instrument base class.
        """
        super().__init__(
            adapter,
            name,
            read_termination='\n',
            write_termination='\n',
            **kwargs
        )
        
    def setup(self):
        self.reset()

    def reset(self):
        """Resets the instrument to its factory default state."""
        self.write("*RST")

    def sync_phase(self):
        """
        Synchronizes the phase of both channels, resetting their phase
        difference to zero.
        """
        self.write("SOURce1:PHASe:SYNChronize")
        log.info("Phase of Channel 1 and 2 synchronized.")

    def remote_mode(self):
        """Sets the instrument to remote mode, locking the front panel."""
        self.write("SYSTem:REMote")

    def local_mode(self):
        """Returns the instrument to local mode, unlocking the front panel."""
        self.write("SYSTem:LOCal")

    error = Instrument.measurement(
        "SYSTem:ERRor?",
        """Reads the next error message from the instrument's error queue."""
    )
