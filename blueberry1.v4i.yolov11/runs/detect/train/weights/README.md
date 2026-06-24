# 训练权重说明

本目录下的 `best.pt` / `last.pt` 为使用 **YOLO11s** 在**网上公开数据集**（Roboflow `blueberry1.v4i.yolov11`）上训练得到的权重。

- `best.pt`：验证集表现最佳的权重
- `last.pt`：最后一个 epoch 的权重
- 对应训练运行：`runs/detect/train`
- 数据集来源：[Roboflow blueberry1 v4](https://universe.roboflow.com/imaya-setty-s-xlynq/blueberry1-mdh56/dataset/4)（类别：RipeBlueBerry / Semi-RipeBlueBerry / UnripeBlueBerry）
