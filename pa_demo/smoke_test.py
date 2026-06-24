#!/usr/bin/env python3
"""pa_demo 冒烟测试：用 Flask test_client，不起服务、零额外依赖。
运行：python3 pa_demo/smoke_test.py  （或在 pa_demo/ 内 python3 smoke_test.py）
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


def main() -> None:
    c = app.test_client()
    check_pages(c)
    check_apis(c)
    print("SMOKE OK")


if __name__ == "__main__":
    main()
