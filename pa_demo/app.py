#!/usr/bin/env python3
"""pa_demo —— 演示站后端：真实 YOLO 检测 + 预置气象数据。
无 weather API / 无数据库 / 无登录；单图/批量检测用 onnx_data/best.onnx 实时推理，其余接口返回预置数据。
面向 PythonAnywhere 免费层（512 MB 磁盘、每天 100 秒 CPU、单工作进程），所以对上传做了大小/像素/张数/每 IP 次数限制。
"""
import json
import os
import re
import time
import traceback
from datetime import date
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request, send_from_directory
from PIL import Image

from detect_engine import detect_single_image, draw_boxes, is_model_loaded, load_model

BASE = Path(__file__).resolve().parent
DEMO = BASE / "demo_data"


def load(name: str):
    return json.loads((DEMO / name).read_text(encoding="utf-8"))


DEMO_OK = {"success": True, "demo": True, "message": "演示模式：该操作在云端不执行"}

app = Flask(__name__, template_folder="static", static_folder="static")

DEMO_BANNER = (
    '<div class="demo-mode-banner" style="position:sticky;top:0;z-index:9999;'
    "background:#1f4e2c;color:#fff;text-align:center;padding:6px 12px;"
    'font-size:14px;font-family:sans-serif">'
    "演示站：检测为真实模型推理（best.onnx · YOLO11s），每日检测次数有限，高峰时段可能较慢；天气仍为预置数据</div>"
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


@app.route("/labelme")
def labelme():
    return page("labelme.html", active="labelme")


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


@app.route("/api/check_login")
def api_check_login():
    return jsonify(logged_in=True, **GUEST)


# ---- 真实检测（免费层限额见模块 docstring）----
MAX_FILES = 5
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000  # 4032×3024 的手机照片是 12.2 MP，必须能过；20 MP 解码约 60 MB
RESULT_TTL_SECONDS = 24 * 3600
DAILY_IMAGE_CAP = 40  # 全站每天（张）：免费层 100 秒 CPU，按每张 2–3 秒就是这个量级
STATS_KEYS = ("RipeBlueBerry", "Semi-RipeBlueBerry", "UnripeBlueBerry", "total")

UPLOADS = BASE / "uploads"
RESULTS = BASE / "results"
UPLOADS.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILES * MAX_IMAGE_BYTES + 1024 * 1024

MODEL_PATH = BASE / "onnx_data" / "best.onnx"
# ponytail: 模块加载时读入模型（单线程约 0.5 秒），单进程站点一次性成本；失败细节由 load_model 打到 stderr
load_model(str(MODEL_PATH), num_threads=1)

# ponytail: 全站计数而不是每 IP：代理头可伪造、无法在部署前验证，而 CPU 额度本来就是全站共用的。内存计数，按天重置，Reload 清零
_daily = {"day": None, "count": 0}


def _take_quota(n: int) -> bool:
    today = date.today()
    if _daily["day"] != today:
        _daily["day"], _daily["count"] = today, 0
    if _daily["count"] + n > DAILY_IMAGE_CAP:
        return False
    _daily["count"] += n
    return True


def _conf() -> float:
    try:
        return min(0.9, max(0.1, float(request.form.get("conf", 0.5))))
    except (TypeError, ValueError):
        return 0.5


def validate_image(storage):
    """返回错误信息；合法返回 None。读文件头取格式和像素，verify() 查结构，不解码像素。"""
    stream = storage.stream
    stream.seek(0, 2)
    size = stream.tell()
    stream.seek(0)
    if size == 0:
        return "文件为空"
    if size > MAX_IMAGE_BYTES:
        return "单张图片不能超过 10 MB"
    try:
        with Image.open(stream) as im:
            fmt, (w, h) = im.format, im.size
            im.verify()
    except Exception:
        return "不是有效的 JPG/PNG 图片"
    finally:
        stream.seek(0)
    if fmt not in ("JPEG", "PNG"):
        return "只支持 JPG/PNG 图片"
    if w * h > MAX_IMAGE_PIXELS:
        return "图片像素过大，请压缩后再上传"
    return None


def prune_results() -> None:
    cutoff = time.time() - RESULT_TTL_SECONDS
    for p in RESULTS.glob("result_*.jpg"):
        try:
            if p.stat().st_mtime < cutoff:
                p.unlink()
        except FileNotFoundError:
            pass


def run_detection(storage, conf: float) -> dict:
    token = os.urandom(8).hex()
    upload = UPLOADS / f"{token}.jpg"
    result_name = f"result_{token}.jpg"
    try:
        storage.save(upload)
        results, stats = detect_single_image(str(upload), conf_threshold=conf)
        draw_boxes(str(upload), results, str(RESULTS / result_name))
        if not (RESULTS / result_name).is_file():
            raise RuntimeError("结果图未生成")
    finally:
        upload.unlink(missing_ok=True)
    return {"results": results, "stats": stats, "result_image": f"/api/result_image/{result_name}"}


@app.errorhandler(413)
def too_large(_e):
    return jsonify(success=False, message="上传超过大小限制"), 413


@app.route("/api/current_model")
def api_current_model():
    return jsonify(success=True, model_loaded=is_model_loaded(), model_name="best.onnx（YOLO11s）")


@app.route("/api/detect_single", methods=["POST"])
def api_detect_single():
    if not is_model_loaded():
        return jsonify(success=False, message="模型未加载")
    f = request.files.get("image")
    if f is None or not f.filename:
        return jsonify(success=False, message="请上传图片")
    err = validate_image(f)
    if err:
        return jsonify(success=False, message=err)
    if not _take_quota(1):
        return jsonify(success=False, message="今日检测次数已达上限"), 429
    prune_results()
    conf = _conf()
    try:
        out = run_detection(f, conf)
    except Exception:
        traceback.print_exc()
        return jsonify(success=False, message="检测失败")
    return jsonify(success=True, conf_threshold=conf, **out)


@app.route("/api/batch_detect_multi", methods=["POST"])
def api_batch_detect_multi():
    if not is_model_loaded():
        return jsonify(success=False, message="模型未加载")
    files = [f for f in request.files.getlist("images") if f.filename]
    if not files:
        return jsonify(success=False, message="请选择图片")
    if len(files) > MAX_FILES:
        return jsonify(success=False, message=f"一次最多 {MAX_FILES} 张")
    errors = [validate_image(f) for f in files]
    valid = sum(1 for e in errors if not e)
    if valid and not _take_quota(valid):  # 只按通过校验的张数扣额；推理失败也算，CPU 已经花了
        return jsonify(success=False, message="今日检测次数已达上限"), 429
    prune_results()
    conf = _conf()
    total = {k: 0 for k in STATS_KEYS}
    items = []
    for f, err in zip(files, errors):
        if not err:
            try:
                out = run_detection(f, conf)
            except Exception:
                traceback.print_exc()
                err = "检测失败"
        if err:
            items.append({"filename": f.filename, "results": [], "stats": {k: 0 for k in STATS_KEYS},
                          "result_image": "", "error": err})
            continue
        for k in STATS_KEYS:
            total[k] += out["stats"].get(k, 0)
        items.append({"filename": f.filename, **out})
    return jsonify(success=True, total_stats=total, results=items)


@app.route("/api/result_image/<filename>")
def api_result_image(filename):
    if not re.fullmatch(r"result_[0-9a-f]{16}\.jpg", filename):
        abort(404)
    return send_from_directory(RESULTS, filename, mimetype="image/jpeg")


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
