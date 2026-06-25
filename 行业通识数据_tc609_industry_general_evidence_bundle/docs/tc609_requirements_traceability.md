# TC609 要求追溯表

## TC609-5-2025-01 建设生命周期

| 阶段 | 要求 | 当前证据 | 状态 | 后续动作 |
| --- | --- | --- | --- | --- |
| 数据需求 | 明确数据范围、内容、可用性、质量模型 | 目标任务、三类标签、2731 条记录、train/validation/test 划分、质量预评估指标 | PASS_FOR_CANDIDATE | 正式申报前确认质量模型审批口径 |
| 数据规划 | 设计数据架构、计划、工作量 | `PLAN.md`、JSONL/CSV/Markdown 包结构、清洗报告 | PASS_FOR_CANDIDATE | 审批正式计划 |
| 数据采集 | 明确采集方式和来源质量 | A/B 公开数据集来源映射、许可和来源报告、141 条中置信度复查 | PASS_FOR_CANDIDATE | 正式发布前保留授权证据和发布边界确认 |
| 数据预处理 | 转换、验证、清洗、聚合、抽样 | `annotation_cleaned/reports/summary.md`、2731 对配对、269 张缺标排除 | PASS_FOR_CANDIDATE | 保存原始处理脚本执行记录 |
| 数据标注 | 标注规程、人员资源、过程质量管理 | `docs/annotation_spec.md`、YOLO 格式验证、标签修正统计、40 张/856 框阶段性复核 | PASS_FOR_CANDIDATE | 如需更高置信度，补抽至约 273-300 张 |
| 模型验证 | 训练模型并反馈数据质量问题 | YOLOv11/YOLOv12 训练结果、test split 指标、失败案例分析 | PASS_FOR_CANDIDATE | 外部泛化测试作为后续增强项 |

## TC609-5-2025-02 格式要求

| 字段 | 当前实现 |
| --- | --- |
| id | `sha256:<image hash>` |
| rid | 当前为空数组，保留关联扩展能力 |
| data_content | 图像模态、相对路径、宽高、SHA-256 |
| annotation | 标签数组、YOLO 文件、标注方式、标注人员类型 |
| original_time | 来源级发布日期/修改日期；如审核要求逐图拍摄时间需补充原始记录 |
| last_modified_time | 本地图片/标签较晚修改日期 |
| version | 1.0.0 |
| license | A/B 来源授权值，正式发布前保留授权边界确认 |
| source | 公开数据集 |
| source_details | Zenodo DOI 或 Kaggle URL |
| generated_data_indicator | 0 |

## TC609-5-2025-04 评测状态

最终状态：高质量数据集候选包。当前数据质量和模型应用维度内部预评估达标；说明文档维度因真实技术支持方式、访问渠道待确认，暂不能按正式达标处理。正式发布前还需保留 40 张阶段性抽检的统计置信度限制或补抽至更高比例。
