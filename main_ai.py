import sys
import time
from math import sqrt
from client import UDPClient


Point = tuple[int, int]


class MainAI:
    def __init__(self, color):
        self.color = color
        self.client = UDPClient("127.0.0.1", "9999")  # TODO Replace with IP of Raspberry Pi
        self.client.sock.sendto(b'', ("0.0.0.0", 1234))  # send random data so that we can get the port number of the socket
        print(self.client.sock)

    def pickUpPlant(self) -> str:
        self.client.send("pickup-plant")
        return self.client.receive()

    def placePlant(self):
        self.client.send("place-plant")
        self.client.receive()

    def moveBotToLoc(self, loc):
        # TODO: Call Pathfinding to create path
        pass

    def orientSolarPanels(self):
        # TODO: call Solar Panel class and use moveBotToLoc
        pass

    def openingPhase(self):
        # TODO: call moveBotToLoc to either push all plants to a corner or knock over all plants
        pass

    def moveBackToHome(self):
        # TODO: call moveBotToLoc to send to charging station
        pass


def distance(node1: Point, node2: Point) -> float:
    x1, y1 = node1
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

    if color not in ['Yellow', 'Blue']:
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
    while startTime - time.time() < 90:  # run beginning strategy until last 10 seconds
        plants: list[Point] = getAvailablePlants()
        main_bot_location: Point = getMainBotLocation()
        enemy_bot_location: Point = getEnemyBotLocation()
        if len(plants) == 0:
            ai.orientSolarPanels()
            plants = getOurReservedPlants()

        nextPlant = nextPlantToGoTo(plants, main_bot_location, enemy_bot_location)
        ai.moveBotToLoc(nextPlant)
        plantType = ai.pickUpPlant()

        # Decide where to place plant
        placeToPlant = nextPlaceToPlant(plantType)

        # Go to planting area and place plant
        ai.moveBotToLoc(placeToPlant)
        ai.placePlant()  # guaranteed to place without error unless emergency stop button is pressed

    # Last 10 seconds now
    # TODO: write last 10 seconds code


if __name__ == "__main__":
    main()
