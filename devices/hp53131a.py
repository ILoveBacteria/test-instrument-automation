import time

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

from devices import TerminationMixin


class HP53131A(TerminationMixin, SCPIMixin, Instrument):
    """
    Represents the Hewlett-Packard 53131A Universal Counter.
    """

    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, 'Hewlett-Packard 53131A', **kwargs)
        
    # Channel-specific configuration properties
    ch1_coupling = Instrument.control(
        ":INP1:COUP?", ":INP1:COUP %s",
        """Sets the input coupling for channel 1.""",
        validator=strict_discrete_set,
        values=['AC', 'DC']
    )

    ch2_coupling = Instrument.control(
        ":INP2:COUP?", ":INP2:COUP %s",
        """Sets the input coupling for channel 2.""",
        validator=strict_discrete_set,
        values=['AC', 'DC']
    )

    ch1_attenuation = Instrument.control(
        ":INP1:ATT?", ":INP1:ATT %d",
        """Sets the input attenuation for channel 1.""",
        validator=strict_discrete_set,
        values=[1, 10]
    )

    ch2_attenuation = Instrument.control(
        ":INP2:ATT?", ":INP2:ATT %d",
        """Sets the input attenuation for channel 2.""",
        validator=strict_discrete_set,
        values=[1, 10]
    )

    ch1_trigger_level = Instrument.control(
        ":SENS:EVEN1:LEV:ABS?", ":SENS:EVEN1:LEV:ABS %f",
        """Sets the trigger level for channel 1 in Volts."""
    )

    ch2_trigger_level = Instrument.control(
        ":SENS:EVEN2:LEV:ABS?", ":SENS:EVEN2:LEV:ABS %f",
        """Sets the trigger level for channel 2 in Volts."""
    )

    ch1_trigger_slope = Instrument.control(
        ":SENS:EVEN1:SLOP?", ":SENS:EVEN1:SLOP %s",
        """Sets the trigger slope for channel 1.""",
        validator=strict_discrete_set,
        values=['POS', 'NEG']
    )

    ch2_trigger_slope = Instrument.control(
        ":SENS:EVEN2:SLOP?", ":SENS:EVEN2:SLOP %s",
        """Sets the trigger slope for channel 2.""",
        validator=strict_discrete_set,
        values=['POS', 'NEG']
    )
        
    def setup(self):
        """
        Initializes the counter to a known, stable state for remote programming.
        """
        self.reset()
        self.clear()
        # Disable all bits in Service Request Enable register
        self.write('*SRE 0')
        # Disable all bits in Standard Event Status Enable register
        self.write('*ESE 0')
        # Preset the Operation and Questionable status registers
        self.write(':STAT:PRES')
        
    def id(self) -> str:
        """Queries the instrument's identification string."""
        return self.ask('*IDN?')

    def reset(self):
        """Resets the instrument to its factory default state."""
        self.write('*RST')
        
    def clear(self):
        """Clears all event registers and the error queue."""
        self.write('*CLS')
        
    def error(self) -> str:
        """
        Queries the instrument for the last error message.
        
        Returns:
            str: The error message, or 'No Error' if no errors are present.
        
        SCPI Command: :SYSTem:ERRor?
        """
        return self.ask(':SYST:ERR?')
    
    # --- Initiate and Reading

    def _wait_for_opc(self, timeout_sec: int):
        """
        Waits for the previous operation to complete by polling the Service
        Request Queue (SRQ) for the Operation Complete (OPC) bit.
        """
        start_time = time.time()
        # *OPC command sets the OPC bit in the Standard Event Status Register
        # when all pending operations are finished.
        self.write('*OPC')
        while not self.adapter.connection.query_srq():
            if time.time() - start_time > timeout_sec:
                raise TimeoutError("Timeout waiting for operation to complete.")
            time.sleep(0.1)
        # Clear status registers after a successful wait to prepare for the next operation
        self.clear()
        
    def initiate(self):
        # Enable the Operation Complete bit (1) to be summarized in the Status Byte
        self.write('*ESE 1')
        # Enable the Status Byte summary (bit 5, weight 32) to assert SRQ
        self.write('*SRE 32')
        # Initiate the measurement
        self.write(':INIT')
        
    def fetch(self) -> float:
        response = self.ask(':FETCH?')
        return float(response)
    
    def wait_and_fetch(self, timeout_sec: int = 10) -> float:
        self._wait_for_opc(timeout_sec)
        return self.fetch()
    
    def initiate_wait_fetch(self, timeout_sec: int = 10) -> float:
        self.initiate()
        return self.wait_and_fetch(timeout_sec)
    
    def fetch_average(self) -> float:
        response = self.ask(":CALC3:DATA?")
        # Clean up by disabling statistics mode
        self.write(":CALC3:AVER:STAT OFF")
        self.write(":TRIG:COUN:AUTO OFF")
        return float(response)
    
    def stop(self):
        """
        Stops the continuous totalizer and fetches the final count.
            
        SCPI Commands:
            :ABORt
        """
        self.write(":ABORt")

    # --- Configuration Functions ---
    def _set_input_coupling(self, channel: int, coupling: str):
        """
        Sets the input coupling for a specified channel.

        Args:
            channel (int): The input channel (1 or 2).
            coupling (str): The coupling type, 'AC' or 'DC'.
        
        SCPI Command: :INPut[1|2]:COUPling <value>
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        coupling_upper = coupling.upper()
        if coupling_upper not in ['AC', 'DC']:
            raise ValueError("Coupling must be 'AC' or 'DC'.")
        self.write(f':INP{channel}:COUP {coupling_upper}')

    def _set_attenuation(self, channel: int, attenuation_x: int):
        """
        Sets the input attenuation for a specified channel.
        
        Args:
            channel: The input channel (1 or 2).
            attenuation_x: The attenuation factor (1 or 10).
        
        SCPI Command: :INPut[1|2]:ATTenuation <value>
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        if attenuation_x not in [1, 10]:
            raise ValueError("Attenuation must be 1 or 10.")
        self.write(f':INP{channel}:ATT {attenuation_x}')

    def _set_trigger_level_volts(self, channel: int, level: float):
        """
        Sets the trigger level to an absolute voltage. This disables auto-trigger.
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self.write(f':SENS:EVEN{channel}:LEV:ABS {level}')

    def get_trigger_level_volts(self, channel: int) -> float:
        """
        Queries the currently configured absolute trigger level in Volts.

        Args:
            channel (int): The input channel (1 or 2).

        Returns:
            float: The trigger level in Volts.
        
        SCPI Command: [:SENSe]:EVENt[1|2]:LEVel[:ABSolute]?
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        response = self.ask(f':SENS:EVEN{channel}:LEV:ABS?')
        return float(response)

    def _set_trigger_level_percent(self, channel: int, percent: float):
        """
        Sets the trigger level as a percentage of the signal's peak-to-peak voltage.
        This requires auto-trigger to be enabled.
        
        Args:
            channel: The input channel (1 or 2).
            percent: The trigger level percentage (0 to 100).
            
        SCPI Commands:
            [:SENSe]:EVENt[1|2]:LEVel[:ABSolute]:AUTO ON
            [:SENSe]:EVENt[1|2]:LEVel:RELative <percent>
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        if not 0 <= percent <= 100:
            raise ValueError("Percent must be between 0 and 100.")
        # Ensure auto-trigger is on before setting a relative level
        self.write(f':SENS:EVEN{channel}:LEV:AUTO ON')
        self.write(f':SENS:EVEN{channel}:LEV:REL {percent}')

    def _set_event_slope(self, channel: int, edge: str):
        """
        Sets the trigger slope for a specified event channel.

        Args:
            channel (int): The event channel (1 or 2).
            edge (str): The trigger edge, 'POS' (positive/rising) or 'NEG' (negative/falling).
        
        SCPI Command: [:SENSe]:EVENt[1|2]:SLOPe <edge>
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        edge_upper = edge.upper()
        if edge_upper not in ['POS', 'NEG']:
            raise ValueError("Edge must be 'POS' or 'NEG'.")
        self.write(f':SENS:EVEN{channel}:SLOP {edge_upper}')

    def _set_time_interval_input_mode(self, mode: str):
        """
        Sets the input routing for Time Interval measurements.

        Args:
            mode (str): 'SEPARATE' to use Channel 1 for start and Channel 2 for stop.
                        'COMMON' to use Channel 1 for both start and stop events.
        
        SCPI Command: [:SENSe]:EVENt2:FEED <source>
        """
        mode_upper = mode.upper()
        if mode_upper not in ['COMMON', 'SEPARATE']:
            raise ValueError("Mode must be 'COMMON' or 'SEPARATE'.")
        
        feed_source = 'INP1' if mode_upper == 'COMMON' else 'INP2'
        self.write(f":SENS:EVEN2:FEED '{feed_source}'")

    def initiate_continuous(self, enabled: bool):
        """
        Enables or disables continuously initiated measurements.
        
        Args:
            enabled: True to enable continuous mode, False to disable.
        
        SCPI Command: :INITiate:CONTinuous <bool>
        """
        self.write(f':INIT:CONT {int(enabled)}')
    
    def measurement_configuration(self, channel: int, coupling: str = 'DC', slope: str = 'POS', attenuation_x: int = 1, trigger_level: float = 0):
        """
        Configures the measurement settings for a specified channel.
        
        Args:
            channel: The input channel (1 or 2).
            coupling: The input coupling ('AC' or 'DC').
            start_edge: The start edge for time interval measurements ('POS' or 'NEG').
            stop_edge: The stop edge for time interval measurements ('POS' or 'NEG').
            attenuation_x: The input attenuation factor (1 or 10).
        """
        self._set_input_coupling(channel, coupling)
        self._set_event_slope(channel, slope)
        self._set_attenuation(channel, attenuation_x)
        self._set_trigger_level_volts(channel, trigger_level)

    # --- Measurement Functions ---

    def measure_frequency(self, channel: int, expected_value: str = 'DEF', resolution: str = 'DEF'):
        """
        Measures frequency using resolution-based arming.
        
        Args:
            channel: The input channel (1, 2, or 3 if option installed).
            expected_value: The approximate expected frequency (e.g., '10MHz'). DEF for default.
            resolution: The desired resolution (e.g., '1Hz'). DEF for default.
        """
        conf_cmd = f":CONF:FREQ {expected_value},{resolution},(@{channel})"
        self.write(conf_cmd)

    def measure_frequency_gated(self, gate_time: float, channel: int = 1):
        """
        Measures frequency using a specified gate time.

        Args:
            gate_time (float): The measurement gate time in seconds.
            channel (int): The input channel (1, 2, or 3).
        
        SCPI Commands:
            :FUNCtion 'FREQ <channel>'
            :FREQuency:ARM:STOP:SOURce TIMer
            :FREQuency:ARM:STOP:TIMer <gate_time>
        """
        self.write(f":FUNC 'FREQ {channel}'")
        self.write(":FREQ:ARM:STAR:SOUR IMM")
        self.write(":FREQ:ARM:STOP:SOUR TIM")
        self.write(f":FREQ:ARM:STOP:TIM {gate_time}")

    def measure_period(self, channel: int, expected_value: str = 'DEF', resolution: str = 'DEF'):
        """
        Measures the period on a specified channel.
        
        Args:
            channel: The input channel (1, 2, or 3 if option installed).
            expected_value: The approximate expected period (e.g., '100ns'). DEF for default.
            resolution: The desired resolution. Setting a higher resolution (e.g., more digits)
                        forces the counter to measure over a longer gate time, effectively
                        averaging the measurement over more cycles of the input signal.
        """
        conf_cmd = f":CONF:PER {expected_value},{resolution},(@{channel})"
        self.write(conf_cmd)

    def measure_time_interval(self):
        """
        Measures the time interval between a specified edge on Channel 1 (start)
        and a specified edge on Channel 2 (stop). Assumes SEPARATE input mode.
        """
        self.write(":CONF:TINT (@1),(@2)")

    def measure_period_average(self, channel: int, num_averages: int):
        """
        Measures the average period over a specified number of measurements.
        
        Args:
            channel: The input channel (1, 2, or 3).
            num_averages: The number of measurements to average (2 to 1,000,000).
        """
        self.write(f":CONF:PER DEF,DEF,(@{channel})")
        self.write(f":CALC3:AVER:COUN {num_averages}")
        self.write(":CALC3:AVER:STAT ON")
        self.write(":TRIG:COUN:AUTO ON")
        self.write(":CALC3:AVER:TYPE MEAN")

    def measure_time_interval_average(self, num_averages: int):
        """
        Measures the average time interval over a specified number of measurements.
        
        Args:
            num_averages: The number of measurements to average (2 to 1,000,000).
        """
        self.write(":CONF:TINT (@1),(@2)")
        self.write(f":CALC3:AVER:COUN {num_averages}")
        self.write(":CALC3:AVER:STAT ON")
        self.write(":TRIG:COUN:AUTO ON")
        self.write(":CALC3:AVER:TYPE MEAN")

    # --- Totalizer (Counter) Functions ---

    def measure_totalize(self):
        """
        Configures and starts a continuous event count (totalizer) on a channel.
        This function always starts a new count from zero. The instrument does not
        support pausing and resuming a hardware count.
        
        Use stop_and_fetch_totalize() to stop and get the result.
            
        SCPI Commands:
            :CONFigure:TOTalize:CONTinuous (@<channel>)
        """
        # This configures for a manually gated (start/stop) totalize measurement
        self.write(f":CONF:TOT:CONT")

    def measure_totalize_timed(self, gate_time: float):
        """
        Counts events on a channel for a specified duration (gate time).

        Args:
            gate_time (float): The duration in seconds for which to count events.

        SCPI Command: :CONFigure:TOTalize:TIMed <gate_time>,(@<channel>)
        """
        conf_cmd = f":CONF:TOT:TIM {gate_time}"
        self.write(conf_cmd)
