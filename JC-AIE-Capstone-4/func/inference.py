from collections import defaultdict
from func.calorie_map import get_calorie_info

import numpy as np
from PIL import Image
import onnxruntime as ort

# Load ONNX model once
session = ort.InferenceSession("model/best.onnx", providers=["CPUExecutionProvider"])

# 🔴 REPLACE with your actual class names in training order
CLASS_NAMES = ["class1", "class2", "class3"]


def preprocess(image_path, img_size=640):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((img_size, img_size))
    img_array = np.array(img).astype(np.float32) / 255.0
    img_array = np.transpose(img_array, (2, 0, 1))
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def analyze_image(image_path, conf=0.25):
    img_input = preprocess(image_path)
    outputs = session.run(None, {"images": img_input})[0]

    foods = []
    for det in outputs[0]:
        score = float(det[4])
        if score < 0.4:
            continue
        class_id = int(det[5])
        label = CLASS_NAMES[class_id]
        foods.append((label, score))

    summary = defaultdict(lambda: {"count": 0, "conf": []})

    for label, conf_score in foods:
        summary[label]["count"] += 1
        summary[label]["conf"].append(conf_score)

    counts = {k: v["count"] for k, v in summary.items()}
    avg_conf = {k: sum(v["conf"]) / len(v["conf"]) for k, v in summary.items()}

    total_calories = 0
    for food, data in summary.items():
        calories, unit = get_calorie_info(food)
        total_calories += calories * data["count"]

    return counts, avg_conf, int(total_calories), None






    
