from multiprocessing.connection import Listener
import time
from ultralytics import YOLO

MODEL = YOLO('models/i900model8500.pt')

def get_plants (img):
    plants = []
    results = MODEL.predict(img, conf=0.4,classes=0, verbose=False)

    for xywh in results[0].boxes.xywh:
        # append only x and y coords of the center
        plants.append((int(xywh[0]), int(xywh[1])))
    return plants

def listen_plant_detector():
    print("STARTED")
    address = ('localhost', 6001)
    listener = Listener(address, authkey=b'secret password')
    print("Listener started in plants_detector2.py")

    conn = listener.accept()  # Accept a connection
    print("Connection accepted in plants_detector2.py")

    while True:
        try:
            img = conn.recv()
            time1 = time.time_ns()
            result = get_plants(img)
            print("plants")
            print(len(result))
            conn.send(result)
            print("model time")
            print(time.time_ns() - time1)
        except EOFError:
            print("Connection closed by client")
            conn = listener.accept()  # Wait for a new connection
            print("Connection accepted in code2")

    # conn.close()
    # listener.close()

if __name__ == '__main__':
    listen_plant_detector()
