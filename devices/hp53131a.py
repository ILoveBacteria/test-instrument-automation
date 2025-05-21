from devices.base import Instrument


class HP53131A(Instrument):
    def setup(self):
        super().setup()
        
    def id(self):
        return self.query('*IDN?')

    def reset(self):
        self.send_command('*RST')