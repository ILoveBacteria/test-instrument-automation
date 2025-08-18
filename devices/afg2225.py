# This script provides a Pymeasure instrument class for the
# GW Instek AFG-2225 Arbitrary Function Generator.

import logging
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AFG2225Channel:
    """
    Represents a single channel of the GW Instek AFG-2225 Function Generator.
    """

    # Waveform shape mappings from user-friendly names to SCPI commands
    SHAPES = {
        'sine': 'SIN', 'square': 'SQU', 'ramp': 'RAMP',
        'pulse': 'PULS', 'noise': 'NOIS', 'user': 'USER'
    }

    # Output load impedance mappings
    LOADS = {'50ohm': 'DEF', 'highZ': 'INF'}

    def __init__(self, instrument, channel_id):
        """
        Initializes the channel.
        :param instrument: The parent AFG2225 instrument instance.
        :param channel_id: The channel number (1 or 2).
        """
        self.instrument = instrument
        self.channel_id = channel_id

    def write(self, command):
        """Writes a command to the instrument for this specific channel."""
        self.instrument.write(command)

    def ask(self, command):
        """Asks a query from the instrument for this specific channel."""
        return self.instrument.ask(command)

    @property
    def shape(self):
        """
        Controls the waveform shape (function) of the channel.
        Values: 'sine', 'square', 'ramp', 'pulse', 'noise', 'user'.
        """
        # The instrument returns the short form (e.g., 'SIN'), so we need to find the key.
        response = self.ask(f"SOURce{self.channel_id}:FUNCtion?")
        for key, value in self.SHAPES.items():
            if value == response.strip():
                return key
        return None

    @shape.setter
    def shape(self, value):
        if value not in self.SHAPES:
            raise ValueError(f"Invalid shape. Must be one of {list(self.SHAPES.keys())}")
        self.write(f"SOURce{self.channel_id}:FUNCtion {self.SHAPES[value]}")

    @property
    def frequency(self):
        """Controls the frequency of the waveform in Hz."""
        return float(self.ask(f"SOURce{self.channel_id}:FREQuency?"))

    @frequency.setter
    def frequency(self, value):
        # Range validation depends on the waveform, here we use a general one.
        # Specific ranges are on page 208 of the manual.
        strict_range(value, [1e-6, 25e6])
        self.write(f"SOURce{self.channel_id}:FREQuency {value}")

    @property
    def amplitude(self):
        """Controls the peak-to-peak amplitude in Volts (Vpp)."""
        return float(self.ask(f"SOURce{self.channel_id}:AMPlitude?"))

    @amplitude.setter
    def amplitude(self, value):
        # Range validation depends on load. Assuming 50 Ohm load.
        strict_range(value, [0.001, 10.0])
        self.write(f"SOURce{self.channel_id}:AMPlitude {value}")

    @property
    def offset(self):
        """Controls the DC offset in Volts."""
        return float(self.ask(f"SOURce{self.channel_id}:DCOffset?"))

    @offset.setter
    def offset(self, value):
        # Range depends on amplitude.
        self.write(f"SOURce{self.channel_id}:DCOffset {value}")

    @property
    def phase(self):
        """Controls the phase shift in degrees."""
        return float(self.ask(f"SOURce{self.channel_id}:PHASe?"))

    @phase.setter
    def phase(self, value):
        strict_range(value, [-360, 360])
        self.write(f"SOURce{self.channel_id}:PHASe {value}")

    @property
    def output_enabled(self):
        """Controls whether the channel output is ON (True) or OFF (False)."""
        return self.ask(f"OUTPut{self.channel_id}?") == '1'

    @output_enabled.setter
    def output_enabled(self, value):
        state = 'ON' if bool(value) else 'OFF'
        self.write(f"OUTPut{self.channel_id} {state}")

    @property
    def load(self):
        """Controls the output load impedance ('50ohm' or 'highZ')."""
        response = self.ask(f"OUTPut{self.channel_id}:LOAD?")
        for key, value in self.LOADS.items():
            if value == response.strip():
                return key
        return None

    @load.setter
    def load(self, value):
        if value not in self.LOADS:
            raise ValueError(f"Invalid load. Must be one of {list(self.LOADS.keys())}")
        self.write(f"OUTPut{self.channel_id}:LOAD {self.LOADS[value]}")

    @property
    def duty_cycle(self):
        """Controls the duty cycle for Square waveforms in percent (1 to 99)."""
        return float(self.ask(f"SOURce{self.channel_id}:SQUare:DCYCle?"))

    @duty_cycle.setter
    def duty_cycle(self, value):
        strict_range(value, [1.0, 99.0])
        self.write(f"SOURce{self.channel_id}:SQUare:DCYCle {value}")

    @property
    def ramp_symmetry(self):
        """Controls the symmetry for Ramp waveforms in percent (0 to 100)."""
        return float(self.ask(f"SOURce{self.channel_id}:RAMP:SYMMetry?"))

    @ramp_symmetry.setter
    def ramp_symmetry(self, value):
        strict_range(value, [0, 100])
        self.write(f"SOURce{self.channel_id}:RAMP:SYMMetry {value}")


class AFG2225(SCPIMixin, Instrument):
    """
    Represents the GW Instek AFG-2225 Arbitrary Function Generator
    and provides a high-level interface for interacting with the instrument.
    """

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
        self.ch1 = AFG2225Channel(self, 1)
        self.ch2 = AFG2225Channel(self, 2)

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

    @property
    def error(self):
        """Reads the next error message from the instrument's error queue."""
        return self.ask("SYSTem:ERRor?")


if __name__ == '__main__':
    # This is an example of how to use the AFG2225 class.
    # You will need to replace 'TCPIP0::192.168.1.100::inst0::INSTR' with the
    # actual VISA resource string for your instrument.
    # You can find this using a VISA resource manager tool.

    print("Connecting to AFG-2225 Function Generator...")
    # Use a placeholder for demonstration purposes
    # In a real scenario, use the actual VISA address.
    # Example: generator = AFG2225("TCPIP0::192.168.1.100::inst0::INSTR")
    try:
        # Pymeasure's DummyInstrument can be used for testing without a real device
        from pymeasure.instruments.dummy import DummyInstrument
        generator = AFG2225(DummyInstrument())
        print("Connected to a dummy instrument for demonstration.")
    except Exception as e:
        print(f"Could not connect to a real instrument. Using a dummy. Error: {e}")
        from pymeasure.instruments.dummy import DummyInstrument
        generator = AFG2225(DummyInstrument())

    print("Resetting instrument to default state...")
    generator.reset()

    # --- Channel 1 Configuration ---
    print("\n--- Configuring Channel 1 ---")
    generator.ch1.shape = 'sine'
    generator.ch1.frequency = 10000  # 10 kHz
    generator.ch1.amplitude = 2.5    # 2.5 Vpp
    generator.ch1.offset = 0.5       # 0.5 V DC offset
    generator.ch1.phase = 0          # 0 degrees phase
    generator.ch1.output_enabled = True

    print(f"CH1 Shape: {generator.ch1.shape}")
    print(f"CH1 Frequency: {generator.ch1.frequency / 1000} kHz")
    print(f"CH1 Amplitude: {generator.ch1.amplitude} Vpp")
    print(f"CH1 Offset: {generator.ch1.offset} V")
    print(f"CH1 Phase: {generator.ch1.phase} degrees")
    print(f"CH1 Output Enabled: {generator.ch1.output_enabled}")

    # --- Channel 2 Configuration ---
    print("\n--- Configuring Channel 2 ---")
    generator.ch2.shape = 'square'
    generator.ch2.frequency = 25000  # 25 kHz
    generator.ch2.amplitude = 3.0    # 3.0 Vpp
    generator.ch2.offset = 0.0       # 0 V DC offset
    generator.ch2.phase = 45         # 45 degrees phase shift relative to CH1
    generator.ch2.duty_cycle = 75    # 75% duty cycle
    generator.ch2.output_enabled = True

    print(f"CH2 Shape: {generator.ch2.shape}")
    print(f"CH2 Frequency: {generator.ch2.frequency / 1000} kHz")
    print(f"CH2 Amplitude: {generator.ch2.amplitude} Vpp")
    print(f"CH2 Offset: {generator.ch2.offset} V")
    print(f"CH2 Phase: {generator.ch2.phase} degrees")
    print(f"CH2 Duty Cycle: {generator.ch2.duty_cycle}%")
    print(f"CH2 Output Enabled: {generator.ch2.output_enabled}")

    # --- Other Functions ---
    print("\n--- Demonstrating Other Functions ---")
    # Synchronize the phase of both channels
    print("Synchronizing phase of both channels...")
    generator.sync_phase()
    print(f"CH1 Phase after sync: {generator.ch1.phase} degrees")
    print(f"CH2 Phase after sync: {generator.ch2.phase} degrees")

    # Set phase again
    generator.ch2.phase = 90
    print(f"\nSet CH2 phase to {generator.ch2.phase} degrees.")

    # Check for errors
    print(f"Checking for system errors: {generator.error}")

    # Turn off outputs
    print("\nDisabling outputs.")
    generator.ch1.output_enabled = False
    generator.ch2.output_enabled = False
    print(f"CH1 Output Enabled: {generator.ch1.output_enabled}")
    print(f"CH2 Output Enabled: {generator.ch2.output_enabled}")

    print("\nDemonstration complete.")
