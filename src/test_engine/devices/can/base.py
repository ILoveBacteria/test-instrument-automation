import os
from collections.abc import Callable

import canopen
from canopen.pdo.base import PdoMap

from adapters.can import CANAdapter


class CANBase:
    NODE_ID = None

    def __init__(self):
        self.adapter = CANAdapter(os.getenv('CANOPEN_HOST', 'ws://192.168.1.102:54701/'))
        self.node = canopen.RemoteNode(self.NODE_ID, 'DS301_profile.eds')
        self.adapter.network.add_node(self.node)
        
    def add_heartbeat_callback(self, callback: Callable[['CANBase', int], None]):
        self.node.nmt.add_heartbeat_callback(lambda state: callback(self, state))
        
    def add_pdo_callback(self, pdo_number: int, callback: Callable[['CANBase', PdoMap], None]):
        self.node.tpdo.read()
        self.node.tpdo[pdo_number].add_callback(lambda message: callback(self, message))
        
    # def write(self, data: bytes):
    #     if self.MESSAGE_ID is None:
    #         raise NotImplementedError("MESSAGE_ID must be defined in subclass")
    #     self.adapter.send_message(self.MESSAGE_ID, data)