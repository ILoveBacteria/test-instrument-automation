import redis
import json
import functools


class BaseLibrary:
    NAME: str = 'unknown_device'
    
    def __init__(self):
        self.measure_type_status = 'unknown'
        self.measure_unit_status = 'unknown'
        self.connected = False
        self._r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        try:
            self._r.ping()
            self.publish(self.publish_format(0.0))
            self.connected = True
        except redis.ConnectionError:
            print(f"Could not connect to Redis")

    def publish(self, event: dict):
        if self.connected:
            self._r.publish('robot_events', json.dumps(event))
        
    def publish_format(self, result: float) -> dict:
        return {
            'type': 'data', 
            'owner': self.NAME, 
            'data': [
                [{'value': result, 'value_type': self.measure_type_status, 'value_unit': self.measure_unit_status}],    
            ], 
        }
    
    def open_connection(self, resource, **kwargs):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def close_connection(self):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    
def publish_result(func):
    @functools.wraps(func)
    def wrapper(self: BaseLibrary, *args, **kwargs):
        result = func(self, *args, **kwargs)
        # publish to Redis
        if self.connected:
            self.publish(self.publish_format(result))
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