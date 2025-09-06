from typing import Literal
from devices.can.base import CANBase


class TCU(CANBase):
    MESSAGE_ID = 0x032

    def __init__(self, channel: str, bitrate: int = 500_000):
        super().__init__(channel, bitrate)

    def tcustmon(self):
        byte0, byte1 = 0x1, 0x0
        self.write(bytes([byte0, byte1]))
        
    def tcuint(self, enable: bool):
        byte0 = 0x2
        byte1 = 0xAA if enable else 0xBB
        self.write(bytes([byte0, byte1]))

    def tcuflow(self, enable: bool):
        byte0 = 0x3
        byte1 = 0xAA if enable else 0xBB
        self.write(bytes([byte0, byte1]))

    def tcuen(self, mode: Literal['G', 'C']):
        byte0 = 0x4
        byte1 = 0xAA if mode == 'G' else 0xBB
        self.write(bytes([byte0, byte1]))