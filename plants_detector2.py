import numpy as np
def get_plants (img, model):
    plants = []
    results = model.predict(img, conf=0.4,classes=0, verbose=False, device='mps')

    for xywh in results[0].boxes.xywh:
        # append only x and y coords of the center
        plants.append((int(xywh[0]), int(xywh[1])))
    return plants

def get_plant_detector(shared_dict):
    print("STARTED")
    from ultralytics import YOLO
    try:
        model = YOLO('i900model8500.pt')
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    while True:
        try:
            img = np.array(shared_dict["img"])
            shared_dict["plants"] = get_plants(img, model)
        except Exception as e:
            print(f"Error during loop execution: {e}")
            break  # Exit the loop in case of error for debugging