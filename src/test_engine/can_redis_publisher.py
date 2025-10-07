import json
import os
import time

import canopen
from canopen.nmt import NMT_STATES
from canopen.node.base import BaseNode
from canopen.pdo.base import PdoMap
import redis


connected = False
r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=os.getenv('REDIS_PORT', 6379), decode_responses=True)
try:
    r.ping()
    connected = True
except redis.ConnectionError:
    print(f"Could not connect to Redis")


def heartbeat_publisher(node: BaseNode):
    def wrapper(state: int):
        if not connected:
            return
        message = {
            'type': 'heartbeat',
            'timestamp': node.nmt.timestamp,
            'state': NMT_STATES[state],
            'node_id': node.id,
        }
        r.publish('can', json.dumps(message))
    return wrapper


def pdo_publisher(message: PdoMap):
    if not connected:
        return
    variables = {v.name: v.raw for v in message}
    pdo_message = {
        'type': 'pdo',
        'timestamp': message.timestamp,
        'node_id': message.pdo_node.node.id,
        'variables': variables,
    }
    r.publish('can', json.dumps(pdo_message))


network = canopen.Network()
network.connect('ws://192.168.1.102:54701/', interface='remote')

node = canopen.RemoteNode(29, 'DS301_profile.eds')
network.add_node(node)

node.nmt.add_heartbeat_callback(heartbeat_publisher(node))
# Read the PDO configuration from the device
node.tpdo.read()
tpdo1 = node.tpdo[1]
tpdo1.add_callback(pdo_publisher)

time.sleep(10)

network.disconnect()