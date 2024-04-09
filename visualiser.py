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

class Visualiser:
    def __init__(self, offset, b_mid, y_mid, b_corner, y_corner, b_reserved, y_reserved, sima_area_b, sima_area_y):
        self.offset_x, self.offset_y, _, _ = offset
        self.reserved_area_b = self.apply_offset(b_reserved)
        self.reserved_area_y = self.apply_offset(y_reserved)
        self.mid_dropoff_b = self.apply_offset(b_mid)
        self.mid_dropoff_y = self.apply_offset(y_mid)
        self.corner_dropoff_b = self.apply_offset(b_corner)
        self.corner_dropoff_y = self.apply_offset(y_corner)
        self.sima_area_b = self.apply_offset(sima_area_b)
        self.sima_area_y = self.apply_offset(sima_area_y)
        self.view = None

    def apply_offset(self, corners):
        updated_corners = []
        for corner in corners:
            updated_corners.append((corner[0] + self.offset_x, corner[1] + self.offset_y))
        return updated_corners

    def draw_plant(self, plant, color = GRAY):
        x, y = plant
        cv.circle(
            self.view,
            center=(x, y),
            radius= 70,
            color=color,
            thickness=5,
        )

    def draw_path(self, path, colour = (255, 0, 0)):
        for i in range(len(path) - 1):
            cv.line(self.view, list(path[i]), list(path[i + 1]), colour, 7)
        return

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


    def update(self, img, plants, path, simas_paths):
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
        self.draw_path(path)
        i = 0
        for path in simas_paths:
            i += 1
            self.draw_path(path, (50 + 40*i, 180, 240/i))
        # self.view
        return self.view
