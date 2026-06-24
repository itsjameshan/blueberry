from PIL import Image
import os
img_root = r"D:/PythonProject/yolo_training_ready/image"
for split in ["train", "validation"]:
    folder = os.path.join(img_root, split)
    for f in os.listdir(folder):
        if f.lower().endswith((".jpg", ".png")):
            path = os.path.join(folder, f)
            try:
                Image.open(path)
            except:
                print(f"损坏图片：{path}")