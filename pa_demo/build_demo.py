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
