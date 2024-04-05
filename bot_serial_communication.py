import subprocess
from math import atan2, pi
import serial
Point = tuple[int, int]


class MainBotSerialCommunication:  # TODO: To be updated as needed
    def __init__(self):
        device1 = serial.Serial("/dev/ttyUSB0", 115200)
        device2 = serial.Serial("/dev/ttyUSB1", 115200)
        device1.write(b'type')
        if device1.read() == 1:
            self.locomotion = device1
            self.arm = device2
        else:
            self.locomotion = device2
            self.arm = device1

    def moveArm(self, x: int, y: int, z: int):  # x, y, and z will be in cm
        byte_val = (1 << 24) + (x << 16) + (y << 8) + z
        self.arm.write(byte_val.to_bytes(4, signed=False))
        self.arm.read()

    def closeArm(self):
        self.arm.write(0)
        self.arm.read()

    def moveBot(self, start: Point, end: Point, angle_from, end_speed):
        angle_to = int((pi + atan2(start[1] - end[1], start[0] - end[0])) * 100)
        angle_from = int((angle_from + pi) * 100)
        byte_val = (start[0] << 88) + (start[1] << 72) + (end[0] << 56) + (end[1] << 40) + (angle_from << 24) + (angle_to << 8) + end_speed
        self.locomotion.write(byte_val.to_bytes(13, signed=False))


