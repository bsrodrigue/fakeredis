import json
import socket
import struct
from typing import Optional


class ProtocolError(Exception):
    """ProtocolError"""


class CacheProtocol:
    @staticmethod
    def make_request(operation: str, key: str, value: Optional[int] = None):
        if operation not in ("GET", "SET", "INCR", "DECR"):
            raise ProtocolError("Invalid Operation")

        if key == "":
            raise ProtocolError("Invalid or missing Key")

        if operation in ("SET",) and not value:
            raise ProtocolError("Missing value")

        payload = {"op": operation, "key": key}

        if value:
            payload["value"] = str(value)

        return payload

    @staticmethod
    def make_response(status: str, value: int):
        return {"status": status, "value": value}

    @staticmethod
    def make_error(error: str):
        return {"status": "error", "error": error}

    @staticmethod
    def encode(payload: dict):
        payload_str = json.dumps(payload)
        payload_bin = payload_str.encode()
        length_prefix = struct.pack("!I", len(payload_bin))

        return length_prefix + payload_bin

    @staticmethod
    def decode(payload_bytes: bytes):
        payload_str = payload_bytes.decode()
        payload_dict = json.loads(payload_str)

        return payload_dict

    @staticmethod
    def write_socket(sock: socket.socket, msg_bin: bytes):
        sock.sendall(msg_bin)

    @staticmethod
    def read_socket(sock: socket.socket):
        raw_length = b""
        while len(raw_length) < 4:
            chunk = sock.recv(4 - len(raw_length))

            if not chunk:
                if not raw_length:
                    raise ProtocolError("Connection closed")
                raise ProtocolError("Incomplete length data")
            raw_length += chunk

        payload_len = struct.unpack("!I", raw_length)[0]

        payload_data = b""

        while len(payload_data) < payload_len:
            chunk = sock.recv(payload_len - len(payload_data))

            if not chunk:
                if not payload_data:
                    raise ProtocolError("Connection closed")
                raise ProtocolError("Incomplete payload data")
            payload_data += chunk

        return payload_data
