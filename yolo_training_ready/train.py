import os
os.environ['ULTRALYTICS_WORKERS'] = '0'
from ultralytics import YOLO

# 配置
DATA_YAML = r"D:/PythonProject/yolo_training_ready/data.yaml"
MODEL = "yolo11s.pt"

if __name__ == '__main__':
    model = YOLO(MODEL)
    model.train(
        data=DATA_YAML,
        epochs=200,
        imgsz=640,
        batch=8,
        device=0,
        patience=20,
        workers=0,
        mosaic=0
    )