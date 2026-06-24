# 文件清单

证据包目录：`/Users/jameshan/Developments/blueberry/tc609_industry_general_evidence_bundle`

本清单逐项说明每个文件的用途。完整图片和 YOLO 标签已经移动到本证据包内的 `data/` 和 `annotations/`。原提交包路径下保留符号链接，旧路径仍可访问。

## 顶层文件

| 文件 | 用途 |
| --- | --- |
| `README.md` | 本证据包的入口说明，解释结论、包含范围和数据体位置。 |
| `FILE_MANIFEST.md` | 本文件，说明所有文件分别用于什么。 |
| `HUMAN_CONFIRMATION_CHECKLIST.md` | 人工确认事项总清单，列出授权、来源、标注、技术支持、访问渠道、模型阈值等需要人工完成的工作。 |
| `WORK_ASSIGNMENT_PLAN.md` | 项目负责人用来派工的工作分配计划，按角色列出任务、输入文件、输出物、完成标准。 |
| `PLAN.md` | 按 Superpowers planning 生成并执行过的总计划，包含标准映射、任务、验证命令和完成勾选。 |
| `PACKAGE_README.md` | 原 TC609 候选提交包的 README 副本，说明包是如何从 `yolo_training_ready` 生成的。 |
| `data.yaml` | YOLO 数据集配置，指向包内训练、验证、测试路径和三类蓝莓成熟度标签。 |

## `data/`

| 路径 | 用途 |
| --- | --- |
| `data/images/train/` | 训练集图片，共 2194 张。 |
| `data/images/validation/` | 验证集图片，共 266 张。 |
| `data/images/test/` | 测试集图片，共 271 张。 |

## `annotations/`

| 路径 | 用途 |
| --- | --- |
| `annotations/yolo/train/` | 训练集 YOLO 标签，共 2194 个。 |
| `annotations/yolo/validation/` | 验证集 YOLO 标签，共 266 个。 |
| `annotations/yolo/test/` | 测试集 YOLO 标签，共 271 个。 |

## `docs/`

| 文件 | 用途 |
| --- | --- |
| `docs/dataset_card.md` | 数据集卡片，说明名称、版本、规模、类别、split、来源统计、局限性、访问和技术支持待确认项。 |
| `docs/dataset_type_decision.md` | 数据集类型判定说明，按 TC609-5-2025-03 图1 判断当前为行业通识候选，并列出升级行业专识的门槛。 |
| `docs/source_and_license_report.md` | 来源与授权报告，说明 A 数据集、B 数据集的 URL/DOI、许可和人工复核要求。 |
| `docs/tc609_requirements_traceability.md` | TC609 要求追溯表，把 TC609-5-2025-01/02/04 的关键要求映射到当前证据文件。 |
| `docs/construction_report.md` | 数据集建设说明，覆盖数据需求、规划、采集、预处理、标注、模型验证。 |
| `docs/quality_evaluation_report.md` | 质量评测报告草案，按说明文档、数据质量、模型应用三大维度列出 PASS/PARTIAL/BLOCKED 状态。 |
| `docs/model_validation_report.md` | 模型验证报告，记录 YOLOv11/YOLOv12 训练结果和仍需补充的独立测试信息。 |
| `docs/annotation_spec.md` | 标注规范，定义三类标签、YOLO 格式、框选规则和验收规则。 |
| `docs/annotation_review_certificate_template.md` | 标注复核证明模板，人工复核后填写，用于解除标注准确性阻塞项。 |
| `docs/completion_plan.md` | 待补充信息完善方案，列出原始时间、授权、来源、技术支持、访问渠道、标注复核、质量评分等必须补齐项。 |

## `metadata/`

| 文件 | 用途 |
| --- | --- |
| `metadata/dataset_records.jsonl` | TC609-5-2025-02 风格逐条记录元数据，共 2731 行，每行对应一张图片。 |
| `metadata/dataset_schema.json` | 数据集 schema 和统计摘要，说明字段、类别、来源证据、记录格式。 |
| `metadata/split_manifest.csv` | 训练/验证/测试划分清单，包含每条记录的图片、标签、尺寸、目标数、类别数和哈希。 |
| `metadata/source_attribution.csv` | 逐条来源归属表，标明 A/B 来源、置信度、授权、来源详情和来源证据。 |
| `metadata/source_license.csv` | 逐条授权/来源完成状态表，用于负责人复核和回填。 |
| `metadata/field_completion_status.csv` | TC609 必填字段完成状态和证据/待处理说明。 |
| `metadata/quality_metrics.json` | 机器可读质量指标映射，覆盖 0101-0104、0201-0208、0301-0305。 |
| `metadata/model_metrics.csv` | 从训练 ZIP 的 `results.csv` 自动抽取的 YOLOv11/YOLOv12 最佳指标。 |
| `metadata/build_summary.json` | 构建统计和验证摘要，包括记录数、split、类别、来源、问题统计。 |
| `metadata/checksums.sha256` | 候选提交包静态文件校验和清单，用于确认文件未被修改。 |

## `manual_review/`

| 文件 | 用途 |
| --- | --- |
| `manual_review/medium_confidence_source_review.csv` | 141 条中置信度来源映射复查表，已留出 `review_result/reviewer/review_date/notes` 字段供人工填写。 |
| `manual_review/work_assignment_matrix.csv` | 派工矩阵模板，项目负责人可填写负责人、截止日期、状态、交付物链接。 |

## `evidence/logs/`

| 文件 | 用途 |
| --- | --- |
| `evidence/logs/01_baseline.log` | 原始 `yolo_training_ready` 输入验证日志，证明 2731 图/2731 标签配对且 YOLO 错误为 0。 |
| `evidence/logs/02_source_type.log` | 来源映射、类型判定和包级验证日志。 |
| `evidence/logs/03_format.log` | TC609 格式字段、JSONL、路径、bbox、checksum 验证日志。 |
| `evidence/logs/04_construction_docs.log` | 建设生命周期文档检查日志。 |
| `evidence/logs/05_quality.log` | 质量指标映射和 TC609-5-2025-04 回看检查日志。 |
| `evidence/logs/06_model.log` | 模型证据检查日志。 |
| `evidence/logs/07_build.log` | 最终构建输出日志。 |
| `evidence/logs/07_final.log` | 最终全量验证日志，显示记录、校验和、文档、质量、模型错误数均为 0。 |

## `evidence/reports/`

| 文件 | 用途 |
| --- | --- |
| `evidence/reports/summary.md` | 标注清洗摘要，记录 3000 原图、2731 导出对、269 缺标、40218 目标框等。 |
| `evidence/reports/issues.csv` | 清洗过程问题清单，包括缺标、重复标注、标签修正、额外图片/标注等。 |
| `evidence/reports/exclusion_report.csv` | 被排除样本说明。 |
| `evidence/reports/retake_report.csv` | 需返工或重拍相关记录。 |
| `evidence/reports/training_manifest.csv` | 训练数据清单，保留组别、标注来源、原始路径等过程字段。 |
| `evidence/reports/group_person_summary.csv` | 分组/人员标注完成情况统计。 |
| `evidence/reports/package_summary.csv` | 包级统计摘要。 |
| `evidence/reports/missing_annotations.csv` | 缺少可用标注的图片清单。 |
| `evidence/reports/files.csv` | 清洗过程中识别到的文件级清单。 |

## `evidence/qc/`

| 文件 | 用途 |
| --- | --- |
| `evidence/qc/contact_sheet.jpg` | 标注/清洗视觉抽查 contact sheet。 |
| `evidence/qc/sample_contact_sheet.jpg` | 样例视觉抽查图，用于人工快速检查图像和标注表现。 |

## `evidence/training_results/`

| 文件 | 用途 |
| --- | --- |
| `evidence/training_results/blueberry1.v4i.yolov11数据集yolov11训练结果.zip` | YOLOv11 训练结果证据包，包含 results.csv、曲线图、混淆矩阵、权重等。 |
| `evidence/training_results/blueberry.v4i.yolov12数据集yolov12训练结果.zip` | YOLOv12 训练结果证据包，包含 results.csv、曲线图、混淆矩阵、权重等。 |

## `tools/`

| 文件 | 用途 |
| --- | --- |
| `tools/build_tc609_submission_package.py` | 构建脚本，生成 TC609 候选包、元数据、文档、质量指标、模型指标和校验和。 |
| `tools/validate_tc609_package.py` | 验证脚本，检查输入数据、包结构、JSONL 字段、bbox、checksum、文档、质量指标、模型证据。 |

## `tests/`

| 文件 | 用途 |
| --- | --- |
| `tests/test_tc609_package.py` | 单元测试，覆盖 YOLO 输入验证、包字段/校验和错误、来源推断、日志不纳入校验和等行为。 |

## `standards_extracts/`

| 文件 | 用途 |
| --- | --- |
| `standards_extracts/tc609_01_construction.txt` | 从 TC609-5-2025-01 建设指南 DOCX 抽取的可检索文本，用于回看建设生命周期要求。 |
| `standards_extracts/tc609_02_format.txt` | 从 TC609-5-2025-02 格式要求 PDF 抽取的可检索文本，用于回看字段和附录 A。 |
| `standards_extracts/tc609_03_classification.txt` | 从 TC609-5-2025-03 分类指南 PDF 抽取的可检索文本，用于回看图1和行业通识/行业专识判定。 |
| `standards_extracts/tc609_04_quality.txt` | 从 TC609-5-2025-04 质量评测规范 DOCX 抽取的可检索文本，用于回看 90 分阈值和 0101-0305 指标。 |
