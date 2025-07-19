import time

from devices import Instrument


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
        
    def error(self) -> str:
        """
        Queries the instrument for the last error message.
        
        Returns:
            str: The error message, or 'No Error' if no errors are present.
        
        SCPI Command: :SYSTem:ERRor?
        """
        return self.query(':SYST:ERR?')

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

    def _execute_and_fetch_average(self, num_averages: int) -> float:
        """
        Private helper to initiate, wait for, and fetch an average measurement result
        after the instrument has been configured.

        Args:
            num_averages (int): The number of measurements to average (2 to 1,000,000).

        Returns:
            The average measured value as a float.
        """
        self.send_command(f":CALC3:AVER:COUN {num_averages}")
        self.send_command(":CALC3:AVER:STAT ON")
        self.send_command(":TRIG:COUN:AUTO ON")
        self.send_command(":CALC3:AVER:TYPE MEAN")
        
        # Enable the Operation Complete bit (1) to be summarized in the Status Byte
        self.send_command('*ESE 1')
        # Enable the Status Byte summary (bit 5, weight 32) to assert SRQ
        self.send_command('*SRE 32')
        # Initiate the block of measurements
        self.send_command(':INIT')
        self._wait_for_opc(timeout_sec=30)
        response = self.query(":CALC3:DATA?")
        
        # Clean up by disabling statistics mode
        self.send_command(":CALC3:AVER:STAT OFF")
        self.send_command(":TRIG:COUN:AUTO OFF")
        return float(response)

    # --- Configuration Functions ---
    # TODO: Test this function.
    def set_input_coupling(self, channel: int, coupling: str):
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
        self.send_command(f':INP{channel}:COUP {coupling_upper}')

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
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self.send_command(f':SENS:EVEN{channel}:LEV:ABS {level}')

    # TODO: Test this function.
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
        response = self.query(f':SENS:EVEN{channel}:LEV:ABS?')
        return float(response)

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

    # TODO: Test this function.
    def set_event_slope(self, channel: int, edge: str):
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
        self.send_command(f':SENS:EVEN{channel}:SLOP {edge_upper}')

    # TODO: Test this function.
    def set_time_interval_input_mode(self, mode: str):
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
        self.send_command(f":SENS:EVEN2:FEED '{feed_source}'")

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
        Measures frequency using resolution-based arming.
        
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

    # TODO: Test this function.
    def measure_frequency_gated(self, gate_time: float, channel: int = 1) -> float:
        """
        Measures frequency using a specified gate time.

        Args:
            gate_time (float): The measurement gate time in seconds.
            channel (int): The input channel (1, 2, or 3).

        Returns:
            The measured frequency in Hz.
        
        SCPI Commands:
            :FUNCtion 'FREQ <channel>'
            :FREQuency:ARM:STOP:SOURce TIMer
            :FREQuency:ARM:STOP:TIMer <gate_time>
        """
        self.send_command(f":FUNC 'FREQ {channel}'")
        self.send_command(":FREQ:ARM:STAR:SOUR IMM")
        self.send_command(":FREQ:ARM:STOP:SOUR TIM")
        self.send_command(f":FREQ:ARM:STOP:TIM {gate_time}")
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

    # TODO: Test this function.
    def measure_time_interval(self, start_edge: str = 'POS', stop_edge: str = 'POS') -> float:
        """
        Measures the time interval between a specified edge on Channel 1 (start)
        and a specified edge on Channel 2 (stop). Assumes SEPARATE input mode.

        Args:
            start_edge: The edge for the start signal on Channel 1 ('POS' or 'NEG').
            stop_edge: The edge for the stop signal on Channel 2 ('POS' or 'NEG').

        Returns:
            The measured time interval in seconds.
        """
        self.send_command(":CONF:TINT (@1),(@2)")
        self.set_event_slope(1, start_edge)
        self.set_event_slope(2, stop_edge)
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
        result = self._execute_and_fetch_average(num_averages)
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
        result = self._execute_and_fetch_average(num_averages)
        return float(result)

    # --- Totalizer (Counter) Functions ---

    def start_totalize(self):
        """
        Configures and starts a continuous event count (totalizer) on a channel.
        This function always starts a new count from zero. The instrument does not
        support pausing and resuming a hardware count.
        
        Use stop_and_fetch_totalize() to stop and get the result.
            
        SCPI Commands:
            :CONFigure:TOTalize:CONTinuous (@<channel>)
            :INITiate
        """
        # This configures for a manually gated (start/stop) totalize measurement
        self.send_command(f":CONF:TOT:CONT")
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

    def measure_totalize_timed(self, gate_time: float) -> int:
        """
        Counts events on a channel for a specified duration (gate time).

        Args:
            gate_time (float): The duration in seconds for which to count events.

        Returns:
            The total number of events counted during the gate time.
        
        SCPI Command: :CONFigure:TOTalize:TIMed <gate_time>,(@<channel>)
        """
        conf_cmd = f":CONF:TOT:TIM {gate_time}"
        self.send_command(conf_cmd)
        result = self._execute_and_fetch()
        return int(result)
