from bot_serial_communication import MainBotSerialCommunication


class MainRobot:
    # TODO: Add Liba's and other bot code here
    def __init__(self):
        self.serial_communicator = MainBotSerialCommunication()

    def moveToLoc(self, data: list[str]):
        startPointRaw = data[1][1:-1].split(",")
        endPointRaw = data[2][1:-1].split(",")
        angleFrom = int(data[3])
        endSpeed = int(data[4])
        startPoint = (int(startPointRaw[0]), int(startPointRaw[1]))
        endPoint = (int(endPointRaw[0]), int(endPointRaw[1]))
        self.serial_communicator.moveBot(startPoint, endPoint, angleFrom, endSpeed)

    def openingPhase(self):
        pass  # TODO

    def pickUpPlant(self):
        pass  # TODO

    def placePlant(self):
        pass  # TODO

    def solarPanels(self):
        pass  # TODO
