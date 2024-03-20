import time
from camera import Camera

class PlantsDetector:
    plants = []
    @staticmethod
    def get_plants (img, model):
        plants = []
        results = model.predict(img, conf=0.4,classes=0, verbose=False, device='mps')

        for xywh in results[0].boxes.xywh:
            # append only x and y coords of the center
            plants.append((int(xywh[0]), int(xywh[1])))
        return plants

    @staticmethod
    def get_plant_detector():
        print("STARTED")
        from ultralytics import YOLO
        try:
            model = YOLO('i900model8500.pt')
        except Exception as e:
            print(f"Error loading model: {e}")
            return

        while True:
            try:
                img = Camera.frame
                times_1 = time.time_ns()
                # PlantsDetector.get_plants(img, model)
                PlantsDetector.plants = PlantsDetector.get_plants(img, model)
                times_2 = time.time_ns()
                time2 = times_2 - times_1
                print("getting plants time:", time2, "\n")
                # PlantsDetector.plants = []
            except Exception as e:
                print(f"Error during loop execution: {e}")
                break  # Exit the loop in case of error for debugging