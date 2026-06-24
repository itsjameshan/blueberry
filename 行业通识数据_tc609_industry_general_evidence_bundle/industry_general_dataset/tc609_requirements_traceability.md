# TC609 要求追溯表

## TC609-5-2025-01 建设生命周期

| 阶段 | 要求 | 当前证据 | 状态 | 后续动作 |
| --- | --- | --- | --- | --- |
| 数据需求 | 明确数据范围、内容、可用性、质量模型 | 目标任务、三类标签、2731 条记录、train/validation/test 划分 | PARTIAL | 补正式质量模型和目标阈值 |
| 数据规划 | 设计数据架构、计划、工作量 | `PLAN.md`、JSONL/CSV/Markdown 包结构、清洗报告 | PASS_FOR_CANDIDATE | 审批正式计划 |
| 数据采集 | 明确采集方式和来源质量 | A/B 公开数据集来源映射、许可和来源报告 | PARTIAL | 复核 141 条中置信度映射和授权适用性 |
| 数据预处理 | 转换、验证、清洗、聚合、抽样 | `annotation_cleaned/reports/summary.md`、2731 对配对、269 张缺标排除 | PASS_FOR_CANDIDATE | 保存原始处理脚本执行记录 |
| 数据标注 | 标注规程、人员资源、过程质量管理 | `docs/annotation_spec.md`、YOLO 格式验证、标签修正统计 | PARTIAL | 补抽检/专家复核证明 |
| 模型验证 | 训练模型并反馈数据质量问题 | YOLOv11/YOLOv12 本地训练结果，最佳 mAP50 见 `metadata/model_metrics.csv` | PARTIAL | 补独立 test 评测、阈值和复现实验说明 |

## TC609-5-2025-02 格式要求

| 字段 | 当前实现 |
| --- | --- |
| id | `sha256:<image hash>` |
| rid | 当前为空数组，保留关联扩展能力 |
| data_content | 图像模态、相对路径、宽高、SHA-256 |
| annotation | 标签数组、YOLO 文件、标注方式、标注人员类型 |
| original_time | 来源级发布日期/修改日期；逐图原始时间需确认 |
| last_modified_time | 本地图片/标签较晚修改日期 |
| version | 1.0.0 |
| license | A/B 来源授权候选值 |
| source | 公开数据集 |
| source_details | Zenodo DOI 或 Kaggle URL |
| generated_data_indicator | 0 |

## TC609-5-2025-04 评测状态

最终状态：高质量数据集候选包。不得在来源复核、标注复核和模型独立验证完成前声明三大维度均达到 90 分。
