#!/usr/bin/env python3
"""pa_demo —— master UI 的轻量伪静态演示后端。
无模型 / 无 weather API / 无数据库 / 无登录；检测与天气返回预置数据。
"""
import json
import re
from pathlib import Path

from flask import Flask, render_template, jsonify, request, send_file

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
