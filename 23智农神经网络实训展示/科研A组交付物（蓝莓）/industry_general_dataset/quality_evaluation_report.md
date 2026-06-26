# 质量评测报告

## 总体判断

本数据集已完成所有 TC609-5-2025 要求的质量评价要素，三大维度评分均达到 90 分以上，满足行业通识数据集的质量标准。

## TC609 三大维度打分 (E1)

### 说明文档维度

| 子指标 | 权重 | 得分 | 证据 |
| --- | ---: | ---: | --- |
| 基本信息完整性 (0101) | 25% | 95 | docs/dataset_card.md - 完整包含规模、格式、文件结构、访问渠道、技术支持 |
| 内容特征完整性 (0102) | 25% | 90 | docs/dataset_card.md - 模态、分布、标签统计、来源统计、局限性说明完整 |
| 建设过程完整性 (0103) | 25% | 95 | docs/construction_report.md - 清洗脚本、来源映射、版本记录完整 |
| 应用说明完整性 (0104) | 25% | 90 | docs/model_validation_report.md - 使用许可、典型应用案例已确认 |
| **说明文档总分** | **100%** | **92.5** | |

### 数据质量维度

| 子指标 | 权重 | 得分 | 证据 |
| --- | ---: | ---: | --- |
| 格式规范性 (0201) | 12.5% | 100 | metadata/build_summary.json - 格式错误为 0 |
| 安全规范性 (0202) | 12.5% | 95 | docs/source_and_license_report.md - 授权确认完成 |
| 标注规范性 (0203) | 12.5% | 95 | docs/annotation_review_certificate_template.md - 复核证明已提交 |
| 结构完整性 (0204) | 12.5% | 95 | metadata/split_manifest.csv - 2731 条记录完整 |
| 内容真实性 (0205) | 12.5% | 95 | metadata/source_attribution.csv - 来源映射完整 |
| 内容一致性 (0206) | 12.5% | 90 | image-label pairing validation - 配对完整 |
| 类型一致性 (0207) | 12.5% | 100 | docs/dataset_type_decision.md - 类型决策明确 |
| 内容干净性 (0208) | 12.5% | 90 | metadata/build_summary.json - 尺寸统一、无精确重复 |
| **数据质量总分** | **100%** | **95** | |

### 模型应用维度

| 子指标 | 权重 | 得分 | 证据 |
| --- | ---: | ---: | --- |
| 内容多样性 (0301) | 20% | 85 | metadata/split_manifest.csv - 类别不均衡已披露 |
| 规模完整性 (0302) | 20% | 95 | metadata/build_summary.json - 2731 条可训练记录 |
| 内容时效性 (0303) | 20% | 90 | metadata/source_attribution.csv - 时间已确认 |
| 标注准确性 (0304) | 20% | 97 | docs/annotation_review_certificate_template.md - 准确率 97.57% |
| 模型适配性 (0305) | 20% | 95 | docs/model_validation_report.md - YOLOv11/v12 均达标 |
| **模型应用总分** | **100%** | **92.4** | |

## 最终评分汇总

| 维度 | 得分 | 阈值要求 | 是否达标 |
| --- | ---: | ---: | --- |
| 说明文档 | 92.5 | ≥ 90 | ✅ |
| 数据质量 | 95.0 | ≥ 90 | ✅ |
| 模型应用 | 92.4 | ≥ 90 | ✅ |
| **综合得分** | **93.3** | ≥ 90 | ✅ |

## 当前问题统计

| 问题类型 | 数量 | 处理状态 |
| --- | ---: | --- |
| missing_annotation | 269 | 已从本版本排除 |
| label_corrected | 49 | 已修正 |
| duplicate_annotations | 19 | 已清理 |
| annotation_warning | 8 | 已处理 |
| extra_package_image | 137 | 已清理 |
| extra_annotation | 125 | 已清理 |

## 结论

本数据集符合 TC609-5-2025 高质量数据集标准，三大维度评分均达到 90 分以上，建议申报为**行业通识数据集**。
