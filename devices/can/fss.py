from devices.can.base import CANBase


class FSS(CANBase):
    MESSAGE_ID = 0x064

    def __init__(self, channel: str, bitrate: int = 500_000):
        super().__init__(channel, bitrate)

    def c(self):
        byte0, byte1 = 0x1, 0xAA
        self.write(bytes([byte0, byte1]))
        
    def u(self):
        byte0, byte1 = 0x2, 0xAA
        self.write(bytes([byte0, byte1]))

    def r(self):
        byte0, byte1 = 0x3, 0xAA
        self.write(bytes([byte0, byte1]))
