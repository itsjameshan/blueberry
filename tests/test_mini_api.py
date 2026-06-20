import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import app as blueberry_app


class MiniApiHelpersTest(unittest.TestCase):
    def test_parse_mini_conf_clamps_invalid_values(self):
        self.assertEqual(blueberry_app.parse_mini_conf(None), 0.5)
        self.assertEqual(blueberry_app.parse_mini_conf("bad"), 0.5)
        self.assertEqual(blueberry_app.parse_mini_conf("-1"), 0.01)
        self.assertEqual(blueberry_app.parse_mini_conf("2"), 0.99)
        self.assertEqual(blueberry_app.parse_mini_conf("0.72"), 0.72)

    def test_build_mini_summary_maps_existing_stats(self):
        stats = {
            "total": 9,
            "RipeBlueBerry": 4,
            "Semi-RipeBlueBerry": 3,
            "UnripeBlueBerry": 2,
        }

        summary = blueberry_app.build_mini_summary(stats)

        self.assertEqual(
            summary,
            {
                "total": 9,
                "ripe": 4,
                "semi_ripe": 3,
                "unripe": 2,
                "harvestable": 4,
            },
        )

    def test_normalize_mini_results_adds_display_names(self):
        results = [
            {
                "class_name": "RipeBlueBerry",
                "confidence": 0.91234,
                "bbox": [1.0, 2.0, 3.0, 4.0],
                "x1": 1.0,
                "y1": 2.0,
                "x2": 3.0,
                "y2": 4.0,
            }
        ]

        normalized = blueberry_app.normalize_mini_results(results)

        self.assertEqual(normalized[0]["display_name"], "成熟可采")
        self.assertEqual(normalized[0]["confidence"], 0.91234)
        self.assertEqual(normalized[0]["bbox"], [1.0, 2.0, 3.0, 4.0])


class MiniApiRoutesTest(unittest.TestCase):
    def setUp(self):
        blueberry_app.app.config["TESTING"] = True
        self.client = blueberry_app.app.test_client()

    def test_mini_health_returns_model_status(self):
        with patch.object(blueberry_app, "get_active_model", return_value={"model_name": "v12best.onnx"}), patch.object(
            blueberry_app, "is_model_loaded", return_value=True
        ):
            response = self.client.get("/api/mini/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"success": True, "model_loaded": True, "model_name": "v12best.onnx"},
        )

    def test_mini_detect_requires_image(self):
        response = self.client.post("/api/mini/detect", data={"conf": "0.5"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["message"], "请上传图片")

    def test_mini_detect_returns_mobile_contract(self):
        fake_results = [
            {
                "class_name": "RipeBlueBerry",
                "confidence": 0.91,
                "bbox": [10.0, 20.0, 80.0, 100.0],
                "x1": 10.0,
                "y1": 20.0,
                "x2": 80.0,
                "y2": 100.0,
            },
            {
                "class_name": "UnripeBlueBerry",
                "confidence": 0.82,
                "bbox": [110.0, 120.0, 180.0, 200.0],
                "x1": 110.0,
                "y1": 120.0,
                "x2": 180.0,
                "y2": 200.0,
            },
        ]
        fake_stats = {
            "total": 2,
            "RipeBlueBerry": 1,
            "Semi-RipeBlueBerry": 0,
            "UnripeBlueBerry": 1,
        }

        with patch.object(blueberry_app, "is_model_loaded", return_value=True), patch.object(
            blueberry_app, "detect_single_image", return_value=(fake_results, fake_stats)
        ), patch.object(blueberry_app, "draw_boxes", return_value=None):
            response = self.client.post(
                "/api/mini/detect",
                data={
                    "conf": "0.65",
                    "image": (io.BytesIO(b"fake image bytes"), "blueberry.jpg"),
                },
                content_type="multipart/form-data",
            )

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["summary"]["total"], 2)
        self.assertEqual(data["summary"]["ripe"], 1)
        self.assertEqual(data["summary"]["unripe"], 1)
        self.assertEqual(data["summary"]["harvestable"], 1)
        self.assertEqual(data["results"][0]["display_name"], "成熟可采")
        self.assertEqual(data["results"][1]["display_name"], "未熟")
        self.assertTrue(data["result_image"].startswith("mini_result_"))
        self.assertIn("/api/mini/result_image/", data["result_image_url"])
        self.assertEqual(data["conf_threshold"], 0.65)


class MiniProgramFilesTest(unittest.TestCase):
    def test_miniprogram_project_files_exist(self):
        root = Path(__file__).resolve().parents[1] / "miniprogram"
        expected = [
            "project.config.json",
            "app.json",
            "app.js",
            "app.wxss",
            "utils/config.js",
            "utils/api.js",
            "README.md",
        ]

        for relative_path in expected:
            self.assertTrue((root / relative_path).exists(), relative_path)

    def test_app_json_registers_index_page(self):
        root = Path(__file__).resolve().parents[1] / "miniprogram"
        app_json = json.loads((root / "app.json").read_text(encoding="utf-8"))

        self.assertEqual(app_json["pages"], ["pages/index/index"])
        self.assertEqual(app_json["window"]["navigationBarTitleText"], "蓝莓成熟度识别")

    def test_index_page_contains_capture_upload_and_result_states(self):
        root = Path(__file__).resolve().parents[1] / "miniprogram" / "pages" / "index"
        expected = ["index.json", "index.wxml", "index.wxss", "index.js"]
        for filename in expected:
            self.assertTrue((root / filename).exists(), filename)

        wxml = (root / "index.wxml").read_text(encoding="utf-8")
        js = (root / "index.js").read_text(encoding="utf-8")

        self.assertIn("拍照识别", wxml)
        self.assertIn("从相册选择", wxml)
        self.assertIn("成熟可采", wxml)
        self.assertIn("半熟", wxml)
        self.assertIn("未熟", wxml)
        self.assertIn("chooseMedia", js)
        self.assertIn("detectBlueberries", js)
        self.assertIn("previewResultImage", js)


if __name__ == "__main__":
    unittest.main()
