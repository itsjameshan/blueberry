# pa_demo —— 蓝莓系统 PythonAnywhere 演示站

master 完整前端 UI 的公开演示站：**单图 / 批量检测用真实模型（`onnx_data/best.onnx`，YOLO11s）实时推理**；天气、果园、预警为预置数据；无登录、无数据库、不调外部接口。面向 PythonAnywhere 免费层（512 MB 磁盘、每天 100 秒 CPU、单工作进程、外网仅白名单）。

## 本地运行

```bash
python3 pa_demo/build_demo.py     # 复制 detect_engine.py + onnx_data/best.onnx 到本目录（模型副本不入库）
pip3 install -r pa_demo/requirements.txt
python3 pa_demo/app.py            # http://127.0.0.1:5050
python3 pa_demo/smoke_test.py     # 冒烟测试：页面、真实检测、恶意输入、批量上限、结果图守卫、每日上限
```

> 用脚本路径方式启动（`python3 pa_demo/app.py`），确保导入的是本目录的 `app.py` 与 `detect_engine.py`。
> `static/` 已与 master 分叉（演示站删掉了退出按钮），**不要**随手跑 `build_demo.py --static` 整体覆盖；只把需要的单个文件从 `../static/` 复制过来。

## 限额（全部为了免费层）

| 项 | 值 | 原因 |
|----|----|------|
| 一次最多 | 5 张 | CPU 额度 |
| 单张 | ≤ 10 MB，≤ 20 MP，JPG/PNG，`verify()` 通过 | 内存、解压炸弹 |
| 全站每天 | 40 张（内存计数，Reload 清零；改 `app.py` 里 `DAILY_IMAGE_CAP`） | 对应每天 100 秒 CPU；不按 IP 是因为代理头可伪造 |
| 结果图保留 | 24 小时，检测请求时顺手清理；上传原图检测完即删 | 512 MB 磁盘 |
| 推理线程 | 1 | 单工作进程，多线程只抢额度 |
| 大图切块 | 不开放 | 一张要十几秒 CPU |

本地实测（Apple Silicon，单线程）：加载模型 0.4–0.6 秒，每张 CPU 1.2–1.4 秒。免费层机器更慢，按每张 2–3 秒估，**全站每天约 30–50 张**；额度用完 PythonAnywhere 不报错，只是请求排队变慢。模型在模块加载时读入，**Reload 后的第一个请求（不论哪个页面）会多等几秒**。

## 部署到 PythonAnywhere（免费层，Python 3.10）

> 只上传本 `pa_demo/` 文件夹（含模型约 45 MB），**不要**克隆整个 blueberry 仓库（git 历史 1.3 GB，超免费层配额）。

1. 把代码放上去，两条路二选一：
   - **路径 A：服务器上已有本仓库的 git 克隆**（`~/blueberry`，WSGI 指向 `~/blueberry/pa_demo`）。先把本次改动推到 `master`，然后 **Bash console**：
     ```bash
     cd ~/blueberry && git pull --ff-only origin master
     mkdir -p pa_demo/onnx_data
     wget https://raw.githubusercontent.com/itsjameshan/blueberry/master/onnx_data/best.onnx -O pa_demo/onnx_data/best.onnx
     ```
     模型不入库，所以要单独 `wget`（`.githubusercontent.com` 在免费层白名单内）。下面的命令里把 `pa_demo` 换成 `~/blueberry/pa_demo`。
   - **路径 B：zip 上传**。本地先跑过 `build_demo.py`（确保 `pa_demo/onnx_data/best.onnx` 存在），再打包：
     ```bash
     zip -r pa_demo.zip pa_demo -x "pa_demo/uploads/*" "pa_demo/results/*" "pa_demo/__pycache__/*"
     ```
     **Files** 页上传 `pa_demo.zip`（约 37 MB）到 `/home/<USER>/`；**Bash console**：`rm -rf pa_demo && unzip -o pa_demo.zip`。
2. 装依赖并自检（**Bash console**）：
   ```bash
   pip3.10 install --user --no-cache-dir -r pa_demo/requirements.txt
   python3.10 -c "import onnxruntime, numpy, PIL; print('ok')"
   du -sh pa_demo ~/.local ~/.cache/pip 2>/dev/null
   ```
   `import` 失败先看报错；`~/.cache/pip` 若有内容直接 `rm -rf`。不要求 `cv2`：有就用它画框，没有走 PIL。
3. 首次部署才需要：**Web** → **Add a new web app** → **Manual configuration** → **Python 3.10**；WSGI 文件改为：
   ```python
   import sys
   path = "/home/<USER>/pa_demo"
   if path in sys.path:
       sys.path.remove(path)
   sys.path.insert(0, path)
   from app import app as application
   ```
   **Static files**：URL `/static/` → Directory `/home/<USER>/pa_demo/static/`。
4. **Reload**。Web 页的绿色 Reload 按钮有时不生效，稳妥的做法是在 Bash console 里 `touch /var/www/<USER>_pythonanywhere_com_wsgi.py`，等 20–30 秒。然后先自己打开一次首页预热，再上传一张真实照片确认有检测框和三类计数。Dashboard 里看 CPU 用量增量，把实测数字记回本 README。
5. Dashboard 磁盘用量应远低于 512 MB（依赖约 100 MB + 模型 37 MB + 代码 8 MB）。

## 说明

- 模型：`best.onnx` = YOLO11s，同学标注的 2700+ 张照片（标注修正前）训练，与 `v12best.onnx`（YOLO12s，原始数据集）不是同一份结果，页面上统一标 "best.onnx（YOLO11s）"。
- 天气仍为预置数据：和风天气的开发者专属域名 `*.re.qweatherapi.com` 不在免费层白名单，可向 support@pythonanywhere.com 申请加入 `qweatherapi.com`。
- 邮件预警不可用：免费层不允许连 `smtp.qq.com`。
- 免费层网站每月到期一次，需登录点 "Run until 1 month from today"。
- 抖音视频由访客浏览器直连抖音播放器加载，服务器不参与。
