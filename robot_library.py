import redis
import json
import functools


class BaseLibrary:
    NAME: str = None
    
    def __init__(self):
        self._r = None
        try:
            self._r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        except Exception as e:
            print(e)

    def publish(self, event: dict):
        self._r.publish('robot_events', json.dumps(event))
    
    
def publish_result(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        # publish to Redis
        if self._r:
            self.publish({'type': 'data', 'owner': self.NAME, 'data': result})
        return result
    return wrapper
