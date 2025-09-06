import can


class CANAdapter:
    """
    Singleton CAN adapter class.
    Only one instance of CANAdapter will exist at any time.
    Repeated instantiations will return the same object.
    To reinitialize with new parameters, call shutdown() first.
    """
    _instance = None

    def __new__(cls, channel: str, bitrate: int):
        if cls._instance is None:
            cls._instance = super(CANAdapter, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, channel: str, bitrate: int):
        if self._initialized:
            return
        self.bus = can.Bus(channel,
                           interface='remote',
                           bitrate=bitrate,
                           receive_own_messages=True)
        self._initialized = True

    def send_message(self, message_id: int, data: bytes):
        self.bus.send(can.Message(arbitration_id=message_id, data=data, is_extended_id=False))

    def shutdown(self):
        self.bus.shutdown()
        CANAdapter._instance = None
        self._initialized = False

    def __del__(self):
        self.shutdown()
