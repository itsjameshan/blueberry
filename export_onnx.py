from ultralytics import YOLO

# 加载模型
model = YOLO(r"D:\pythonProject\bule\blueberry1.v4i.yolov11\runs\detect\train\weights\best.pt")

# 导出：无最大尺寸限制 + 完全动态
model.export(
    format="onnx",
    dynamic=True,      # ✅ 核心：动态尺寸
    simplify=True,
    opset=17
)