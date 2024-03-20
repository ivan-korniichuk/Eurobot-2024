import cv2 as cv
import numpy as np

DICTIONAIRY = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_100)
PARAMS = cv.aruco.DetectorParameters()
PARAMS.adaptiveThreshWinSizeMin = 141  # default 3
PARAMS.adaptiveThreshWinSizeMax = 251  # default 23
PARAMS.adaptiveThreshWinSizeStep = 20  # default 10
PARAMS.adaptiveThreshConstant = 4      # default 7
PARAMS.cornerRefinementMethod = cv.aruco.CORNER_REFINE_CONTOUR
MAIN_DETECTOR = cv.aruco.ArucoDetector(DICTIONAIRY, PARAMS)

PARAMS_2 = cv.aruco.DetectorParameters()
SOLAR_DETECTOR = cv.aruco.ArucoDetector(DICTIONAIRY, PARAMS_2)

class ImageProcessor:
    def __init__(self, img, width_height, offset, matrix, dist_coeffs):

        self.width, self.height = width_height
        self.x_offset, self.y_offset = offset
        self.bot = None
        self.plants = []
        self.perspective_transform = None
        self.matrix = matrix
        self.dist_coeffs = dist_coeffs

        h,  w = img.shape[:2]
        self.newcameramtx, _ = cv.getOptimalNewCameraMatrix(self.matrix, self.dist_coeffs, (w,h), 0, (w,h))

        self.differences = [0]*3
        self.dst_mat = np.float32(
        [
            [self.x_offset, self.y_offset],
            [self.width - self.x_offset, self.y_offset],
            [self.x_offset, self.height - self.y_offset],
            [self.width - self.x_offset, self.height - self.y_offset],
        ])
        # for solar panels
        # self.dst_mat = np.float32(
        # [
        #     [self.x_offset, self.y_offset],
        #     [3000 - self.x_offset, self.y_offset],
        #     [self.x_offset, 2000 - self.y_offset],
        #     [3000 - self.x_offset, 2000 - self.y_offset],
        # ])
        try:
            self.perspective_transform = self.get_perspective_transform(self.calibrate_img(img))
        except:
            print("no aruco grid found")

    def get_perspective_transform(self, frame):
        grid = [0] * 4

        corners, ids, _ = MAIN_DETECTOR.detectMarkers(frame)
        if len(corners) != 0:
            for (corner, id) in zip(corners, ids):
                if not id in range(20, 24):
                    continue
                tl, _, br, _ = corner.reshape((4, 2))
                cX = int((tl[0] + br[0]) / 2.0)
                cY = int((tl[1] + br[1]) / 2.0)
                grid[id[0] % 20] = (cX, cY)


        for i in range(3):
            if grid[i] and grid[i+1]:
                self.differences[i] = (grid[i+1][0] - grid[i][0], grid[i+1][1] - grid[i][1])

        for i in range(3):
            if grid[i+1] == 0:
                if self.differences[i] != 0 and grid[i] != 0:
                    grid[i+1] = (grid[i][0] + self.differences[i][0], grid[i][1] + self.differences[i][1])

        for i in reversed(range(1, 4)):
            if grid[i-1] == 0:
                if self.differences[i] != 0 and grid[i] != 0:
                    grid[i-1] = (grid[i][0] - self.differences[i-1][0], grid[i][1] - self.differences[i-1][1])

        img_mat = np.float32(grid)
        return cv.getPerspectiveTransform(img_mat, self.dst_mat)

    def calibrate_img (self, img):
        dst = cv.undistort(img, self.matrix, self.dist_coeffs, None, self.newcameramtx)
        return dst

    def get_transformed_img (self, img):
        dst = self.calibrate_img(img)
        new_frame = cv.warpPerspective(
            dst, self.perspective_transform, (self.width, self.height))
        return new_frame

    def adapt_and_calibrate_img (self, img):
        try:
            self.perspective_transform = self.get_perspective_transform(self.calibrate_img(img))
        except:
            print("no aruco grid found")
        return self.get_transformed_img(img)

    def get_solar_panels (self, img):
        solar_panels = [0]*9
        # cut 60%
        # tresholding
        # get markers id-47
        # save their rotations
        return solar_panels