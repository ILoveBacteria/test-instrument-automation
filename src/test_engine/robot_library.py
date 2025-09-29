import os
import redis
import json
import functools

from robot.api.deco import library


@library(scope='GLOBAL', auto_keywords=True)
class BaseLibrary:
    NAME: str = 'unknown_device'
    CHANNELS = None
    FIELDS = None
    PRIORITY = 1
    
    def __init__(self):
        self.measure_type_status = 'unknown'
        self.measure_unit_status = 'unknown'
        self.connected = False
        self._r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=os.getenv('REDIS_PORT', 6379), decode_responses=True)
        try:
            self._r.ping()
            self.connected = True
        except redis.ConnectionError:
            print(f"Could not connect to Redis")
        self._publish(self._publish_format(0.0))

    def _publish(self, channels: list):
        event = {'type': 'data', 'priority': self.PRIORITY, 'status': 'OK', 'owner': self.NAME}
        event['data'] = channels
        if self.connected:
            self._r.publish('robot_events', json.dumps(event))
        
    def _publish_format(self, result: float) -> list:
        return  [
                [{'value': result, 'value_type': self.measure_type_status, 'value_unit': self.measure_unit_status}],    
            ]
    
    def open_connection(self, address: int, **kwargs):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def close_connection(self):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    
def publish_result(func):
    @functools.wraps(func)
    def wrapper(self: BaseLibrary, *args, **kwargs):
        result = func(self, *args, **kwargs)
        # publish to Redis
        if self.connected:
            self._publish(self._publish_format(result))
        return result
    return wrapper


def publish_status(func):
    @functools.wraps(func)
    def wrapper(self: BaseLibrary, *args, **kwargs):
        result = func(self, *args, **kwargs)
        status = [[] for _ in range(self.CHANNELS)]
        for ch in range(self.CHANNELS):
            channel_obj = getattr(self.device, f'ch{ch+1}')
            status[ch].append({
                'value': channel_obj.frequency,
                'value_type': 'frequency',
                'value_unit': 'Hz'
            })
            status[ch].append({
                'value': channel_obj.amplitude,
                'value_type': 'amplitude',
                'value_unit': 'Vpp'
            })
            status[ch].append({
                'value': channel_obj.shape,
                'value_type': 'shape',
                'value_unit': '-'
            })

        if self.connected:
            self._publish(status)
        return result
    return wrapper


def measure(type: str, unit: str):
    """
    Args:
        type (str): What the device is measuring? (e.g frequency, voltage)
        unit (str): The unit of the data (e.g Hz, Volt)
    """
    def inner(func):
        @functools.wraps(func)
        def wrapper(self: BaseLibrary, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.measure_type_status = type.lower()
            self.measure_unit_status = unit.lower()
            return result
        return wrapper
    return inner