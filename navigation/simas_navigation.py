from navigation.path_finder import Path_Finder
# import time
# import numpy as np
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

class SimaNavigation:
    def __init__(self, offset, team_color, sima_1_id, sima_2_id, sima_3_id, sima_4_id, camera_position, height, simas_height, 
                 small_bbox = (220,220), plant_height = 50, simas_base = ("ERROR"), sima_bbox = ("ERROR"), plant_bbox =("ERROR"),
                reserved_blue = ("ERROR"), reserved_yellow = ("ERROR")):
        self.small_bbox = small_bbox
        self.sima_bbox = sima_bbox
        self.plant_bbox = plant_bbox
        self.contours = []
        self.our_base = []
        self.their_base = []
        self.simas_base = simas_base
        self.our_ids = -1
        self.their_ids = -1
        self.camera_position = camera_position
        self.height = height
        self.simas_height = simas_height
        self.plant_height = plant_height
        self.sima_1_id = sima_1_id
        self.sima_2_id = sima_2_id
        self.sima_3_id = sima_3_id
        self.sima_4_id = sima_4_id
        # [[x,y], rot]
        self.robot = [] 
        self.sima_1 = [] 
        self.sima_2 = [] 
        self.sima_3 = [] 
        self.sima_4 = [] 
        # self.simas_ids = [0,0,0,0]
        # self.simas = [[], [], [], []]

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

        self.def_contours = [self.add_bounding_box(self.simas_base, small_bbox, offset), 
                             self.add_bounding_box(their_base, small_bbox, offset)]
        self.simas_path_finder = Path_Finder(offset, [], h_w=(2000,3000), cluster_objects=True)

    def add_bounding_box(self, box, bbox, offset = (0,0)):
        box[0] = (box[0][0] - bbox[0] + offset[0], box[0][1] - bbox[1] + offset[1])
        box[1] = (box[1][0] - bbox[0] + offset[0], box[1][1] + bbox[1] + offset[1])
        box[2] = (box[2][0] + bbox[0] + offset[0], box[2][1] + bbox[1] + offset[1])
        box[3] = (box[3][0] + bbox[0] + offset[0], box[2][1] - bbox[1] + offset[1])
        return box
    
    def create_bounding_box(self, point, bbox):
        if point and bbox:
            contours = [0]*4
            contours[0] = (point[0] - bbox[0], point[1] - bbox[1])
            contours[1] = (point[0] + bbox[0], point[1] - bbox[1])
            contours[2] = (point[0] + bbox[0], point[1] + bbox[1])
            contours[3] = (point[0] - bbox[0], point[1] + bbox[1])
            return contours
        else:
            return []
        
    def unite_bboxes(self, bbox1, bbox2):
        return [bbox1[0] + bbox2[0], bbox1[1]+ bbox2[1]]
    
    def set_if_exists(self, object, index):
        if object and object[index]:
            return object[index]
        else:
            return []
        
    def append_if_exists(self, list, object):
        if object:
            list.append(object)
    
    def navigate_sima(self, img, sima_no, plants, end):
        # might get an error if not all simas have coords == []
        rot = None
        contours = [] 
        other_simas = []
        our_robot, other_robot = self.detect_robots(img)
        our_robot = self.set_if_exists(our_robot, 0)
        other_robot_contours = self.create_bounding_box(other_robot, self.unite_bboxes(self.sima_bbox, self.small_bbox))
        our_robot_contours = self.create_bounding_box(our_robot, self.unite_bboxes(self.sima_bbox, self.small_bbox))
        # contours += our_robot_contours
        # contours += other_robot_contours
        # cv.imwrite("img2.png", img)
        self.append_if_exists(contours, our_robot_contours)
        self.append_if_exists(contours, other_robot_contours)

        sima_1_pos = self.set_if_exists(self.sima_1, 0)
        sima_2_pos = self.set_if_exists(self.sima_2, 0)
        sima_3_pos = self.set_if_exists(self.sima_3, 0)
        sima_4_pos = self.set_if_exists(self.sima_4, 0)

        if sima_no == 1 and self.sima_1:
            rot = self.sima_1[1]
            other_simas.append(sima_2_pos)
            other_simas.append(sima_3_pos)
            other_simas.append(sima_4_pos)
        elif sima_no == 2 and self.sima_2:
            rot = self.sima_2[1]
            other_simas.append(sima_1_pos)
            other_simas.append(sima_3_pos)
            other_simas.append(sima_4_pos)
        elif sima_no == 3 and self.sima_3:
            rot = self.sima_3[1]
            other_simas.append(sima_1_pos)
            other_simas.append(sima_2_pos)
            other_simas.append(sima_4_pos)
        elif sima_no == 4 and self.sima_4:
            rot = self.sima_4[1]
            other_simas.append(sima_1_pos)
            other_simas.append(sima_2_pos)
            other_simas.append(sima_3_pos)

        for sima in other_simas:
            contours.append(self.create_bounding_box(sima, self.unite_bboxes(self.sima_bbox, self.sima_bbox)))

        for plant in plants:
            new_plant_pos = self.camera_compensation(plant, self.plant_height)
            contours.append(self.create_bounding_box(new_plant_pos, self.unite_bboxes(self.sima_bbox, self.plant_bbox)))
        self.simas_path_finder.update(contours)

        if sima_no == 1 and sima_1_pos != []:
            self.simas_path_finder.find_path(sima_1_pos, end)
        elif sima_no == 2 and sima_2_pos != []:
            self.simas_path_finder.find_path(sima_2_pos, end)
        elif sima_no == 3 and sima_3_pos != []:
            self.simas_path_finder.find_path(sima_3_pos, end)
        elif sima_no == 4 and sima_4_pos != []:
            self.simas_path_finder.find_path(sima_4_pos, end)

        return [rot, self.simas_path_finder.find_shortest_path()]
    
    def camera_compensation(self, position, height):
        line = LineString([position, self.camera_position[:2]])
        not_known = height * line.length / self.camera_position[2]
        actual_pos = line.interpolate(not_known)
        x, y = int(actual_pos.x), int(actual_pos.y)
        return [x,y]
    
    def detect_robots(self, img):
        their_robot = []
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
                if not (id in self.our_ids or id in self.their_ids or 
                        id in [self.sima_1_id, self.sima_2_id, self.sima_3_id, self.sima_4_id]):
                    continue
                tl, _, br, bl  = corner.reshape((4, 2))
                cX = int((tl[0] + br[0]) / 2.0)
                cY = int((tl[1] + br[1]) / 2.0)

                vector = (tl-bl)
                rot = math.atan2(vector[1],vector[0])
                
                if id in self.our_ids or id in self.their_ids:
                    cX, cY = self.camera_compensation((cX, cY), self.height)
                else: 
                    cX, cY = self.camera_compensation((cX, cY), self.simas_height)

                if id in self.their_ids:
                    their_robot = (cX,cY)
                elif id in self.our_ids:
                    out_robot = [(cX, cY), rot]
                    self.robot = out_robot
                elif id == self.sima_1_id:
                    self.sima_1 = [(cX, cY), rot]
                elif id == self.sima_2_id:
                    self.sima_2 = [(cX, cY), rot]
                elif id == self.sima_3_id:
                    self.sima_3 = [(cX, cY), rot]
                elif id == self.sima_4_id:
                    self.sima_4 = [(cX, cY), rot]
        return out_robot, their_robot