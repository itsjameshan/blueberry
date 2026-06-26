# 待补充信息完善方案

## 必须补齐后才能声明完全符合 TC609

| 信息项 | 当前状态 | 完善方式 | 建议责任人 |
| --- | --- | --- | --- |
| 原始时间 `original_time` | REQUIRES_CONFIRMATION | 按图片原始采集时间、公开数据发布时间或原始数据集发布时间回填；无法追溯的样本应剔除或披露限制 | 数据负责人 |
| 授权类型 `license` | REQUIRES_CONFIRMATION | 确认开源、公共授权、商业授权、仅内部或其他；保存授权证明 | 数据负责人 |
| 来源类型 `source` | REQUIRES_CONFIRMATION | 按互联网、自采、公开数据集、组织机构等分类 | 数据负责人 |
| 来源详情 `source_details` | REQUIRES_CONFIRMATION | 填 URL、数据集名、采集地点/设备、授权文件编号等 | 数据负责人 |
| 技术支持方式 | REQUIRES_CONFIRMATION | 填联系人、邮箱、仓库地址或维护单位 | 项目负责人 |
| 访问渠道 | REQUIRES_CONFIRMATION | 填数据获取路径、网盘、仓库或内部系统 | 项目负责人 |
| 标注复核证明 | REQUIRES_CONFIRMATION | 完成抽检或全量复核，填写复核模板 | 复核人 |
| 质量评分 | 未最终打分 | 三大维度按 TC609-5-2025-04 给出分子、分母、权重和得分 | 质量负责人 |

## 推荐整改顺序

1. 先确认正式提交范围为 2731 条已清洗记录，不把 269 张缺标图片写入 v1.0.0。
2. 回填 `metadata/source_license.csv` 的来源、授权和原始时间。
3. 若存在无法确认授权或来源的记录，决定剔除还是作为限制项披露。
4. 完成标注抽检，填写 `docs/annotation_review_certificate_template.md`。
5. 将 `docs/quality_evaluation_report.md` 从草案更新为正式评分报告。
6. 重新运行 `tools/build_tc609_submission_package.py` 生成最终包和校验和。

## 可接受的阶段性表述

可以表述为：本数据集已完成 TC609 格式化整理，具备 YOLO 目标检测训练可用性，当前为高质量数据集候选提交包。

不建议表述为：本数据集已完全符合 TC609-5-2025-01/02/03/04。
