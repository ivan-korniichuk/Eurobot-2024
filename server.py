import socketserver
import socket
import sys
from main_robot import MainRobot

main_robot = MainRobot()


class UDPServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        if self.client_address[0] != sys.argv[1]:
            print("did not receive data from laptop...")
            return
        data = self.request[0].strip()
        returnAddr = self.request[1]
        print("received request:")
        print("data: " + str(data, "utf-8"))
        print("socker object: " + str(returnAddr))
        parsed_data = str(data, "utf-8").split(" ")
        match parsed_data[0]:
            case "openingPhase":
                returnVal = main_robot.openingPhase()
            case "pickup-plant":
                returnVal = main_robot.pickUpPlant()
            case "place-plant":
                returnVal = main_robot.placePlant()
            case "moveToLoc":
                returnVal = main_robot.moveToLoc(parsed_data)
            case "solar-panels":
                returnVal = main_robot.solarPanels()
            case _:
                returnVal = None
        if returnVal is not None:
            returnAddr.sendto(returnVal, self.client_address)


def get_ip():
    a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    a.connect(("1.1.1.1", 1))
    return a.getsockname()[0]


def main():
    try:
        sys.argv[1]
    except IndexError:
        print("no remote computer address supplied.")
        return
    with socketserver.UDPServer((get_ip(), 9999), UDPServerHandler) as server:
        print("server listening on", get_ip(), "with port 9999")
        server.serve_forever()


if __name__ == "__main__":
    main()
