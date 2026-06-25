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
| 技术支持方式 | 待项目负责人确认正式联系人、邮箱、仓库或工单系统 |
| 访问渠道 | 待项目负责人确认网盘、仓库、内网系统或正式发布路径 |

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

当前包已生成逐条元数据记录和 `metadata/source_attribution.csv`。A/B 来源已按公开页面和文件名规则形成映射，并已完成中置信度记录复查；正式对外发布前仍应保留授权、删减范围和发布边界的人工确认记录。

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
- 标注准确性已完成 40 张、856 框阶段性抽样复核；该比例可支撑候选包预评估，但不能等同于 10%/300 张正式抽检。
- 技术支持方式和访问渠道仍为待确认项，正式发布前必须回填真实联系人和交付路径。
- 图片首次出现时间采用来源级发布日期/修改日期；如审核要求逐图拍摄时间，应补充原始采集记录或保留限制说明。
