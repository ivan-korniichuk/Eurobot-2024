import cv2 as cv
import numpy as np
from image_processor_new import ImageProcessor

from multiprocessing.connection import Client
import subprocess

from visualiser import Visualiser
import time
from data_analiser import DataAnaliser

if __name__ == "__main__":

    WIDTH_HEIGHT = (3000, 2000)
    OFFSET = (750, 500)
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

    visualiser = Visualiser(DROP_OFF_B_MID, DROP_OFF_Y_MID, DROP_OFF_B_COR, DROP_OFF_Y_COR, RESERVED_AREA_B,
                            RESERVED_AREA_Y, SIMA_AREA_B, SIMA_AREA_Y)
    data_analiser = DataAnaliser(DROP_OFF_B_MID, DROP_OFF_Y_MID, DROP_OFF_B_COR, DROP_OFF_Y_COR, RESERVED_AREA_B,
                                RESERVED_AREA_Y)

    cap = cv.VideoCapture(1)
    while True:
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
    plants_detector_process = subprocess.Popen(['python3', 'plants_detector.py'])
    time.sleep(2)

    address = ('localhost', 6001)
    retries = 5
    delay = 1  # Delay in seconds
    img = frame
    # 
    cv.namedWindow("frame1", cv.WINDOW_NORMAL)   # Create window with freedom of dimensions
    # 

    for attempt in range(retries):
        try:
            with Client(address, authkey=b'secret password') as conn:
                while True:
                    ret, frame = cap.read()
                    time1 = time.time_ns()
                    conn.send(img)
                    time2 = time.time_ns()
                    # img = image_processor.get_transformed_img(frame)
                    img = image_processor.adapt_and_calibrate_img(frame)
                    img2 = img.copy()
                    time3 = time.time_ns()
                    plants = conn.recv()
                    time4 = time.time_ns()
                    data_analiser.update(plants)
                    plants = data_analiser.cluster_plants()
                    visualiser.update(img2, plants)
                    time5 = time.time_ns()
                    print("send time")
                    print(time2 - time1)
                    print("receive time")
                    print(time4 - time3)
                    print("img processing time")
                    print(time3 - time2)
                    print("visualiser processing")
                    print(time5-time4)
                    # 
                    # cv.resizeWindow("frame1", 600,400)
                    # 
                    cv.imshow("frame1", visualiser.view)

                    if cv.waitKey(1) == ord("q"):
                        conn.send("close")
                        # plants_detector_process.terminate()  # Ensure code2 is terminated
                        # plants_detector_process.wait()  # Wait for the process to finish
                        break
        except (ConnectionRefusedError, EOFError) as e:
            print(f"Attempt {attempt + 1}: {str(e)}")
            time.sleep(delay)
    # plants_detector_process.terminate()  # Ensure code2 is terminated
    # plants_detector_process.wait()  # Wait for the process to finish
    raise Exception("Failed to connect to code2")