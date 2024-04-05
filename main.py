import cv2 as cv
import numpy as np
from multiprocessing.connection import Client
import subprocess
import time
import threading

from data_analiser import DataAnaliser
from main_robot_navigation.main_robot_navigation import MainNavigation
from image_processor import ImageProcessor
from visualiser import Visualiser

# TEAM_IS_BLUE = True
# TEAM_IS_BLUE = 
# WIDTH_HEIGHT = (3000, 2000)
WIDTH_HEIGHT = (4000, 3000)
MARKER_OFFSET = (750, 500)
OFFSET = (500, 0, 500, 1000)
DIST_COEFFS = np.array([-3.4, -0.2, 0.015, 0, 0.05])
CAMERA_MATRIX = np.array([[5000, 0, 970],
                        [0, 5000, 550],
                        [0, 0, 1]])

RESERVED_AREA_B = [(0, 0), (450, 450)]
RESERVED_AREA_Y = ((2550, 0), (3000, 450))

DROP_OFF_B_MID = [(2550, 775), (3000, 1225)]
DROP_OFF_B_COR = [(0, 1550), (450, 2000)]
DROP_OFF_Y_MID = [(0, 775), (450, 1225)]
DROP_OFF_Y_COR = [(2550, 1550), (3000, 2000)]
# SOLAR_PANELS_Y = [(), (), ()]
# SOLAR_PANELS_B = [(), (), ()]
# SOLAR_PANELS_G = [(), (), ()]
SIMA_AREA_Y = [(1500, 0), (1950, 150)]
SIMA_AREA_B = [(1050, 0), (1500, 150)]
SIMAS_AREA = [(1050, 0), (1050, 150), (1950, 150),(1950, 0)]

MAIN_BBOX = [450, 450]
# temporary
CAMERA_POS = [1500, -240, 1570]
CAMERA_POS = [CAMERA_POS[0] + OFFSET[0], CAMERA_POS[1] + OFFSET[1], CAMERA_POS[2]]
# CAMERA_POS_Y = 
# CAMERA_POS_B = 

class Main:
    def __init__(self, team_color = "None", height = 430):
        self.cap = cv.VideoCapture(1)
        self.visualiser = Visualiser(OFFSET, DROP_OFF_B_MID, DROP_OFF_Y_MID, DROP_OFF_B_COR, DROP_OFF_Y_COR, RESERVED_AREA_B,
                            RESERVED_AREA_Y, SIMA_AREA_B, SIMA_AREA_Y)
        self.data_analiser = DataAnaliser(OFFSET, DROP_OFF_B_MID, DROP_OFF_Y_MID, DROP_OFF_B_COR, DROP_OFF_Y_COR, RESERVED_AREA_B,
                                RESERVED_AREA_Y)
        self.image_processor = None
        self.img = None
        self.set_image_processor()
        self.main_navigation = MainNavigation(OFFSET, team_color, main_bounding_box=MAIN_BBOX, simas_base=SIMAS_AREA,
                                            reserved_yellow=RESERVED_AREA_Y, reserved_blue=RESERVED_AREA_B, camera_position=CAMERA_POS, height=height)
        self.angle_and_path = [0, []]
        self.main_is_running = False
        self.lock = threading.Lock()
        self.on_navigation_event = threading.Event()

    def set_image_processor(self): 
        while True:
            ret, frame = self.cap.read()
            if ret:
                image_processor = ImageProcessor(
                    frame, 
                    WIDTH_HEIGHT,
                    MARKER_OFFSET,
                    OFFSET,
                    CAMERA_MATRIX,
                    DIST_COEFFS
                )
                if image_processor.perspective_transform is not None:
                    self.image_processor = image_processor
                    break
        self.img = frame
        return
    
    def start(self):
        plants_detector_process = subprocess.Popen(['python3', 'plants_detector.py'])
        time.sleep(2)
        self.main_is_running = True

        address = ('localhost', 6001)
        retries = 5
        delay = 1  # Delay in seconds

        for attempt in range(retries):
            try:
                with Client(address, authkey=b'secret password') as conn:
                    while True:
                        ret, frame = self.cap.read()
                        time1 = time.time_ns()
                        conn.send(self.img)
                        time2 = time.time_ns()
                        # self.img = self.image_processor.get_transformed_img(frame)
                        self.img = self.image_processor.adapt_and_calibrate_img(frame)
                        # start navigation here
                        img2 = self.img.copy()
                        time3 = time.time_ns()
                        plants = conn.recv()
                        time4 = time.time_ns()
                        self.data_analiser.update(plants)
                        plants = self.data_analiser.cluster_plants()

                        self.on_navigation_event.set()
                        with self.lock:
                            pass
                        self.on_navigation_event.clear()
                        # path = self.main_navigation.navigate(self.img, (2775,1775))
                        if self.main_navigation.robot:
                            cv.putText(img2, str(round(self.main_navigation.robot[1],2)), self.main_navigation.robot[0], 6,4, (255, 100,120), 9)
                        self.visualiser.update(img2, plants, self.angle_and_path[1])
                        
                        # time5 = time.time_ns()
                        # print("send time")
                        # print(time2 - time1)
                        # print("receive time")
                        # print(time4 - time3)
                        # print("img processing time")
                        # print(time3 - time2)
                        # print("visualiser processing")
                        # print(time5-time4)
            except (ConnectionRefusedError, EOFError) as e:
                print(f"Attempt {attempt + 1}: {str(e)}")
                time.sleep(delay)

        plants_detector_process.terminate()  # Ensure code2 is terminated
        plants_detector_process.wait()  # Wait for the process to finish
        raise Exception("Error in main/plants_detector")
    
    def navigate_robot(self, start):
        self.on_navigation_event.wait()

        with self.lock:
            self.angle_and_path = self.main_navigation.navigate(self.img, (start[0] + OFFSET[0], start[1] + OFFSET[1]))

    def get_robot(self):
        return self.main_navigation.get_robot(self.img)

        