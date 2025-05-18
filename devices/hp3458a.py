import time

from devices.base import Instrument


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
        # Back to previous configs
        self.send_command(f'NRDGS 1,AUTO')
        self.send_command(f'TIMER 1')
        
    def external_buffer(self, enabled: bool):
        command = 'TBUFF ON' if enabled else 'TBUFF OFF'
        self.send_command(command)
        
    def memory(self):
        self.send_command('MEM FIFO') 
        
    def reading_counts(self):
        self.send_command('MCOUNT?')
        
    def temperature(self):
        """
        29.3
        """
        self.send_command('TEMP?')
        
    def error(self):
        """
        102,"TRIGGER TOO FAST" - 0,"NO ERROR"
        """
        self.send_command('ERRSTR?')
        
    def display(self, message: str):
        if len(message) > 75:
            raise ValueError()
        self.send_command(f'DISP MSG,"{message}"')
        
    def wait_for_data(self, timeout=5):
        """Poll the instrument until data is ready (bit 7 set)."""
        start = time.time()
        while True:
            # send(sock, '++spoll')  # Serial Poll
            # status = read(sock)
            self.send_command('++spoll')
            status = self.read_response()
            print(status)
            status_byte = int(status)
            if status_byte & 0b10000000:  # Check bit 7 (data ready)
                return True
            if (time.time() - start) > timeout:
                raise TimeoutError('Timeout waiting for data ready')
            time.sleep(0.1)
