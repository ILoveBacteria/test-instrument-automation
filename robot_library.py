import redis
import json
import functools


class BaseLibrary:
    NAME: str = None
    
    def __init__(self):
        self.measure_type_status = 'unknown'
        self.measure_unit_status = 'unknown'
        self._r = None
        try:
            self._r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.publish(self.publish_format(0.0))
        except Exception as e:
            print(e)

    def publish(self, event: dict):
        self._r.publish('robot_events', json.dumps(event))
        
    def publish_format(self, result: float) -> dict:
        return {
            'type': 'data', 
            'owner': self.NAME, 
            'data': result, 
            'measure_type_status': self.measure_type_status,
            'measure_unit_status': self.measure_unit_status,
            }
    
    
def publish_result(func):
    @functools.wraps(func)
    def wrapper(self: BaseLibrary, *args, **kwargs):
        result = func(self, *args, **kwargs)
        # publish to Redis
        if self._r:
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