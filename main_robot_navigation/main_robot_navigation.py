from main_robot_navigation.path_finder import Path_Finder
# import time
import numpy as np
import cv2 as cv
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
    def __init__(self, team_color, robot_id, main_bounding_box = (450,450)):
        self.main_bounding_box = main_bounding_box
        self.robot = []
        self.contours = []
        self.path_finder = Path_Finder([])
        pass

    def navigate(self, img, end):
        self.update_obstacles(img, [])
        self.path_finder.update(self.contours, h_w=(2000,3000))
        path = []
        # risky change later
        if self.robot != []:
            self.path_finder.find_path(self.robot, end)
            path = self.path_finder.find_shortest_path()
        # self.path_finder.draw_graph()
        # for i in range(len(path) - 1):
        #     cv.line(img, list(path[i]), list(path[i + 1]), (255, 0, 0), 3)

        # cv.imshow("Eurobot Playmate Current Board", img)
        # cv.waitKey(1)
        # print(path)
        return path
    
    
    def update_obstacles(self, img, contours):
        robot_contours = self.detect_opponents_robot(img)
        contours.append(robot_contours)
        self.contours = contours
        return contours
    
    def detect_opponents_robot(self, img, id_range = [1,47]):
        robot_corners = []
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(gray, (9, 9), 0)
        contrast_enhanced = cv.equalizeHist(blurred)
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_applied = clahe.apply(contrast_enhanced)
        # cv.imshow("k", clahe_applied)
        corners, ids, _ = MARKER_DETECTOR.detectMarkers(clahe_applied)
        if len(corners) != 0:
            for (corner, id) in zip(corners, ids):
                # if not id in range(id_range[0], id_range[1]):
                #     continue
                if not id in id_range:
                    continue
                tl, _, br, _ = corner.reshape((4, 2))
                cX = int((tl[0] + br[0]) / 2.0)
                cY = int((tl[1] + br[1]) / 2.0)
                cv.circle(img,(cX,cY), 100, (255,0,255), 15)
                if id == 47:
                    robot_corners = [0]*4
                    robot_corners[0] = (cX - self.main_bounding_box[0], cY - self.main_bounding_box[1])
                    robot_corners[1] = (cX + self.main_bounding_box[0], cY - self.main_bounding_box[1])
                    robot_corners[2] = (cX + self.main_bounding_box[0], cY + self.main_bounding_box[1])
                    robot_corners[3] = (cX - self.main_bounding_box[0], cY + self.main_bounding_box[1])
                elif id == 1:
                    self.robot = [cX, cY]
                # break might not be the best option, maybe use all of the markers in range detected
                # break
        return robot_corners