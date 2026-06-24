# pa_demo PythonAnywhere 伪静态部署 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `blueberry` 根目录新建自包含文件夹 `pa_demo/`，复刻 master 完整前端 UI，但后端换成超轻 Flask（无模型 / 无 weather API / 无数据库 / 无登录），检测与天气返回预置演示数据，可整文件夹上传到 PythonAnywhere 免费层。

**Architecture:** 复用 master 的 `Flask(template_folder='static')` 渲染方式 —— `pa_demo/app.py` 定义同名页面路由（render_template）+ 约 15 个 `/api/*` 桩（返回 `demo_data/` 的 canned JSON / 示例图）。前端 HTML/CSS/JS/图片由 `build_demo.py` 从 master `static/` 整份拷贝进 `pa_demo/static/` 并提交，使该文件夹自包含、可单独上传。

**Tech Stack:** Python 3.x、Flask（仅此一个运行期依赖）、原生 `json`/`shutil`/`pathlib`、Flask `test_client`（测试，无需起服务、无需额外依赖）。

## Global Constraints

- 运行期依赖只允许 `flask`。**禁止**引入 `onnxruntime`、`opencv-python`、`numpy`、`requests`、`python-dotenv`，**禁止** `import detect_engine`、`import database`。
- 全开放无登录：无 session、无数据库、无鉴权；不保留 `/login`、`/logout`、admin、labelme。
- 页面范围：`/` `/about` `/tech` `/more` `/portal` `/weather` `/weather/alerts` `/garden` `/index` `/single_detect` `/batch_detect`。**排除** big_image / admin / labelme。
- 演示提示条文案，逐字使用：`演示模式：云端不做实时预测，检测与天气均为示例数据`。
- `pa_demo/` 必须自包含：`pa_demo/static/` 要提交进 git（接受与 master `static/` 的 ~6MB 重复，换取可单独上传部署）。
- 不改动 `blueberry` master 任何现有文件（只新增 `pa_demo/` 与本计划/规格文档）。
- 本地运行端口用 `5050`，避免与 master（5000/5001）冲突。
- 检测三类名固定：`RipeBlueBerry` / `Semi-RipeBlueBerry` / `UnripeBlueBerry`，加 `total`。
- 规格来源：`docs/superpowers/specs/2026-06-24-pa-demo-pythonanywhere-deploy-design.md`。

---

## File Structure

```
pa_demo/
├── app.py            # 精简 Flask：页面路由 + API 桩 + 演示提示条注入
├── build_demo.py     # 从 ../static 整份同步 pa_demo/static（开发期重建用）
├── smoke_test.py     # Flask test_client 冒烟测试：页面 200 + banner + API JSON 形状
├── wsgi.py           # PythonAnywhere WSGI 入口
├── requirements.txt  # 仅 flask
├── README.md         # PythonAnywhere 部署步骤（含静态映射）
├── demo_data/        # 预置演示数据
│   ├── detect_single.json
│   ├── batch_item.json
│   ├── gardens.json
│   ├── weather.json
│   ├── alerts.json
│   ├── alerts_stats.json
│   ├── thresholds.json
│   └── sample_result.jpg
└── static/           # 由 build_demo.py 从 ../static 拷贝（提交进 git）
```

各文件职责单一：`app.py` 只做路由与桩；`build_demo.py` 只做资源同步；`demo_data/` 是唯一的演示数据来源（single source）；`smoke_test.py` 是唯一测试入口。

---

## Task 1: 资源同步脚本与依赖声明

**Files:**
- Create: `pa_demo/build_demo.py`
- Create: `pa_demo/requirements.txt`

**Interfaces:**
- Produces: 运行 `python pa_demo/build_demo.py` 后存在 `pa_demo/static/`（含 `landing.html`、`css/`、`js/`、`img/`），内容等同 master `static/`。后续所有 Task 依赖该目录存在。

- [ ] **Step 1: 写 `pa_demo/requirements.txt`**

```text
flask==3.1.1
```

- [ ] **Step 2: 写 `pa_demo/build_demo.py`**

```python
#!/usr/bin/env python3
"""把 master 的 static/ 整份同步到 pa_demo/static/。

用法（在仓库任意位置）：python pa_demo/build_demo.py
让演示站始终反映当前 master 前端。可重复运行，会整体替换 pa_demo/static。
"""
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent      # .../blueberry/pa_demo
REPO = HERE.parent                           # .../blueberry
SRC = REPO / "static"
DST = HERE / "static"


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"master static 不存在: {SRC}")
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    files = [p for p in DST.rglob("*") if p.is_file()]
    assert (DST / "landing.html").is_file(), "拷贝后缺 landing.html"
    print(f"copied {len(files)} files -> {DST}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 运行同步，验证产物**

Run: `python pa_demo/build_demo.py`
Expected: 打印 `copied <N> files -> .../pa_demo/static`（N 约为数百），无报错。

- [ ] **Step 4: 校验关键资源到位**

Run: `ls pa_demo/static/landing.html pa_demo/static/js/landing.js pa_demo/static/img/covers/n1.webp`
Expected: 三个路径都存在（页面、视频脚本、抖音封面）。

- [ ] **Step 5: 提交**

```bash
git add pa_demo/build_demo.py pa_demo/requirements.txt pa_demo/static
git commit -m "feat(pa_demo): add asset sync script and vendored static UI"
```

---

## Task 2: 精简 Flask —— 页面路由 + 演示提示条

**Files:**
- Create: `pa_demo/app.py`
- Create: `pa_demo/smoke_test.py`

**Interfaces:**
- Consumes: `pa_demo/static/`（Task 1 产物）。
- Produces: 模块级 `app`（Flask 实例，`template_folder='static'`、`static_folder='static'`）。后续 Task 在同一 `app.py` 上追加 `/api/*` 路由。`smoke_test.py` 通过 `from app import app` 取得它。
- Produces: 所有 HTML 响应经 `after_request` 注入含 `class="demo-mode-banner"` 的提示条 `<div>`。

- [ ] **Step 1: 写 `pa_demo/smoke_test.py`（先只测页面，预期失败）**

```python
#!/usr/bin/env python3
"""pa_demo 冒烟测试：用 Flask test_client，不起服务、零额外依赖。
运行：python pa_demo/smoke_test.py
"""
from app import app

PAGES = [
    "/", "/about", "/tech", "/more", "/portal",
    "/weather", "/weather/alerts", "/garden",
    "/index", "/single_detect", "/batch_detect",
]


def check_pages(c) -> None:
    for path in PAGES:
        r = c.get(path)
        assert r.status_code == 200, f"{path} -> {r.status_code}"
        assert b"demo-mode-banner" in r.data, f"banner 缺失: {path}"
    print(f"[ok] pages: {len(PAGES)} routes 200 + banner")


def main() -> None:
    c = app.test_client()
    check_pages(c)
    print("SMOKE OK")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `cd pa_demo && python smoke_test.py`
Expected: FAIL —— `ModuleNotFoundError: No module named 'app'`（app.py 尚未创建）。

- [ ] **Step 3: 写 `pa_demo/app.py`（仅页面路由 + 提示条）**

```python
#!/usr/bin/env python3
"""pa_demo —— master UI 的轻量伪静态演示后端。
无模型 / 无 weather API / 无数据库 / 无登录；检测与天气返回预置数据。
"""
import re
from pathlib import Path

from flask import Flask, render_template

BASE = Path(__file__).resolve().parent

app = Flask(__name__, template_folder="static", static_folder="static")

DEMO_BANNER = (
    '<div class="demo-mode-banner" style="position:sticky;top:0;z-index:9999;'
    "background:#1f4e2c;color:#fff;text-align:center;padding:6px 12px;"
    'font-size:14px;font-family:sans-serif">'
    "演示模式：云端不做实时预测，检测与天气均为示例数据</div>"
)

# 演示访客上下文：页面里若引用 username/role/active，Jinja 默认 Undefined 静默为空，安全。
GUEST = {"username": "游客", "role": "guest"}


def page(name: str, **extra):
    return render_template(name, **GUEST, **extra)


@app.route("/")
def landing():
    return page("landing.html", active="home")


@app.route("/about")
def about():
    return page("about.html", active="about")


@app.route("/tech")
def tech():
    return page("tech.html", active="tech")


@app.route("/more")
def more():
    return page("more.html", active="more")


@app.route("/portal")
def portal():
    return page("portal.html")


@app.route("/weather")
def weather():
    return page("weather.html")


@app.route("/weather/alerts")
def weather_alerts():
    return page("alerts.html")


@app.route("/garden")
def garden():
    return page("garden.html")


@app.route("/index")
def index():
    return page("index.html")


@app.route("/single_detect")
def single_detect():
    return page("single_detect.html")


@app.route("/batch_detect")
def batch_detect_page():
    return page("batch_detect.html")


@app.after_request
def inject_banner(resp):
    ctype = resp.content_type or ""
    if ctype.startswith("text/html"):
        body = resp.get_data(as_text=True)
        if "<body" in body and "demo-mode-banner" not in body:
            body = re.sub(r"(<body[^>]*>)", r"\1" + DEMO_BANNER, body, count=1)
            resp.set_data(body)
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `cd pa_demo && python smoke_test.py`
Expected: 打印 `[ok] pages: 11 routes 200 + banner` 和 `SMOKE OK`。

- [ ] **Step 5: 人工浏览器走查（启动本地服务）**

Run: `cd pa_demo && python app.py`
打开 `http://127.0.0.1:5050/` —— 确认：顶部绿色“演示模式”提示条；landing 视频封面（7 张）显示；点导航能进 portal / weather / 检测页（页面渲染，API 暂未实现可忽略报错）。确认后 Ctrl+C 停服务。

- [ ] **Step 6: 提交**

```bash
git add pa_demo/app.py pa_demo/smoke_test.py
git commit -m "feat(pa_demo): page routes + demo banner + page smoke test"
```

---

## Task 3: 演示数据 + API 桩

**Files:**
- Create: `pa_demo/demo_data/detect_single.json`
- Create: `pa_demo/demo_data/batch_item.json`
- Create: `pa_demo/demo_data/gardens.json`
- Create: `pa_demo/demo_data/weather.json`
- Create: `pa_demo/demo_data/alerts.json`
- Create: `pa_demo/demo_data/alerts_stats.json`
- Create: `pa_demo/demo_data/thresholds.json`
- Create: `pa_demo/demo_data/sample_result.jpg`（从 `results/` 拷一张真实标注图）
- Modify: `pa_demo/app.py`（追加 API 路由 + 数据加载）
- Modify: `pa_demo/smoke_test.py`（追加 API 断言）

**Interfaces:**
- Consumes: Task 2 的 `app`。
- Produces 的 API 响应形状（已对照前端 JS 逐一确认）：
  - `GET /api/check_login` → `{logged_in: true, username, role}`（`static/js/portal.js` 只读 `logged_in`）
  - `GET /api/current_model` → `{success: true, model_loaded: true, model_name}`（`single_detect.html`/`batch_detect.html`）
  - `POST /api/detect_single` → `{success, result_image, stats:{RipeBlueBerry,Semi-RipeBlueBerry,UnripeBlueBerry,total}, results:[{class_name,confidence,x1,y1,x2,y2}]}`（`static/js/single_detect.js`）
  - `POST /api/batch_detect_multi` → `{success, total_stats:{...}, results:[{filename,result_image,stats:{...},results:[...]}]}`（`static/js/batch_detect.js`，按上传文件名回显）
  - `GET /api/result_image/<filename>` → image/jpeg（发 `demo_data/sample_result.jpg`）
  - `GET /api/gardens` → `{success, gardens:[{id,name,location,growth_stage,plant_date,created_at}]}`（`weather.js`/`garden.js`/`alerts.js`）
  - `GET /api/weather/check-all` → `{success: true, sent: 0}`（`weather.js`）
  - `GET /api/weather/<int:garden_id>` → `{success, garden, weather:{fetched_at,realtime,forecast}, alerts, advice}`（`weather.js` renderWeather）
  - `GET /api/alerts` → `{success, alerts:[{level,title,garden_name,content,start_time,end_time,created_at}]}`（`alerts.js`）
  - `GET /api/alerts/stats` → `{success, stats:{total,by_level,by_garden,by_date}}`（`alerts.js`）
  - `GET /api/user/info` → `{success, user:{email}}`（`weather.js`）
  - `GET /api/user/thresholds` → `{success, thresholds:{temp_high,temp_low,humidity_high,humidity_low,wind_speed_high,precipitation_high}}`（`alerts.js`）
  - 写操作 `POST /api/user/email`、`POST/GET 之外的 /api/user/thresholds POST`、`POST /api/weather/<int:garden_id>/notify` → `{success: true, demo: true, message: "演示模式：该操作在云端不执行"}`

- [ ] **Step 1: 拷贝一张真实标注结果图作演示图**

Run: `cp "$(ls results/result_*.jpg | head -1)" pa_demo/demo_data/sample_result.jpg && ls -l pa_demo/demo_data/sample_result.jpg`
Expected: `pa_demo/demo_data/sample_result.jpg` 存在（非空）。
（说明：`results/` 是 master 已有的检测输出标注图，作演示结果展示。）

- [ ] **Step 2: 写 `pa_demo/demo_data/detect_single.json`**

```json
{
  "success": true,
  "result_image": "/api/result_image/sample_result.jpg",
  "stats": { "RipeBlueBerry": 3, "Semi-RipeBlueBerry": 2, "UnripeBlueBerry": 1, "total": 6 },
  "results": [
    { "class_name": "RipeBlueBerry", "confidence": 0.94, "x1": 122, "y1": 88, "x2": 168, "y2": 140 },
    { "class_name": "RipeBlueBerry", "confidence": 0.91, "x1": 210, "y1": 132, "x2": 256, "y2": 182 },
    { "class_name": "RipeBlueBerry", "confidence": 0.88, "x1": 64, "y1": 196, "x2": 110, "y2": 244 },
    { "class_name": "Semi-RipeBlueBerry", "confidence": 0.81, "x1": 300, "y1": 90, "x2": 344, "y2": 138 },
    { "class_name": "Semi-RipeBlueBerry", "confidence": 0.76, "x1": 158, "y1": 250, "x2": 202, "y2": 296 },
    { "class_name": "UnripeBlueBerry", "confidence": 0.69, "x1": 360, "y1": 210, "x2": 404, "y2": 258 }
  ]
}
```

- [ ] **Step 3: 写 `pa_demo/demo_data/batch_item.json`**（单张图的模板，桩按上传文件数复制）

```json
{
  "stats": { "RipeBlueBerry": 3, "Semi-RipeBlueBerry": 2, "UnripeBlueBerry": 1, "total": 6 },
  "results": [
    { "class_name": "RipeBlueBerry", "confidence": 0.94, "x1": 122, "y1": 88, "x2": 168, "y2": 140 },
    { "class_name": "Semi-RipeBlueBerry", "confidence": 0.81, "x1": 300, "y1": 90, "x2": 344, "y2": 138 },
    { "class_name": "UnripeBlueBerry", "confidence": 0.69, "x1": 360, "y1": 210, "x2": 404, "y2": 258 }
  ]
}
```

- [ ] **Step 4: 写 `pa_demo/demo_data/gardens.json`**

```json
{
  "success": true,
  "gardens": [
    { "id": 1, "name": "示范蓝莓园 A 区", "location": "云南·昆明", "growth_stage": "fruiting", "plant_date": "2024-03-02", "created_at": "2026-06-24 09:00" },
    { "id": 2, "name": "示范蓝莓园 B 区", "location": "云南·玉溪", "growth_stage": "flowering", "plant_date": "2024-03-15", "created_at": "2026-06-24 09:00" }
  ]
}
```

- [ ] **Step 5: 写 `pa_demo/demo_data/weather.json`**

```json
{
  "success": true,
  "garden": { "name": "示范蓝莓园 A 区", "location": "云南·昆明", "growth_stage": "fruiting" },
  "weather": {
    "fetched_at": "2026-06-24 09:00",
    "realtime": { "temp": 24, "text": "多云", "feelsLike": 25, "humidity": 68, "windDir": "东南风", "windSpeed": 9, "precipitation": 0.0, "pressure": 1008, "visibility": 22 },
    "forecast": [
      { "date": "2026-06-24", "textDay": "多云", "tempMin": 17, "tempMax": 26 },
      { "date": "2026-06-25", "textDay": "晴", "tempMin": 18, "tempMax": 28 },
      { "date": "2026-06-26", "textDay": "阵雨", "tempMin": 16, "tempMax": 24 },
      { "date": "2026-06-27", "textDay": "小雨", "tempMin": 15, "tempMax": 22 }
    ]
  },
  "alerts": [ { "title": "高温预警", "content": "未来两天午后气温偏高，注意遮阴与灌溉。" } ],
  "advice": [
    { "level": "warning", "title": "高温防护", "content": "午后高温时段加强灌溉，避免果实日灼。" },
    { "level": "info", "title": "采收建议", "content": "成熟蓝莓比例较高，建议近两日安排采收。" }
  ]
}
```

- [ ] **Step 6: 写 `pa_demo/demo_data/alerts.json`**

```json
{
  "success": true,
  "alerts": [
    { "level": "warning", "title": "高温预警", "garden_name": "示范蓝莓园 A 区", "content": "午后最高气温达 33°C，注意遮阴与补水。", "start_time": "2026-06-24 12:00", "end_time": "2026-06-25 18:00", "created_at": "2026-06-24 09:00" },
    { "level": "info", "title": "降水提示", "garden_name": "示范蓝莓园 B 区", "content": "明日有阵雨，注意排涝。", "start_time": "", "end_time": "", "created_at": "2026-06-24 08:30" }
  ]
}
```

- [ ] **Step 7: 写 `pa_demo/demo_data/alerts_stats.json`**

```json
{
  "success": true,
  "stats": {
    "total": 5,
    "by_level": [ { "level": "warning", "count": 2 }, { "level": "info", "count": 3 } ],
    "by_garden": [ { "garden_name": "A 区", "count": 3 }, { "garden_name": "B 区", "count": 2 } ],
    "by_date": [ { "date": "06-22", "count": 1 }, { "date": "06-23", "count": 2 }, { "date": "06-24", "count": 2 } ]
  }
}
```

- [ ] **Step 8: 写 `pa_demo/demo_data/thresholds.json`**

```json
{
  "success": true,
  "thresholds": { "temp_high": 35, "temp_low": 5, "humidity_high": 85, "humidity_low": 30, "wind_speed_high": 40, "precipitation_high": 25 }
}
```

- [ ] **Step 9: 在 `pa_demo/app.py` 顶部追加数据加载工具**

在 `import re` 行后、`app = Flask(...)` 前插入：

```python
import json

from flask import jsonify, request, send_file

DEMO = BASE / "demo_data"


def load(name: str):
    return json.loads((DEMO / name).read_text(encoding="utf-8"))


DEMO_OK = {"success": True, "demo": True, "message": "演示模式：该操作在云端不执行"}
```

（注意：`from flask import Flask, render_template` 保持不变；上面单独再 import 所需符号即可。）

- [ ] **Step 10: 在 `pa_demo/app.py` 的 `@app.after_request` 之前追加 API 桩**

```python
@app.route("/api/check_login")
def api_check_login():
    return jsonify(logged_in=True, **GUEST)


@app.route("/api/current_model")
def api_current_model():
    return jsonify(success=True, model_loaded=True, model_name="v11best（演示）")


@app.route("/api/detect_single", methods=["POST"])
def api_detect_single():
    return jsonify(load("detect_single.json"))


@app.route("/api/batch_detect_multi", methods=["POST"])
def api_batch_detect_multi():
    files = request.files.getlist("images")
    names = [f.filename for f in files] or ["示例图片.jpg"]
    tpl = load("batch_item.json")
    keys = ("RipeBlueBerry", "Semi-RipeBlueBerry", "UnripeBlueBerry", "total")
    total = {k: 0 for k in keys}
    results = []
    for nm in names:
        results.append({
            "filename": nm,
            "result_image": "/api/result_image/sample_result.jpg",
            "stats": tpl["stats"],
            "results": tpl["results"],
        })
        for k in keys:
            total[k] += tpl["stats"][k]
    return jsonify(success=True, total_stats=total, results=results)


@app.route("/api/result_image/<path:filename>")
def api_result_image(filename):
    return send_file(DEMO / "sample_result.jpg", mimetype="image/jpeg")


@app.route("/api/gardens")
def api_gardens():
    return jsonify(load("gardens.json"))


@app.route("/api/weather/check-all")
def api_weather_check_all():
    return jsonify(success=True, sent=0)


@app.route("/api/weather/<int:garden_id>")
def api_weather(garden_id):
    return jsonify(load("weather.json"))


@app.route("/api/weather/<int:garden_id>/notify", methods=["POST"])
def api_weather_notify(garden_id):
    return jsonify(DEMO_OK)


@app.route("/api/alerts")
def api_alerts():
    return jsonify(load("alerts.json"))


@app.route("/api/alerts/stats")
def api_alerts_stats():
    return jsonify(load("alerts_stats.json"))


@app.route("/api/user/info")
def api_user_info():
    return jsonify(success=True, user={"email": ""})


@app.route("/api/user/thresholds", methods=["GET", "POST"])
def api_user_thresholds():
    if request.method == "POST":
        return jsonify(DEMO_OK)
    return jsonify(load("thresholds.json"))


@app.route("/api/user/email", methods=["POST"])
def api_user_email():
    return jsonify(DEMO_OK)
```

- [ ] **Step 11: 在 `pa_demo/smoke_test.py` 追加 API 断言**

在 `check_pages` 函数后、`main` 前插入：

```python
def check_apis(c) -> None:
    d = c.get("/api/current_model").get_json()
    assert d["success"] and d["model_loaded"] and d["model_name"], "current_model"

    d = c.get("/api/check_login").get_json()
    assert d["logged_in"] is True, "check_login"

    d = c.post("/api/detect_single").get_json()
    assert d["success"], "detect_single.success"
    for k in ("RipeBlueBerry", "Semi-RipeBlueBerry", "UnripeBlueBerry", "total"):
        assert k in d["stats"], f"detect_single.stats.{k}"
    assert d["results"] and "class_name" in d["results"][0], "detect_single.results"

    import io
    data = {"images": (io.BytesIO(b"x"), "a.jpg")}
    d = c.post("/api/batch_detect_multi", data=data, content_type="multipart/form-data").get_json()
    assert d["success"] and d["results"][0]["filename"] == "a.jpg", "batch echo filename"
    assert d["total_stats"]["total"] == d["results"][0]["stats"]["total"], "batch total"

    r = c.get("/api/result_image/sample_result.jpg")
    assert r.status_code == 200 and r.content_type.startswith("image/"), "result_image"

    d = c.get("/api/gardens").get_json()
    assert d["success"] and d["gardens"][0]["growth_stage"] in ("dormant", "sprouting", "flowering", "fruiting"), "gardens"

    d = c.get("/api/weather/1").get_json()
    assert d["success"] and d["weather"]["realtime"]["temp"] is not None, "weather.realtime"
    assert len(d["weather"]["forecast"]) > 1, "weather.forecast"

    d = c.get("/api/alerts").get_json()
    assert d["success"] and "garden_name" in d["alerts"][0], "alerts"

    d = c.get("/api/alerts/stats").get_json()
    assert d["stats"]["by_level"] and d["stats"]["by_garden"], "alerts.stats"

    d = c.get("/api/user/thresholds").get_json()
    assert d["thresholds"]["temp_high"], "thresholds"

    d = c.post("/api/user/email").get_json()
    assert d["demo"] is True, "user/email demo"

    print("[ok] apis: shapes match frontend")
```

并把 `main` 改为：

```python
def main() -> None:
    c = app.test_client()
    check_pages(c)
    check_apis(c)
    print("SMOKE OK")
```

- [ ] **Step 12: 运行测试，确认全绿**

Run: `cd pa_demo && python smoke_test.py`
Expected: 依次打印 `[ok] pages: 11 ...`、`[ok] apis: shapes match frontend`、`SMOKE OK`。

- [ ] **Step 13: 人工浏览器走查**

Run: `cd pa_demo && python app.py`
检查：单图检测页点“检测”出示例标注图 + 三类计数 + 明细表；批量检测上传 1-2 张图出汇总（图片数与上传数一致）；天气页选园出实时卡片 + 3 天预报 + 农业建议；预警页出告警卡片与统计图；浏览器控制台无红色报错。确认后 Ctrl+C。

- [ ] **Step 14: 提交**

```bash
git add pa_demo/demo_data pa_demo/app.py pa_demo/smoke_test.py
git commit -m "feat(pa_demo): canned demo data + stubbed API routes + api smoke tests"
```

---

## Task 4: WSGI 入口、部署文档、终检

**Files:**
- Create: `pa_demo/wsgi.py`
- Create: `pa_demo/README.md`

**Interfaces:**
- Consumes: 前三个 Task 的完整 `pa_demo/`。
- Produces: `wsgi.py` 暴露 `application`（PythonAnywhere 约定）；`README.md` 部署步骤。

- [ ] **Step 1: 写 `pa_demo/wsgi.py`**

```python
"""PythonAnywhere WSGI 入口。
在 Web 标签的 WSGI 配置文件里：把工作目录指向本文件所在目录，并
`from wsgi import application`（或直接 `from app import app as application`）。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from app import app as application  # noqa: E402
```

- [ ] **Step 2: 写 `pa_demo/README.md`**

````markdown
# pa_demo —— 蓝莓系统 PythonAnywhere 演示部署

master 完整前端 UI 的轻量伪静态拷贝：能看到所有页面与抖音视频，但**云端不做实时预测、不调天气 API、无数据库、无登录**。检测与天气均为预置演示数据。

## 本地运行

```bash
pip install -r requirements.txt
python app.py          # http://127.0.0.1:5050
python smoke_test.py   # 冒烟测试
```

## 重新同步前端（master UI 有改动时）

```bash
python build_demo.py   # 从 ../static 重新拷贝到 ./static，然后提交
```

## 部署到 PythonAnywhere（免费层）

> 只上传本 `pa_demo/` 文件夹（约 6MB），**不要**克隆整个 blueberry 仓库（含数 GB 训练数据，会超免费层 512MB 配额）。

1. 本地打包：在仓库根目录执行 `zip -r pa_demo.zip pa_demo`。
2. 注册 / 登录 PythonAnywhere，进入 **Files**，上传 `pa_demo.zip` 到 `/home/<USER>/`，在 **Bash console** 里 `unzip pa_demo.zip`。
3. **Web** 标签 → **Add a new web app** → **Manual configuration** → **Python 3.x**。
4. 配置 virtualenv（可选）并安装依赖：Bash console 里 `pip install --user flask`。
5. 编辑 Web 标签里的 **WSGI configuration file**：删掉默认内容，改为指向本应用：
   ```python
   import sys
   path = "/home/<USER>/pa_demo"
   if path not in sys.path:
       sys.path.insert(0, path)
   from app import app as application
   ```
6. **Static files** 映射（即“网页端要定义的那几项”）：
   - URL: `/static/`  →  Directory: `/home/<USER>/pa_demo/static/`
7. 点 **Reload**，访问 `https://<USER>.pythonanywhere.com/`。

## 说明

- 本应用无任何外部网络调用（天气为预置数据），不受免费层出站代理白名单影响。
- 抖音视频由访客浏览器直连抖音播放器加载，服务器不参与。
- 真实模型推理、和风天气、用户系统在完整版 `blueberry`（master）里，不在本演示。
````

- [ ] **Step 3: 终检 —— 无重依赖**

Run: `grep -nE "onnxruntime|opencv|cv2|numpy|requests|detect_engine|import database" pa_demo/app.py pa_demo/wsgi.py || echo "CLEAN: no heavy deps"`
Expected: 打印 `CLEAN: no heavy deps`。

- [ ] **Step 4: 终检 —— 体积**

Run: `du -sh pa_demo && du -sh pa_demo/static`
Expected: `pa_demo` 总体积 < 10MB（static 约 6MB + demo_data 一张图）。

- [ ] **Step 5: 终检 —— 冒烟全绿 + 依赖仅 flask**

Run: `cd pa_demo && python smoke_test.py && cat requirements.txt`
Expected: `SMOKE OK`；`requirements.txt` 只有 `flask==3.1.1`。

- [ ] **Step 6: 提交**

```bash
git add pa_demo/wsgi.py pa_demo/README.md
git commit -m "feat(pa_demo): wsgi entry + PythonAnywhere deploy doc"
```

- [ ] **Step 7（用户手动，不在本计划自动执行）：** 按 `pa_demo/README.md` 打包上传到 PythonAnywhere，配置 WSGI 与静态映射，Reload 后回看完整 UI + 演示数据。

---

## Self-Review

**1. Spec coverage（对照规格逐节）**
- §3 决策表（精简 Flask / 无登录 / 完整 UI / 无模型 / canned 天气 / 视频照搬 / `pa_demo` / 排除 admin·labelme·big_image / 提示条）→ 全部落在 Global Constraints + Task 1-4。✓
- §4.1 文件夹布局 → File Structure 与 Task 文件清单一致。✓
- §4.2 复用 Jinja 渲染 → Task 2 `app.py`（`template_folder='static'` + render_template + GUEST 上下文）。✓
- §4.3 路由与 API 桩清单 → Task 2（页面）+ Task 3（API），逐条对齐。✓
- §4.4 提示条 → Task 2 `after_request` 注入（单一来源、survive 重建）。✓
- §5 去掉/桩掉 → Global Constraints 禁依赖 + Task 终检 grep。✓
- §6 抖音视频 → Task 1 校验 `js/landing.js`+`img/covers/` 到位；Task 2 走查封面。✓
- §7 测试策略 → `smoke_test.py`（test_client，零依赖）+ 每 Task 走查 + 终检体积/依赖。✓
- §8 部署文档 → Task 4 README（含静态映射、只传 pa_demo 不克隆全仓）。✓
- §9 阶段 → Task 1-4 对应 P1-P4。✓
- §10 验收 → Task 4 终检覆盖（启动、视频、演示数据、无重依赖、smoke、体积、README、不动 master）。✓

**2. Placeholder scan：** 无 TBD/TODO；所有步骤含真实代码/命令/预期输出。✓

**3. Type/shape consistency：** API 形状均取自前端 JS 实读（`single_detect.js` 用 `data.stats.RipeBlueBerry`/`data.results[].class_name`；`batch_detect.js` 用 `data.total_stats`/`item.filename`；`weather.js` 用 `weather.realtime`/`forecast`/`advice` 且 `growth_stage∈{dormant,sprouting,flowering,fruiting}`；`alerts.js` 用 `stats.by_level/by_garden/by_date`、`a.garden_name`；`thresholds` 六字段）。`smoke_test.py` 断言与桩返回字段一致。✓

---

## Execution Handoff

计划已存到 `docs/superpowers/plans/2026-06-24-pa-demo-pythonanywhere-deploy.md`。两种执行方式：

1. **Subagent-Driven（推荐）** —— 每个 Task 派一个全新 subagent，Task 间复核，迭代快。
2. **Inline Execution** —— 本会话内按 executing-plans 批量执行，带检查点。

（用户已表示用 `/goal` 执行；`/goal` 可直接吃这份计划逐 Task 落地。）
