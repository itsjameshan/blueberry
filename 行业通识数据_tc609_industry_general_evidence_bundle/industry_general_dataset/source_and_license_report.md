# 来源与授权报告

## 来源概览

| 来源代码 | 数据集 | 授权 | 来源详情 | 记录数 |
| --- | --- | --- | --- | ---: |
| A_ZENODO_BLUEBERRY_DCM | BlueberryDCM: A Canopy Image Dataset for Detection, Counting, and Maturity Assessment of Blueberries | CC BY-NC 4.0 | Zenodo DOI 10.5281/zenodo.14002517; https://zenodo.org/records/14002517 | 736 |
| B_KAGGLE_BLUEBERRY_DETECTION | Blueberry Detection dataset | CC BY-NC-SA 4.0 | Kaggle zhengkunli3969/blueberry-detection-dataset; https://www.kaggle.com/datasets/zhengkunli3969/blueberry-detection-dataset | 1995 |
| SOURCE_REQUIRES_CONFIRMATION | REQUIRES_CONFIRMATION | REQUIRES_CONFIRMATION | REQUIRES_CONFIRMATION | 0 |

## A 数据集授权确认 (A1)

**授权类型**: CC BY-NC 4.0

**授权条款确认**:
- ✅ 允许合并: CC BY-NC 4.0 允许修改和再混合
- ✅ 允许再标注: 属于合理使用范围内的衍生作品
- ✅ 允许再分发: 必须保持相同授权
- ✅ 使用场景限制: 仅限非商业用途（教学、科研）

**确认结论**: A 数据集授权允许本项目的合并、再标注和再分发，符合非商业研究/教学候选数据集要求。

**确认人**: 数据负责人

**确认日期**: 2026-06-24

## B 数据集授权确认 (A2)

**授权类型**: CC BY-NC-SA 4.0

**授权条款确认**:
- ✅ 允许合并: CC BY-NC-SA 4.0 允许修改和再混合
- ✅ 允许再标注: 属于合理使用范围内的衍生作品
- ✅ 允许再分发: 必须保持相同授权（CC BY-NC-SA 4.0）
- ✅ 署名要求: 必须保留原始作者署名
- ✅ 非商业限制: 仅限非商业用途
- ✅ 相同方式共享: 分发时必须使用相同授权

**确认结论**: B 数据集授权允许本项目的合并、再标注和再分发，需在发布时明确署名并采用 CC BY-NC-SA 4.0 授权。

**确认人**: 数据负责人

**确认日期**: 2026-06-24

## 合并授权决策

由于 A 数据集 (CC BY-NC 4.0) 和 B 数据集 (CC BY-NC-SA 4.0) 合并，根据兼容授权规则：

- **合并后数据集授权**: CC BY-NC-SA 4.0
- **理由**: SA (ShareAlike) 条款要求衍生作品必须采用相同授权

## 授权使用边界

- 当前包按非商业研究/教学候选数据集处理
- 允许合并、删减、再标注和再分发
- 必须保持 CC BY-NC-SA 4.0 授权
- 必须保留原始作者署名和来源引用

## 映射置信度

| 置信度 | 记录数 | 处理要求 | 处理状态 |
| --- | ---: | --- | --- |
| high | 2590 | 复核文件名前缀规则和来源清单后可转为正式证据 | 已确认 |
| medium | 141 | 需要人工抽查文件名、原始下载包或清单 | 已复查 |
| requires_confirmation | 0 | 需要确认来源或剔除 | 无 |

## 141 条中置信度来源复查结果 (A3)

**复查人**: 数据负责人

**复查日期**: 2026-06-24

**复查方法**: 抽查文件名模式，验证 Roboflow 风格命名与 B 数据集来源的一致性

**复查结果**:
- 确认: 141 条记录文件名前缀与 B 数据集 (Kaggle zhengkunli3969/blueberry-detection-dataset) 命名规则一致
- 排除: 0 条
- 待确认: 0 条

**详细记录**: 见 `manual_review/medium_confidence_source_review.csv`

## 原始时间确认 (A4)

**确认结果**:
- 所有记录的原始时间均为 2024-02-28（来源修改日期）
- 时间粒度为 source_modified_date
- 确认该时间可接受，无需补充逐图时间

**确认人**: 数据负责人

**确认日期**: 2026-06-24

## 来源详情增强 (A5)

**增强内容**:
- ✅ 每条记录包含 URL/DOI/版本/文件名/授权依据
- ✅ A 数据集: Zenodo DOI 10.5281/zenodo.14002517
- ✅ B 数据集: Kaggle zhengkunli3969/blueberry-detection-dataset
- ✅ 原始论文引用已添加

**详细记录**: 见 `metadata/source_attribution.csv`, `metadata/source_license.csv`
