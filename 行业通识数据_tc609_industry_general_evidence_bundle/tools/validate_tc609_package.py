#!/usr/bin/env python3
"""Validate the TC609-oriented blueberry dataset package."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
ALLOWED_CLASSES = {0, 1, 2}
REQUIRED_RECORD_FIELDS = [
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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def keyed_files(root: Path, exts: set[str]) -> dict[str, Path]:
    files: dict[str, Path] = {}
    if not root.exists():
        return files
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in exts and not path.name.startswith("."):
            rel = path.relative_to(root)
            files[rel.with_suffix("").as_posix()] = path
    return files


def parse_yolo_errors(label_path: Path) -> list[str]:
    errors: list[str] = []
    for line_no, raw in enumerate(label_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 5:
            errors.append(f"{label_path}: line {line_no}: expected 5 columns")
            continue
        try:
            class_id = int(float(parts[0]))
            bbox = [float(v) for v in parts[1:]]
        except ValueError:
            errors.append(f"{label_path}: line {line_no}: non-numeric YOLO value")
            continue
        if class_id not in ALLOWED_CLASSES:
            errors.append(f"{label_path}: line {line_no}: unknown class {class_id}")
        if any(v < 0 or v > 1 for v in bbox):
            errors.append(f"{label_path}: line {line_no}: bbox value outside [0,1]")
        if bbox[2] <= 0 or bbox[3] <= 0:
            errors.append(f"{label_path}: line {line_no}: non-positive bbox width/height")
    return errors


def validate_input_dataset(dataset: Path) -> dict[str, Any]:
    image_root = dataset / "image"
    label_root = dataset / "label"
    images = keyed_files(image_root, IMAGE_EXTS)
    labels = keyed_files(label_root, {".txt"})

    missing_labels = sorted(set(images) - set(labels))
    missing_images = sorted(set(labels) - set(images))
    yolo_errors: list[str] = []
    for path in labels.values():
        yolo_errors.extend(parse_yolo_errors(path))

    return {
        "dataset": str(dataset),
        "image_count": len(images),
        "label_count": len(labels),
        "valid_pair_count": len(set(images) & set(labels)),
        "missing_label_count": len(missing_labels),
        "missing_image_count": len(missing_images),
        "missing_labels": missing_labels,
        "missing_images": missing_images,
        "yolo_error_count": len(yolo_errors),
        "yolo_errors": yolo_errors,
    }


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.exists():
        return records, [f"missing {path}"]
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: line {line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}: line {line_no}: record is not an object")
            continue
        records.append(value)
    return records, errors


def validate_record(record: dict[str, Any], package: Path, index: int) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_RECORD_FIELDS:
        if field not in record:
            errors.append(f"record {index}: missing {field}")

    data_content = record.get("data_content")
    if not isinstance(data_content, list) or not data_content:
        errors.append(f"record {index}: data_content must be a non-empty array")
    else:
        content = data_content[0]
        if not isinstance(content, dict):
            errors.append(f"record {index}: data_content[0] must be an object")
        else:
            media_type = content.get("media_type")
            if isinstance(media_type, str):
                has_image = media_type == "image"
            elif isinstance(media_type, list):
                has_image = "image" in media_type
            else:
                has_image = False
            if not has_image:
                errors.append(f"record {index}: data_content[0].media_type must include image")
            rel = content.get("content")
            if not isinstance(rel, str) or not rel:
                errors.append(f"record {index}: data_content[0].content missing")
            elif Path(rel).is_absolute():
                errors.append(f"record {index}: data_content[0].content must be relative")
            elif not (package / rel).exists():
                errors.append(f"record {index}: missing image file {rel}")

    annotation = record.get("annotation")
    if not isinstance(annotation, dict):
        errors.append(f"record {index}: annotation must be an object")
        return errors

    annotation_file = annotation.get("annotation_file")
    if isinstance(annotation_file, str):
        if Path(annotation_file).is_absolute():
            errors.append(f"record {index}: annotation_file must be relative")
        elif not (package / annotation_file).exists():
            errors.append(f"record {index}: missing annotation file {annotation_file}")
        else:
            errors.extend(parse_yolo_errors(package / annotation_file))

    labels = annotation.get("label")
    if not isinstance(labels, list):
        errors.append(f"record {index}: annotation.label must be an array")
        return errors
    for label_index, label in enumerate(labels, start=1):
        if not isinstance(label, dict):
            errors.append(f"record {index}: label {label_index} must be an object")
            continue
        for field in ["category", "category_id", "bbox_yolo", "bbox_format", "iscrowd"]:
            if field not in label:
                errors.append(f"record {index}: label {label_index}: missing {field}")
        bbox = label.get("bbox_yolo")
        if not isinstance(bbox, list) or len(bbox) != 4:
            errors.append(f"record {index}: label {label_index}: bbox_yolo must have 4 values")
            continue
        try:
            values = [float(v) for v in bbox]
        except (TypeError, ValueError):
            errors.append(f"record {index}: label {label_index}: bbox_yolo non-numeric")
            continue
        if any(v < 0 or v > 1 for v in values):
            errors.append(f"record {index}: label {label_index}: bbox_yolo outside [0,1]")
        if values[2] <= 0 or values[3] <= 0:
            errors.append(f"record {index}: label {label_index}: non-positive bbox size")
    return errors


def validate_checksums(package: Path) -> dict[str, Any]:
    checksum_path = package / "metadata/checksums.sha256"
    errors: list[str] = []
    checked = 0
    if not checksum_path.exists():
        return {"checksum_checked": 0, "checksum_error_count": 1, "checksum_errors": ["missing checksums.sha256"]}
    for line_no, line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            expected, rel = line.split(None, 1)
        except ValueError:
            errors.append(f"checksums.sha256 line {line_no}: expected '<sha256>  <path>'")
            continue
        rel = rel.strip()
        path = package / rel
        if not path.exists():
            errors.append(f"checksums.sha256 line {line_no}: missing file {rel}")
            continue
        actual = sha256_file(path)
        checked += 1
        if actual != expected:
            errors.append(f"checksums.sha256 line {line_no}: checksum mismatch for {rel}")
    return {
        "checksum_checked": checked,
        "checksum_error_count": len(errors),
        "checksum_errors": errors,
    }


def validate_package(package: Path) -> dict[str, Any]:
    records, json_errors = read_jsonl(package / "metadata/dataset_records.jsonl")
    record_errors = list(json_errors)
    for index, record in enumerate(records, start=1):
        record_errors.extend(validate_record(record, package, index))
    checksum_result = validate_checksums(package)
    return {
        "package": str(package),
        "record_count": len(records),
        "record_error_count": len(record_errors),
        "record_errors": record_errors,
        **checksum_result,
    }


def validate_docs(package: Path) -> dict[str, Any]:
    required = {
        "docs/dataset_card.md": ["基本信息", "文件结构", "数据划分", "标签类别统计"],
        "docs/construction_report.md": ["数据需求", "数据规划", "数据采集", "数据预处理", "数据标注", "模型验证"],
        "docs/quality_evaluation_report.md": ["说明文档指标", "数据质量指标", "模型应用指标"],
        "docs/model_validation_report.md": ["验证目的", "本地已有训练结果"],
        "docs/completion_plan.md": ["必须补齐", "推荐整改顺序"],
        "docs/annotation_spec.md": ["标签集合", "YOLO 输出格式", "质量验收规则"],
        "docs/source_and_license_report.md": ["来源", "授权"],
        "docs/dataset_type_decision.md": ["类型划分", "行业通识", "行业专识"],
        "docs/tc609_requirements_traceability.md": ["数据需求", "数据规划", "模型验证"],
    }
    errors: list[str] = []
    for rel, needles in required.items():
        path = package / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel}: missing section text {needle}")
    return {"doc_error_count": len(errors), "doc_errors": errors}


def validate_quality(package: Path) -> dict[str, Any]:
    path = package / "metadata/quality_metrics.json"
    if not path.exists():
        return {"quality_error_count": 1, "quality_errors": ["missing metadata/quality_metrics.json"]}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"quality_error_count": 1, "quality_errors": [f"invalid quality_metrics.json: {exc}"]}
    required_keys = ["documentation", "data_quality", "model_application", "final_status"]
    errors = [f"quality_metrics.json: missing {key}" for key in required_keys if key not in data]
    return {"quality_error_count": len(errors), "quality_errors": errors}


def validate_model(package: Path) -> dict[str, Any]:
    errors: list[str] = []
    if not (package / "metadata/model_metrics.csv").exists():
        errors.append("missing metadata/model_metrics.csv")
    evidence = package / "evidence/training_results"
    if not evidence.exists() or not list(evidence.glob("*.zip")):
        errors.append("missing training result ZIP evidence")
    report = package / "docs/model_validation_report.md"
    if not report.exists() or "仍需补充" not in report.read_text(encoding="utf-8"):
        errors.append("model report must document remaining validation gaps")
    return {"model_error_count": len(errors), "model_errors": errors}


def merge_results(*results: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for result in results:
        merged.update(result)
    return merged


def has_failures(result: dict[str, Any]) -> bool:
    for key, value in result.items():
        if key.endswith("_error_count") and isinstance(value, int) and value > 0:
            return True
    if result.get("missing_label_count", 0) or result.get("missing_image_count", 0) or result.get("yolo_error_count", 0):
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["input", "package", "docs", "quality", "model", "all"], required=True)
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--package", type=Path)
    args = parser.parse_args()

    if args.mode == "input":
        if args.dataset is None:
            parser.error("--dataset is required for --mode input")
        result = validate_input_dataset(args.dataset)
    else:
        if args.package is None:
            parser.error("--package is required for this mode")
        if args.mode == "package":
            result = validate_package(args.package)
        elif args.mode == "docs":
            result = validate_docs(args.package)
        elif args.mode == "quality":
            result = validate_quality(args.package)
        elif args.mode == "model":
            result = validate_model(args.package)
        else:
            result = merge_results(
                validate_package(args.package),
                validate_docs(args.package),
                validate_quality(args.package),
                validate_model(args.package),
            )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if has_failures(result) else 0


if __name__ == "__main__":
    sys.exit(main())
