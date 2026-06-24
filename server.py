import socket
import selectors
from protocol import CacheProtocol, ProtocolError
from cache import InMemoryCache

selector = selectors.DefaultSelector()
SERVER_SOCKET_KEY = object()

CACHE = InMemoryCache()


class ServerSocketManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def __enter__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.setblocking(False)
            sock.bind((self.host, self.port))
            sock.listen()

            self.sock = sock
            return sock
        except:
            sock.close()
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.sock is not None:
            self.sock.close()


def handle_connection(key, mask):
    sock = key.fileobj

    try:
        if mask & selectors.EVENT_READ:
            payload_bytes = CacheProtocol.read_socket(sock)
            payload = CacheProtocol.decode(payload_bytes)

            response = CACHE.execute_payload(payload)
            selector.modify(sock, selectors.EVENT_WRITE, data=response)

        if mask & selectors.EVENT_WRITE:
            data = key.data
            payload_bytes = CacheProtocol.encode(data)
            CacheProtocol.write_socket(sock, payload_bytes)
            selector.modify(sock, selectors.EVENT_READ, data=None)
    except Exception:
        selector.unregister(sock)
        sock.close()


def main():
    with ServerSocketManager(host="localhost", port=8080) as server_socket:
        # Register server socket
        selector.register(server_socket, selectors.EVENT_READ, data=SERVER_SOCKET_KEY)
        print("PoorRedis v0.0.1")

        while True:
            events = selector.select(timeout=1.0)

            for key, mask in events:
                if key.data is SERVER_SOCKET_KEY:
                    client_conn, client_addr = server_socket.accept()
                    print(f"Accepted connection from {client_addr}")

                    client_conn.setblocking(False)
                    selector.register(
                        client_conn,
                        selectors.EVENT_READ,
                        data={"addr": client_addr, "inb": b"", "outb": b""},
                    )

                else:
                    # Handle connection
                    handle_connection(key, mask)


if __name__ == "__main__":
    main()
