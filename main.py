import cv2 as cv
import numpy as np
from image_processor import ImageProcessor
from visualiser import Visualiser
import time
from multiprocessing import Process
from data_analiser import DataAnaliser

# for solar panels
CAMERA_MATRIX = np.array([[5000, 0, 970],
                          [0, 5000, 550],
                          [0, 0, 1]])
DIST_COEFFS = np.array([-3.4, -0.2, 0.015, 0, 0.05])

F = 2
WIDTH_HEIGHT = (300*F, 200*F)
OFFSET = (75*F, 50*F)
RESERVED_AREA_B = [(0,0), (45*F,45*F)]
RESERVED_AREA_Y = ((255*F,0), (300*F, 45*F))
DROP_OFFS_Y = [[(255*F,155*F), (300*F,200*F)],[(0, 77*F), (45*F, 122*F)]]
DROP_OFFS_B = [[(0,155*F), (45*F,200*F)],[(255*F, 77*F), (300*F, 122*F)]]
SIMA_AREA_Y = [(150*F, 0), (195*F, 150*F)]
SIMA_AREA_B = [(105*F, 0), (150*F, 150*F)]

cap = cv.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if ret:
        image_processor = ImageProcessor(frame, WIDTH_HEIGHT,OFFSET,CAMERA_MATRIX,DIST_COEFFS)
        if image_processor.perspective_transform is not None:
            break

print("calibrated")
visualiser = Visualiser(RESERVED_AREA_B, RESERVED_AREA_Y, DROP_OFFS_B, DROP_OFFS_Y, SIMA_AREA_B, SIMA_AREA_Y)
data_analiser = DataAnaliser(DROP_OFFS_B, DROP_OFFS_Y, RESERVED_AREA_B, RESERVED_AREA_Y)

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
    print("model time: ", time2,"    img time: ",time1)
    visualiser.update(img, plants)
    if ret:
        cv.imshow("frame", visualiser.view)

    if cv.waitKey(1) == ord("q"):
        break
    
