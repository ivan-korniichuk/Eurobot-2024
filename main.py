import cv2 as cv
import numpy as np
from image_processor import ImageProcessor
from visualiser import Visualiser
import time
# from multiprocessing import Process
from data_analiser import DataAnaliser

# for solar panels
# WIDTH_HEIGHT = (3000, 2300)
WIDTH_HEIGHT = (3000, 2000)
OFFSET = (750, 500)
DIST_COEFFS = np.array([-3.4, -0.2, 0.015, 0, 0.05])
CAMERA_MATRIX = np.array([[5000, 0, 970],
                          [0, 5000, 550],
                          [0, 0, 1]]) 

RESERVED_AREA_B = [(0,0), (450,450)]
RESERVED_AREA_Y = ((2550,0), (3000, 450))
# DROP_OFFS_Y = [[(2550,1550), (3000,2000)],[(0, 775), (450, 1225)]]
# DROP_OFFS_B = [[(0,1550), (450,2000)],[(2550, 775), (3000, 1225)]]
DROP_OFF_B_MID = [(2550, 775), (3000, 1225)]
DROP_OFF_B_COR = [(0,1550), (450,2000)]
DROP_OFF_Y_MID = [(0, 775), (450, 1225)]
DROP_OFF_Y_COR = [(2550,1550), (3000,2000)]
# SOLAR_PANELS_Y = [(), (), ()]
# SOLAR_PANELS_B = [(), (), ()]
# SOLAR_PANELS_G = [(), (), ()]
SIMA_AREA_Y = [(1500, 0), (1950, 150)]
SIMA_AREA_B = [(1050, 0), (1500, 150)]

cap = cv.VideoCapture(1)

while True:
    print("2")
    ret, frame = cap.read()
    if ret:
        image_processor = ImageProcessor(
            frame, 
            WIDTH_HEIGHT,
            OFFSET,
            CAMERA_MATRIX,
            DIST_COEFFS
        )
        if image_processor.perspective_transform is not None:
            break

print("calibrated")
visualiser = Visualiser(DROP_OFF_B_MID, DROP_OFF_Y_MID, DROP_OFF_B_COR, DROP_OFF_Y_COR, RESERVED_AREA_B, RESERVED_AREA_Y, SIMA_AREA_B, SIMA_AREA_Y)
data_analiser = DataAnaliser(DROP_OFF_B_MID, DROP_OFF_Y_MID, DROP_OFF_B_COR, DROP_OFF_Y_COR, RESERVED_AREA_B, RESERVED_AREA_Y)

while True:
    ret, frame = cap.read()
    times_1 = time.time_ns()
    # img = image_processor.get_transformed_img(frame)
    # this one takes 0.1 sec but adapts to camera changes
    img = image_processor.adapt_and_calibrate_img(frame)
    times_2 = time.time_ns()
    plants = image_processor.get_plants(img)
    # plants = image_processor.get_plants(img)
    times_3 = time.time_ns()
    time1 = times_2 - times_1
    time2 = times_3 - times_2
    data_analiser.update(plants)
    plants = data_analiser.cluster_plants()
    print("model time")
    print(time2)
    print("img time")
    print(time1)
    visualiser.update(img, plants)
    if ret:
        cv.imshow("frame", visualiser.view)

    if cv.waitKey(1) == ord("q"):
        break
    
cap.release()
cv.destroyAllWindows()