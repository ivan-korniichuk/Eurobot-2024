from main_robot_navigation.path_finder import Path_Finder
# import time
import numpy as np
import cv2 as cv
import math
from shapely.geometry import LineString

DICTIONAIRY = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_100)
PARAMS = cv.aruco.DetectorParameters()
# PARAMS.adaptiveThreshWinSizeMin = 141  # default 3
# PARAMS.adaptiveThreshWinSizeMax = 251  # default 23
# PARAMS.adaptiveThreshWinSizeStep = 20  # default 10
# PARAMS.adaptiveThreshConstant = 4      # default 7
# PARAMS.cornerRefinementMethod = cv.aruco.CORNER_REFINE_CONTOUR
PARAMS.adaptiveThreshWinSizeMin = 5
PARAMS.adaptiveThreshWinSizeMax = 25
PARAMS.adaptiveThreshWinSizeStep = 10
PARAMS.perspectiveRemoveIgnoredMarginPerCell = 0.4
PARAMS.maxErroneousBitsInBorderRate = 0.5  # Allow for more distortion
MARKER_DETECTOR = cv.aruco.ArucoDetector(DICTIONAIRY, PARAMS)

TEAM_BLUE_IDS = range(1,6)
TEAM_YELLOW_IDS = range(6,11)

class MainNavigation:
    def __init__(self, offset, team_color, camera_position, height, main_bounding_box, small_bounding_box = (220,220), simas_base = ("ERROR"),
                reserved_blue = ("ERROR"), reserved_yellow = ("ERROR")):
        self.main_bounding_box = main_bounding_box
        self.robot = []
        self.contours = []
        self.our_base = []
        self.their_base = []
        self.simas_base = simas_base
        self.our_ids = -1
        self.their_ids = -1
        self.camera_position = camera_position
        self.height = height

        if team_color == "Yellow":
            self.our_base = reserved_yellow
            self.their_base = reserved_blue
            self.our_ids = TEAM_YELLOW_IDS
            self.their_ids = TEAM_BLUE_IDS
        elif team_color == "Blue":
            self.our_base = reserved_blue
            self.their_base = reserved_yellow
            self.our_ids = TEAM_BLUE_IDS
            self.their_ids = TEAM_YELLOW_IDS
        else:
            print("This team is not defined")
            raise("Team is not defined")
        
        their_base = [self.their_base[0], (self.their_base[0][0], self.their_base[1][1]),
                       self.their_base[1], (self.their_base[1][0], self.their_base[0][1])]

        self.def_contours = [self.add_bounding_box(self.simas_base, small_bounding_box, offset), 
                             self.add_bounding_box(their_base, small_bounding_box, offset)]
        self.path_finder = Path_Finder(offset, [], h_w=(2000,3000))

    def add_bounding_box(self, box, bbox, offset = (0,0)):
        box[0] = (box[0][0] - bbox[0] + offset[0], box[0][1] - bbox[1] + offset[1])
        box[1] = (box[1][0] - bbox[0] + offset[0], box[1][1] + bbox[1] + offset[1])
        box[2] = (box[2][0] + bbox[0] + offset[0], box[2][1] + bbox[1] + offset[1])
        box[3] = (box[3][0] + bbox[0] + offset[0], box[2][1] - bbox[1] + offset[1])
        return box

    def navigate(self, img, end):
        self.update_obstacles(img, [])
        self.path_finder.update(contours = self.contours)
        path = []
        
        if self.robot != []:
            self.path_finder.find_path(self.robot[0], end)
            path = self.path_finder.find_shortest_path()
        return [self.robot[1], path]
    
    
    def update_obstacles(self, img, contours):
        _, other_robot_contours = self.detect_robots(img)
        if other_robot_contours:
            contours.append(other_robot_contours)
        contours += self.def_contours
        print(contours)
        self.contours = contours
        return contours
    
    def camera_compensation(self, position):
        line = LineString([position, self.camera_position[:2]])
        not_known = self.height * line.length / self.camera_position[2]
        actual_pos = line.interpolate(not_known)
        x, y = int(actual_pos.x), int(actual_pos.y)
        return [x,y]
    
    def detect_robots(self, img):
        their_robot_corners = []
        out_robot = []
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(gray, (9, 9), 0)
        contrast_enhanced = cv.equalizeHist(blurred)
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_applied = clahe.apply(contrast_enhanced)
        # cv.imshow("k", clahe_applied)
        corners, ids, _ = MARKER_DETECTOR.detectMarkers(clahe_applied)
        if len(corners) != 0:
            for (corner, id) in zip(corners, ids):
                if not (id in self.our_ids or id in self.their_ids):
                    continue
                tl, _, br, bl  = corner.reshape((4, 2))
                cX = int((tl[0] + br[0]) / 2.0)
                cY = int((tl[1] + br[1]) / 2.0)

                cX, cY = self.camera_compensation((cX, cY))

                if id in self.their_ids:
                    their_robot_corners = [0]*4
                    their_robot_corners[0] = (cX - self.main_bounding_box[0], cY - self.main_bounding_box[1])
                    their_robot_corners[1] = (cX + self.main_bounding_box[0], cY - self.main_bounding_box[1])
                    their_robot_corners[2] = (cX + self.main_bounding_box[0], cY + self.main_bounding_box[1])
                    their_robot_corners[3] = (cX - self.main_bounding_box[0], cY + self.main_bounding_box[1])
                elif id in self.our_ids:
                    vector = (tl-bl)
                    rot = math.atan2(vector[1],vector[0])
                    out_robot = [(cX, cY), rot]
                    self.robot = out_robot
        return out_robot, their_robot_corners
    
    def get_robot(self, img):
        out_robot = []
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(gray, (9, 9), 0)
        contrast_enhanced = cv.equalizeHist(blurred)
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_applied = clahe.apply(contrast_enhanced)
        corners, ids, _ = MARKER_DETECTOR.detectMarkers(clahe_applied)
        if len(corners) != 0:
            for (corner, id) in zip(corners, ids):
                if not (id in self.our_ids):
                    continue
                tl, _, br, bl  = corner.reshape((4, 2))
                cX = int((tl[0] + br[0]) / 2.0)
                cY = int((tl[1] + br[1]) / 2.0)

                cX, cY = self.camera_compensation((cX, cY))

                if id in self.our_ids:
                    vector = (tl-bl)
                    rot = math.atan2(vector[1],vector[0])
                    out_robot = [(cX, cY), rot]
                    self.robot = out_robot
                    return out_robot
        return []