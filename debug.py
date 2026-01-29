from ultralytics import YOLO

model = YOLO("runs/detect/calory_final/weights/best.pt")

results = model(r"C:\Users\Amjad\Documents\Amjad\Purwadhika\JCAIEJKTAM01\JC-AIE-Projects\JC-AIE-Capstone-4\dataset\test\images\474187_jpg.rf.97f9b538a559d43fe97943aee915a22d.jpg", conf=0.2, iou=0.5, imgsz=832)[0]

print("Detected boxes:", len(results.boxes))
for box in results.boxes:
    print(model.names[int(box.cls)], float(box.conf))
