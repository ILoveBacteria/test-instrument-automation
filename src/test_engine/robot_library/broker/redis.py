import os
import redis
import json
import time
from redis.commands.json.path import Path


class RedisBroker:
    _instance = None

    def __new__(cls, host=os.getenv('REDIS_HOST', 'localhost'), port=os.getenv('REDIS_PORT', 6379)):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_redis_connection(host, port)
        return cls._instance

    def _init_redis_connection(self, host, port):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)
        self.r.ping()

    def store_device(self, device_name: str, window: int,
                    fixed_status: dict = None, active: dict = None, alert=None):
        """
        Create or overwrite device JSON with fixed_status (dict) and active measurement (dict).
        active should be: {"name": "...", "value": <>, "unit": "...", "ts": <>}
        """
        now = int(time.time())
        fixed_status = fixed_status or {}
        active = active or {}

        data = {
            "window": window,
            "alert": alert,
            "timestamp": now,
            "fixed_status": fixed_status,
            "active": active,
        }

        key = f"device:{device_name}"
        self.r.json().set(key, Path.root_path(), data)
        self.r.sadd("devices", device_name)
        return True

    # -------------------------
    def set_active_measurement(self, device_name: str, name: str, value, unit=None, publish=True):
        """
        Set or replace the active measurement object and optionally publish an event.
        """
        ts = int(time.time())
        active_obj = {"name": name, "value": value, "unit": unit, "ts": ts}
        key = f"device:{device_name}"
        self.r.json().set(key, "$.active", active_obj)

        if publish:
            event = {
                "device": device_name,
                "event": "active_set",
                "name": name,
                "value": value,
                "unit": unit,
                "ts": ts,
            }
            self.r.publish(f"device_updates:{device_name}", json.dumps(event))
        return True

    # -------------------------
    def update_active_value(self, device_name: str, value, unit=None, publish=True):
        """
        Update only the value (and optionally unit) of the current active measurement.
        If you don't pass unit, the existing unit is preserved.
        This fetches $.active.name to include it in the published event.
        """
        key = f"device:{device_name}"
        ts = int(time.time())

        # Update value and ts
        self.r.json().set(key, "$.active.value", value)
        self.r.json().set(key, "$.active.ts", ts)

        # Optionally update unit
        if unit is not None:
            self.r.json().set(key, "$.active.unit", unit)

        if publish:
            # read the active.name so we can include it in the event
            active_name = self.r.json().get(key, "$.active.name")
            # RedisJSON returns [name] when using path root style; normalize:
            if isinstance(active_name, list) and len(active_name) > 0:
                active_name = active_name[0]
            event = {
                "device": device_name,
                "event": "measurement_update",
                "name": active_name,
                "value": value,
                "unit": unit,
                "ts": ts,
            }
            self.r.publish(f"device_updates:{device_name}", json.dumps(event))
        return True

    # -------------------------
    def update_fixed_status(self, device_name: str, field: str, value):
        """
        Update a fixed_status entry under $.fixed_status.<field>. Example: heartbeat, connection.
        """
        ts = int(time.time())
        obj = {"value": value, "ts": ts}
        key = f"device:{device_name}"
        path = f"$.fixed_status.{field}"
        self.r.json().set(key, path, obj)
        return True

    # -------------------------
    def set_heartbeat(self, device_name: str, ttl: int = 30):
        """
        Set ephemeral heartbeat:<device> with TTL and also update fixed_status.heartbeat timestamp.
        """
        hb_key = f"heartbeat:{device_name}"
        self.r.set(hb_key, "1", ex=ttl)
        # update fixed_status.heartbeat value=timestamp
        ts = int(time.time())
        self.r.json().set(f"device:{device_name}", "$.fixed_status.heartbeat", {"value": ts, "ts": ts})
        return True

    # -------------------------
    def clear_status(self, device_name: str):
        """
        Clear both fixed_status and active (no publish).
        """
        key = f"device:{device_name}"
        self.r.json().set(key, "$.fixed_status", {})
        self.r.json().set(key, "$.active", {})
        print(f"[RedisBroker] Cleared status for {device_name}")
        return True