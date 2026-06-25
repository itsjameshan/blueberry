# TC609 行业通识数据集自证材料包

本文件夹汇总了用于证明“蓝莓成熟度目标检测数据集”为农业/智慧农业方向行业通识数据集候选包的材料。

## 结论

- 当前建议类型：行业通识数据集候选。
- 当前可表述：数据质量和模型应用维度内部预评估达到 90 分阈值，具备申报行业通识数据集候选的基础。
- 当前待补齐：真实技术支持方式和访问渠道未确认，说明文档维度暂不能按正式达标处理。
- 当前不建议直接宣称：已由外部或主管部门认定为 TC609 高质量数据集，或已达到行业专识数据集。
- 数据体位置：`/Users/jameshan/Developments/blueberry/images/tc609_submission_package_v1.0.0`
- 原始 YOLO 数据位置：`/Users/jameshan/Developments/blueberry/images/yolo_training_ready`

## 本证据包包含什么

- 完整数据体：2731 张图片和 2731 个 YOLO 标签。
- TC609 规划与执行清单。
- 数据集说明、建设报告、分类决策、质量评测、来源授权、模型验证等文档。
- 逐条元数据、来源归属、质量指标、模型指标、split 清单。
- 构建和验证日志。
- 清洗报告、标注问题报告、QC contact sheet、训练结果 ZIP。
- 构建脚本、验证脚本、单元测试。
- 从四份 TC609 标准中抽取出的可检索文本。
- 人工确认清单和 141 条中置信度来源复查表。

## 完整数据体位置

完整数据体已经移动到本证据包：

```text
/Users/jameshan/Developments/blueberry/tc609_industry_general_evidence_bundle/data
/Users/jameshan/Developments/blueberry/tc609_industry_general_evidence_bundle/annotations
```

原提交包路径下保留了符号链接，所以旧路径仍可访问。

## 先看哪几个文件

1. `FILE_MANIFEST.md`：所有文件用途清单。
2. `HUMAN_CONFIRMATION_CHECKLIST.md`：还必须人工完成的事项。
3. `WORK_ASSIGNMENT_PLAN.md`：项目负责人分配人工工作的派工表。
4. `manual_review/work_assignment_matrix.csv`：可填负责人、截止日期、状态的派工矩阵。
5. `docs/dataset_type_decision.md`：为什么当前是行业通识候选，不是行业专识。
6. `docs/tc609_requirements_traceability.md`：四份 TC609 标准要求如何映射到材料。
7. `metadata/quality_metrics.json`：机器可读质量评测状态。
8. `evidence/logs/07_final.log`：最终全量验证结果。
