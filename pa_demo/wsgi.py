"""PythonAnywhere WSGI 入口。

在 Web 标签的 WSGI 配置文件里：把工作目录指向本文件所在目录，并
`from wsgi import application`（或直接 `from app import app as application`）。
把 pa_demo 目录插到 sys.path 最前，避免被同名 app.py 抢占导入。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) in sys.path:
    sys.path.remove(str(HERE))
sys.path.insert(0, str(HERE))

from app import app as application  # noqa: E402
