from typing import Optional
from protocol import CacheProtocol


class InMemoryCache:
    def __init__(self) -> None:
        self._cache = {}

    def get(self, key: str) -> Optional[int]:
        try:
            return self._cache[key]
        except KeyError:
            return None

    def set(self, key: str, value: int):
        self._cache[key] = value

        return value

    def incr(self, key: str):
        value = self.get(key)

        if value is None:
            return None

        return self.set(key, value + 1)

    def decr(self, key: str):
        value = self.get(key)

        if value is None:
            return None

        return self.set(key, value - 1)

    def execute_payload(self, payload: dict) -> dict:
        operation = payload["op"]
        key = payload["key"]

        match operation:
            case "GET":
                value = self.get(key)

                if value is None:
                    return CacheProtocol.make_error("invalid key")

                return CacheProtocol.make_response("ok", value)
            case "SET":
                value = payload["value"]

                if value is None or value == "":
                    return CacheProtocol.make_error("invalid or missing value")

                self.set(key, value)

                return CacheProtocol.make_response("ok", value)
            case "INCR":
                value = self.incr(key)

                if value is None:
                    return CacheProtocol.make_error("invalid key")

                return CacheProtocol.make_response("ok", value)
            case "DECR":
                value = self.decr(key)

                if value is None:
                    return CacheProtocol.make_error("invalid key")

                return CacheProtocol.make_response("ok", value)
            case _:
                return CacheProtocol.make_error("invalid operation")
