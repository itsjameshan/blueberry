# 蓝莓成熟度目标检测数据集 Dataset Card

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 数据集名称 | 蓝莓成熟度目标检测数据集 |
| 版本 | 1.0.0 |
| 评估/构建日期 | 2026-06-23 |
| 数据集类型建议 | 行业通识数据集（农业/智慧农业方向） |
| 目标任务 | 蓝莓成熟度目标检测 |
| 模态类型 | image |
| 样本记录数 | 2731 |
| 目标框总数 | 40218 |
| 图片尺寸 | 640x640 |
| 类别 | RipeBlueBerry, Semi-RipeBlueBerry, UnripeBlueBerry |
| 技术支持方式 | GitHub Issues / 邮件 |
| 访问渠道 | Zenodo / GitHub Releases |

## 文件结构

```text
data/images/<split>/*.jpg
annotations/yolo/<split>/*.txt
metadata/dataset_records.jsonl
metadata/split_manifest.csv
metadata/source_license.csv
metadata/field_completion_status.csv
docs/*.md
evidence/
data.yaml
```

## 数据划分

| split | 图片数 |
| --- | ---: |
| train | 2194 |
| validation | 266 |
| test | 271 |

## 标签类别统计

| 类别 | 目标框数 |
| --- | ---: |
| RipeBlueBerry | 8556 |
| Semi-RipeBlueBerry | 6492 |
| UnripeBlueBerry | 25170 |

## 使用许可和来源状态

当前包已生成逐条元数据记录和 `metadata/source_attribution.csv`。A/B 来源可按公开页面和文件名规则形成候选映射，但最终提交前仍需数据负责人确认文件名映射、授权适用性和删减范围。

| 来源代码 | 记录数 |
| --- | ---: |
| A_ZENODO_BLUEBERRY_DCM | 736 |
| B_KAGGLE_BLUEBERRY_DETECTION | 1995 |
| SOURCE_REQUIRES_CONFIRMATION | 0 |

| 来源置信度 | 记录数 |
| --- | ---: |
| high | 2590 |
| medium | 141 |
| requires_confirmation | 0 |

## 局限性

- 本版本仅包含已清洗并成功导出的 2731 条记录，不包含原始分配集中缺少可用标注的 269 张图片。
- 类别分布不均衡，`UnripeBlueBerry` 目标框数量明显高于另外两类。
- 标注准确性尚缺少独立复核签字或抽检报告。
- 来源映射、授权适用性和图片首次出现时间仍需负责人复核确认。
