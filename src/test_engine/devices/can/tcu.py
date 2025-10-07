from typing import Literal
from devices.can.base import CANBase


class TCU(CANBase):
    NODE_ID = None

    def __init__(self):
        super().__init__()

    def tcustmon(self):
        pass
        
    def tcuint(self, enable: bool):
        pass

    def tcuflow(self, enable: bool):
        pass
    
    def tcuen(self, mode: Literal['G', 'C']):
        pass