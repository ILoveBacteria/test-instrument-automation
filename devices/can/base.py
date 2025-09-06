from adapters.can import CANAdapter


class CANBase:
    MESSAGE_ID = None

    def __init__(self, channel: str, bitrate: int):
        self.adapter = CANAdapter(channel, bitrate)
        
    def write(self, data: bytes):
        if self.MESSAGE_ID is None:
            raise NotImplementedError("MESSAGE_ID must be defined in subclass")
        self.adapter.send_message(self.MESSAGE_ID, data)