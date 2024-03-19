import math
import cv2 as cv
import numpy as np

# Colours, BGR
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
GRAY = (220, 220, 220)
RED = (0, 0, 255)
PURPLE = (230, 20, 160)
BLACK = (0, 0, 0)

# RESERVED_AREA_B = [(0,0), (450,450)]
# RESERVED_AREA_Y = ((3000,2000), (2550, 1550))
# DROP_OFFS_Y = [[(2550,0), (3000,450)],[(0, 775), (450, 1225)]]
# DROP_OFFS_B = [[(0,1550), (450,2000)],[(2550, 775), (3000, 1225)]]
# SOLAR_PANELS_Y = [(), (), ()]
# SOLAR_PANELS_B = [(), (), ()]
# SOLAR_PANELS_G = [(), (), ()]
# SIMA_AREA_Y = [(1500, 0), (1950, 150)]
# SIMA_AREA_B = [(1050, 0), (1500, 150)]

class Visualiser:
    def __init__(self, reserved_area_b, reserved_area_y, drop_offs_b, drop_offs_y, sima_area_b, sima_area_y):
        self.reserved_area_b = reserved_area_b
        self.reserved_area_y = reserved_area_y
        self.drop_offs_b = drop_offs_b
        self.drop_offs_y = drop_offs_y
        self.sima_area_b = sima_area_b
        self.sima_area_y = sima_area_y

    def draw_plant(self, plant, color = GRAY):
        x, y = plant
        cv.circle(
            self.view,
            center=(x, y),
            radius= 50,
            color=color,
            thickness=5,
        )

    # delete, move to data_analyser
    def draw_rectangles (self, rectangles, color, thickness = 5):
        for area in rectangles:
            cv.rectangle(self.view, area[0], area[1], color, thickness)
    def draw_rectangle (self, rectangle, color, thickness = 5):
        cv.rectangle(self.view, rectangle[0], rectangle[1], color, thickness)
    
    def map_areas (self):
        self.draw_rectangle(self.reserved_area_y, YELLOW)
        self.draw_rectangle(self.reserved_area_b, BLUE)
        # BLUE DROP OFFS
        self.draw_rectangles(self.drop_offs_b, BLUE)
        # Y DROP OFFS
        self.draw_rectangles(self.drop_offs_y, YELLOW)
        self.draw_rectangle(self.sima_area_b, BLUE)
        self.draw_rectangle(self.sima_area_y, YELLOW)


    def update(self, img, plants):
        self.view = img
        if plants:
            non_assigned_plants, b_plants, y_plants, b_reserved_plants, y_reserved_plants = plants
            self.map_areas()
            for plant in non_assigned_plants:
                self.draw_plant(plant, BLACK)
            for plant in b_plants:
                self.draw_plant(plant, BLUE)
            for plant in y_plants:
                self.draw_plant(plant, YELLOW)
            for plant in b_reserved_plants:
                self.draw_plant(plant, RED)
            for plant in y_reserved_plants:
                self.draw_plant(plant, RED)
        return self.view
