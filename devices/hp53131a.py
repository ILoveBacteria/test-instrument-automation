from time import sleep

from devices.base import Instrument


class HP53131A(Instrument):
    def setup(self):
        super().setup()
        self.reset()
        self.clear()
        self.send_command('*SRE 0')
        self.send_command('*ESE 0')
        self.send_command(':STAT:PRES')
        
    def id(self):
        return self.query('*IDN?')

    def reset(self):
        self.send_command('*RST')
        
    def clear(self):
        self.send_command('*CLS')
        
    def measure_frequency(self, expected_value: str = '10 MHz', channel: int = 1):
        self.send_command(f':CONF:FREQ {expected_value},DEF,(@1)')
        self.send_command('*ESE 1')
        self.send_command('*SRE 32')
        self.send_command(':INIT')
        self.send_command('*OPC')
        self.wait()
        self.send_command(':FETCH?')
        
    def initiate_continuous(self, enabled: bool):
        self.send_command(f':INIT:CONT {int(enabled)}')
        
    def wait(self):
        while not self.adapter.query_srq():
            sleep(0.1)
            