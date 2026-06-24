# 项目负责人派工计划

这个文件是项目负责人分配人工工作的主文件。建议把每个任务分配给明确责任人，并同步填写 `manual_review/work_assignment_matrix.csv` 的 `assignee`、`due_date`、`status`、`deliverable_link` 字段。

## 如何使用

1. 先确认最终申报口径：当前建议为“行业通识数据集候选”。
2. 按下表分配责任人，每个任务指定一个 owner。
3. owner 完成后，把证据文件放回本证据包对应路径。
4. 质量负责人根据完成证据更新 `docs/quality_evaluation_report.md` 和 `metadata/quality_metrics.json`。
5. 最后重新运行构建和验证脚本。

## 派工总表

| 任务 ID | 工作包 | 建议角色 | 输入文件 | 需要完成的输出 | 完成标准 |
| --- | --- | --- | --- | --- | --- |
| A1 | A 数据集授权确认 | 数据负责人/法务 | `docs/source_and_license_report.md`, `metadata/source_attribution.csv` | A 来源授权确认说明 | 明确 CC BY-NC 4.0 是否允许本项目合并、再标注、再分发和使用场景 |
| A2 | B 数据集授权确认 | 数据负责人/法务 | `docs/source_and_license_report.md`, `metadata/source_attribution.csv` | B 来源授权确认说明 | 明确 CC BY-NC-SA 4.0 的署名、非商业、相同方式共享要求 |
| A3 | 141 条中置信度来源复查 | 数据负责人 | `manual_review/medium_confidence_source_review.csv` | 填完的复查 CSV | 141 行全部填写 `review_result/reviewer/review_date/notes` |
| A4 | 原始时间确认 | 数据负责人 | `metadata/source_attribution.csv`, 原始采集/下载记录 | 原始时间确认说明或回填表 | 明确使用来源发布时间/修改时间是否可接受；不可接受则补逐图时间 |
| A5 | 来源详情增强 | 数据负责人 | `metadata/source_license.csv`, `metadata/source_attribution.csv` | 完整来源详情表 | 每条记录可追溯到 URL/DOI/版本/文件名/授权依据 |
| B1 | 标注抽检方案 | 质量负责人 | `docs/annotation_spec.md`, `metadata/split_manifest.csv` | 抽检方案 | 写明抽样比例、按 split/类别/来源分层规则、判定标准 |
| B2 | 标注人工复核 | 复核人/农业视觉专家 | `data/`, `annotations/`, `evidence/qc/` | 复核问题记录 | 记录漏标、错标、框偏移、重复框、类别混淆数量 |
| B3 | 标注复核证明 | 复核人 | `docs/annotation_review_certificate_template.md` | 已填写复核证明 | 包含复核人、资质/角色、日期、范围、结果和结论 |
| C1 | 技术支持方式确认 | 项目负责人 | `docs/dataset_card.md` | 技术支持信息 | 填维护单位、联系人、邮箱、仓库或工单地址 |
| C2 | 访问渠道确认 | 项目负责人 | `docs/dataset_card.md`, `PACKAGE_README.md` | 访问渠道说明 | 填网盘、仓库、内网系统或正式发布路径 |
| C3 | 发布边界确认 | 项目负责人/法务 | `docs/source_and_license_report.md` | 发布边界说明 | 写清教学、科研、内部验证或公开发布条件 |
| D1 | 模型目标阈值设定 | 模型负责人 | `metadata/model_metrics.csv`, `docs/model_validation_report.md` | 目标阈值说明 | 明确 mAP50、mAP50-95、Recall、误检/漏检等阈值 |
| D2 | 独立测试方案确认 | 模型负责人 | `docs/model_validation_report.md` | 独立测试方案 | 写清训练命令、环境、随机种子、数据版本、评估 split |
| D3 | 独立测试执行 | 模型负责人 | `data/`, `annotations/`, 训练脚本/模型权重 | 独立测试报告 | 输出 test split 指标和失败案例分析 |
| E1 | TC609 三大维度打分 | 质量负责人 | `metadata/quality_metrics.json`, `docs/quality_evaluation_report.md` | 正式评分表 | 说明文档、数据质量、模型应用均给出分子/分母/权重/得分 |
| E2 | 最终申报类型确认 | 项目负责人 | `docs/dataset_type_decision.md` | 最终类型决策 | 确认申报行业通识；若申报行业专识则补内部场景和专家证据 |

## 交付顺序建议

1. 先做 A1-A5：授权和来源不清，后续发布和评分都无法闭环。
2. 再做 B1-B3：标注准确性是模型应用指标的关键阻塞项。
3. 同时做 C1-C3：这些是说明文档完整性的基本项。
4. 然后做 D1-D3：补模型阈值、独立测试和失败案例。
5. 最后做 E1-E2：质量负责人打分，项目负责人确认申报类型。

## 分配后需要更新的文件

| 完成事项 | 更新文件 |
| --- | --- |
| 来源和授权确认完成 | `metadata/source_license.csv`, `docs/source_and_license_report.md` |
| 141 条来源复查完成 | `manual_review/medium_confidence_source_review.csv` |
| 标注复核完成 | `docs/annotation_review_certificate_template.md`, `docs/quality_evaluation_report.md` |
| 技术支持和访问渠道确认 | `docs/dataset_card.md`, `PACKAGE_README.md` |
| 模型阈值和独立测试完成 | `docs/model_validation_report.md`, `metadata/model_metrics.csv` |
| 最终评分完成 | `docs/quality_evaluation_report.md`, `metadata/quality_metrics.json` |
| 最终类型确认 | `docs/dataset_type_decision.md` |

