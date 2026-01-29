from collections import defaultdict
from func.calorie_map import get_calorie_info
import numpy as np
from PIL import Image
import onnxruntime as ort
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "best.onnx")

# Load ONNX model (CPU)
session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])

# Class labels from training YAML (order MUST match training)
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
    "food-z7p4"  # extra class not in calorie map (safe to ignore)
]


def analyze_image(image_path, conf=0.25):
    """
    Food detection and calorie counting based on detected items only.
    """

    # Load and prepare image
    img = Image.open(image_path).convert("RGB")
    img = img.resize((640, 640))
    img_array = np.array(img).astype(np.float32) / 255.0
    img_array = np.transpose(img_array, (2, 0, 1))  # HWC → CHW
    img_array = np.expand_dims(img_array, axis=0)

    # Run ONNX model
    outputs = session.run(None, {"images": img_array})[0]

    foods = []

    #for each box detected in the results/ keep info
    for det in outputs[0]:
        confidence = float(det[4])  # show confidence
        if confidence < 0.4:  # filter low confidence detections
            continue

        class_id = int(det[5])

        # Skip invalid or unknown class IDs safely
        if class_id < 0 or class_id >= len(CLASS_NAMES):
            continue

        label = CLASS_NAMES[class_id] #give label
        foods.append((label, confidence))

    summary = defaultdict(lambda: {"count": 0, "conf": []})

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

    return counts, avg_conf, int(total_calories), None













    
