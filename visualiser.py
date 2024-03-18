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
    def __init__(self, b_mid, y_mid, b_corner, y_corner, b_reserved, y_reserved, sima_area_b, sima_area_y):
        self.reserved_area_b = b_reserved
        self.reserved_area_y = y_reserved
        self.mid_dropoff_b = b_mid
        self.mid_dropoff_y = y_mid
        self.corner_dropoff_b = b_corner
        self.corner_dropoff_y = y_corner
        self.sima_area_b = sima_area_b
        self.sima_area_y = sima_area_y

    def draw_plant(self, plant, color = GRAY):
        x, y = plant
        cv.circle(
            self.view,
            center=(x, y),
            radius= 70,
            color=color,
            thickness=5,
        )

    # # delete, move to data_analyser
    # def draw_rectangles (self, rectangles, color, thickness = 5):
    #     for area in rectangles:
    #         cv.rectangle(self.view, area[0], area[1], color, thickness)
    def draw_rectangle (self, rectangle, color, thickness = 5):
        cv.rectangle(self.view, rectangle[0], rectangle[1], color, thickness)
    
    def map_areas (self):
        self.draw_rectangle(self.reserved_area_y, YELLOW)
        self.draw_rectangle(self.reserved_area_b, BLUE)

        self.draw_rectangle(self.mid_dropoff_b, BLUE)
        self.draw_rectangle(self.mid_dropoff_y, YELLOW)
        self.draw_rectangle(self.corner_dropoff_b, BLUE)
        self.draw_rectangle(self.corner_dropoff_y, YELLOW)
        # # BLUE DROP OFFS
        # self.draw_rectangles(self.drop_offs_b, BLUE)
        # # Y DROP OFFS
        # self.draw_rectangles(self.drop_offs_y, YELLOW)
        self.draw_rectangle(self.sima_area_b, BLUE)
        self.draw_rectangle(self.sima_area_y, YELLOW)


    def update(self, img, plants):
        self.view = img
        if plants:
            non_assigned_plants, b_mid_plants, y_mid_plants, b_corner_plants, y_corner_plants, b_reserved_plants, y_reserved_plants = plants
            self.map_areas()
            for plant in non_assigned_plants:
                self.draw_plant(plant, BLACK)
            for plant in b_mid_plants:
                self.draw_plant(plant, BLUE)
            for plant in y_mid_plants:
                self.draw_plant(plant, YELLOW)
            for plant in b_corner_plants:
                self.draw_plant(plant, BLUE)
            for plant in y_corner_plants:
                self.draw_plant(plant, YELLOW)
            for plant in b_reserved_plants:
                self.draw_plant(plant, RED)
            for plant in y_reserved_plants:
                self.draw_plant(plant, RED)
        return self.view
