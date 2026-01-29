from ultralytics import YOLO
from collections import defaultdict
from func.calorie_map import get_calorie_info

model = YOLO("model/best.pt")

 # path to trained model

def analyze_image(image_path, conf=0.25):
    """
    Food detection and calorie counting based on detected items only.
    """

    results = model(image_path, conf=conf, iou=0.6, imgsz=640)[0] # change imgsz if needed this also run the detektion using yolo

    foods = []

    #for each box detected in the results/ keep info
    for box in results.boxes:
        label = model.names[int(box.cls)] #give label
        confidence = float(box.conf) #show confidence
        foods.append((label, confidence))

    summary = defaultdict(lambda: {"count": 0, "conf": []})
    #conf is confidence this is also confidence but threshold for filtering detections
    CONF_THRESHOLD = 0.4

    for label, conf_score in foods:
        if conf_score < CONF_THRESHOLD: #make sure lower confidence dont affect calorie calculation
            continue
        summary[label]["count"] += 1
        summary[label]["conf"].append(conf_score)

    #Counting
    counts = {k: v["count"] for k, v in summary.items()}
    avg_conf = {k: sum(v["conf"]) / len(v["conf"]) for k, v in summary.items()}

    total_calories = 0

            # Might give false estimation for very small or very large items but worth a try
            # itwont display the rigid data number but give estimation based on portion size

        #calories, unit = get_calorie_info(food)
        #total_calories += calories * data["count"] * portion_factor

        # Nvm since the data was to small , the protion factor resulted in the same exact answer as before
    for food, data in summary.items():
        calories, unit = get_calorie_info(food)
        total_calories += calories * data["count"]

    return counts, avg_conf, int(total_calories), results







    
