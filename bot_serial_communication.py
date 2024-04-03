from math import atan2, pi
import serial
Point = tuple[int, int]


class MainBotSerialCommunication:  # TODO: To be updated as needed
    def __init__(self):
        self.locomotion = serial.Serial('/dev/', 115200)  # TODO: Replace with correct ports
        self.arm = serial.Serial('/dev/', 115200)  # TODO: Replace with correct ports

    def moveArm(self, x: int, y: int, z: int):  # x, y, and z will be in cm
        byte_val = (x << 16) + (y << 8) + z
        self.arm.write(byte_val.to_bytes(3, signed=False))
        self.arm.read()

    def moveBot(self, start: Point, end: Point, angle_from, end_speed):
        angle_to = int((pi + atan2(start[1] - end[1], start[0] - end[0])) * 100)
        angle_from = int((angle_from + pi) * 100)
        byte_val = (start[0] << 88) + (start[1] << 72) + (end[0] << 56) + (end[1] << 40) + (angle_from << 24) + (angle_to << 8) + end_speed
        self.locomotion.write(byte_val.to_bytes(13, signed=False))


