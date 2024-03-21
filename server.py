import socketserver
import socket
import sys


class UDPServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("received request:")
        print("data: " + str(data, "utf-8"))
        print("socker object: " + str(socket))
        # TODO: Call function in main bot code


def get_ip():
    a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    a.connect(("1.1.1.1", 1))
    return a.getsockname()[0]

def main():
    with socketserver.UDPServer((get_ip(), 9999), UDPServerHandler) as server:
        print("server listening on", get_ip(), "with port 9999")
        server.serve_forever()


if __name__ == "__main__":
    main()
