import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image


def write_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (10, 10), color=(20, 40, 80)).save(path)


class Tc609ValidatorTests(unittest.TestCase):
    def test_validate_input_dataset_reports_pairing_and_yolo_errors(self) -> None:
        from tools.validate_tc609_package import validate_input_dataset

        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp)
            write_image(dataset / "image/train/valid.jpg")
            (dataset / "label/train").mkdir(parents=True, exist_ok=True)
            (dataset / "label/train/valid.txt").write_text(
                "0 0.5 0.5 0.2 0.2\n", encoding="utf-8"
            )

            write_image(dataset / "image/train/bad.jpg")
            (dataset / "label/train/bad.txt").write_text(
                "7 0.5 0.5 0.2 0.2\n", encoding="utf-8"
            )

            write_image(dataset / "image/train/missing_label.jpg")
            (dataset / "label/train/orphan.txt").write_text(
                "0 0.5 0.5 0.2 0.2\n", encoding="utf-8"
            )

            result = validate_input_dataset(dataset)

        self.assertEqual(result["image_count"], 3)
        self.assertEqual(result["label_count"], 3)
        self.assertEqual(result["missing_label_count"], 1)
        self.assertEqual(result["missing_image_count"], 1)
        self.assertEqual(result["yolo_error_count"], 1)
        self.assertIn("unknown class 7", "\n".join(result["yolo_errors"]))

    def test_validate_package_reports_required_field_and_checksum_errors(self) -> None:
        from tools.validate_tc609_package import validate_package

        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            write_image(package / "data/images/train/img.jpg")
            label = package / "annotations/yolo/train/img.txt"
            label.parent.mkdir(parents=True, exist_ok=True)
            label.write_text("0 0.5 0.5 0.2 0.2\n", encoding="utf-8")

            metadata = package / "metadata"
            metadata.mkdir(parents=True, exist_ok=True)
            record = {
                "id": "sha256:test",
                "rid": [],
                "data_content": [
                    {
                        "media_type": ["image"],
                        "content": "data/images/train/img.jpg",
                        "width": 10,
                        "height": 10,
                        "sha256": "not-used-in-this-test",
                    }
                ],
                "annotation": {
                    "label": [
                        {
                            "category": "RipeBlueBerry",
                            "category_id": 0,
                            "bbox_yolo": [0.5, 0.5, 0.2, 0.2],
                            "bbox_format": "normalized_xywh",
                            "iscrowd": 0,
                        }
                    ],
                    "annotation_file": "annotations/yolo/train/img.txt",
                },
                "original_time": "2024-02-28",
                "last_modified_time": "2026-06-23",
                "version": "1.0.0",
                "license": "CC BY-NC-SA 4.0",
                "source": "公开数据集",
                "generated_data_indicator": 0,
            }
            (metadata / "dataset_records.jsonl").write_text(
                json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            (metadata / "checksums.sha256").write_text(
                "0000  data/images/train/img.jpg\n", encoding="utf-8"
            )

            result = validate_package(package)

        self.assertEqual(result["record_count"], 1)
        self.assertIn("missing source_details", "\n".join(result["record_errors"]))
        self.assertEqual(result["checksum_error_count"], 1)


class Tc609SourceAttributionTests(unittest.TestCase):
    def test_infer_source_attribution_maps_known_source_patterns(self) -> None:
        from tools.build_tc609_submission_package import infer_source_attribution

        a = infer_source_attribution("MSState_YL_Cropped_0001_0_0.jpg")
        self.assertEqual(a["source_dataset_code"], "A_ZENODO_BLUEBERRY_DCM")
        self.assertEqual(a["license"], "CC BY-NC 4.0")
        self.assertEqual(a["source_confidence"], "high")

        b = infer_source_attribution("DSCF5235_JPG.rf.abc_4_1.jpg")
        self.assertEqual(b["source_dataset_code"], "B_KAGGLE_BLUEBERRY_DETECTION")
        self.assertEqual(b["license"], "CC BY-NC-SA 4.0")
        self.assertIn(b["source_confidence"], {"high", "medium"})

        unknown = infer_source_attribution("unmapped_image.jpg")
        self.assertEqual(unknown["source_dataset_code"], "SOURCE_REQUIRES_CONFIRMATION")
        self.assertEqual(unknown["license"], "REQUIRES_CONFIRMATION")

    def test_checksum_file_paths_excludes_volatile_logs(self) -> None:
        from tools.build_tc609_submission_package import checksum_file_paths

        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            checksum = package / "metadata/checksums.sha256"
            checksum.parent.mkdir(parents=True, exist_ok=True)
            checksum.write_text("", encoding="utf-8")
            (package / "data").mkdir(parents=True, exist_ok=True)
            (package / "data/file.txt").write_text("stable", encoding="utf-8")
            (package / "evidence/logs").mkdir(parents=True, exist_ok=True)
            (package / "evidence/logs/run.log").write_text("volatile", encoding="utf-8")

            rels = [p.relative_to(package).as_posix() for p in checksum_file_paths(package, checksum)]

        self.assertEqual(rels, ["data/file.txt"])


if __name__ == "__main__":
    unittest.main()
