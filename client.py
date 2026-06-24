import socket
from protocol import CacheProtocol


class ClientSocketManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def __enter__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((self.host, self.port))
            self.sock = sock
            return self.sock
        except:
            sock.close()
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.sock is not None:
            self.sock.close()


def main():
    with ClientSocketManager(host="localhost", port=8080) as client_socket:
        while True:
            prompt = input("poor_redis>_ ")

            # Parse prompt
            tokens = prompt.strip().split()

            operation = tokens[0]
            key = tokens[1]
            value = None

            if len(tokens) == 3:
                value = int(tokens[2])

            payload_dict = CacheProtocol.make_request(operation.upper(), key, value)
            payload_bytes = CacheProtocol.encode(payload_dict)
            CacheProtocol.write_socket(client_socket, payload_bytes)

            response_bytes = CacheProtocol.read_socket(client_socket)
            response_dict = CacheProtocol.decode(response_bytes)

            print(response_dict)


if __name__ == "__main__":
    main()
