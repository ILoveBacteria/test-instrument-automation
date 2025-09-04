# https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-version-3
import json
import redis


class RobotRedisListener:
    ROBOT_LISTENER_API_VERSION = 3
    
    def __init__(self, host='localhost', port=6379, channel='robot_events'):
        # uri passed by robot: e.g. --listener robot_event_listener.py:localhost:6379
        self.host = host
        self.port = port
        self.channel = channel
        self.connected = False
        self._r = redis.Redis(host=self.host, port=self.port, decode_responses=True)
        try:
            self._r.ping()
            self.connected = True
        except redis.ConnectionError:
            print(f"Could not connect to Redis at {self.host}:{self.port}")

    def _pub(self, event: dict):
        print(event)
        if self.connected:
            self._r.publish(self.channel, json.dumps(event))

    def start_suite(self, data, result):
        result = result.to_dict()
        self._pub({'lineno': -1, 'type': 'suite', 'action': 'start', 'name': result['name'], 'status': result['status'], 'start_time': result['start_time'], 'elapsed_time': result['elapsed_time']})

    def end_suite(self, data, result):
        result = result.to_dict()
        self._pub({'lineno': -1, 'type': 'suite', 'action': 'end', 'name': result['name'], 'status': result['status'], 'start_time': result['start_time'], 'elapsed_time': result['elapsed_time']})

    def start_keyword(self, data, result):
        result = result.to_dict()
        self._pub({'lineno': data.lineno, 'type': 'keyword', 'action': 'start', 'name': result['name'], 'status': result['status'], 'start_time': result['start_time'], 'elapsed_time': result['elapsed_time']})

    def end_keyword(self, data, result):
        result = result.to_dict()
        self._pub({'lineno': data.lineno, 'type': 'keyword', 'action': 'end', 'name': result['name'], 'status': result['status'], 'start_time': result['start_time'], 'elapsed_time': result['elapsed_time']})
