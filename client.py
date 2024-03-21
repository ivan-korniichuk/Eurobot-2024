import socket
from typing import Any


class UDPClient:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port

    def send(self, data: Any):
        self.sock.sendto(bytes(data + "\n", "utf-8"), (self.host, self.port))

    def receive(self) -> str:
        return str(self.sock.recv(1024), "utf-8")
