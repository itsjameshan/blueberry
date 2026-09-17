#!/usr/bin/env python3
"""替你点 PythonAnywhere 免费站的 "Run until 1 month from today" 按钮。

需要环境变量 PA_USERNAME、PA_PASSWORD（GitHub Actions 里从 Secrets 注入）。
流程和浏览器里一样：登录页拿 CSRF → 提交登录表单 → Web 页拿 CSRF → POST 延期地址 → 回读到期日确认变了。
表单字段和地址于 2026-09-17 在真实页面上核对过：
  登录  POST /login/            字段 auth-username / auth-password / login_view-current_step=auth
  延期  POST /user/<u>/webapps/<u>.pythonanywhere.com/extend
"""
import os
import re
import sys

import requests

BASE = "https://www.pythonanywhere.com"
DISABLED_ON = re.compile(r"disabled on\s+<strong>([^<]+)</strong>|disabled on\s+([A-Za-z]+ \d{1,2} [A-Za-z]+ \d{4})")


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    if not m:
        raise SystemExit("页面里没找到 csrfmiddlewaretoken")
    return m.group(1)


def disabled_on(html: str) -> str:
    m = DISABLED_ON.search(html)
    return (m.group(1) or m.group(2)).strip() if m else "?"


def main() -> None:
    user = os.environ.get("PA_USERNAME")
    password = os.environ.get("PA_PASSWORD")
    if not user or not password:
        raise SystemExit("缺少 PA_USERNAME / PA_PASSWORD 环境变量")

    s = requests.Session()
    s.headers["User-Agent"] = "pa-extend/1.0 (+github actions)"

    login_page = s.get(f"{BASE}/login/", timeout=30)
    login_page.raise_for_status()
    r = s.post(
        f"{BASE}/login/",
        data={
            "csrfmiddlewaretoken": csrf_from(login_page.text),
            "auth-username": user,
            "auth-password": password,
            "login_view-current_step": "auth",
        },
        headers={"Referer": f"{BASE}/login/"},
        timeout=30,
    )
    if "auth-password" in r.text or r.url.rstrip("/").endswith("/login"):
        raise SystemExit("登录失败：用户名或密码不对，或页面结构变了")

    webapps_url = f"{BASE}/user/{user}/webapps/"
    page = s.get(webapps_url, timeout=30)
    page.raise_for_status()
    before = disabled_on(page.text)

    r = s.post(
        f"{BASE}/user/{user}/webapps/{user}.pythonanywhere.com/extend",
        data={"csrfmiddlewaretoken": csrf_from(page.text)},
        headers={"Referer": webapps_url},
        timeout=30,
    )
    if r.status_code >= 400:
        raise SystemExit(f"延期请求被拒：HTTP {r.status_code}")

    after = disabled_on(s.get(webapps_url, timeout=30).text)
    print(f"到期日：{before} -> {after}")
    if after == "?":
        raise SystemExit("延期后读不到到期日，请人工检查 Web 页")


if __name__ == "__main__":
    main()
