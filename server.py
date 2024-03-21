import socketserver


class UDPServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("received request:")
        print("data: " + str(data, "utf-8"))
        print("socker object: " + str(socket))
        # TODO: Call function in main bot code


def main():
    with socketserver.UDPServer(("127.0.0.1", 9999), UDPServerHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
