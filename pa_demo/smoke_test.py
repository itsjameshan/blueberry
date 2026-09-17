#!/usr/bin/env python3
"""pa_demo 冒烟测试：Flask test_client，不起服务；需要 onnx_data/best.onnx（先跑 build_demo.py）。
运行：python3 pa_demo/smoke_test.py  （或在 pa_demo/ 内 python3 smoke_test.py）
"""
import io
import time
from pathlib import Path

from PIL import Image

import app as demo
from app import app

HERE = Path(__file__).resolve().parent
PHOTO = HERE / "static" / "BlueBerrytree.jpg"  # 演示站自带的真实蓝莓照片，zip 里一定有

PAGES = [
    "/", "/about", "/tech", "/more", "/portal",
    "/weather", "/weather/alerts", "/garden",
    "/index", "/single_detect", "/batch_detect",
]
STATS_KEYS = ("RipeBlueBerry", "Semi-RipeBlueBerry", "UnripeBlueBerry", "total")


def photo():
    return (io.BytesIO(PHOTO.read_bytes()), "tree.jpg")


def post_single(c, file, conf=None):
    data = {"image": file}
    if conf is not None:
        data["conf"] = conf
    return c.post("/api/detect_single", data=data, content_type="multipart/form-data")


def post_batch(c, files):
    return c.post("/api/batch_detect_multi", data={"images": files}, content_type="multipart/form-data")


def check_pages(c) -> None:
    for path in PAGES:
        r = c.get(path)
        assert r.status_code == 200, f"{path} -> {r.status_code}"
        assert b"demo-mode-banner" in r.data, f"banner 缺失: {path}"
    print(f"[ok] pages: {len(PAGES)} routes 200 + banner")


def check_model(c) -> None:
    d = c.get("/api/current_model").get_json()
    assert d["success"] and d["model_loaded"] is True, "模型未加载：先跑 pa_demo/build_demo.py"
    assert "best.onnx" in d["model_name"], d["model_name"]
    print("[ok] current_model:", d["model_name"])


def check_single(c) -> None:
    t = time.time()
    d = post_single(c, photo()).get_json()
    assert d["success"], d
    assert all(k in d["stats"] for k in STATS_KEYS), d["stats"]
    assert d["stats"]["total"] >= 1, "真实照片应至少检出 1 颗"
    assert d["results"][0]["class_name"] in STATS_KEYS[:3]
    assert d["conf_threshold"] == 0.5
    r = c.get(d["result_image"])
    assert r.status_code == 200 and r.content_type.startswith("image/jpeg"), d["result_image"]
    assert not list(demo.UPLOADS.iterdir()), "uploads/ 应在检测后清空"
    print(f"[ok] single: total={d['stats']['total']} in {time.time() - t:.2f}s")

    d = post_single(c, photo(), conf="0.1").get_json()
    assert d["success"] and d["conf_threshold"] == 0.1, d
    print(f"[ok] single conf=0.1: total={d['stats']['total']}")

    d = post_single(c, photo(), conf="abc").get_json()
    assert d["success"] and d["conf_threshold"] == 0.5, "非法 conf 应回退 0.5"
    print("[ok] single conf=abc -> 0.5")


def check_bad_inputs(c) -> None:
    d = c.post("/api/detect_single").get_json()
    assert not d["success"] and "上传" in d["message"], d
    d = post_single(c, (io.BytesIO(b"hello, not an image"), "fake.jpg")).get_json()
    assert not d["success"] and "有效" in d["message"], d
    d = post_single(c, (io.BytesIO(b"\xff\xd8" + b"\0" * (11 * 1024 * 1024)), "big.jpg")).get_json()
    assert not d["success"] and "10 MB" in d["message"], d
    buf = io.BytesIO()
    Image.new("RGB", (6000, 4000), (20, 40, 60)).save(buf, format="PNG")  # 24 MP > 20 MP
    d = post_single(c, (io.BytesIO(buf.getvalue()), "huge.png")).get_json()
    assert not d["success"] and "像素" in d["message"], d
    assert not list(demo.UPLOADS.iterdir())
    print("[ok] bad inputs: missing / fake / 11MB / 24MP all rejected")


def check_batch(c) -> None:
    d = post_batch(c, [photo() for _ in range(6)]).get_json()
    assert not d["success"] and "5" in d["message"], d
    d = post_batch(c, [photo(), (io.BytesIO(b"nope"), "bad.jpg")]).get_json()
    assert d["success"] and len(d["results"]) == 2, d
    assert d["results"][0]["filename"] == "tree.jpg" and d["results"][0]["stats"]["total"] >= 1
    assert d["results"][1]["error"] and d["results"][1]["result_image"] == ""
    assert d["total_stats"]["total"] == d["results"][0]["stats"]["total"]
    assert c.get(d["results"][0]["result_image"]).status_code == 200
    d = post_batch(c, []).get_json()
    assert not d["success"], d
    print("[ok] batch: 6 rejected, 1 good + 1 bad partial, empty rejected")


def check_result_image_guard(c) -> None:
    for path in ("/api/result_image/sample_result.jpg", "/api/result_image/..%2Fapp.py",
                 "/api/result_image/result_zzzz.jpg", "/api/result_image/result_0123456789abcdef.jpg"):
        assert c.get(path).status_code == 404, path
    print("[ok] result_image: non-matching / missing names -> 404")


def check_quota(c) -> None:
    saved = demo.DAILY_IMAGE_CAP
    demo.DAILY_IMAGE_CAP = 2
    demo._daily["count"] = 0
    try:
        assert post_single(c, photo()).get_json()["success"]
        assert post_single(c, photo()).get_json()["success"]
        r = post_single(c, photo())
        assert r.status_code == 429 and "上限" in r.get_json()["message"], r.get_json()
        r = c.post("/api/detect_single", data={"image": photo()}, content_type="multipart/form-data",
                   headers={"X-Forwarded-For": "1.2.3.4"})
        assert r.status_code == 429, "换 IP 也不应绕过全站上限"
        d = post_single(c, (io.BytesIO(b"nope"), "bad.jpg")).get_json()
        assert not d["success"] and "上限" not in d["message"], "无效文件应在扣额前被拒，且不占额度"
    finally:
        demo.DAILY_IMAGE_CAP = saved
        demo._daily["count"] = 0
    print("[ok] quota: 3rd image -> 429 regardless of IP, invalid file rejected before quota")


def check_preset_apis(c) -> None:
    d = c.get("/api/check_login").get_json()
    assert d["logged_in"] is True
    d = c.get("/api/gardens").get_json()
    assert d["success"] and d["gardens"][0]["growth_stage"] in ("dormant", "sprouting", "flowering", "fruiting")
    d = c.get("/api/weather/1").get_json()
    assert d["success"] and d["weather"]["realtime"]["temp"] is not None and len(d["weather"]["forecast"]) > 1
    d = c.get("/api/alerts").get_json()
    assert d["success"] and "garden_name" in d["alerts"][0]
    d = c.get("/api/alerts/stats").get_json()
    assert d["stats"]["by_level"] and d["stats"]["by_garden"]
    d = c.get("/api/user/thresholds").get_json()
    assert d["thresholds"]["temp_high"]
    d = c.post("/api/user/email").get_json()
    assert d["success"] and d.get("demo") is True
    print("[ok] preset apis: login / gardens / weather / alerts / thresholds / email")


def main() -> None:
    app.config["TESTING"] = True
    before = set(demo.RESULTS.glob("result_*.jpg"))
    try:
        with app.test_client() as c:
            check_pages(c)
            check_model(c)
            check_single(c)
            check_bad_inputs(c)
            check_batch(c)
            check_result_image_guard(c)
            check_quota(c)
            check_preset_apis(c)
    finally:
        for p in set(demo.RESULTS.glob("result_*.jpg")) - before:
            p.unlink(missing_ok=True)
    print("ALL OK")


if __name__ == "__main__":
    main()
