# WeChat Mini Program MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone WeChat Mini Program MVP that lets a user take or choose one blueberry photo, upload it to Flask, and see total, ripe, semi-ripe, and unripe counts plus an annotated image.

**Architecture:** Keep the existing Flask web app intact. Add mini-program-specific Flask API helpers and routes in `app.py`, then add a new `miniprogram/` WeChat project that calls those routes. Server-side ONNX inference continues to use `detect_engine.py`.

**Tech Stack:** Flask, Python `unittest`/Flask test client, WeChat Mini Program WXML/WXSS/JS, `wx.chooseMedia`, `wx.uploadFile`, `wx.previewImage`.

---

## File Structure

- Modify: `app.py`
  - Add class display labels, confidence parsing, mini result URL construction, mini result normalization, and three `/api/mini/*` routes.
  - Do not change existing browser routes or existing login-required APIs.
- Create: `tests/test_mini_api.py`
  - Backend tests for helper behavior and mini detection route contract.
- Create: `miniprogram/project.config.json`
  - WeChat Developer Tools project config.
- Create: `miniprogram/app.json`
  - Mini program page registration and window settings.
- Create: `miniprogram/app.js`
  - Minimal app bootstrap.
- Create: `miniprogram/app.wxss`
  - Global mobile styles.
- Create: `miniprogram/utils/config.js`
  - Backend base URL configuration.
- Create: `miniprogram/utils/api.js`
  - Upload API wrapper.
- Create: `miniprogram/pages/index/index.json`
  - Page title.
- Create: `miniprogram/pages/index/index.wxml`
  - Main capture/upload/result UI.
- Create: `miniprogram/pages/index/index.wxss`
  - Page layout.
- Create: `miniprogram/pages/index/index.js`
  - Page interaction, image choosing, upload, result preview, and reset.
- Create: `miniprogram/README.md`
  - Local development and production configuration notes.

## Task 1: Backend Mini API Contract

**Files:**
- Create: `tests/test_mini_api.py`
- Modify: `app.py`

- [ ] **Step 1: Write failing helper and route tests**

Create `tests/test_mini_api.py`:

```python
import io
import unittest
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_mini_api -v
```

Expected: FAIL because `parse_mini_conf`, `build_mini_summary`, `normalize_mini_results`, and `/api/mini/*` routes do not exist.

- [ ] **Step 3: Implement minimal backend helpers and mini routes**

In `app.py`, add these helper definitions near the existing folder constants:

```python
MINI_CLASS_DISPLAY_NAMES = {
    "RipeBlueBerry": "成熟可采",
    "Semi-RipeBlueBerry": "半熟",
    "UnripeBlueBerry": "未熟",
}

MINI_LABELS = {
    "ripe": "成熟可采",
    "semi_ripe": "半熟",
    "unripe": "未熟",
}


def parse_mini_conf(value):
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return 0.5
    return min(max(conf, 0.01), 0.99)


def build_mini_summary(stats):
    ripe = int(stats.get("RipeBlueBerry", 0))
    semi_ripe = int(stats.get("Semi-RipeBlueBerry", 0))
    unripe = int(stats.get("UnripeBlueBerry", 0))
    total = int(stats.get("total", ripe + semi_ripe + unripe))
    return {
        "total": total,
        "ripe": ripe,
        "semi_ripe": semi_ripe,
        "unripe": unripe,
        "harvestable": ripe,
    }


def normalize_mini_results(results):
    normalized = []
    for item in results:
        normalized.append({
            **item,
            "display_name": MINI_CLASS_DISPLAY_NAMES.get(item.get("class_name"), item.get("class_name", "未知")),
        })
    return normalized


def build_public_url(path):
    base_url = app.config.get("PUBLIC_BASE_URL", "").rstrip("/")
    if base_url:
        return f"{base_url}{path}"
    return request.host_url.rstrip("/") + path
```

Add these routes after `api_check_login` or before the existing login-required detection routes:

```python
@app.route("/api/mini/health")
def api_mini_health():
    model = get_active_model()
    return jsonify({
        "success": True,
        "model_loaded": is_model_loaded(),
        "model_name": model["model_name"] if model else "未配置模型",
    })


@app.route("/api/mini/detect", methods=["POST"])
def api_mini_detect():
    if "image" not in request.files:
        return jsonify({"success": False, "message": "请上传图片"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "message": "请选择图片"}), 400
    if not is_model_loaded():
        return jsonify({"success": False, "message": "模型未加载，请先加载ONNX模型"}), 503

    conf = parse_mini_conf(request.form.get("conf", 0.5))
    filename = f"mini_{os.urandom(8).hex()}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        results, stats = detect_single_image(filepath, conf_threshold=conf)
        result_filename = f"mini_result_{filename}"
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        draw_boxes(filepath, results, result_path)
    except RuntimeError as exc:
        return jsonify({"success": False, "message": str(exc)}), 503
    except Exception as exc:
        return jsonify({"success": False, "message": f"检测失败: {str(exc)}"}), 500

    result_path_url = f"/api/mini/result_image/{result_filename}"
    return jsonify({
        "success": True,
        "summary": build_mini_summary(stats),
        "labels": MINI_LABELS,
        "results": normalize_mini_results(results),
        "result_image": result_filename,
        "result_image_url": build_public_url(result_path_url),
        "conf_threshold": conf,
    })


@app.route("/api/mini/result_image/<filename>")
def api_mini_result_image(filename):
    path = os.path.join(RESULT_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({"success": False, "message": "图片不存在"}), 404
    return send_file(path, mimetype="image/jpeg")
```

- [ ] **Step 4: Run tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_mini_api -v
```

Expected: PASS.

- [ ] **Step 5: Commit backend mini API**

Run:

```bash
git add app.py tests/test_mini_api.py
git commit -m "feat: add mini program detection API"
```

## Task 2: Mini Program Project Shell and API Wrapper

**Files:**
- Create: `miniprogram/project.config.json`
- Create: `miniprogram/app.json`
- Create: `miniprogram/app.js`
- Create: `miniprogram/app.wxss`
- Create: `miniprogram/utils/config.js`
- Create: `miniprogram/utils/api.js`
- Create: `miniprogram/README.md`

- [ ] **Step 1: Write static verification test**

Append this class to `tests/test_mini_api.py`:

```python
import json
from pathlib import Path


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
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_mini_api.MiniProgramFilesTest -v
```

Expected: FAIL because `miniprogram/` files do not exist.

- [ ] **Step 3: Create mini program shell files**

Create `miniprogram/project.config.json`:

```json
{
  "description": "Blueberry maturity detection mini program",
  "packOptions": {
    "ignore": []
  },
  "setting": {
    "urlCheck": false,
    "es6": true,
    "enhance": true,
    "postcss": true,
    "minified": true
  },
  "compileType": "miniprogram",
  "libVersion": "latest",
  "appid": "touristappid",
  "projectname": "blueberry-mini-program",
  "condition": {}
}
```

Create `miniprogram/app.json`:

```json
{
  "pages": [
    "pages/index/index"
  ],
  "window": {
    "navigationBarTitleText": "蓝莓成熟度识别",
    "navigationBarBackgroundColor": "#2f6f4e",
    "navigationBarTextStyle": "white",
    "backgroundColor": "#f6f8f5"
  },
  "permission": {
    "scope.camera": {
      "desc": "用于拍摄蓝莓照片并进行成熟度识别"
    }
  },
  "style": "v2",
  "sitemapLocation": "sitemap.json"
}
```

Create `miniprogram/app.js`:

```javascript
App({
  globalData: {}
});
```

Create `miniprogram/app.wxss`:

```css
page {
  min-height: 100%;
  background: #f6f8f5;
  color: #1f2a24;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

button {
  font: inherit;
}
```

Create `miniprogram/utils/config.js`:

```javascript
const config = {
  baseUrl: "http://127.0.0.1:5000"
};

module.exports = config;
```

Create `miniprogram/utils/api.js`:

```javascript
const config = require("./config");

function parseUploadResponse(data) {
  if (typeof data === "string") {
    return JSON.parse(data);
  }
  return data;
}

function detectBlueberries(filePath, conf) {
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${config.baseUrl}/api/mini/detect`,
      filePath,
      name: "image",
      formData: {
        conf: String(conf || 0.5)
      },
      success(response) {
        let payload;
        try {
          payload = parseUploadResponse(response.data);
        } catch (error) {
          reject(new Error("服务器返回格式错误"));
          return;
        }

        if (response.statusCode >= 200 && response.statusCode < 300 && payload.success) {
          resolve(payload);
          return;
        }

        reject(new Error(payload.message || "检测失败"));
      },
      fail() {
        reject(new Error("无法连接检测服务"));
      }
    });
  });
}

module.exports = {
  detectBlueberries
};
```

Create `miniprogram/README.md`:

```markdown
# 蓝莓成熟度识别小程序

## 本地运行

1. 启动 Flask 后端：`python app.py`。
2. 用微信开发者工具打开本目录 `miniprogram/`。
3. 本地开发时关闭微信开发者工具里的合法域名校验。
4. 如后端不是 `http://127.0.0.1:5000`，修改 `utils/config.js` 的 `baseUrl`。

## 真机或上线

小程序正式访问必须使用 HTTPS 后端域名。部署 Flask 后，将 HTTPS 域名配置到微信公众平台的小程序 request、uploadFile、downloadFile 合法域名中，再修改 `utils/config.js`。
```

- [ ] **Step 4: Run tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_mini_api.MiniProgramFilesTest -v
```

Expected: PASS.

- [ ] **Step 5: Commit mini program shell**

Run:

```bash
git add miniprogram tests/test_mini_api.py
git commit -m "feat: add mini program project shell"
```

## Task 3: Mini Program Capture and Result Page

**Files:**
- Create: `miniprogram/pages/index/index.json`
- Create: `miniprogram/pages/index/index.wxml`
- Create: `miniprogram/pages/index/index.wxss`
- Create: `miniprogram/pages/index/index.js`
- Modify: `tests/test_mini_api.py`

- [ ] **Step 1: Write static page verification test**

Append this test method to `MiniProgramFilesTest` in `tests/test_mini_api.py`:

```python
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
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_mini_api.MiniProgramFilesTest.test_index_page_contains_capture_upload_and_result_states -v
```

Expected: FAIL because the index page files do not exist.

- [ ] **Step 3: Create index page files**

Create `miniprogram/pages/index/index.json`:

```json
{
  "navigationBarTitleText": "蓝莓成熟度识别"
}
```

Create `miniprogram/pages/index/index.wxml`:

```xml
<view class="page">
  <view class="hero">
    <view class="hero-title">蓝莓成熟度识别</view>
    <view class="hero-subtitle">拍一张蓝莓照片，快速统计成熟可采、半熟和未熟数量</view>
  </view>

  <view class="photo-panel">
    <view class="image-frame" bindtap="previewSelectedImage">
      <image wx:if="{{imagePath}}" class="selected-image" src="{{imagePath}}" mode="aspectFit"></image>
      <view wx:else class="empty-image">
        <view class="empty-icon">+</view>
        <view class="empty-text">选择或拍摄蓝莓照片</view>
      </view>
    </view>

    <view class="actions">
      <button class="btn primary" loading="{{choosingSource === 'camera'}}" disabled="{{loading}}" bindtap="chooseFromCamera">拍照识别</button>
      <button class="btn secondary" loading="{{choosingSource === 'album'}}" disabled="{{loading}}" bindtap="chooseFromAlbum">从相册选择</button>
    </view>

    <view class="conf-row">
      <text>置信度 {{conf}}</text>
      <slider min="0.1" max="0.9" step="0.05" value="{{conf}}" activeColor="#2f6f4e" block-size="18" bindchange="onConfChange"></slider>
    </view>

    <button class="detect-btn" loading="{{loading}}" disabled="{{!imagePath || loading}}" bindtap="startDetect">开始检测</button>
  </view>

  <view wx:if="{{errorMessage}}" class="error-box">{{errorMessage}}</view>

  <view wx:if="{{result}}" class="result-panel">
    <view class="section-title">识别结果</view>
    <image class="result-image" src="{{result.result_image_url}}" mode="aspectFit" bindtap="previewResultImage"></image>

    <view class="summary-grid">
      <view class="summary-card total">
        <view class="summary-value">{{result.summary.total}}</view>
        <view class="summary-label">总数</view>
      </view>
      <view class="summary-card ripe">
        <view class="summary-value">{{result.summary.ripe}}</view>
        <view class="summary-label">成熟可采</view>
      </view>
      <view class="summary-card semi">
        <view class="summary-value">{{result.summary.semi_ripe}}</view>
        <view class="summary-label">半熟</view>
      </view>
      <view class="summary-card unripe">
        <view class="summary-value">{{result.summary.unripe}}</view>
        <view class="summary-label">未熟</view>
      </view>
    </view>

    <view class="detail-header">检测明细</view>
    <view wx:if="{{result.results.length === 0}}" class="empty-result">未识别到蓝莓，请换一张更清晰的照片。</view>
    <view wx:for="{{result.results}}" wx:key="index" class="detail-row">
      <view>
        <view class="detail-name">{{item.display_name}}</view>
        <view class="detail-box">({{item.x1}}, {{item.y1}}, {{item.x2}}, {{item.y2}})</view>
      </view>
      <view class="detail-confidence">{{item.confidencePercent}}</view>
    </view>

    <button class="btn reset" bindtap="reset">再拍一张</button>
  </view>
</view>
```

Create `miniprogram/pages/index/index.js`:

```javascript
const { detectBlueberries } = require("../../utils/api");

Page({
  data: {
    imagePath: "",
    conf: 0.5,
    loading: false,
    choosingSource: "",
    result: null,
    errorMessage: ""
  },

  chooseFromCamera() {
    this.chooseImage(["camera"], "camera");
  },

  chooseFromAlbum() {
    this.chooseImage(["album"], "album");
  },

  chooseImage(sourceType, sourceName) {
    this.setData({
      choosingSource: sourceName,
      errorMessage: ""
    });

    wx.chooseMedia({
      count: 1,
      mediaType: ["image"],
      sourceType,
      sizeType: ["compressed"],
      success: (res) => {
        const file = res.tempFiles && res.tempFiles[0];
        if (!file || !file.tempFilePath) {
          this.setData({ errorMessage: "没有获取到图片" });
          return;
        }
        this.setData({
          imagePath: file.tempFilePath,
          result: null,
          errorMessage: ""
        });
      },
      fail: () => {
        this.setData({ errorMessage: "已取消选择图片" });
      },
      complete: () => {
        this.setData({ choosingSource: "" });
      }
    });
  },

  onConfChange(event) {
    this.setData({
      conf: Number(event.detail.value).toFixed(2)
    });
  },

  startDetect() {
    if (!this.data.imagePath || this.data.loading) {
      return;
    }

    this.setData({
      loading: true,
      errorMessage: "",
      result: null
    });

    detectBlueberries(this.data.imagePath, this.data.conf)
      .then((result) => {
        const normalized = {
          ...result,
          results: (result.results || []).map((item) => ({
            ...item,
            confidencePercent: `${(Number(item.confidence || 0) * 100).toFixed(1)}%`
          }))
        };
        this.setData({ result: normalized });
      })
      .catch((error) => {
        this.setData({ errorMessage: error.message || "检测失败" });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  previewSelectedImage() {
    if (!this.data.imagePath) {
      return;
    }
    wx.previewImage({
      urls: [this.data.imagePath],
      current: this.data.imagePath
    });
  },

  previewResultImage() {
    if (!this.data.result || !this.data.result.result_image_url) {
      return;
    }
    wx.previewImage({
      urls: [this.data.result.result_image_url],
      current: this.data.result.result_image_url
    });
  },

  reset() {
    this.setData({
      imagePath: "",
      result: null,
      errorMessage: ""
    });
  }
});
```

Create `miniprogram/pages/index/index.wxss`:

```css
.page {
  min-height: 100vh;
  padding: 32rpx;
  box-sizing: border-box;
}

.hero {
  padding: 16rpx 0 28rpx;
}

.hero-title {
  font-size: 46rpx;
  font-weight: 700;
  color: #183529;
}

.hero-subtitle {
  margin-top: 12rpx;
  font-size: 26rpx;
  line-height: 1.5;
  color: #5f6f66;
}

.photo-panel,
.result-panel {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 12rpx 40rpx rgba(31, 42, 36, 0.08);
}

.image-frame {
  height: 520rpx;
  border: 2rpx dashed #b9c9bf;
  border-radius: 12rpx;
  background: #f9fbf8;
  overflow: hidden;
}

.selected-image,
.result-image {
  width: 100%;
  height: 100%;
}

.empty-image {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6d7c72;
}

.empty-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  border: 2rpx solid #8dac99;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 56rpx;
}

.empty-text {
  margin-top: 18rpx;
  font-size: 26rpx;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
  margin-top: 24rpx;
}

.btn,
.detect-btn {
  border-radius: 12rpx;
  font-size: 28rpx;
}

.btn.primary,
.detect-btn {
  background: #2f6f4e;
  color: #ffffff;
}

.btn.secondary {
  background: #edf4ef;
  color: #28543e;
}

.btn.reset {
  margin-top: 24rpx;
  background: #edf4ef;
  color: #28543e;
}

.conf-row {
  margin: 24rpx 0;
  color: #506258;
  font-size: 26rpx;
}

.error-box {
  margin-top: 24rpx;
  padding: 20rpx 24rpx;
  border-radius: 12rpx;
  background: #fff0f0;
  color: #b42318;
  font-size: 26rpx;
}

.result-panel {
  margin-top: 28rpx;
}

.section-title,
.detail-header {
  font-size: 30rpx;
  font-weight: 700;
  color: #183529;
  margin-bottom: 18rpx;
}

.result-image {
  height: 560rpx;
  border-radius: 12rpx;
  background: #f0f4f1;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  margin: 24rpx 0;
}

.summary-card {
  padding: 22rpx;
  border-radius: 12rpx;
  background: #f6f8f5;
}

.summary-card.ripe {
  background: #eaf6ee;
}

.summary-card.semi {
  background: #fff6df;
}

.summary-card.unripe {
  background: #eef3ff;
}

.summary-value {
  font-size: 44rpx;
  font-weight: 700;
  color: #183529;
}

.summary-label {
  margin-top: 4rpx;
  font-size: 24rpx;
  color: #617267;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 18rpx;
  padding: 18rpx 0;
  border-top: 1rpx solid #edf1ee;
}

.detail-name {
  font-size: 28rpx;
  color: #1f2a24;
}

.detail-box {
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #7b897f;
}

.detail-confidence {
  flex: 0 0 auto;
  font-size: 26rpx;
  font-weight: 600;
  color: #2f6f4e;
}

.empty-result {
  padding: 22rpx;
  border-radius: 12rpx;
  background: #f6f8f5;
  color: #617267;
  font-size: 26rpx;
}
```

- [ ] **Step 4: Run tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_mini_api.MiniProgramFilesTest -v
```

Expected: PASS.

- [ ] **Step 5: Commit mini program page**

Run:

```bash
git add miniprogram tests/test_mini_api.py
git commit -m "feat: build mini program detection page"
```

## Task 4: Final Verification

**Files:**
- No new files.

- [ ] **Step 1: Run backend unit tests**

Run:

```bash
python3 -m unittest tests.test_mini_api -v
```

Expected: PASS.

- [ ] **Step 2: Run Python compile check**

Run:

```bash
python3 -m compileall app.py database.py detect_engine.py tests
```

Expected: PASS with no syntax errors.

- [ ] **Step 3: Verify web assets are untouched**

Run:

```bash
git diff --name-only HEAD~3..HEAD -- static
```

Expected: no output.

- [ ] **Step 4: Inspect final changed files**

Run:

```bash
git status --short
git log --oneline -4
```

Expected: clean working tree after commits, with commits for spec, backend API, mini shell, and mini page.
