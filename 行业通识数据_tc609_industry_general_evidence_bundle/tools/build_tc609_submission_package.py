#!/usr/bin/env python3
"""Build a TC609-oriented submission package for the blueberry YOLO dataset."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image


REPO = Path("/Users/jameshan/Developments/blueberry")
DATASET = REPO / "images/yolo_training_ready"
PACKAGE = REPO / "images/tc609_submission_package_v1.0.0"
REPORTS = REPO / "images/annotation_cleaned/reports"
QC_DIR = REPO / "images/annotation_cleaned/qc"

CLASSES = {
    0: "RipeBlueBerry",
    1: "Semi-RipeBlueBerry",
    2: "UnripeBlueBerry",
}

CONFIRM = "REQUIRES_CONFIRMATION"
VERSION = "1.0.0"
DATASET_NAME = "蓝莓成熟度目标检测数据集"
BUILD_DATE = "2026-06-23"

SOURCE_A = {
    "source_dataset_code": "A_ZENODO_BLUEBERRY_DCM",
    "source_dataset_name": "BlueberryDCM: A Canopy Image Dataset for Detection, Counting, and Maturity Assessment of Blueberries",
    "source": "公开数据集",
    "source_details": "Zenodo DOI 10.5281/zenodo.14002517; https://zenodo.org/records/14002517",
    "license": "CC BY-NC 4.0",
    "original_time": "2024-10-28",
    "original_time_granularity": "source_release_date",
    "reference": "Deng, B., Lu, Y., Li, Z. (2024). Detection, counting, and maturity assessment of blueberries in canopy images using YOLOv8 and YOLOv9. DOI 10.1016/j.atech.2024.100620.",
}

SOURCE_B = {
    "source_dataset_code": "B_KAGGLE_BLUEBERRY_DETECTION",
    "source_dataset_name": "Blueberry Detection dataset",
    "source": "公开数据集",
    "source_details": "Kaggle zhengkunli3969/blueberry-detection-dataset; https://www.kaggle.com/datasets/zhengkunli3969/blueberry-detection-dataset",
    "license": "CC BY-NC-SA 4.0",
    "original_time": "2024-02-28",
    "original_time_granularity": "source_modified_date",
    "reference": "Li, Zhengkun et al. Blueberry Yield Estimation Through Multi-View Imagery with YOLOv8 Object Detection, ASABE 2023.",
}

MODEL_RESULT_ZIPS = [
    ("YOLOv11", REPO / "blueberry1.v4i.yolov11数据集yolov11训练结果.zip"),
    ("YOLOv12", REPO / "blueberry.v4i.yolov12数据集yolov12训练结果.zip"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def infer_source_attribution(filename: str) -> dict[str, str]:
    stem = Path(filename).stem
    if stem.startswith(("MSState_YL_Cropped_", "MSU_Josh_Cropped_")):
        return {
            **SOURCE_A,
            "source_confidence": "high",
            "source_evidence": "filename prefix matches BlueberryDCM-derived MSState/MSU crop naming",
        }
    if stem.startswith(("DSCF", "MVIMG")):
        return {
            **SOURCE_B,
            "source_confidence": "high",
            "source_evidence": "filename prefix matches Kaggle field-camera image naming in merged local dataset",
        }
    if ".rf." in filename or "_jpg.rf." in filename or "_jpeg_jpg.rf." in filename:
        return {
            **SOURCE_B,
            "source_confidence": "medium",
            "source_evidence": "Roboflow-style filename in the user-described B dataset subset; confirm before final submission",
        }
    return {
        "source_dataset_code": "SOURCE_REQUIRES_CONFIRMATION",
        "source_dataset_name": CONFIRM,
        "source": CONFIRM,
        "source_details": CONFIRM,
        "license": CONFIRM,
        "original_time": CONFIRM,
        "original_time_granularity": CONFIRM,
        "reference": CONFIRM,
        "source_confidence": "requires_confirmation",
        "source_evidence": "no source rule matched this filename",
    }


def ensure_dirs() -> None:
    for rel in [
        "data/images/train",
        "data/images/validation",
        "data/images/test",
        "annotations/yolo/train",
        "annotations/yolo/validation",
        "annotations/yolo/test",
        "metadata",
        "docs",
        "evidence/reports",
        "evidence/qc",
        "evidence/training_results",
    ]:
        (PACKAGE / rel).mkdir(parents=True, exist_ok=True)


def copy_if_needed(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size == src.stat().st_size:
        return
    shutil.copy2(src, dst)


def load_training_manifest() -> dict[str, dict[str, str]]:
    manifest = REPORTS / "training_manifest.csv"
    rows: dict[str, dict[str, str]] = {}
    if not manifest.exists():
        return rows
    with manifest.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            stem = row.get("图片ID", "")
            if stem:
                rows[stem] = row
    return rows


def load_issue_counts() -> Counter[str]:
    issues = REPORTS / "issues.csv"
    counts: Counter[str] = Counter()
    if not issues.exists():
        return counts
    with issues.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            counts[row.get("type", "")] += 1
    return counts


def parse_yolo(label_path: Path) -> list[dict[str, object]]:
    labels: list[dict[str, object]] = []
    for index, line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(f"{label_path}: line {index} should have 5 columns")
        class_id = int(float(parts[0]))
        if class_id not in CLASSES:
            raise ValueError(f"{label_path}: line {index} unknown class {class_id}")
        bbox = [round(float(x), 6) for x in parts[1:]]
        if any(v < 0 or v > 1 for v in bbox):
            raise ValueError(f"{label_path}: line {index} bbox outside [0,1]")
        if bbox[2] <= 0 or bbox[3] <= 0:
            raise ValueError(f"{label_path}: line {index} non-positive bbox size")
        labels.append(
            {
                "category": CLASSES[class_id],
                "category_id": class_id,
                "bbox_yolo": bbox,
                "bbox_format": "normalized_xywh",
                "iscrowd": 0,
            }
        )
    return labels


def local_date(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()


def collect_records() -> tuple[list[dict[str, object]], dict[str, object]]:
    manifest = load_training_manifest()
    records: list[dict[str, object]] = []
    split_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    class_counts_by_split: defaultdict[str, Counter[str]] = defaultdict(Counter)
    dimensions: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    source_confidence_counts: Counter[str] = Counter()

    image_root = DATASET / "image"
    label_root = DATASET / "label"
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    images = sorted(
        p
        for p in image_root.rglob("*")
        if p.is_file() and p.suffix.lower() in image_exts and not p.name.startswith(".")
    )

    for image_src in images:
        rel_image_src = image_src.relative_to(image_root)
        split = rel_image_src.parts[0]
        stem = image_src.stem
        label_src = label_root / rel_image_src.with_suffix(".txt")
        if not label_src.exists():
            raise FileNotFoundError(f"Missing label for {image_src}")

        labels = parse_yolo(label_src)
        image_hash = sha256_file(image_src)
        label_hash = sha256_file(label_src)
        record_id = f"sha256:{image_hash}"
        with Image.open(image_src) as image:
            width, height = image.size

        image_dst = PACKAGE / "data/images" / split / image_src.name
        label_dst = PACKAGE / "annotations/yolo" / split / label_src.name
        copy_if_needed(image_src, image_dst)
        copy_if_needed(label_src, label_dst)

        row = manifest.get(stem, {})
        group = row.get("组别", "")
        person = row.get("学生", "")
        original_path = row.get("原始图片路径", "")
        annotation_source = row.get("标注来源", "")
        annotation_source_format = row.get("标注来源格式", "yolo")
        source_info = infer_source_attribution(image_src.name)
        source_complete = source_info["source_dataset_code"] != "SOURCE_REQUIRES_CONFIRMATION"

        split_counts[split] += 1
        dimensions[f"{width}x{height}"] += 1
        source_counts[source_info["source_dataset_code"]] += 1
        source_confidence_counts[source_info["source_confidence"]] += 1
        label_counter = Counter(item["category"] for item in labels)
        for category, count in label_counter.items():
            class_counts[category] += count
            class_counts_by_split[split][category] += count

        record = {
            "id": record_id,
            "rid": [],
            "data_content": [
                {
                    "media_type": ["image"],
                    "content": f"data/images/{split}/{image_src.name}",
                    "width": width,
                    "height": height,
                    "sha256": image_hash,
                }
            ],
            "annotation": {
                "label": labels,
                "annotation_method": "人工标注",
                "annotator": "普通标注员",
                "annotation_file": f"annotations/yolo/{split}/{label_src.name}",
                "annotation_format": "YOLO normalized xywh",
                "annotation_sha256": label_hash,
                "annotation_source_format": annotation_source_format,
                "annotation_source": annotation_source,
            },
            "original_time": source_info["original_time"],
            "last_modified_time": max(local_date(image_src), local_date(label_src)),
            "version": VERSION,
            "license": source_info["license"],
            "source": source_info["source"],
            "source_details": source_info["source_details"],
            "generated_data_indicator": 0,
            "tc609_completion_status": {
                "id": "COMPLETE",
                "data_content": "COMPLETE",
                "annotation": "COMPLETE",
                "original_time": "COMPLETE_FROM_SOURCE_LEVEL_DATE" if source_complete else "BLOCKED_BY_SOURCE_CONFIRMATION",
                "last_modified_time": "COMPLETE_FROM_LOCAL_FILE_MTIME",
                "version": "COMPLETE",
                "license": "COMPLETE_FROM_SOURCE_LICENSE" if source_complete else "BLOCKED_BY_AUTHORIZATION_CONFIRMATION",
                "source": "COMPLETE_FROM_SOURCE_RULE" if source_complete else "BLOCKED_BY_SOURCE_CONFIRMATION",
                "source_details": "COMPLETE_FROM_SOURCE_RULE" if source_complete else "BLOCKED_BY_SOURCE_CONFIRMATION",
                "generated_data_indicator": "COMPLETE_ASSUMED_NON_GENERATED_FROM_PROJECT_CONTEXT",
            },
            "project_extension": {
                "split": split,
                "original_image_path": original_path,
                "group": group,
                "annotator_name_or_student": person,
                "object_count": len(labels),
                "class_counts": dict(label_counter),
                "source_dataset_code": source_info["source_dataset_code"],
                "source_dataset_name": source_info["source_dataset_name"],
                "source_confidence": source_info["source_confidence"],
                "source_evidence": source_info["source_evidence"],
                "source_reference": source_info["reference"],
                "original_time_granularity": source_info["original_time_granularity"],
            },
        }
        records.append(record)

    stats = {
        "record_count": len(records),
        "split_counts": dict(split_counts),
        "class_counts": dict(class_counts),
        "class_counts_by_split": {k: dict(v) for k, v in class_counts_by_split.items()},
        "dimensions": dict(dimensions),
        "total_objects": sum(class_counts.values()),
        "issue_counts": dict(load_issue_counts()),
        "source_counts": dict(source_counts),
        "source_confidence_counts": dict(source_confidence_counts),
    }
    return records, stats


def write_metadata(records: list[dict[str, object]], stats: dict[str, object]) -> None:
    metadata = PACKAGE / "metadata"
    records_path = metadata / "dataset_records.jsonl"
    with records_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    with (metadata / "split_manifest.csv").open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "record_id",
            "split",
            "image_path",
            "label_path",
            "width",
            "height",
            "object_count",
            "RipeBlueBerry",
            "Semi-RipeBlueBerry",
            "UnripeBlueBerry",
            "image_sha256",
            "label_sha256",
            "group",
            "annotator_name_or_student",
            "original_image_path",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            content = record["data_content"][0]
            annotation = record["annotation"]
            ext = record["project_extension"]
            counts = Counter(ext["class_counts"])
            writer.writerow(
                {
                    "record_id": record["id"],
                    "split": ext["split"],
                    "image_path": content["content"],
                    "label_path": annotation["annotation_file"],
                    "width": content["width"],
                    "height": content["height"],
                    "object_count": ext["object_count"],
                    "RipeBlueBerry": counts["RipeBlueBerry"],
                    "Semi-RipeBlueBerry": counts["Semi-RipeBlueBerry"],
                    "UnripeBlueBerry": counts["UnripeBlueBerry"],
                    "image_sha256": content["sha256"],
                    "label_sha256": annotation["annotation_sha256"],
                    "group": ext["group"],
                    "annotator_name_or_student": ext["annotator_name_or_student"],
                    "original_image_path": ext["original_image_path"],
                }
            )

    with (metadata / "source_license.csv").open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "record_id",
            "image_path",
            "original_time",
            "license",
            "source",
            "source_details",
            "generated_data_indicator",
            "completion_status",
            "required_action",
            "source_dataset_code",
            "source_confidence",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            ext = record["project_extension"]
            complete = ext["source_dataset_code"] != "SOURCE_REQUIRES_CONFIRMATION"
            writer.writerow(
                {
                    "record_id": record["id"],
                    "image_path": record["data_content"][0]["content"],
                    "original_time": record["original_time"],
                    "license": record["license"],
                    "source": record["source"],
                    "source_details": record["source_details"],
                    "generated_data_indicator": record["generated_data_indicator"],
                    "completion_status": "COMPLETE_FROM_SOURCE_RULE" if complete else "BLOCKED_BY_CONFIRMATION",
                    "required_action": "复核来源映射规则与授权适用性；不确定样本需确认或剔除。",
                    "source_dataset_code": ext["source_dataset_code"],
                    "source_confidence": ext["source_confidence"],
                }
            )

    with (metadata / "source_attribution.csv").open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "record_id",
            "image_path",
            "source_dataset_code",
            "source_dataset_name",
            "source_confidence",
            "source_evidence",
            "source",
            "source_details",
            "license",
            "original_time",
            "original_time_granularity",
            "source_reference",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            ext = record["project_extension"]
            writer.writerow(
                {
                    "record_id": record["id"],
                    "image_path": record["data_content"][0]["content"],
                    "source_dataset_code": ext["source_dataset_code"],
                    "source_dataset_name": ext["source_dataset_name"],
                    "source_confidence": ext["source_confidence"],
                    "source_evidence": ext["source_evidence"],
                    "source": record["source"],
                    "source_details": record["source_details"],
                    "license": record["license"],
                    "original_time": record["original_time"],
                    "original_time_granularity": ext["original_time_granularity"],
                    "source_reference": ext["source_reference"],
                }
            )

    complete_source_rows = sum(
        1 for record in records if record["project_extension"]["source_dataset_code"] != "SOURCE_REQUIRES_CONFIRMATION"
    )
    blocked_source_rows = len(records) - complete_source_rows
    status_rows = [
        ("id", "COMPLETE", "使用图片 SHA-256 生成稳定全域唯一候选标识。"),
        ("data_content", "COMPLETE", "已写入图像模态、相对路径、宽高和 SHA-256。"),
        ("annotation.label", "COMPLETE", "已从 YOLO txt 转为标签数组，保留类别和归一化 bbox。"),
        ("annotation_method", "COMPLETE_WITH_PROJECT_CONTEXT", "当前按人工标注填写；最终提交前需由项目负责人确认。"),
        ("annotator", "COMPLETE_WITH_PROJECT_CONTEXT", "当前按普通标注员填写，并保留学生/组别扩展字段；最终提交前需确认标注人员类型。"),
        ("original_time", "PARTIAL_FROM_SOURCE_LEVEL_DATE", f"{complete_source_rows} 条使用来源发布日期/修改日期；{blocked_source_rows} 条需确认图片级或来源级时间。"),
        ("last_modified_time", "COMPLETE_FROM_LOCAL_FILE_MTIME", "使用图片/标签本地修改日期较晚者。"),
        ("version", "COMPLETE", f"统一为 {VERSION}。"),
        ("license", "PARTIAL_FROM_SOURCE_LICENSE", f"{complete_source_rows} 条已按 A/B 公开来源填充授权；{blocked_source_rows} 条需确认。"),
        ("source", "PARTIAL_FROM_SOURCE_RULE", f"{complete_source_rows} 条已按 A/B 公开来源填充；{blocked_source_rows} 条需确认。"),
        ("source_details", "PARTIAL_FROM_SOURCE_RULE", f"{complete_source_rows} 条已按 A/B URL/DOI 填充；{blocked_source_rows} 条需确认。"),
        ("generated_data_indicator", "COMPLETE_WITH_PROJECT_CONTEXT", "按项目上下文填写为 0；若存在生成/合成图片需逐条修正。"),
    ]
    with (metadata / "field_completion_status.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["field", "status", "evidence_or_required_action"])
        writer.writerows(status_rows)

    schema = {
        "dataset_name": DATASET_NAME,
        "version": VERSION,
        "standard_reference": [
            "TC609-5-2025-01 高质量数据集 建设指南",
            "TC609-5-2025-02 高质量数据集 格式要求",
            "TC609-5-2025-03 高质量数据集 分类指南",
            "TC609-5-2025-04 高质量数据集 质量评测规范",
        ],
        "record_format": "JSON Lines; one data record per image",
        "required_fields": {
            "id": "string, sha256:<image hash>",
            "rid": "array",
            "data_content": "array of image content objects",
            "annotation": "object with label array and annotation metadata",
            "original_time": "date string; currently requires confirmation",
            "last_modified_time": "date string from local image/label modification date",
            "version": "semantic version string",
            "license": "authorization type; currently requires confirmation",
            "source": "source type; currently requires confirmation",
            "source_details": "source details; currently requires confirmation",
            "generated_data_indicator": "0 for non-generated data, 1 for generated data",
        },
        "class_names": CLASSES,
        "source_evidence": {
            "A_ZENODO_BLUEBERRY_DCM": SOURCE_A,
            "B_KAGGLE_BLUEBERRY_DETECTION": SOURCE_B,
            "mapping_note": "Per-record source attribution is stored in metadata/source_attribution.csv. Filename-derived mappings must be reviewed before final submission.",
        },
        "stats": stats,
    }
    (metadata / "dataset_schema.json").write_text(
        json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def markdown_table(rows: list[tuple[str, object]]) -> str:
    out = ["| 项目 | 内容 |", "| --- | --- |"]
    for key, value in rows:
        out.append(f"| {key} | {value} |")
    return "\n".join(out)


def extract_model_metrics() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for model_name, zpath in MODEL_RESULT_ZIPS:
        if not zpath.exists():
            continue
        with zipfile.ZipFile(zpath) as zf:
            result_names = [name for name in zf.namelist() if name.endswith("results.csv")]
            if not result_names:
                continue
            text = zf.read(result_names[0]).decode("utf-8")
        parsed = list(csv.DictReader(io.StringIO(text)))
        if not parsed:
            continue
        best = max(parsed, key=lambda row: float(row.get("metrics/mAP50(B)", "0") or 0))
        rows.append(
            {
                "model": model_name,
                "result_zip": zpath.name,
                "results_csv": result_names[0],
                "best_epoch_by_mAP50": best.get("epoch", ""),
                "precision": best.get("metrics/precision(B)", ""),
                "recall": best.get("metrics/recall(B)", ""),
                "mAP50": best.get("metrics/mAP50(B)", ""),
                "mAP50_95": best.get("metrics/mAP50-95(B)", ""),
            }
        )
    return rows


def write_model_metrics_csv(rows: list[dict[str, str]]) -> None:
    path = PACKAGE / "metadata/model_metrics.csv"
    fieldnames = [
        "model",
        "result_zip",
        "results_csv",
        "best_epoch_by_mAP50",
        "precision",
        "recall",
        "mAP50",
        "mAP50_95",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def model_metrics_markdown(rows: list[dict[str, str]]) -> str:
    out = [
        "| 模型 | 最佳轮次 | Precision | Recall | mAP50 | mAP50-95 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        out.append(
            f"| {row['model']} | {row['best_epoch_by_mAP50']} | {row['precision']} | {row['recall']} | {row['mAP50']} | {row['mAP50_95']} |"
        )
    return "\n".join(out)


def write_docs(stats: dict[str, object]) -> None:
    docs = PACKAGE / "docs"
    split = stats["split_counts"]
    cls = stats["class_counts"]
    issues = stats["issue_counts"]
    source_counts = stats.get("source_counts", {})
    source_confidence_counts = stats.get("source_confidence_counts", {})
    total = stats["record_count"]
    objects = stats["total_objects"]
    model_metrics = extract_model_metrics()
    write_model_metrics_csv(model_metrics)
    model_table = model_metrics_markdown(model_metrics)
    best_model = max(model_metrics, key=lambda row: float(row.get("mAP50", "0") or 0)) if model_metrics else {}
    best_model_summary = (
        f"{best_model.get('model')} 最佳 mAP50 {best_model.get('mAP50')}，mAP50-95 {best_model.get('mAP50_95')}"
        if best_model
        else "未找到可解析的本地训练结果"
    )

    dataset_card = f"""# {DATASET_NAME} Dataset Card

## 基本信息

{markdown_table([
    ("数据集名称", DATASET_NAME),
    ("版本", VERSION),
    ("评估/构建日期", BUILD_DATE),
    ("数据集类型建议", "行业通识数据集（农业/智慧农业方向）"),
    ("目标任务", "蓝莓成熟度目标检测"),
    ("模态类型", "image"),
    ("样本记录数", total),
    ("目标框总数", objects),
    ("图片尺寸", "640x640"),
    ("类别", "RipeBlueBerry, Semi-RipeBlueBerry, UnripeBlueBerry"),
    ("技术支持方式", CONFIRM),
    ("访问渠道", CONFIRM),
])}

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
| train | {split.get("train", 0)} |
| validation | {split.get("validation", 0)} |
| test | {split.get("test", 0)} |

## 标签类别统计

| 类别 | 目标框数 |
| --- | ---: |
| RipeBlueBerry | {cls.get("RipeBlueBerry", 0)} |
| Semi-RipeBlueBerry | {cls.get("Semi-RipeBlueBerry", 0)} |
| UnripeBlueBerry | {cls.get("UnripeBlueBerry", 0)} |

## 使用许可和来源状态

当前包已生成逐条元数据记录和 `metadata/source_attribution.csv`。A/B 来源可按公开页面和文件名规则形成候选映射，但最终提交前仍需数据负责人确认文件名映射、授权适用性和删减范围。

| 来源代码 | 记录数 |
| --- | ---: |
| A_ZENODO_BLUEBERRY_DCM | {source_counts.get("A_ZENODO_BLUEBERRY_DCM", 0)} |
| B_KAGGLE_BLUEBERRY_DETECTION | {source_counts.get("B_KAGGLE_BLUEBERRY_DETECTION", 0)} |
| SOURCE_REQUIRES_CONFIRMATION | {source_counts.get("SOURCE_REQUIRES_CONFIRMATION", 0)} |

| 来源置信度 | 记录数 |
| --- | ---: |
| high | {source_confidence_counts.get("high", 0)} |
| medium | {source_confidence_counts.get("medium", 0)} |
| requires_confirmation | {source_confidence_counts.get("requires_confirmation", 0)} |

## 局限性

- 本版本仅包含已清洗并成功导出的 {total} 条记录，不包含原始分配集中缺少可用标注的 269 张图片。
- 类别分布不均衡，`UnripeBlueBerry` 目标框数量明显高于另外两类。
- 标注准确性尚缺少独立复核签字或抽检报告。
- 来源映射、授权适用性和图片首次出现时间仍需负责人复核确认。
"""
    (docs / "dataset_card.md").write_text(dataset_card, encoding="utf-8")

    construction_report = f"""# 数据集建设说明书

## 数据需求

本数据集面向蓝莓成熟度目标检测任务，目标是在图像中定位蓝莓并识别成熟度类别。类别限定为 `RipeBlueBerry`、`Semi-RipeBlueBerry`、`UnripeBlueBerry` 三类。

## 数据规划

当前冻结版本定义为 {VERSION}，纳入已通过清洗并导出的 {total} 条记录。数据按训练、验证、测试三部分组织：train {split.get("train", 0)} 条，validation {split.get("validation", 0)} 条，test {split.get("test", 0)} 条。

## 数据采集

本数据集由用户说明的 A/B 两个公开数据集子集整合而来。当前构建脚本按文件名规则形成候选来源映射：A 数据集为 Zenodo BlueberryDCM，B 数据集为 Kaggle Blueberry Detection dataset。映射结果写入 `metadata/source_attribution.csv`；未匹配或低置信样本需由数据负责人复核后才能作为最终来源证据。

| 来源代码 | 记录数 | 主要证据 |
| --- | ---: | --- |
| A_ZENODO_BLUEBERRY_DCM | {source_counts.get("A_ZENODO_BLUEBERRY_DCM", 0)} | Zenodo DOI、ScienceDirect 论文、MSState/MSU 文件名前缀 |
| B_KAGGLE_BLUEBERRY_DETECTION | {source_counts.get("B_KAGGLE_BLUEBERRY_DETECTION", 0)} | Kaggle 页面 JSON-LD、DSCF/MVIMG/Roboflow 风格文件名 |
| SOURCE_REQUIRES_CONFIRMATION | {source_counts.get("SOURCE_REQUIRES_CONFIRMATION", 0)} | 未匹配规则，需人工确认 |

## 数据预处理

已有清洗流程完成以下工作：

- 将可用 LabelMe/YOLO 标注统一导出为 YOLO 格式。
- 修正 49 行标签拼写问题。
- 排除 269 张缺少可用标注的原始图片。
- 排除 137 张包内额外图片和 125 个额外标注。
- 对 19 项重复标注选择目标框更多的版本导出。
- 生成训练清单、问题清单、剔除报告和返工报告。

## 数据标注

当前标签文件为 YOLO normalized xywh 格式，每行包含 `class_id x_center y_center width height`。类别 ID 为：0 `RipeBlueBerry`，1 `Semi-RipeBlueBerry`，2 `UnripeBlueBerry`。

## 模型验证

本地训练结果显示：

{model_table}

上述结果可作为模型验证证据，但正式认定高质量数据集前，还需补充目标性能阈值、独立测试评估方法和复现实验说明。
"""
    (docs / "construction_report.md").write_text(construction_report, encoding="utf-8")

    annotation_spec = """# 标注规范

## 标签集合

| class_id | 标签 | 含义 |
| ---: | --- | --- |
| 0 | RipeBlueBerry | 成熟蓝莓 |
| 1 | Semi-RipeBlueBerry | 半成熟蓝莓 |
| 2 | UnripeBlueBerry | 未成熟蓝莓 |

## 框选规则

1. 每个可见蓝莓目标应使用一个最小外接矩形框标注。
2. 框应覆盖完整可见果实，不应包含明显无关背景。
3. 严重遮挡、极度模糊或无法判断成熟度的目标应提交复核，不应随意归类。
4. 多个蓝莓相互接触但边界可区分时，应分别框选。
5. 标签只允许使用三类标准标签，不允许使用拼写变体。

## YOLO 输出格式

每行格式为：

```text
class_id x_center y_center width height
```

坐标为相对图片宽高归一化后的 `xywh`，取值范围为 `[0, 1]`，宽高必须大于 0。

## 质量验收规则

1. 图片和标签文件必须一一配对。
2. 每个标签文件必须能被 YOLO 训练程序读取。
3. class_id 必须属于 0、1、2。
4. bbox 坐标必须在 `[0, 1]` 范围内。
5. 抽检样本应记录错标、漏标、框偏移、重复框和类别混淆情况。
6. 最终提交前应由复核人填写 `annotation_review_certificate_template.md`。
"""
    (docs / "annotation_spec.md").write_text(annotation_spec, encoding="utf-8")

    quality_report = f"""# 质量评测报告草案

## 总体判断

当前包已完成可自动证明部分的质量整理，但尚不能声明满足 TC609-5-2025-04 的三项 90 分阈值。阻塞项集中在来源授权、原始时间、说明文档确认和标注复核证明。

## 说明文档指标

| 子指标 | 当前状态 | 证据/缺口 |
| --- | --- | --- |
| 基本信息完整性 | PARTIAL | 已有规模、格式、文件结构；访问渠道和技术支持方式待确认 |
| 内容特征完整性 | PARTIAL | 已有模态、分布、标签统计、来源统计；样本示例和局限性已说明；需正式确认 |
| 建设过程完整性 | PARTIAL | 已有清洗脚本、来源候选映射和报告；来源映射、版本控制待负责人确认 |
| 应用说明完整性 | PARTIAL | 已有目标场景和模型结果；使用许可、典型应用案例待确认 |

## 数据质量指标

| 子指标 | 当前状态 | 证据/缺口 |
| --- | --- | --- |
| 格式规范性 | PASS | {total} 张图片和 {total} 个 YOLO 标签配对，YOLO 格式错误为 0 |
| 安全规范性 | PARTIAL | 农业图像通常风险较低；仍需人工确认不含侵权、敏感或违法内容 |
| 标注规范性 | PARTIAL | 格式规范已通过；标注准确性需抽检/复核证明 |
| 结构完整性 | PASS_FOR_2731_SCOPE | 本版本 {total} 条记录完整；原始 3000 范围下仍有 269 张缺标 |
| 内容真实性 | PARTIAL | A/B 来源候选映射已生成；{source_counts.get("SOURCE_REQUIRES_CONFIRMATION", 0)} 条来源需确认，且所有映射需负责人复核 |
| 内容一致性 | PARTIAL | 图像与标签文件配对完整；语义级错标漏标需人工复核 |
| 类型一致性 | PASS_WITH_SCOPE | 建议按农业行业通识图像目标检测数据集申报 |
| 内容干净性 | PARTIAL | 尺寸统一、精确重复未发现；需补水印、模糊、遮挡、感知重复抽检 |

## 模型应用指标

| 子指标 | 当前状态 | 证据/缺口 |
| --- | --- | --- |
| 内容多样性 | PARTIAL | 有三类样本和不同划分；类别不均衡需披露 |
| 规模完整性 | PARTIAL | {total} 条可训练记录；目标规模阈值待确认 |
| 内容时效性 | BLOCKED_BY_CONFIRMATION | 原始时间和更新要求待确认 |
| 标注准确性 | BLOCKED_BY_REVIEW | 需要复核报告或抽检统计 |
| 模型适配性 | PARTIAL | {best_model_summary}；目标阈值和独立测试待确认 |

## 当前问题统计

| 问题类型 | 数量 |
| --- | ---: |
| missing_annotation | {issues.get("missing_annotation", 0)} |
| label_corrected | {issues.get("label_corrected", 0)} |
| duplicate_annotations | {issues.get("duplicate_annotations", 0)} |
| annotation_warning | {issues.get("annotation_warning", 0)} |
| extra_package_image | {issues.get("extra_package_image", 0)} |
| extra_annotation | {issues.get("extra_annotation", 0)} |
"""
    (docs / "quality_evaluation_report.md").write_text(quality_report, encoding="utf-8")

    model_report = """# 模型验证报告

## 验证目的

使用目标检测模型验证数据集对蓝莓成熟度识别任务的支撑能力。

## 本地已有训练结果

{model_table}

## 已归档证据

- `evidence/training_results/blueberry1.v4i.yolov11数据集yolov11训练结果.zip`
- `evidence/training_results/blueberry.v4i.yolov12数据集yolov12训练结果.zip`

## 仍需补充

1. 明确目标应用场景的预期性能阈值。
2. 给出训练硬件、软件版本、随机种子、训练命令和数据版本。
3. 对独立 test split 输出最终评测结果。
4. 提供失败案例分析，包括漏检、错检和类别混淆。
"""
    (docs / "model_validation_report.md").write_text(model_report, encoding="utf-8")

    review_template = f"""# 标注复核证明模板

数据集名称：{DATASET_NAME}  
版本：{VERSION}  
记录数：{total}  
目标框数：{objects}  
复核日期：{CONFIRM}  
复核人：{CONFIRM}  
复核人资质/角色：{CONFIRM}  

## 复核范围

| 复核方式 | 数量 | 比例 |
| --- | ---: | ---: |
| 全量复核 | {CONFIRM} | {CONFIRM} |
| 抽样复核 | {CONFIRM} | {CONFIRM} |

## 复核结果

| 问题类型 | 数量 | 处理结果 |
| --- | ---: | --- |
| 漏标 | {CONFIRM} | {CONFIRM} |
| 错标 | {CONFIRM} | {CONFIRM} |
| 框偏移 | {CONFIRM} | {CONFIRM} |
| 重复框 | {CONFIRM} | {CONFIRM} |
| 类别混淆 | {CONFIRM} | {CONFIRM} |

## 结论

复核结论：{CONFIRM}

复核人签名：{CONFIRM}
"""
    (docs / "annotation_review_certificate_template.md").write_text(review_template, encoding="utf-8")

    completion_plan = f"""# 待补充信息完善方案

## 必须补齐后才能声明完全符合 TC609

| 信息项 | 当前状态 | 完善方式 | 建议责任人 |
| --- | --- | --- | --- |
| 原始时间 `original_time` | {CONFIRM} | 按图片原始采集时间、公开数据发布时间或原始数据集发布时间回填；无法追溯的样本应剔除或披露限制 | 数据负责人 |
| 授权类型 `license` | {CONFIRM} | 确认开源、公共授权、商业授权、仅内部或其他；保存授权证明 | 数据负责人 |
| 来源类型 `source` | {CONFIRM} | 按互联网、自采、公开数据集、组织机构等分类 | 数据负责人 |
| 来源详情 `source_details` | {CONFIRM} | 填 URL、数据集名、采集地点/设备、授权文件编号等 | 数据负责人 |
| 技术支持方式 | {CONFIRM} | 填联系人、邮箱、仓库地址或维护单位 | 项目负责人 |
| 访问渠道 | {CONFIRM} | 填数据获取路径、网盘、仓库或内部系统 | 项目负责人 |
| 标注复核证明 | {CONFIRM} | 完成抽检或全量复核，填写复核模板 | 复核人 |
| 质量评分 | 未最终打分 | 三大维度按 TC609-5-2025-04 给出分子、分母、权重和得分 | 质量负责人 |

## 推荐整改顺序

1. 先确认正式提交范围为 {total} 条已清洗记录，不把 269 张缺标图片写入 v1.0.0。
2. 回填 `metadata/source_license.csv` 的来源、授权和原始时间。
3. 若存在无法确认授权或来源的记录，决定剔除还是作为限制项披露。
4. 完成标注抽检，填写 `docs/annotation_review_certificate_template.md`。
5. 将 `docs/quality_evaluation_report.md` 从草案更新为正式评分报告。
6. 重新运行 `tools/build_tc609_submission_package.py` 生成最终包和校验和。

## 可接受的阶段性表述

可以表述为：本数据集已完成 TC609 格式化整理，具备 YOLO 目标检测训练可用性，当前为高质量数据集候选提交包。

不建议表述为：本数据集已完全符合 TC609-5-2025-01/02/03/04。
"""
    (docs / "completion_plan.md").write_text(completion_plan, encoding="utf-8")

    source_report = f"""# 来源与授权报告

## 来源概览

| 来源代码 | 数据集 | 授权 | 来源详情 | 记录数 |
| --- | --- | --- | --- | ---: |
| A_ZENODO_BLUEBERRY_DCM | {SOURCE_A['source_dataset_name']} | {SOURCE_A['license']} | {SOURCE_A['source_details']} | {source_counts.get("A_ZENODO_BLUEBERRY_DCM", 0)} |
| B_KAGGLE_BLUEBERRY_DETECTION | {SOURCE_B['source_dataset_name']} | {SOURCE_B['license']} | {SOURCE_B['source_details']} | {source_counts.get("B_KAGGLE_BLUEBERRY_DETECTION", 0)} |
| SOURCE_REQUIRES_CONFIRMATION | {CONFIRM} | {CONFIRM} | {CONFIRM} | {source_counts.get("SOURCE_REQUIRES_CONFIRMATION", 0)} |

## 授权使用边界

- A 数据集公开页面标注为 CC BY-NC 4.0，当前包按非商业研究/教学候选数据集处理。
- B 数据集公开页面 JSON-LD 标注为 CC BY-NC-SA 4.0，当前包按非商业、署名、相同方式共享候选数据集处理。
- 正式对外发布前，需确认合并、删减、再标注和再分发是否符合两个来源许可要求。

## 映射置信度

| 置信度 | 记录数 | 处理要求 |
| --- | ---: | --- |
| high | {source_confidence_counts.get("high", 0)} | 复核文件名前缀规则和来源清单后可转为正式证据 |
| medium | {source_confidence_counts.get("medium", 0)} | 需要人工抽查文件名、原始下载包或清单 |
| requires_confirmation | {source_confidence_counts.get("requires_confirmation", 0)} | 需要确认来源或剔除 |

逐条映射见 `metadata/source_attribution.csv`。
"""
    (docs / "source_and_license_report.md").write_text(source_report, encoding="utf-8")

    type_decision = f"""# 数据集类型划分决策

## 类型划分方法

根据 TC609-5-2025-03 图1，先综合判断是否符合行业专识数据集；若不符合，再判断是否符合行业通识数据集；若仍不符合，才归为通识数据集。

## 类型要素判定

| 类型要素 | 当前证据 | 判定 |
| --- | --- | --- |
| 知识内容 | 蓝莓成熟度目标检测，面向农业/智慧农业视觉识别任务 | 符合行业领域通用知识 |
| 来源类型 | A/B 均为公开农业/蓝莓检测相关数据集，逐条映射见 `metadata/source_attribution.csv` | 符合行业通识；不满足组织机构内部系统来源 |
| 时效性 | A 来源发布时间 2024-10-28，B 来源修改时间 2024-02-28；业务更新周期待确认 | 行业通识候选 |
| 标注人员类型 | 本地清洗报告显示普通标注/学生标注痕迹，缺少专家复核证明 | 不满足行业专识专家标注条件 |
| 敏感程度 | 农业图像，当前未见个人敏感信息；授权适用性仍需确认 | 行业通识候选 |
| 模型类型 | 支撑 YOLO 系列通用/行业目标检测模型 | 行业通识 |
| 主题范围 | 聚焦蓝莓成熟度和目标检测，属于农业视觉共性任务；不是某机构内部岗位流程专属数据 | 行业通识 |

## 当前结论

当前建议申报为：**行业通识数据集候选（农业/智慧农业方向）**。

## 行业专识升级门槛

如需升级为行业专识数据集，需补齐以下证据：

1. 具体组织机构内部业务场景说明，例如某蓝莓基地采收决策、产量估算、表型分析或质检流程。
2. 行业领域专家参与标注或复核的证明。
3. 内部授权、权限管理或特定岗位使用边界。
4. 场景模型目标、预期性能阈值、独立测试结果和失败案例分析。
"""
    (docs / "dataset_type_decision.md").write_text(type_decision, encoding="utf-8")

    traceability = f"""# TC609 要求追溯表

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
| version | {VERSION} |
| license | A/B 来源授权候选值 |
| source | 公开数据集 |
| source_details | Zenodo DOI 或 Kaggle URL |
| generated_data_indicator | 0 |

## TC609-5-2025-04 评测状态

最终状态：高质量数据集候选包。不得在来源复核、标注复核和模型独立验证完成前声明三大维度均达到 90 分。
"""
    (docs / "tc609_requirements_traceability.md").write_text(traceability, encoding="utf-8")

    quality_metrics = {
        "documentation": {
            "0101": {"name": "基本信息完整性", "status": "PARTIAL", "evidence": "docs/dataset_card.md"},
            "0102": {"name": "内容特征完整性", "status": "PARTIAL", "evidence": "docs/dataset_card.md"},
            "0103": {"name": "建设过程完整性", "status": "PARTIAL", "evidence": "docs/construction_report.md"},
            "0104": {"name": "应用说明完整性", "status": "PARTIAL", "evidence": "docs/model_validation_report.md"},
        },
        "data_quality": {
            "0201": {"name": "格式规范性", "status": "PASS", "value": 1.0, "evidence": "metadata/build_summary.json"},
            "0202": {"name": "安全规范性", "status": "PARTIAL", "evidence": "requires manual content/license review"},
            "0203": {"name": "标注规范性", "status": "PARTIAL", "evidence": "docs/annotation_spec.md"},
            "0204": {"name": "结构完整性", "status": "PASS_FOR_2731_SCOPE", "value": 1.0, "evidence": "metadata/split_manifest.csv"},
            "0205": {"name": "内容真实性", "status": "PARTIAL", "evidence": "metadata/source_attribution.csv"},
            "0206": {"name": "内容一致性", "status": "PARTIAL", "evidence": "image-label pairing validation"},
            "0207": {"name": "类型一致性", "status": "PASS_WITH_SCOPE", "evidence": "docs/dataset_type_decision.md"},
            "0208": {"name": "内容干净性", "status": "PARTIAL", "evidence": "metadata/build_summary.json"},
        },
        "model_application": {
            "0301": {"name": "内容多样性", "status": "PARTIAL", "evidence": "metadata/split_manifest.csv"},
            "0302": {"name": "规模完整性", "status": "PARTIAL", "value": total, "evidence": "metadata/build_summary.json"},
            "0303": {"name": "内容时效性", "status": "PARTIAL", "evidence": "metadata/source_attribution.csv"},
            "0304": {"name": "标注准确性", "status": "BLOCKED_BY_REVIEW", "evidence": "docs/annotation_review_certificate_template.md"},
            "0305": {"name": "模型适配性", "status": "PARTIAL", "evidence": "metadata/model_metrics.csv"},
        },
        "final_status": "CANDIDATE_NOT_YET_FULL_TC609_HIGH_QUALITY",
        "blocking_items": [
            "source/license mapping owner review",
            "annotation accuracy review certificate",
            "independent model test and target threshold",
            "technical support and access channel confirmation",
        ],
    }
    (PACKAGE / "metadata/quality_metrics.json").write_text(
        json.dumps(quality_metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def copy_evidence() -> None:
    for name in [
        "summary.md",
        "files.csv",
        "issues.csv",
        "exclusion_report.csv",
        "retake_report.csv",
        "training_manifest.csv",
        "group_person_summary.csv",
        "package_summary.csv",
        "missing_annotations.csv",
    ]:
        src = REPORTS / name
        if src.exists():
            copy_if_needed(src, PACKAGE / "evidence/reports" / name)

    for src in [QC_DIR / "contact_sheet.jpg", REPO / "images/annotation_qc/sample_contact_sheet.jpg"]:
        if src.exists():
            copy_if_needed(src, PACKAGE / "evidence/qc" / src.name)

    for src in [
        REPO / "blueberry1.v4i.yolov11数据集yolov11训练结果.zip",
        REPO / "blueberry.v4i.yolov12数据集yolov12训练结果.zip",
    ]:
        if src.exists():
            copy_if_needed(src, PACKAGE / "evidence/training_results" / src.name)

    data_yaml = """path: .
train: data/images/train
val: data/images/validation
test: data/images/test
names:
  0: RipeBlueBerry
  1: Semi-RipeBlueBerry
  2: UnripeBlueBerry
"""
    (PACKAGE / "data.yaml").write_text(data_yaml, encoding="utf-8")

    readme = f"""# {DATASET_NAME} TC609 Submission Package v{VERSION}

This package was generated on {BUILD_DATE} from `/Users/jameshan/Developments/blueberry/images/yolo_training_ready`.

The package is a TC609-oriented candidate submission package. It includes complete YOLO training data, per-record JSONL metadata, manifests, checksums, documentation drafts, and evidence files. Fields that cannot be proven from local files are marked as `{CONFIRM}` and listed in `docs/completion_plan.md`.
"""
    (PACKAGE / "README.md").write_text(readme, encoding="utf-8")


def checksum_file_paths(package: Path, checksum_path: Path) -> list[Path]:
    files = []
    for path in sorted(p for p in package.rglob("*") if p.is_file() and p != checksum_path):
        rel = path.relative_to(package).as_posix()
        if rel.startswith("evidence/logs/"):
            continue
        files.append(path)
    return files


def write_checksums() -> None:
    checksum_path = PACKAGE / "metadata/checksums.sha256"
    files = checksum_file_paths(PACKAGE, checksum_path)
    with checksum_path.open("w", encoding="utf-8") as f:
        for path in files:
            rel = path.relative_to(PACKAGE).as_posix()
            f.write(f"{sha256_file(path)}  {rel}\n")


def validate(records: list[dict[str, object]]) -> dict[str, object]:
    required = [
        "id",
        "rid",
        "data_content",
        "annotation",
        "original_time",
        "last_modified_time",
        "version",
        "license",
        "source",
        "source_details",
        "generated_data_indicator",
    ]
    errors = []
    confirmation_counts: Counter[str] = Counter()
    for idx, record in enumerate(records, start=1):
        for key in required:
            if key not in record:
                errors.append(f"line {idx}: missing {key}")
        for key in ["original_time", "license", "source", "source_details"]:
            if record.get(key) == CONFIRM:
                confirmation_counts[key] += 1
    return {
        "record_count": len(records),
        "errors": errors,
        "confirmation_counts": dict(confirmation_counts),
    }


def main() -> None:
    ensure_dirs()
    records, stats = collect_records()
    write_metadata(records, stats)
    write_docs(stats)
    copy_evidence()
    write_checksums()
    result = validate(records)
    (PACKAGE / "metadata/build_summary.json").write_text(
        json.dumps({"stats": stats, "validation": result}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_checksums()
    print(json.dumps({"package": str(PACKAGE), "stats": stats, "validation": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
