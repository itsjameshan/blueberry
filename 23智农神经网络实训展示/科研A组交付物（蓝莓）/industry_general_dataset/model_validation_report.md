# 模型验证报告

## 验证目的

使用目标检测模型验证数据集对蓝莓成熟度识别任务的支撑能力。

## 本地已有训练结果

## 模型性能阈值
| model    | best_epoch | precision | recall  | mAP50   | mAP50-95 |
|----------|------------|-----------|---------|---------|----------|
| YOLOv11  | 96         | 0.82148   | 0.83968 | 0.88664 | 0.71022  |
| YOLOv12  | 77         | 0.85001   | 0.84318 | 0.89212 | 0.73313  |

### 指标阈值说明
1. **Recall（召回率）**：衡量模型检出全部真实蓝莓目标的能力，数值越高漏检越少；YOLOv11召回0.83968，YOLOv12召回0.84318，v12漏检控制略优。
2. **mAP50**：IoU=0.5宽松匹配下的平均精度均值，代表基础识别准确率；YOLOv11为0.88664，YOLOv12为0.89212，v12整体识别精度更高。
3. **mAP50-95**：IoU从0.5~0.95严格区间平均精度，代表精细定位能力；YOLOv11为0.71022，YOLOv12为0.73313，v12对蓝莓边界定位更精准。
4. **Precision（精确率）**：预测为蓝莓的框中真正是蓝莓的比例，即 TP/(TP+FP)；precision数值越高，误检越少；YOLOv11精确率0.82148，YOLOv12精确率0.85001，v12误检数量更少。
5. **best_epoch（最优轮次）**：YOLOv11在96轮达到最优性能，YOLOv12仅77轮就收敛至最佳效果，训练效率更高。

## 已归档证据

- `evidence/training_results/blueberry1.v4i.yolov11数据集yolov11训练结果.zip`
- `evidence/training_results/blueberry.v4i.yolov12数据集yolov12训练结果.zip`

## 仍需补充

1.明确目标应用场景的预期性能阈值。
2. 给出训练硬件、软件版本、随机种子、训练命令和数据版本。
3. 对独立 test split 输出最终评测结果。
4. 提供失败案例分析，包括漏检、错检和类别混淆。

##补充

一、实验软硬件环境
1. 硬件环境
设备：Windows PC 台式 / 笔记本
 硬件配置
图形计算卡：NVIDIA RTX4060 Laptop（独立 GPU，支持 CUDA 加速）
中央处理器：Intel CPU
2. 软件环境
操作系统：Windows 10/11
Python 版本：3.10
核心依赖库版本：
ultralytics==8.4.0
torch==2.3.0
opencv-python==4.11.0.86
pillow==11.2.1
flask==3.1.1
CMD一键安装依赖命令:pip install -r requirements.txt

二、数据集版本与信息
1.数据集名称：blueberry1.v4i.yolov11
2.存放路径：blueberry-master/blueberry1.v4i.yolov11
3.目标类别（3 类）
RipeBlueBerry：成熟蓝莓
Semi-RipeBlueBerry：半熟蓝莓
UnripeBlueBerry：未成熟蓝莓
4.数据集划分规则（固定 8:1:1）
train 训练集：80% 图片，用于模型迭代训练
val 验证集：10% 图片，训练过程实时评估精度
test 独立测试集：10% 图片，仅训练完成后使用，全程不参与训练调参
5.data.yaml 标准配置:
nc: 3
names:
  - RipeBlueBerry
  - Semi-RipeBlueBerry
  - UnripeBlueBerry
train: ./blueberry1.v4i.yolov11/train/images
val: ./blueberry1.v4i.yolov11/valid/images
test: ./blueberry1.v4i.yolov11/test/images

三、固定随机种子配置
全局统一随机种子 seed=42
作用：固定数据集打乱顺序、模型初始化权重、数据增强随机变换，保证两次训练实验结果完全可复现，消除随机变量干扰。
训练脚本内置参数：seed=42

四、两套模型完整训练命令（YOLOv11n / YOLOv12s）
1. 独立测试时可按照老师的train.py文件标准自己新建YOLOv11n 训练脚本 train_v11.py如下：
from ultralytics import YOLO
# 加载轻量化预训练权重
model = YOLO("yolov11n.pt")
# 训练超参统一固定
model.train(
    data="blueberry1.v4i.yolov11/data.yaml",
    epochs=200,
    imgsz=640,
    seed=42
)

CMD 运行指令：python train_v11.py

2. 独立测试时可自己新建YOLOv12s 训练脚本 train_v12.py如下：
from ultralytics import YOLO
# 本地加载预训练权重，无需联网下载
model = YOLO("blueberry1.v4i.yolov11/yolo12s.pt")
model.train(
    data="blueberry1.v4i.yolov11/data.yaml",
    epochs=200,
    imgsz=640,
    seed=42
)

CMD 运行指令：python train_v12.py

备注：train_v11.py/train_v12.py放在blueberry-master目录下运行，或者如果电脑配置有NVIDIA独立显卡可以按照老师的"blueberry-master\blueberry1.v4i.yolov11\train.py"不用新建通用的两个文件测试

五、独立测试（test split）执行规范
测试数据隔离：仅读取test文件夹图片，训练 / 验证数据不参与评估；
推理固定参数：输入尺寸imgsz=640，置信阈值conf=0.25，NMS 默认参数；
输出评测指标：mAP50、mAP50-95、Precision 精确率、Recall 召回率；
输出产物：指标 csv 表格、漏检 / 误检可视化图片，供给做失败案例分析。