import sys
from math import sqrt
from client import UDPClient


Point = tuple[int, int]


class MainAI:
    def __init__(self, color):
        self.color = color
        self.client = UDPClient("127.0.0.1", "9999")  # TODO Replace with IP of Raspberry Pi

    def pickUpPlant(self):
        self.client.send("pickup-plant")
        self.client.receive()

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


def nextPlantToGoTo(plants, main_bot_location):
    smallestDistance = distance(main_bot_location, plants[0])
    smallestIndex = 0
    for i, plant in enumerate(plants[1:]):
        if distance(plant, main_bot_location) < smallestDistance:
            smallestDistance = distance(plant, main_bot_location)
            smallestIndex = i
        if distance(plant, main_bot_location) == smallestDistance:  # if the distances are same, use plant furthest from opponent
            enemyBot = getEnemyBotLocation()
            if distance(plant, enemyBot) > distance(plants[smallestIndex], enemyBot):
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

    # BEGIN THE GAME
    ai.openingPhase()
    while True:
        # TODO: Incomplete Code, will develop a detailed strategy with all or most possible outcomes
        plants: list[Point] = getAvailablePlants()
        main_bot_location: Point = getMainBotLocation()
        nextPlant = nextPlantToGoTo(plants, main_bot_location)
        ai.moveBotToLoc(nextPlant)
        ai.pickUpPlant()

        # Decide where to place plant
        # ig place into a planter but im not 100% sure
        ai.moveBotToLoc(reservedPlanter)
        if not ai.placePlant():
            ai.moveBotToLoc(otherPlanter)
            ai.placePlant()
