# 人工确认清单

这些事项不能由脚本替你确认。完成前，建议只表述为“TC609 高质量数据集候选包”或“行业通识数据集候选”，不要写成“已完全满足 TC609 高质量数据集”。

## A. 授权和来源确认

| 序号 | 人工事项 | 为什么必须人工做 | 输入文件 | 输出/完成标准 | 建议责任人 |
| ---: | --- | --- | --- | --- | --- |
| A1 | 确认 A 数据集授权适用性 | A 数据集为 CC BY-NC 4.0，需要确认合并、再标注、再分发、教学/科研用途是否符合非商业授权 | `docs/source_and_license_report.md`, `metadata/source_attribution.csv` | 在 `metadata/source_license.csv` 或单独授权说明中确认 A 来源可用于本包 | 数据负责人/法务或项目负责人 |
| A2 | 确认 B 数据集授权适用性 | B 数据集为 CC BY-NC-SA 4.0，需要确认相同方式共享、非商业、署名和删减后再发布要求 | `docs/source_and_license_report.md`, `metadata/source_attribution.csv` | 在授权说明中写明 B 来源合规边界 | 数据负责人/法务或项目负责人 |
| A3 | 复查 141 条中置信度来源映射 | 这些记录靠 Roboflow 风格文件名映射到 B 数据集，不能只凭脚本作为最终来源证据 | `manual_review/medium_confidence_source_review.csv` | 每行填写 `review_result/reviewer/review_date/notes`；无法确认的样本剔除或标为限制项 | 数据负责人 |
| A4 | 确认逐图或来源级原始时间 | 当前使用来源发布时间/修改时间，不一定是图片实际拍摄时间 | `metadata/source_attribution.csv`, 原始下载包/采集记录 | 明确可接受的时间粒度；必要时补 `original_time` 字段 | 数据负责人 |
| A5 | 确认来源详情是否足够 | TC609-5-2025-02 要求 `source_details` 可追溯；URL/DOI 之外可能还要下载版本、文件名或授权截图 | `metadata/source_attribution.csv`, `metadata/source_license.csv` | `source_details` 足以让第三方追溯到来源 | 数据负责人 |

## B. 标注准确性复核

| 序号 | 人工事项 | 为什么必须人工做 | 输入文件 | 输出/完成标准 | 建议责任人 |
| ---: | --- | --- | --- | --- | --- |
| B1 | 设定抽检比例或全量复核策略 | 脚本只能验证格式，不能证明漏标、错标、框偏移是否满足业务要求 | `docs/annotation_spec.md`, `metadata/split_manifest.csv` | 写明抽检规则，例如按 split/类别/来源分层抽样 | 质量负责人 |
| B2 | 执行标注复核 | TC609 模型应用指标含标注准确性，必须有人看图确认 | 完整数据体 `data/images` 和 `annotations/yolo`; QC 图在 `evidence/qc/` | 记录漏标、错标、框偏移、重复框、类别混淆数量 | 复核人/农业视觉专家 |
| B3 | 填写复核证明 | 没有签字/责任人就不能把标注准确性从 `BLOCKED_BY_REVIEW` 改为通过 | `docs/annotation_review_certificate_template.md` | 生成正式复核证明，含日期、复核人、范围、结果、结论 | 复核人 |
| B4 | 更新质量评测状态 | 复核后需要把报告从候选状态更新为正式状态 | `docs/quality_evaluation_report.md`, `metadata/quality_metrics.json` | 更新 0304 标注准确性和相关数据质量指标 | 质量负责人 |

## C. 技术支持和访问渠道

| 序号 | 人工事项 | 为什么必须人工做 | 输入文件 | 输出/完成标准 | 建议责任人 |
| ---: | --- | --- | --- | --- | --- |
| C1 | 填技术支持方式 | TC609-5-2025-04 的 0101 基本信息完整性要求包含技术支持方式 | `docs/dataset_card.md` | 填维护单位、联系人、邮箱、仓库或工单地址 | 项目负责人 |
| C2 | 填访问渠道 | 说明文档必须让审核方知道如何获取数据 | `docs/dataset_card.md`, `PACKAGE_README.md` | 填网盘、仓库、内网系统、归档路径或发布页 | 项目负责人 |
| C3 | 确认发布边界 | A/B 均为非商业授权，不能随意商业发布 | `docs/source_and_license_report.md` | 写清楚使用范围：教学、科研、内部验证或公开发布条件 | 项目负责人/法务 |

## D. 模型测试阈值和独立验证

| 序号 | 人工事项 | 为什么必须人工做 | 输入文件 | 输出/完成标准 | 建议责任人 |
| ---: | --- | --- | --- | --- | --- |
| D1 | 设定目标性能阈值 | TC609-5-2025-04 的 0305 模型适配性需要与预期性能比较 | `metadata/model_metrics.csv`, `docs/model_validation_report.md` | 写明目标，例如 mAP50、mAP50-95、Recall、误检/漏检阈值 | 模型负责人 |
| D2 | 确认独立测试方案 | 现有训练结果可作为证据，但需要明确是否使用独立 test split、随机种子、硬件和命令 | `docs/model_validation_report.md`, 训练结果 ZIP | 写清训练命令、环境、种子、数据版本、评估 split | 模型负责人 |
| D3 | 执行或补充独立测试 | 只有训练/验证曲线不足以证明最终应用效果 | 完整数据体和训练脚本/模型权重 | 输出独立测试报告和失败案例分析 | 模型负责人 |
| D4 | 更新模型适配性结论 | 没有目标阈值时不能计算 0305 是否达标 | `docs/quality_evaluation_report.md`, `metadata/quality_metrics.json` | 将 0305 从 `PARTIAL` 更新为 PASS/PARTIAL/FAIL，并写明依据 | 质量负责人 |

## E. 最终评分和申报口径

| 序号 | 人工事项 | 为什么必须人工做 | 输入文件 | 输出/完成标准 | 建议责任人 |
| ---: | --- | --- | --- | --- | --- |
| E1 | 按 TC609-5-2025-04 三大维度打分 | 标准要求说明文档、数据质量、模型应用均达到 90 分及以上 | `metadata/quality_metrics.json`, `docs/quality_evaluation_report.md` | 给出每项分子、分母、权重、得分和总分 | 质量负责人 |
| E2 | 决定是否仍按行业通识申报 | 当前证据支持行业通识候选；行业专识需要更多内部业务和专家证据 | `docs/dataset_type_decision.md` | 明确最终申报类型 | 项目负责人 |
| E3 | 如要申报行业专识，补四类证据 | 行业专识要求内部业务场景、专家标注/复核、权限授权、场景模型目标 | `docs/dataset_type_decision.md` | 补齐后重跑构建和验证，重新出类型决策 | 项目负责人/专家复核人 |

## 快速检查

- 141 条来源复查表：`manual_review/medium_confidence_source_review.csv`
- 标注复核模板：`docs/annotation_review_certificate_template.md`
- 候选包剩余事项：`docs/completion_plan.md`
- 最终验证日志：`evidence/logs/07_final.log`

