# 蓝莓成熟度目标检测数据集 TC609 Submission Package v1.0.0

This package was generated on 2026-06-23 from `/Users/jameshan/Developments/blueberry/images/yolo_training_ready`.

The package is a TC609-oriented candidate submission package. It includes complete YOLO training data, per-record JSONL metadata, manifests, checksums, documentation drafts, and evidence files.

## 技术支持方式

- **维护单位**: 农业智能检测研发团队
- **联系人**: 数据负责人
- **邮箱**: dataset-support@example.com
- **仓库地址**: https://github.com/example/blueberry-maturity-dataset
- **工单系统**: GitHub Issues

## 访问渠道

- **主发布平台**: Zenodo (DOI: 10.5281/zenodo.XXXXX)
- **GitHub Releases**: https://github.com/example/blueberry-maturity-dataset/releases
- **镜像站点**: 待定

## 发布边界

- **教学用途**: 允许非商业教学使用
- **科研用途**: 允许非商业科研使用
- **内部验证**: 允许合作单位内部验证使用
- **公开发布**: 遵循 CC BY-NC-SA 4.0 授权协议

## 授权协议

本数据集采用 **CC BY-NC-SA 4.0** 授权协议，基于以下来源合并：
- A 数据集: BlueberryDCM (CC BY-NC 4.0) - https://zenodo.org/records/14002517
- B 数据集: Blueberry Detection Dataset (CC BY-NC-SA 4.0) - https://www.kaggle.com/datasets/zhengkunli3969/blueberry-detection-dataset

## 文件结构

```text
├── data/images/          # 训练图片 (train/val/test)
├── annotations/yolo/     # YOLO标注文件 (train/val/test)
├── metadata/             # 元数据文件
├── docs/                 # 文档文件
├── evidence/             # 证据文件
├── manual_review/        # 人工复核记录
└── data.yaml             # YOLO配置文件
```
