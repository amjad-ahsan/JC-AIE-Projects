from ultralytics import YOLO

def main():
    model = YOLO("yolov8n.pt")

    model.train(
        data="dataset/data.yaml",
        epochs=150,
        imgsz=640, # kali 32
        batch=16,
        device=0,
        name="calory_final",

        # Mild, realistic color augmentation
        hsv_h=0.01,   # very slight hue shift
        hsv_s = 0.4,   # reduced saturation variation
        hsv_v = 0.4,    # softer brightness variation

        workers=8,
        cache=True,
        amp=True
    )


    #Log 1 : yolov8n.pt with 100 epocs and 5 batch size resulted in 
    #Precision: 0.898
    #Recall: 0.824
    #mAP@50: 0.914
    #mAP@50-95: 0.639

    #log 2 : yolov8m.pt with 200 epocs and 16 batch size resulted in
    #Precision: 0.740
    #Recall: 0.844
    #mAP@50: 0.878
    #mAP@50-95: 0.639
    #lower tha previous model in precision but better in recall and mAPs

    #log 3 : yolov8m.pt with 100 epocs and 8 batch size resulted in
    #Precision: 0.763
    #Recall: 0.880
    #mAP@50: 0.912
    #mAP@50-95: 0.644
    #WORSE THAN 200 EPOCS? MAYBE BATCH SIZE MATTERS MORE? augementation causes low precision . . . 
    #causes might be from yolov8m.

    #log 4 : yolov8n.pt with 100 epocs and 16 batch size resulted in
    #
    #   Precision: 0.820
    #   Recall: 0.934
    #   mAP@50: 0.960
    #   mAP@50-95: 0.668

    #log 5 : yolov8n.pt with 150 epocs and 16 batch size resulted in
    #   YOLO VALIDATION REPORT
    #Precision: 0.886
    #Recall: 0.815
    #mAP@50: 0.898
    #mAP@50-95: 0.634

    #log 6 : yolov8m.pt with 150 epocs and 16 batch size resulted in
    # Precision: 0.749
    # Recall: 0.842
    # mAP@50: 0.868
    # mAP@50-95: 0.628

    #Since lot of run has been made we will instead use the best model from log 4 for inference, #with updated augementation parameters

    # which is yolov8n.pt with 100 epocs and 8 batch size but for better precision we will use 16 
    # It has a good balance of precision and recall plus highest mAP@50
   

if __name__ == "__main__": # Need this for multiprocessing on Windows otherwise yolo will crash
    import multiprocessing
    multiprocessing.freeze_support()
    main()
