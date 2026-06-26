# 周实训工作日志

## 周一：

### 上午：

- 配合教师完成 repo 讲解，说明 app\.py、detect\_engine\.py、database\.py、static、onnx\_data 的作用。

- 带领各组完成 Python 环境、requirements\.txt、Flask 启动和默认 admin/admin123 登录检查。trae 和豆包理解项目代码。

- 梳理 3000 images 实训用\.zip、YOLOv11/YOLOv12 训练结果包和 onnx\_data 模型的关系。

- 帮助其他同学解决电脑配置问题

### 下午：

- 教各组如何使用LabelME，建立统一提交目录、命名规范和标注数据收集表，并完成代码组A本组 5060 张图片标注。

- 接收各组标注，统一转换为教师指定的新 YOLO 训练格式\.txt，完成 train/val/test 划分。

### 晚上：

仅由代码/训练支持同学协助整理各组标注数据，准备 YOLO 训练命令、模型导出和 ONNX 兜底方案。

---

## 周二：

### 第一节 Standup：

汇报环境、训练、模型文件和阻塞问题。

### 上午：

- 展示周一夜间训练结果，独立解释 results\.csv

- 演示模型加载与推理闭环，说明 preprocess、postprocess、NMS、conf\_threshold。

- 移交图片结果给发布组A

### 下午：

- 将 v11best\.onnx/v12best\.onnx 接入 app\.py，联调单图检测、批量检测、大图裁剪重建和检测记录。

- 同步排查路径、模型配置、记录下载等接口问题。

---

## 周三：

### 上午 Standup：

汇报 APP 联调进度、已修复问题和当天目标。

- 帮助发布组A部署网页，重点保证登录、模型管理、单图检测、批量检测、大图裁剪重建、检测记录可演示。

- 整理 README、运行命令、依赖安装和常见错误。

### 下午：

帮助科研组A完成数据集部分数据的整理

---

## 周四：

### 上午：

1. 学习智能体辅助开发和 Loop Engineer 工作流。使用智能体检查 app\.py、detect\_engine\.py、database\.py 的关键风险。

### 下午：

演示系统运行、模型加载、检测流程和接口联调过程。

> （注：部分内容可能由 AI 生成）
