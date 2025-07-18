from devices import Instrument


class HP3458A(Instrument):
    def setup(self):
        super().setup()
        self.send_command('TRIG HOLD') # Hold triggering
        
    def id(self):
        return self.query('ID?')

    def reset(self):
        self.send_command('RESET')
        
    def beep(self):
        self.send_command('BEEP')
        
    # TODO: Remove this function after testing new ones.
    def measure_voltage(self, reading_times: int = 1, interval: float = 1.0):
        """
        Args:
            reading_times (int): Number of readings to take.
            interval (float): Time interval between readings in seconds.
        """
        self.send_command('FUNC DCV')
        self.send_command('MEM FIFO') # Enable memory. remove all existing data in memory
        self.send_command(f'TIMER {interval}')
        self.send_command(f'NRDGS {reading_times},TIMER')
        self.send_command('TRIG SGL')
        
    def external_buffer(self, enabled: bool):
        command = 'TBUFF ON' if enabled else 'TBUFF OFF'
        self.send_command(command)
        
    def memory(self):
        self.send_command('MEM FIFO') 
        
    def reading_counts(self):
        return self.query('MCOUNT?')
        
    def temperature(self):
        """
        Reads the internal temperature of the multimeter.
        Example response: 29.3
        """
        return self.query('TEMP?')
        
    def error(self):
        """
        Reads the error string from the instrument.
        Example response: 0,"NO ERROR" or 102,"TRIGGER TOO FAST"
        """
        return self.query('ERRSTR?')
        
    def display(self, message: str):
        if len(message) > 75:
            raise ValueError("Display message cannot exceed 75 characters.")
        self.send_command(f'DISP MSG,"{message}"')

    def get_reading(self):
        """Triggers a single reading and returns the value."""
        self.send_command('TRIG SGL') # Trigger reading
        return float(self.read_response())
    
    # --- Helper & Configuration Functions ---
    # TODO: Implement interrupt before reading.

    def set_filter(self, enable=True):
        """Enables/disables the low-pass filter with the -3dB point at 75kHz."""
        self.send_command('LFILTER ON' if enable else 'LFILTER OFF')

    # TODO: test this function. Is SGL also hold?
    def set_triggering(self, source='SGL', arm_source='AUTO'):
        """
        Sets the trigger and trigger arming source.

        Args:
            source (str): The trigger event source. Common values:
                          'SGL' (single software trigger), 'EXT' (external),
                          'HOLD' (wait for TRIG command). Defaults to 'SGL'.
            arm_source (str): The event that arms the trigger. Common values:
                              'AUTO', 'SGL', 'EXT', 'HOLD'. Defaults to 'AUTO'.
        
        SCPI Commands: TARM, TRIG
        """
        self.send_command(f'TARM {arm_source}')
        self.send_command(f'TRIG {source}')

    # TODO: test this. I think it needs MEM FIFO enabled.
    def set_reading_burst(self, count: int, interval: float = None):
        """
        Configures the instrument to take a burst of readings.

        Args:
            count (int): The number of readings to take per trigger.
            interval (float, optional): The time interval between readings in seconds.
                                        If provided, the sample event is set to TIMER.
                                        Defaults to None, which uses AUTO event.
        
        SCPI Commands: NRDGS, TIMER
        """
        if interval:
            self.send_command(f'TIMER {interval}')
            self.send_command(f'NRDGS {count},TIMER')
        else:
            self.send_command(f'NRDGS {count},AUTO')

    def __set_range(self, mrange: float | None, nplc: float):
        if mrange is None:
            self.send_command('RANGE AUTO')
        else:
            self.send_command(f'RANGE {mrange:0.6f}')
        self.send_command(f'NPLC {nplc:0.3f}')

    def __autoZero(self, enabled=True):
        self.send_command('AZERO ON' if enabled else 'AZERO OFF')

    def __hiZ(self, enabled=True):
        self.send_command('FIXEDZ OFF' if enabled else 'FIXEDZ ON')

    def __ocomp(self, enabled=True):
        self.send_command('OCOMP ON' if enabled else 'OCOMP OFF')

    # --- Measurement Configuration Functions ---

    def conf_function_DCV(self, mrange=None, nplc=1, AutoZero=True, HiZ=True):
        """Configures the meter to measure DCV. If range=None the meter is set to Autorange."""
        self.send_command('PRESET NORM')
        self.send_command('DCV')
        self.send_command('NDIG 6')
        self.send_command('TRIG SGL')
        self.__set_range(mrange, nplc)
        self.__autoZero(AutoZero)
        self.__hiZ(HiZ)

    def conf_function_DCI(self, mrange=None, nplc=1, AutoZero=True, HiZ=True):
        """Configures the meter to measure DCI. If range=None the meter is set to Autorange."""
        self.send_command('PRESET NORM')
        self.send_command('DCI')
        self.send_command('NDIG 6')
        self.send_command('TRIG SGL')
        self.__set_range(mrange, nplc)
        self.__autoZero(AutoZero)
        self.__hiZ(HiZ)

    def conf_function_ACV(self, mrange=None, nplc=1, AutoZero=True, HiZ=True):
        """Configures the meter to measure ACV (True RMS). If range=None the meter is set to Autorange."""
        self.send_command('PRESET NORM')
        self.send_command('ACV')
        self.send_command('SETACV SYNC')
        self.send_command('NDIG 6')
        self.send_command('TRIG SGL')
        self.__set_range(mrange, nplc)
        self.__autoZero(AutoZero)
        self.__hiZ(HiZ)

    def conf_function_ACI(self, mrange=None, nplc=1, AutoZero=True, HiZ=True):
        """Configures the meter to measure ACI. If range=None the meter is set to Autorange."""
        self.send_command('PRESET NORM')
        self.send_command('ACI')
        self.send_command('NDIG 6')
        self.send_command('TRIG SGL')
        self.__set_range(mrange, nplc)
        self.__autoZero(AutoZero)
        self.__hiZ(HiZ)

    def conf_function_OHM2W(self, mrange=None, nplc=1, AutoZero=True, OffsetCompensation=True):
        """Configures the meter to measure OHM2W. If range=None the meter is set to Autorange."""
        self.send_command('PRESET NORM')
        self.send_command('OHM')
        self.send_command('NDIG 6')
        self.send_command('TRIG SGL')
        self.__set_range(mrange, nplc)
        self.__autoZero(AutoZero)
        self.__ocomp(OffsetCompensation)

    def conf_function_OHM4W(self, mrange=None, nplc=1, AutoZero=True, OffsetCompensation=True):
        """Configures the meter to measure OHM4W. If range=None the meter is set to Autorange."""
        self.send_command('PRESET NORM')
        self.send_command('OHMF')
        self.send_command('NDIG 6')
        self.send_command('TRIG SGL')
        self.__set_range(mrange, nplc)
        self.__autoZero(AutoZero)
        self.__ocomp(OffsetCompensation)
        
    def conf_function_FREQ(self, mrange='AUTO', gate_time=1.0):
        """
        Configures the meter to measure Frequency.

        Args:
            mrange (str or float, optional): Input voltage range (e.g., 10 for 10V) or 'AUTO'.
                                            Defaults to 'AUTO'.
            gate_time (float, optional): The measurement gate time in seconds. A longer
                                         gate time results in higher resolution.
                                         Valid values: 1.0, 0.1, 0.01, 0.001, 0.0001.
                                         Defaults to 1.0.
        """
        gate_time_map = {
            1.0:    0.00001,  # 7 digits
            0.1:    0.0001,   # 7 digits
            0.01:   0.001,    # 6 digits
            0.001:  0.01,     # 5 digits
            0.0001: 0.1       # 4 digits
        }
        if gate_time not in gate_time_map:
            raise ValueError(f"Invalid gate_time. Must be one of {list(gate_time_map.keys())}")
            
        resolution_param = gate_time_map[gate_time]
        range_param = 'AUTO' if mrange == 'AUTO' else f'{mrange:0.6f}'

        self.send_command('PRESET NORM')
        # Use FSOURCE to define the signal type for frequency measurement (default is ACV)
        self.send_command('FSOURCE ACV')
        # Use the FUNC command for a concise setup
        self.send_command(f'FUNC FREQ, {range_param}, {resolution_param}')
        self.send_command('TRIG SGL')

    def conf_function_ACDCV(self, mrange=None, nplc=1, ac_bandwidth_low=20, HiZ=True):
        """
        Configures the meter to measure combined AC+DC Voltage (True RMS).

        Args:
            mrange (float, optional): The measurement range (e.g., 10 for 10V).
                                      Defaults to None (Autorange).
            nplc (float, optional): Integration time in Number of Power Line Cycles. Defaults to 100.
            ac_bandwidth_low (int, optional): The expected lowest frequency component in Hz.
                                              Defaults to 20.
            HiZ (bool, optional): Use high input impedance. Defaults to True.
        """
        self.send_command('PRESET NORM')
        self.send_command('ACDCV')
        self.send_command(f'ACBAND {ac_bandwidth_low}')
        self.send_command('NDIG 6')
        self.send_command('TRIG SGL')
        self.__set_range(mrange, nplc)
        self.__autoZero(True)
        self.__hiZ(HiZ)

    # TODO: Test this function.
    def conf_function_digitize(self, mode='DSDC', mrange=10, delay=0, num_samples=1024, sample_interval=100e-9):
        """
        Configures the meter for high-speed digitizing using the track-and-hold circuit.

        Args:
            mode (str): 'DSDC' for AC+DC sampling, 'DSAC' for AC-only. Defaults to 'DSDC'.
            mrange (float): The measurement range (e.g., 10 for 10V). Defaults to 10.
            delay (float): Delay in seconds between trigger and first sample. Defaults to 0.
            num_samples (int): The total number of samples to take. Defaults to 1024.
            sample_interval (float): The time interval between samples in seconds. Defaults to 100e-9.
        
        SCPI Commands: PRESET DIG, DSDC/DSAC, RANGE, DELAY, SWEEP
        """
        if mode.upper() not in ['DSDC', 'DSAC']:
            raise ValueError("Mode must be 'DSDC' or 'DSAC'.")
        
        self.send_command('PRESET DIG') # Use the digitizing preset
        self.send_command(mode.upper())
        self.send_command(f'RANGE {mrange}')
        if delay > 0:
            self.send_command(f'DELAY {delay}')
        
        # SWEEP command sets the sample interval and number of samples
        self.send_command(f'SWEEP {sample_interval}, {num_samples}')
        
        # After configuration, the meter will wait for a trigger.
        # Use set_triggering() to define the trigger source.
