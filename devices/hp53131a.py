import time

from devices.base import Instrument


# TODO: implement an error function. Maybe it is better to add to father class. error()
class HP53131A(Instrument):
    """
    Driver for the Agilent/HP 53131A Universal Counter.
    
    This class implements methods for configuring and performing various
    measurements such as frequency, period, time interval, and totalize.
    """
    def setup(self):
        """
        Initializes the counter to a known, stable state for remote programming.
        """
        super().setup()
        self.reset()
        self.clear()
        # Disable all bits in Service Request Enable register
        self.send_command('*SRE 0')
        # Disable all bits in Standard Event Status Enable register
        self.send_command('*ESE 0')
        # Preset the Operation and Questionable status registers
        self.send_command(':STAT:PRES')
        
    def id(self) -> str:
        """Queries the instrument's identification string."""
        return self.query('*IDN?')

    def reset(self):
        """Resets the instrument to its factory default state."""
        self.send_command('*RST')
        
    def clear(self):
        """Clears all event registers and the error queue."""
        self.send_command('*CLS')

    def _wait_for_opc(self, timeout_sec: int = 10):
        """
        Waits for the previous operation to complete by polling the Service
        Request Queue (SRQ) for the Operation Complete (OPC) bit.
        """
        start_time = time.time()
        # *OPC command sets the OPC bit in the Standard Event Status Register
        # when all pending operations are finished.
        self.send_command('*OPC')
        while not self.adapter.query_srq():
            if time.time() - start_time > timeout_sec:
                raise TimeoutError("Timeout waiting for operation to complete.")
            time.sleep(0.1)
        # Clear status registers after a successful wait to prepare for the next operation
        self.clear()

    def _execute_and_fetch(self) -> float:
        """
        Private helper to initiate, wait for, and fetch a single measurement result
        after the instrument has been configured.
        
        Returns:
            The measured value as a float.
        """
        # Enable the Operation Complete bit (1) to be summarized in the Status Byte
        self.send_command('*ESE 1')
        # Enable the Status Byte summary (bit 5, weight 32) to assert SRQ
        self.send_command('*SRE 32')
        # Initiate the measurement
        self.send_command(':INIT')
        # Wait for the measurement to finish
        self._wait_for_opc()
        # Fetch the result
        response = self.query(':FETCH?')
        return float(response)

    # --- Configuration Functions ---

    def set_attenuation(self, channel: int, attenuation_x: int):
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
        self.send_command(f':INP{channel}:ATT {attenuation_x}')

    def set_trigger_level_volts(self, channel: int, level: float):
        """
        Sets the trigger level to an absolute voltage. This disables auto-trigger.
        
        Args:
            channel: The input channel (1 or 2).
            level: The trigger level in Volts.
            
        SCPI Command: [:SENSe]:EVENt[1|2]:LEVel[:ABSolute] <level>
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        # Setting the absolute level automatically disables auto-trigger
        self.send_command(f':SENS:EVEN{channel}:LEV:ABS {level}')

    def set_trigger_level_percent(self, channel: int, percent: float):
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
        self.send_command(f':SENS:EVEN{channel}:LEV:AUTO ON')
        self.send_command(f':SENS:EVEN{channel}:LEV:REL {percent}')

    def initiate_continuous(self, enabled: bool):
        """
        Enables or disables continuously initiated measurements.
        
        Args:
            enabled: True to enable continuous mode, False to disable.
        
        SCPI Command: :INITiate:CONTinuous <bool>
        """
        self.send_command(f':INIT:CONT {int(enabled)}')

    # --- Measurement Functions ---

    def measure_frequency(self, channel: int = 1, expected_value: str = 'DEF', resolution: str = 'DEF') -> float:
        """
        Measures the frequency on a specified channel.
        
        Args:
            channel: The input channel (1, 2, or 3 if option installed).
            expected_value: The approximate expected frequency (e.g., '10MHz'). DEF for default.
            resolution: The desired resolution (e.g., '1Hz'). DEF for default.
            
        Returns:
            The measured frequency in Hz.
        """
        conf_cmd = f":CONF:FREQ {expected_value},{resolution},(@{channel})"
        self.send_command(conf_cmd)
        return self._execute_and_fetch()

    def measure_period(self, channel: int = 1, expected_value: str = 'DEF', resolution: str = 'DEF') -> float:
        """
        Measures the period on a specified channel.
        
        Args:
            channel: The input channel (1, 2, or 3 if option installed).
            expected_value: The approximate expected period (e.g., '100ns'). DEF for default.
            resolution: The desired resolution. Setting a higher resolution (e.g., more digits)
                        forces the counter to measure over a longer gate time, effectively
                        averaging the measurement over more cycles of the input signal.
            
        Returns:
            The measured period in seconds.
        """
        conf_cmd = f":CONF:PER {expected_value},{resolution},(@{channel})"
        self.send_command(conf_cmd)
        return self._execute_and_fetch()

    def measure_time_interval(self) -> float:
        """
        Measures the time interval between a start event on Channel 1 and a stop event on Channel 2.
        By default, this measures the time between the rising edge on Ch1 and the rising edge on Ch2.
        
        Returns:
            The measured time interval in seconds.
        """
        self.send_command(":CONF:TINT (@1),(@2)")
        return self._execute_and_fetch()

    def measure_time_interval_edge_to_edge(self, start_edge: str, stop_edge: str) -> float:
        """
        Measures the time interval between a specified edge on Channel 1 (start)
        and a specified edge on Channel 2 (stop).

        Args:
            start_edge: The edge for the start signal on Channel 1 ('POS' or 'NEG').
            stop_edge: The edge for the stop signal on Channel 2 ('POS' or 'NEG').

        Returns:
            The measured time interval in seconds.
            
        SCPI Commands:
            :CONFigure:TINTerval (@1),(@2)
            [:SENSe]:EVENt1:SLOPe <edge>
            [:SENSe]:EVENt2:SLOPe <edge>
            :INITiate
            :FETCh?
        """
        valid_edges = ['POS', 'NEG']
        start_edge_upper = start_edge.upper()
        stop_edge_upper = stop_edge.upper()
        
        if start_edge_upper not in valid_edges or stop_edge_upper not in valid_edges:
            raise ValueError("Edge arguments must be 'POS' or 'NEG'.")

        # 1. Configure for a generic time interval measurement.
        # This also resets related settings to defaults (like slope).
        self.send_command(":CONF:TINT (@1),(@2)")

        # 2. Set the specific slopes for the start and stop events.
        self.send_command(f":SENS:EVEN1:SLOP {start_edge_upper}")
        self.send_command(f":SENS:EVEN2:SLOP {stop_edge_upper}")
        return self._execute_and_fetch()

    def measure_period_average(self, channel: int, num_averages: int) -> float:
        """
        Measures the average period over a specified number of measurements.
        
        Args:
            channel: The input channel (1, 2, or 3).
            num_averages: The number of measurements to average (2 to 1,000,000).
            
        Returns:
            The average period in seconds.
        """
        self.send_command(f":CONF:PER DEF,DEF,(@{channel})")
        self.send_command(f":CALC3:AVER:COUN {num_averages}")
        self.send_command(":CALC3:AVER:STAT ON")
        self.send_command(":TRIG:COUN:AUTO ON")
        self.send_command(":CALC3:AVER:TYPE MEAN")
        
        # Initiate the block of measurements
        self.send_command(':INIT')
        self._wait_for_opc(timeout_sec=30)
        result = self.query(":CALC3:DATA?")
        
        # Clean up by disabling statistics mode
        self.send_command(":CALC3:AVER:STAT OFF")
        self.send_command(":TRIG:COUN:AUTO OFF")
        return float(result)

    def measure_time_interval_average(self, num_averages: int) -> float:
        """
        Measures the average time interval over a specified number of measurements.
        
        Args:
            num_averages: The number of measurements to average (2 to 1,000,000).
            
        Returns:
            The average time interval in seconds.
        """
        self.send_command(":CONF:TINT (@1),(@2)")
        self.send_command(f":CALC3:AVER:COUN {num_averages}")
        self.send_command(":CALC3:AVER:STAT ON")
        self.send_command(":TRIG:COUN:AUTO ON")
        self.send_command(":CALC3:AVER:TYPE MEAN")
        
        self.send_command(':INIT')
        self._wait_for_opc(timeout_sec=30)
        result = self.query(":CALC3:DATA?")
        
        self.send_command(":CALC3:AVER:STAT OFF")
        self.send_command(":TRIG:COUN:AUTO OFF")
        return float(result)

    # --- Totalizer (Counter) Functions ---

    def start_totalize(self, channel: int = 1):
        """
        Configures and starts a continuous event count (totalizer) on a channel.
        This function always starts a new count from zero. The instrument does not
        support pausing and resuming a hardware count.
        
        Use stop_and_fetch_totalize() to stop and get the result.
        
        Args:
            channel: The channel to count events on (1 or 2).
            
        SCPI Commands:
            :CONFigure:TOTalize:CONTinuous (@<channel>)
            :INITiate
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        # This configures for a manually gated (start/stop) totalize measurement
        self.send_command(f":CONF:TOT:CONT (@{channel})")
        # This starts the counting
        self.send_command(":INIT")

    def stop_and_fetch_totalize(self) -> int:
        """
        Stops the continuous totalizer and fetches the final count.
        
        Returns:
            The total number of events counted.
            
        SCPI Commands:
            :ABORt
            :FETCh?
        """
        # The ABORt command is the correct way to stop a continuous totalize measurement
        self.send_command(":ABORt")
        result = self.query(":FETCH?")
        return int(float(result))

    def measure_totalize_timed(self, gate_time: float, channel: int = 1) -> int:
        """
        Counts events on a channel for a specified duration (gate time).

        Args:
            gate_time (float): The duration in seconds for which to count events.
            channel (int): The channel to count events on (1 or 2).

        Returns:
            The total number of events counted during the gate time.
        
        SCPI Command: :CONFigure:TOTalize:TIMed <gate_time>,(@<channel>)
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
            
        conf_cmd = f":CONF:TOT:TIM {gate_time},(@{channel})"
        self.send_command(conf_cmd)
        result = self._execute_and_fetch()
        return int(result)
