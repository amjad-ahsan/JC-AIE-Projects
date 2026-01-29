from collections import defaultdict
from func.calorie_map import get_calorie_info
import numpy as np
from PIL import Image, ImageDraw
import onnxruntime as ort
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "best.onnx")

session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])

CLASS_NAMES = [
    "ayam goreng",
    "capcay",
    "nasi",
    "sayur bayam",
    "sayur kangkung",
    "sayur sop",
    "tahu",
    "telur dadar",
    "telur mata sapi",
    "telur rebus",
    "tempe",
    "tumis buncis",
    "food-z7p4"
]


def analyze_image(image_path, conf=0.25):
    """
    Food detection and calorie counting based on detected items only.
    """

    original = Image.open(image_path).convert("RGB")
    img = original.resize((640, 640))  # change imgsz if needed this also run the detektion using yolo
    img_array = np.array(img).astype(np.float32) / 255.0
    img_array = np.transpose(img_array, (2, 0, 1))
    img_array = np.expand_dims(img_array, axis=0)

    results = session.run(None, {"images": img_array})[0]  # run the detection using ONNX model

    draw = ImageDraw.Draw(original)
    foods = []

    #for each box detected in the results/ keep info
    for det in results[0]:
        confidence = float(det[4]) #show confidence
        if confidence < 0.4: #make sure lower confidence dont affect calorie calculation
            continue

        class_id = int(det[5])
        if class_id < 0 or class_id >= len(CLASS_NAMES):
            continue

        label = CLASS_NAMES[class_id] #give label
        foods.append((label, confidence))

        # draw bounding box on original image
        x1, y1, x2, y2 = det[:4]
        w_scale = original.width / 640
        h_scale = original.height / 640
        box = [x1*w_scale, y1*h_scale, x2*w_scale, y2*h_scale]

        draw.rectangle(box, outline="red", width=3)
        draw.text((box[0], box[1]-10), f"{label} {confidence:.2f}", fill="red")

    summary = defaultdict(lambda: {"count": 0, "conf": []})
    #conf is confidence this is also confidence but threshold for filtering detections

    for label, conf_score in foods:
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

    return counts, avg_conf, int(total_calories), original













    
