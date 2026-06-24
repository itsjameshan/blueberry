# 数据集建设说明书

## 数据需求

本数据集面向蓝莓成熟度目标检测任务，目标是在图像中定位蓝莓并识别成熟度类别。类别限定为 `RipeBlueBerry`、`Semi-RipeBlueBerry`、`UnripeBlueBerry` 三类。

## 数据规划

当前冻结版本定义为 1.0.0，纳入已通过清洗并导出的 2731 条记录。数据按训练、验证、测试三部分组织：train 2194 条，validation 266 条，test 271 条。

## 数据采集

本数据集由用户说明的 A/B 两个公开数据集子集整合而来。当前构建脚本按文件名规则形成候选来源映射：A 数据集为 Zenodo BlueberryDCM，B 数据集为 Kaggle Blueberry Detection dataset。映射结果写入 `metadata/source_attribution.csv`；未匹配或低置信样本需由数据负责人复核后才能作为最终来源证据。

| 来源代码 | 记录数 | 主要证据 |
| --- | ---: | --- |
| A_ZENODO_BLUEBERRY_DCM | 736 | Zenodo DOI、ScienceDirect 论文、MSState/MSU 文件名前缀 |
| B_KAGGLE_BLUEBERRY_DETECTION | 1995 | Kaggle 页面 JSON-LD、DSCF/MVIMG/Roboflow 风格文件名 |
| SOURCE_REQUIRES_CONFIRMATION | 0 | 未匹配规则，需人工确认 |

## 数据预处理

已有清洗流程完成以下工作：

- 将可用 LabelMe/YOLO 标注统一导出为 YOLO 格式。
- 修正 49 行标签拼写问题。
- 排除 269 张缺少可用标注的原始图片。
- 排除 137 张包内额外图片和 125 个额外标注。
- 对 19 项重复标注选择目标框更多的版本导出。
- 生成训练清单、问题清单、剔除报告和返工报告。

## 数据标注

当前标签文件为 YOLO normalized xywh 格式，每行包含 `class_id x_center y_center width height`。类别 ID 为：0 `RipeBlueBerry`，1 `Semi-RipeBlueBerry`，2 `UnripeBlueBerry`。

## 模型验证

本地训练结果显示：

| 模型 | 最佳轮次 | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| YOLOv11 | 96 | 0.82148 | 0.83968 | 0.88664 | 0.71022 |
| YOLOv12 | 77 | 0.85001 | 0.84318 | 0.89212 | 0.73313 |

上述结果可作为模型验证证据，但正式认定高质量数据集前，还需补充目标性能阈值、独立测试评估方法和复现实验说明。
