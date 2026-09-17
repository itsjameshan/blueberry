#!/usr/bin/env python3
"""把 master 的 detect_engine.py 和演示模型复制到 pa_demo/；加 --static 时再整体同步 static/。

用法（在仓库任意位置）：
    python pa_demo/build_demo.py            # 复制 detect_engine.py + onnx_data/best.onnx
    python pa_demo/build_demo.py --static   # 另外整体替换 pa_demo/static（会覆盖演示站自己的改动，如已删的退出按钮）
模型副本 pa_demo/onnx_data/ 不入库（见 .gitignore），打包 zip 前必须先跑一次。
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent      # .../blueberry/pa_demo
REPO = HERE.parent                           # .../blueberry
SRC = REPO / "static"
DST = HERE / "static"
ENGINE = REPO / "detect_engine.py"
MODEL = REPO / "onnx_data" / "best.onnx"


def sync_static() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"master static 不存在: {SRC}")
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    files = [p for p in DST.rglob("*") if p.is_file()]
    assert (DST / "landing.html").is_file(), "拷贝后缺 landing.html"
    print(f"copied {len(files)} files -> {DST}")


def sync_engine() -> None:
    shutil.copy2(ENGINE, HERE / ENGINE.name)
    print(f"copied {ENGINE.name}")

    if not MODEL.is_file():
        raise SystemExit(f"演示模型不存在: {MODEL}")
    (HERE / "onnx_data").mkdir(exist_ok=True)
    shutil.copy2(MODEL, HERE / "onnx_data" / MODEL.name)
    print(f"copied {MODEL.name} ({MODEL.stat().st_size // 1_000_000} MB)")


def main() -> None:
    if "--static" in sys.argv:
        sync_static()
    sync_engine()


if __name__ == "__main__":
    main()
