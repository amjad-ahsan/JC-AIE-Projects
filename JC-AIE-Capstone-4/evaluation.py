from ultralytics import YOLO

def evaluate_model():
    model = YOLO("runs/detect/calory_detect4/weights/best.pt") # add calory_detect+1 for every new training
    metrics = model.val(data="dataset/data.yaml")

    print("\nYOLO VALIDATION REPORT")
    print(f"Precision: {metrics.box.mp:.3f}")
    print(f"Recall: {metrics.box.mr:.3f}")
    print(f"mAP@50: {metrics.box.map50:.3f}")
    print(f"mAP@50-95: {metrics.box.map:.3f}")

if __name__ == "__main__":
    evaluate_model()



