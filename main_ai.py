import sys
import time
from math import sqrt
from threading import Thread
from client import UDPClient
from main import Main

Point = tuple[int, int]
TeamColors = ["Blue", "Yellow"]


class MainAI:
    MAX_DISTANCE_TRAVEL = sqrt(2775 ** 2 + 1775 ** 2)

    def __init__(self, color):
        self.oldLoc = None
        self.color = color
        self.client = UDPClient("127.0.0.1", "9999")  # TODO Replace with IP of Raspberry Pi
        self.client.sock.sendto(b'', ("0.0.0.0", 1234))  # send random data so that we can get the port number of the socket
        self.main_class = Main(color)
        self.main_thread = Thread(target=self.main_class.start)
        self.main_thread.start()
        self.numPlantsInReservedPlanter = 0
        print(self.client.sock)

    def pickUpPlant(self) -> str:
        self.client.send("pickup-plant")
        return self.client.receive()

    def placePlant(self):
        self.client.send("place-plant")
        self.client.receive()

    def moveBotToLoc(self, loc: Point) -> None:
        while distance(loc, self.getBotLocations()) >= 150:  # Continue calculating paths until we are close enough to point
            try:
                self.main_class.navigate_robot(loc)
                angleFrom, path = self.main_class.angle_and_path
                if self.oldLoc != path[1]:  # only send new path once a new waypoint is given
                    self.oldLoc = path[1]
                    if len(path) == 2:
                        endSpeed = 0
                    else:
                        # Map distance to 0-255 value
                        endSpeed = round((distance(path[0], path[1]) / distance(path[1], path[2])) * (255/self.MAX_DISTANCE_TRAVEL))
                    self.client.send(f"moveToLoc {str(path[0]).replace(' ', '')} {str(path[1]).replace(' ', '')} {angleFrom} {endSpeed}")
            except Exception:
                self.client.send("stop-moving")

    def orientSolarPanels(self, overide_move):
        # TODO: call Solar Panel class and use moveBotToLoc
        pass

    def openingPhase(self):
        self.client.send("openingPhase")
        self.client.receive()

    def moveBackToHome(self):
        # Plan is to start is our reserved area (at least for now), so go to area with least number of plants
        if len(self.main_class.data_analiser.plants[1 + TeamColors.index(self.color)]) < len(self.main_class.data_analiser.plants[3 + TeamColors.index(self.color)]):
            # TODO: pre-determine some location where bot is partially inside area
            self.main_class.navigate_robot(self.main_class.data_analiser.plants[1 + TeamColors.index(self.color)][0])
        else:
            # TODO: same as above
            self.main_class.navigate_robot(self.main_class.data_analiser.plants[3 + TeamColors.index(self.color)][0])

        self.moveBotToLoc(self.main_class.path)

    def getAvailablePlants(self):
        while self.main_class.data_analiser.plants == [0, 0, 0, 0, 0, 0, 0]:
            pass
        return self.main_class.data_analiser.plants[0]

    def getBotLocations(self):
        our_bot, opponent_corners = self.main_class.main_navigation.detect_robots(self.main_class.img)
        if opponent_corners:
            tl, _, br, _ = opponent_corners[0]
            cX = int((tl[0] + br[0]) / 2.0)
            cY = int((tl[1] + br[1]) / 2.0)
            opponent_corners = [cX, cY]
        return our_bot[0], opponent_corners

    def getOurReservedPlants(self):
        return self.main_class.data_analiser.plants[5 + TeamColors.index(self.color)]

    def nextPlaceToPlant(self, plantType) -> Point:
        pass


def distance(node1: Point, node2: Point) -> float:
    x1, y1 = node1 if node1 else (0, 0)
    x2, y2 = node2
    return sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))


def nextPlantToGoTo(plants, main_bot_location, enemy_bot_location):
    smallestDistance = distance(main_bot_location, plants[0]) - distance(enemy_bot_location, plants[0])
    smallestIndex = 0
    for i, plant in enumerate(plants[1:]):
        distanceCompare = distance(plant, main_bot_location) - distance(plant, enemy_bot_location)
        if distanceCompare < smallestDistance:
            smallestDistance = distanceCompare
            smallestIndex = i

    return plants[smallestIndex]


def main():
    try:
        color = sys.argv[1]
    except IndexError:
        print("Inputted team color is required.")
        return

    if color not in TeamColors:
        print("Inputted team color must be Yellow or Blue.")
        return

    ai = MainAI(color)

    print("Ready to begin.")

    # Wait for the pulling of cord
    while ai.client.receive() != "go\n":
        pass

    # BEGIN THE GAME
    startTime = time.time()
    print("GO")
    ai.openingPhase()
    while time.time() - startTime < 85:  # run beginning strategy until last 15 seconds
        plants: list[Point] = ai.getAvailablePlants()
        main_bot_location, enemy_bot_location = ai.getBotLocations()
        if not main_bot_location:
            continue
        if not plants:
            ai.orientSolarPanels(False)
            plants = ai.getOurReservedPlants()

        nextPlant = nextPlantToGoTo(plants, main_bot_location, enemy_bot_location)
        ai.moveBotToLoc(nextPlant)
        plantType = ai.pickUpPlant()

        # Decide where to place plant
        placeToPlant = ai.nextPlaceToPlant(plantType)

        # Go to planting area and place plant
        ai.moveBotToLoc(placeToPlant)
        ai.placePlant()  # guaranteed to place without error unless emergency stop button is pressed

    # Last 15 seconds now
    ai.orientSolarPanels(True)


if __name__ == "__main__":
    main()
