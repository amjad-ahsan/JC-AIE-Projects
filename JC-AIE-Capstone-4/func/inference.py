from collections import defaultdict
from func.calorie_map import get_calorie_info

_model = None  # global cache


def get_model():
    """Load YOLO model only once (lazy load)."""
    global _model
    if _model is None:
        from ultralytics import YOLO  # import here to avoid Streamlit startup crash
        _model = YOLO("model/best.pt")
    return _model


def analyze_image(image_path, conf=0.25):
    """
    Food detection and calorie counting based on detected items only.
    """
    model = get_model()

    results = model(image_path, conf=conf, iou=0.6, imgsz=640)[0]

    foods = []
    for box in results.boxes:
        label = model.names[int(box.cls)]
        confidence = float(box.conf)
        foods.append((label, confidence))

    summary = defaultdict(lambda: {"count": 0, "conf": []})
    CONF_THRESHOLD = 0.4

    for label, conf_score in foods:
        if conf_score < CONF_THRESHOLD:
            continue
        summary[label]["count"] += 1
        summary[label]["conf"].append(conf_score)

    counts = {k: v["count"] for k, v in summary.items()}
    avg_conf = {k: sum(v["conf"]) / len(v["conf"]) for k, v in summary.items()}

    total_calories = 0
    for food, data in summary.items():
        calories, unit = get_calorie_info(food)
        total_calories += calories * data["count"]

    return counts, avg_conf, int(total_calories), results




    
