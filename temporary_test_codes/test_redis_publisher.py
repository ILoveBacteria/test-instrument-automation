import redis
import json
import time
import random

# --- Configuration ---
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_CHANNEL = 'robot_events'

# --- Test Scenario Steps ---
TEST_STEPS = [
    # Suite 1: DC Voltage Check
    {'type': 'suite', 'action': 'start', 'name': 'DC Voltage Check on HP3458A', 'status': 'RUNNING'},
    {'type': 'keyword', 'action': 'start', 'name': 'Configure HP3458A for DCV', 'status': 'RUNNING'},
    {'type': 'keyword', 'action': 'end', 'name': 'Configure HP3458A for DCV', 'status': 'PASS'},
    {'type': 'keyword', 'action': 'start', 'name': 'Measure DC Voltage', 'status': 'RUNNING'},
    {'type': 'data', 'owner': 'HP3458A', 'data': round(5.0 + random.uniform(-0.05, 0.05), 4)},
    {'type': 'keyword', 'action': 'end', 'name': 'Measure DC Voltage', 'status': 'PASS'},
    {'type': 'suite', 'action': 'end', 'name': 'DC Voltage Check on HP3458A', 'status': 'PASS'},
    
    # Suite 2: Frequency Measurement with Failure
    {'type': 'suite', 'action': 'start', 'name': 'Frequency Measurement on HP53131A', 'status': 'RUNNING'},
    {'type': 'keyword', 'action': 'start', 'name': 'Configure HP53131A for Frequency', 'status': 'RUNNING'},
    {'type': 'keyword', 'action': 'end', 'name': 'Configure HP53131A for Frequency', 'status': 'PASS'},
    {'type': 'keyword', 'action': 'start', 'name': 'Measure Frequency', 'status': 'RUNNING'},
    {'type': 'data', 'owner': 'HP53131A', 'data': round(10_000_000 + random.uniform(-100, 100), 2)},
    time.sleep(1),
    {'type': 'data', 'owner': 'HP53131A', 'data': round(10_000_000 + random.uniform(-100, 100), 2)},
    {'type': 'keyword', 'action': 'end', 'name': 'Measure Frequency', 'status': 'PASS'},
    {'type': 'keyword', 'action': 'start', 'name': 'Validate Frequency Stability on HP53131A', 'status': 'RUNNING'},
    {'type': 'data', 'owner': 'HP53131A', 'data': round(9_800_000 + random.uniform(-100, 100), 2)},
    {'type': 'keyword', 'action': 'end', 'name': 'Validate Frequency Stability on HP53131A', 'status': 'FAIL'},
    {'type': 'suite', 'action': 'end', 'name': 'Frequency Measurement on HP53131A', 'status': 'FAIL'},

    # Suite 3: Noise Figure check
    {'type': 'suite', 'action': 'start', 'name': 'Noise Figure Check on HP8970B', 'status': 'RUNNING'},
    {'type': 'keyword', 'action': 'start', 'name': 'Measure Noise Figure', 'status': 'RUNNING'},
    {'type': 'data', 'owner': 'HP8970B', 'data': random.uniform(-0.2, 10.0)},
    {'type': 'keyword', 'action': 'end', 'name': 'Measure Noise Figure', 'status': 'PASS'},
    {'type': 'suite', 'action': 'end', 'name': 'Noise Figure Check on HP8970B', 'status': 'PASS'},

    # Suite 4: S-Parameter check
    {'type': 'suite', 'action': 'start', 'name': 'S-Parameter Check on HP8510C', 'status': 'RUNNING'},
    {'type': 'keyword', 'action': 'start', 'name': 'Measure S21', 'status': 'RUNNING'},
    {'type': 'data', 'owner': 'HP8510C', 'data': random.uniform(-0.2, 10.0)},
    {'type': 'keyword', 'action': 'end', 'name': 'Measure S21', 'status': 'PASS'},
    {'type': 'suite', 'action': 'end', 'name': 'S-Parameter Check on HP8510C', 'status': 'PASS'},
]


def main():
    """Connects to Redis and publishes test data indefinitely."""
    print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}...")
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        print(f"Successfully connected. Publishing to channel '{REDIS_CHANNEL}'.")
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        return

    while True:
        print("\n--- Starting new test run ---")
        for step in TEST_STEPS:
            if isinstance(step, dict):
                payload = json.dumps(step)
                print(f"Publishing: {payload}")
                r.publish(REDIS_CHANNEL, payload)
                time.sleep(0.1)
            else:
                step

        print("\n--- Test run finished. Restarting in 10 seconds... ---")
        time.sleep(3)


if __name__ == "__main__":
    main()

