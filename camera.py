import time
import cv2 as cv
import numpy as np

from image_processor import ImageProcessor

WIDTH_HEIGHT = (3000, 2000)
OFFSET = (750, 500)
DIST_COEFFS = np.array([-3.4, -0.2, 0.015, 0, 0.05])
CAMERA_MATRIX = np.array([[5000, 0, 970],
                          [0, 5000, 550],
                          [0, 0, 1]])

class Camera:
    frame = None
    def __init__(self):
        self.cap = cv.VideoCapture(1)

    def start_camera(self):
        while True:
            ret, frame = self.cap.read()
            if ret:
                Camera.frame = frame


def main():
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
    while True:
        ret, frame = cap.read()
        if ret:
            times_1 = time.time_ns()
            frame = image_processor.adapt_and_calibrate_img(frame)
            times_2 = time.time_ns()
            time2 = times_2 - times_1
            print("updating camera time:", time2, "\n")
            Camera.frame = frame

if __name__ == "__main__":
    main()