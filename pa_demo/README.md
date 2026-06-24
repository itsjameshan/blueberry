# pa_demo —— 蓝莓系统 PythonAnywhere 演示部署

master 完整前端 UI 的轻量伪静态拷贝：能看到所有页面与抖音视频，但**云端不做实时预测、不调天气 API、无数据库、无登录**。检测与天气均为预置演示数据。

## 本地运行

```bash
pip3 install -r requirements.txt
python3 app.py          # http://127.0.0.1:5050
python3 smoke_test.py   # 冒烟测试（页面 200 + API 形状）
```

> 注意：用 `python3 app.py` / `python3 smoke_test.py`（脚本路径方式）启动，确保导入的是本目录的 `app.py`，而不是仓库根目录 master 的 `app.py`。

## 重新同步前端（master UI 有改动时）

```bash
python3 build_demo.py   # 从 ../static 重新拷贝到 ./static，然后提交
```

## 部署到 PythonAnywhere（免费层）

> 只上传本 `pa_demo/` 文件夹（约 8MB），**不要**克隆整个 blueberry 仓库（含数 GB 训练数据，会超免费层 512MB 配额）。

1. 本地打包：在仓库根目录执行 `zip -r pa_demo.zip pa_demo`。
2. 注册 / 登录 PythonAnywhere，进入 **Files**，上传 `pa_demo.zip` 到 `/home/<USER>/`，在 **Bash console** 里 `unzip pa_demo.zip`。
3. **Web** 标签 → **Add a new web app** → **Manual configuration** → **Python 3.x**。
4. 安装依赖：Bash console 里 `pip3 install --user flask`。
5. 编辑 Web 标签里的 **WSGI configuration file**：删掉默认内容，改为指向本应用：
   ```python
   import sys
   path = "/home/<USER>/pa_demo"
   if path in sys.path:
       sys.path.remove(path)
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
