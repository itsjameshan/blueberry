# 蓝莓检测系统 - 微信小程序部署流程

> 本文档记录蓝莓检测系统部署到微信小程序的完整流程，作为开发参考。

---

## 一、项目概述

| 项目 | 说明 |
|------|------|
| **后端框架** | Flask + ONNX Runtime |
| **前端技术** | Jinja2 模板 + 响应式 CSS |
| **小程序框架** | 微信小程序原生 + web-view |
| **数据库** | SQLite |
| **部署方式** | 局域网内网自测 |

---

## 二、整体架构

```
┌────────────────────────────────────────────────────┐
│               微信小程序 (Miniprogram)               │
│  ┌──────────────────────────────────────────────┐  │
│  │   pages/index/index.wxml                     │  │
│  │   <web-view src="http://10.77.56.49:5000">  │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
                        ↓ HTTP 请求
┌────────────────────────────────────────────────────┐
│                Flask 后端 (app.py)                  │
│  跨域配置 │ Session 管理 │ 文件上传 │ API 接口        │
└────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────┬─────────────────────────────┐
│   detect_engine.py   │       database.py            │
│  模型推理 │ 图像处理  │  用户管理 │ 检测记录 │ 模型配置 │
└──────────────────────┴─────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│           SQLite 数据库 + ONNX 模型文件              │
└────────────────────────────────────────────────────┘
```

---

## 三、搭建流程

### 阶段 1：环境准备

#### 1.1 安装 Python 依赖

```powershell
# 进入项目目录
cd e:\blue

# 安装核心依赖
python -m pip install flask flask-cors onnxruntime opencv-python pillow werkzeug
```

#### 1.2 安装微信开发者工具

- 访问 https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
- 下载并安装微信开发者工具
- 使用微信扫码登录

---

### 阶段 2：后端配置

#### 2.1 配置跨域支持（关键）

修改 `app.py`，添加 `flask-cors` 支持：

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__, template_folder='static')
app.secret_key = 'blueberry_detection_secret_key_2026'

# 跨域配置 - 关键，支持小程序 web-view 访问
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Session 配置
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 * 24 * 7
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False
```

#### 2.2 配置自动模型加载

修改 `database.py` 的 `init_db()` 函数，让系统启动时自动扫描 `onnx_data/` 目录：

```python
import os
from datetime import datetime

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 创建数据表（users, detection_records, model_config）
    # ...

    # 扫描 onnx_data 目录，自动添加模型配置
    onnx_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'onnx_data')
    if os.path.exists(onnx_folder):
        cursor.execute("SELECT COUNT(*) as cnt FROM model_config")
        if cursor.fetchone()['cnt'] == 0:
            onnx_files = sorted([f for f in os.listdir(onnx_folder) if f.endswith('.onnx')])
            if onnx_files:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for i, onnx_file in enumerate(onnx_files):
                    model_path = os.path.join(onnx_folder, onnx_file)
                    is_active = 1 if i == 0 else 0
                    cursor.execute(
                        "INSERT INTO model_config (model_name, model_path, is_active, created_at) VALUES (?, ?, ?, ?)",
                        (onnx_file, model_path, is_active, now)
                    )

    conn.commit()
    conn.close()
```

#### 2.3 添加启动日志

修改 `app.py` 启动代码：

```python
if __name__ == '__main__':
    init_db()
    model = get_active_model()
    if model:
        print(f"找到激活模型: {model['model_name']}")
        print(f"模型路径: {model['model_path']}")
        if os.path.exists(model['model_path']):
            success = load_model(model['model_path'])
            if success:
                print("✅ 模型加载成功！")
            else:
                print("❌ 模型加载失败！")
        else:
            print(f"❌ 模型文件不存在: {model['model_path']}")
    else:
        print("⚠️ 未找到激活模型")
    print("蓝莓检测系统启动中...")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
```

#### 2.4 启动后端服务

```powershell
cd e:\blue
python app.py
```

启动成功后显示：
```
找到激活模型: v11best.onnx
模型路径: E:\blue\onnx_data\v11best.onnx
✅ 模型加载成功！
蓝莓检测系统启动中...
```

---

### 阶段 3：获取局域网 IP

```powershell
ipconfig
```

找到 **无线局域网适配器 WLAN** 的 IPv4 地址，例如：`10.77.56.49`

---

### 阶段 4：配置 Windows 防火墙

放行 5000 端口（图形化操作）：

1. 打开 **控制面板 → 系统和安全 → Windows Defender 防火墙**
2. 点击 **高级设置**
3. 选择 **入站规则 → 新建规则**
4. 规则类型：**端口**
5. 协议：**TCP**，特定本地端口：**5000**
6. 操作：**允许连接**
7. 配置文件：全部勾选
8. 名称：**Flask 5000 端口**

---

### 阶段 5：手机端 CSS 适配

为每个页面添加移动端响应式样式，在 CSS 文件末尾添加：

```css
/* ========== 移动端适配 ========== */
@media (max-width: 768px) {
    .navbar { padding: 10px 15px; }
    .nav-links { gap: 10px; }
    .nav-link { font-size: 13px; padding: 4px 8px; }

    .hero { padding: 40px 15px; }
    .hero h1 { font-size: 24px; }
    .hero p { font-size: 14px; }

    .container { padding: 15px; }
    .card { padding: 15px; }

    .grid { grid-template-columns: 1fr; gap: 15px; }

    button, .btn { width: 100%; padding: 12px; font-size: 15px; }

    input, select, textarea {
        font-size: 16px;
        padding: 10px;
    }
}
```

需要适配的文件：
- `static/css/style.css`
- `static/css/login.css`
- `static/css/single_detect.css`
- `static/css/big_image.css`
- `static/css/batch_detect.css`
- `static/css/admin.css`

---

### 阶段 6：创建小程序项目

#### 6.1 创建目录结构

```
e:\blue\miniprogram\
├── app.js
├── app.json
├── app.wxss
├── project.config.json
├── project.private.config.json
└── pages/
    └── index/
        ├── index.js
        ├── index.json
        ├── index.wxml
        └── index.wxss
```

#### 6.2 配置文件内容

**`app.json`**
```json
{
  "pages": ["pages/index/index"],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#ffffff",
    "navigationBarTitleText": "蓝莓检测系统",
    "navigationBarTextStyle": "black"
  }
}
```

**`pages/index/index.wxml`**
```xml
<web-view src="http://10.77.56.49:5000"></web-view>
```

**`pages/index/index.json`**
```json
{
  "navigationStyle": "custom",
  "disableScroll": true
}
```

**`project.config.json`**
```json
{
  "description": "蓝莓检测系统微信小程序",
  "appid": "wx94db46c5a8692a5e",
  "projectname": "blueberry-miniprogram",
  "setting": {
    "checkSiteMap": false,
    "urlCheck": false
  }
}
```

---

### 阶段 7：解决 sitemap 错误

微信小程序要求配置 sitemap.json，否则真机调试会报错。

#### 解决方法

1. **删除 `sitemap.json` 文件**（如果存在）
2. **修改 `project.config.json`**：
   ```json
   "checkSiteMap": false
   ```
3. **修改 `app.json`**：移除 `sitemapLocation` 字段

---

### 阶段 8：导入项目到开发者工具

1. 打开微信开发者工具
2. 点击 **导入项目**
3. 项目目录：`e:\blue\miniprogram\`
4. AppID：自动读取（应该是 `wx94db46c5a8692a5e`）
5. 点击 **导入**

---

### 阶段 9：真机调试

1. 确保手机和电脑连接**同一 WiFi**
2. 在开发者工具顶部点击 **真机调试**
3. 用手机微信扫码
4. 小程序自动打开并访问 Flask 后端

---

## 四、推送代码到 GitHub

### 4.1 初始化 Git 仓库

```powershell
cd e:\blue
git init
```

### 4.2 创建 .gitignore

```gitignore
__pycache__/
*.pyc
*.pyo
uploads/
results/
crop_output/
*.db
*.log
.vscode/
project.private.config.json
```

### 4.3 创建独立分支

```powershell
git add .
git commit -m "feat: 添加微信小程序部署支持"
git remote add origin https://github.com/itsjameshan/blueberry.git
git checkout -b "微信小程序"
git push -u origin "微信小程序"
```

### 4.4 注意事项

⚠️ **不要合并到 master** - 会覆盖 master 分支的完整代码
✅ **保持分支独立** - 在"微信小程序"分支上独立开发

---

## 五、常见问题

### Q1: 真机调试显示"模型未配置或未加载"

**原因**：数据库中没有激活的模型配置

**解决**：
- 检查 `onnx_data/` 目录下是否有 `.onnx` 文件
- 删除 `blueberry.db` 数据库文件，让 `init_db()` 重新初始化
- 重启后端服务

### Q2: 小程序显示"连接断开、服务器繁忙"

**原因**：
- 局域网 IP 变了
- Flask 服务未启动
- 防火墙未放行 5000 端口

**解决**：
- 确认 Flask 服务在运行
- 重新获取 IP 并修改 `index.wxml`
- 检查防火墙设置

### Q3: sitemap 错误

**解决**：
- 删除 `sitemap.json`
- 在 `project.config.json` 中设置 `"checkSiteMap": false`
- 在 `app.json` 中移除 `sitemapLocation` 字段

### Q4: 跨域问题导致 session 丢失

**解决**：
- 安装 `flask-cors`：`pip install flask-cors`
- 在 `app.py` 中添加跨域配置
- 配置 `SESSION_COOKIE_SAMESITE = None`

---

## 六、文件清单

### 后端文件

| 文件 | 作用 |
|------|------|
| `app.py` | Flask 主程序，包含路由、API、跨域配置 |
| `database.py` | SQLite 数据库操作 |
| `detect_engine.py` | ONNX 模型推理引擎 |
| `onnx_data/*.onnx` | 模型文件 |
| `blueberry.db` | SQLite 数据库 |

### 前端文件（static/）

| 文件 | 作用 |
|------|------|
| `login.html` | 登录注册页 |
| `index.html` | 首页 |
| `single_detect.html` | 单图检测页 |
| `batch_detect.html` | 批量检测页 |
| `big_image.html` | 大图检测页 |
| `result.html` | 检测记录页 |
| `admin.html` | 管理后台 |
| `css/*.css` | 各页面样式 |
| `js/*.js` | 各页面交互逻辑 |

### 小程序文件（miniprogram/）

| 文件 | 作用 |
|------|------|
| `app.json` | 小程序配置 |
| `app.js` | 小程序入口 |
| `pages/index/*` | web-view 容器页面 |

---

## 七、总结

本项目通过 **web-view 嵌套** 的方式实现微信小程序：

1. ✅ **优势**：复用现有 Flask 网页，开发快
2. ⚠️ **限制**：无法使用小程序原生能力（如扫码、定位）
3. 🔧 **关键点**：跨域配置 + Session 共享 + 局域网 IP

后续如需扩展小程序原生能力，可在小程序中新增原生页面，通过 `wx.navigateTo` 跳转。
