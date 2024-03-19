import cv2 as cv

class Camera:
    frame = None

    def __init__(self):
        self.cap = cv.VideoCapture(0)

    def start_camera(self):
        while True:
            ret, frame = self.cap.read()
            if ret:
                Camera.frame = frame


def main():
    camera = Camera()
    camera.start_camera()

if __name__ == "__main__":
    main()
