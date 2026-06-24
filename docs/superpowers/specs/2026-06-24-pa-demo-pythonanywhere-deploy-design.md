# 设计规格：`pa_demo/` —— master UI 的轻量伪静态部署

- 日期：2026-06-24
- 状态：已确认设计，待落实施计划
- 目标读者：实施本任务的 AI 编程助手 / 开发者

---

## 1. 背景

仓库里存在两份蓝莓检测系统：

- **`blueberry` master（本仓库）**：完整版。`Flask(template_folder='static')`，页面从 `static/*.html` 渲染，含 landing/portal/tech/about/more/weather/alerts/garden/index/single_detect/batch_detect 等 16 个页面；后端依赖 3 个 onnx 模型（约 115MB）、weather 和风 API、SQLite、登录会话。`app.py` 约 1230 行。前端调用约 20 个 `/api/*` 接口。
- **`fabu`（`/Users/jameshan/Developments/fabu`，远端 `origin/master` / `blueberry/fabu-master-import`）**：较旧的精简 Flask 版，Jinja `templates/`，仅检测相关页面（login/index/single/batch/admin/result），带 2 个 onnx 模型（约 77MB），**无 weather、无 landing/portal**。曾验证可部署到 PythonAnywhere。

**问题**：master 完整版太重，直接上 PythonAnywhere 免费层（磁盘 512MB、CPU 受限、出站白名单代理）会爆掉；模型推理与和风 API 在免费层也跑不动 / 被拦。但希望有一个公开网址，让访客点进来能看到 master 的完整漂亮界面。

**解法**：在 `blueberry` 根目录新建自包含文件夹 `pa_demo/`，放 master 前端的一份可独立部署拷贝，后端换成超轻 Flask —— 无模型、无 weather API、无数据库、无登录，检测与天气返回预置演示数据。部署这个文件夹即可。

---

## 2. 目标与非目标

### 目标
1. `blueberry` 根目录下新建 `pa_demo/`，自包含、可独立部署。
2. 复刻 master 完整公开 UI（含抖音视频），访客可点遍所有公开页面。
3. 后端极简：检测、天气、各类接口返回预置演示数据，云端不做实时计算。
4. 体积小、依赖少，PythonAnywhere 免费层轻松容纳。
5. 每个实施阶段都有可运行的测试验证。
6. 附 PythonAnywhere 部署文档（含 Web 标签静态映射配置）。

### 非目标
- 不在云端做真实模型推理。
- 不调用真实和风天气 API。
- 不带数据库、不做用户管理 / 登录鉴权。
- 不改动 `blueberry` master 现有任何功能（pa_demo 是新增独立文件夹）。
- 不负责真正点击部署到 PythonAnywhere（由用户按文档手动完成）；本任务交付到“本地验证通过 + 部署文档”为止。

---

## 3. 已锁定决策

| 决策点 | 选择 |
|---|---|
| 部署形态 | 精简版 Flask（复刻 master UI，桩掉重后端） |
| 登录 | 全开放无登录，无 session、无数据库 |
| UI 来源 | master 当前 `static/` 完整前端 |
| 模型 | 不带 onnx，检测返回预置示例图 + 计数 |
| 天气 | 不调和风 API，返回 canned 天气 / 告警 |
| 抖音视频 | 照搬，前端 iframe 由访客浏览器直连抖音，服务器不参与 |
| 文件夹名 | `pa_demo/` |
| 页面范围 | 公开页 + 单图/批量检测；排除 admin / labelme / big_image（内部工具） |
| 演示提示条 | 加“演示模式：云端不做实时预测”提示 |

---

## 4. 架构

### 4.1 文件夹布局
```
pa_demo/
├── app.py            # 精简 Flask：页面路由 render_template + API 桩
├── static/           # 从 master/static 整份拷贝（约 6.2MB：html + css + js + img）
├── demo_data/        # 预置 JSON + 1 张示例标注结果图
│   ├── detect_single.json
│   ├── batch_detect.json
│   ├── weather.json
│   ├── alerts.json
│   ├── gardens.json
│   └── sample_result.jpg
├── requirements.txt  # 仅 flask（去掉 onnxruntime/opencv/numpy/requests）
├── wsgi.py           # PythonAnywhere WSGI 入口
├── build_demo.py     # 从 master/static 一键重新同步页面资源（防漂移）
├── smoke_test.py     # 冒烟测试：每个路由 200 + 关键内容/JSON 形状
└── README.md         # PythonAnywhere 部署步骤
```

### 4.2 复用 master 的渲染方式
master 用 `Flask(__name__, template_folder='static')`，页面里含 Jinja（`{{ url_for('static', ...) }}`、`{{ username }}`）和指向 Flask 路由的导航（`href="/index"`、`/weather` 等）。pa_demo 的 `app.py` **同样** `template_folder='static'` 并定义对应页面路由，因此：
- Jinja 原样渲染（传 `username='游客', role='guest'`），不用预处理 HTML。
- 导航链接原样可用（pa_demo 定义了这些路由）。
- 不需要把页面预渲染成纯 `.html`、不需要改写链接。

### 4.3 `app.py` 路由清单

**页面路由**（`render_template(page, username='游客', role='guest', active=...)`）：
`/` `/about` `/tech` `/more` `/portal` `/weather` `/weather/alerts` `/garden` `/index` `/single_detect` `/batch_detect`

**API 桩**（返回 `demo_data/` 中 canned 内容）：
- 放行 / 状态类：
  - `/api/check_login` → `{logged_in: true, username: '游客', role: 'guest'}`
  - `/api/current_model` → `{loaded: true, model: 'v11best（演示）'}`
- 检测类：
  - `/api/detect_single`（POST）→ 预置计数 + 结果图引用（`demo_data/detect_single.json`）
  - `/api/batch_detect_multi`（POST）→ `demo_data/batch_detect.json`
  - `/api/result_image/<filename>` → 发送 `demo_data/sample_result.jpg`
- 天气类：
  - `/api/gardens` → `demo_data/gardens.json`
  - `/api/weather/<int:garden_id>` → `demo_data/weather.json`
  - `/api/alerts` → `demo_data/alerts.json`
  - `/api/alerts/stats` → canned 统计
  - `/api/user/info` → `{username: '游客', email: ''}`
- 写操作 / 副作用类（统一返回演示占位，前端弹“演示模式”提示）：
  - `/api/user/email`（POST）、`/api/user/thresholds`（GET/POST）、`/api/weather/<id>/notify`（POST）→ `{ok: true, demo: true, message: '演示模式：该操作在云端不执行'}`

**明确不实现**（前端若调用，由前端的 demo 提示兜底或返回上面的占位）：
`/api/batch_detect` `/api/crop` `/api/crop_tile/<>` `/api/rebuild`（属 big_image，本期排除）；以及 admin 相关 `/api/users` `/api/models*` `/api/records` `/api/stats`。

**绝不引入**：`import detect_engine`、`import database`、`onnxruntime`、`opencv`、`numpy`、`requests`。

### 4.4 演示提示条
在被复用的页面顶部注入一条轻量提示“演示模式：云端不做实时预测，检测与天气为示例数据”。实现方式优先用最小侵入：在 `app.py` 渲染时传入一个 `demo_banner=True` 变量，或在 `build_demo.py` 拷贝后向 `static/_base.html`（公共布局）插入一段固定 banner。具体方式在实施时择一，保持单一来源、可一键关闭。

---

## 5. 去掉 / 桩掉对照

| master | pa_demo |
|---|---|
| onnx 模型（约 115MB）+ `detect_engine` + opencv/numpy | 删，检测返回预置示例图 + 计数 |
| weather → 和风 API（`requests`、`python-dotenv`） | 删，返回 canned 天气 / 告警 |
| SQLite + `database.py` | 删，无数据库 |
| login / session / `login_required` / admin / labelme | 删，全开放无登录 |
| big_image（crop / tile / rebuild） | 本期排除 |

---

## 6. 抖音视频处理

- 视频数据在前端 `static/js/landing.js` 的 `DOUYIN_VIDEOS` 数组（7 条：`vid` / `url` / `cover`），封面图在 `static/img/covers/`（7 张 webp，已确认齐全）。
- 点击播放时前端注入 `<iframe src="https://open.douyin.com/player/video?vid=...">`，由**访客浏览器**直连抖音，服务器不参与，免费层出站白名单不影响。
- 不可内嵌的条目（`noEmbed`）点击直接跳抖音链接，逻辑已在 `landing.js`，pa_demo 继承不改。
- `build_demo.py` 拷 `static/` 时连 `js/landing.js` 与 `img/covers/` 一并带走，视频表现与 master 一致。
- 已知客户端侧前提（非 pa_demo 限制）：能否内嵌取决于抖音播放器策略与访客网络可达性，墙外 / 地域限制时播放失败，与真实站点一致。

---

## 7. 测试策略（强调中间过程）

每阶段结束都要可运行验证：

- **本地起服务**：`python pa_demo/app.py`（指定端口），不与 master 端口冲突。
- **`smoke_test.py`**：
  - 对每个页面路由断言 HTTP 200，且响应含该页关键标记（如标题文案）。
  - 对每个 API 桩断言返回 JSON 且字段形状符合前端预期。
  - 断言 `app.py` 不导入重依赖（源码扫描无 onnxruntime/opencv/numpy/requests/detect_engine/database）。
- **浏览器走查**：首页 → portal → 单图检测点“检测”出示例结果图 → 批量检测出示例 → 天气页出 canned 数据 → landing 视频封面显示、点击尝试内嵌 → 控制台无报错。
- **体积核查**：`du -sh pa_demo` < 10MB；`requirements.txt` 仅 flask（系）。

---

## 8. PythonAnywhere 部署文档（写进 `pa_demo/README.md`）

1. 注册 / 登录 PythonAnywhere 免费账号。
2. Bash console：`git clone` 本仓库或上传 `pa_demo/`。
3. Web 标签 → Add a new web app → Manual configuration → Python 3.x。
4. 配置 virtualenv，`pip install flask`。
5. 编辑 WSGI 配置文件：指向 `pa_demo/app.py`，`from app import app as application`，设置工作目录与 `sys.path`。
6. **Static files 映射**（用户提到的“网页端要定义的那几项”）：URL `/static/` → Directory `/home/<USER>/pa_demo/static/`，让 CSS/JS/图片由平台静态服务，不走 Flask。
7. Reload，访问 `<USER>.pythonanywhere.com`，确认完整 UI + 演示数据。
8. 说明：pa_demo 无任何外部调用，免费层出站代理白名单不影响。

---

## 9. 实施阶段（每阶段 ≤5 文件，测完再进下一步）

- **P1 脚手架**：`pa_demo/build_demo.py`（从 `../static` 拷贝页面与资源）、`requirements.txt`、`app.py`（仅页面路由 + 演示提示条）。
  - 测：本地起服务，所有页面路由 200、导航可点、视频封面显示。
- **P2 接口桩 + 演示数据**：`demo_data/*.json`、`sample_result.jpg`、`app.py` 补全 API 桩。
  - 测：单图/批量检测出示例结果，天气/告警出 canned 数据，控制台无报错。
- **P3 测试与文档**：`smoke_test.py`、`wsgi.py`、`README.md`，体积/依赖核查。
  - 测：冒烟全绿，`du -sh pa_demo` < 10MB，依赖仅 flask。
- **P4 部署（用户手动）**：按 `README.md` 部署到 PythonAnywhere 并回看。

---

## 10. 验收标准

1. `pa_demo/` 本地 `python app.py` 可启动，所有列出的页面路由返回 200。
2. landing 页 7 个抖音视频封面显示，点击按 master 同样逻辑内嵌 / 跳转。
3. 单图检测、批量检测、天气、告警页均显示预置演示数据，无后端报错。
4. `app.py` 不含 onnxruntime/opencv/numpy/requests/detect_engine/database 等重依赖。
5. `smoke_test.py` 全部通过。
6. `du -sh pa_demo` < 10MB。
7. `pa_demo/README.md` 含可照做的 PythonAnywhere 部署步骤（含静态映射）。
8. `blueberry` master 原有功能未被改动。

---

## 11. 待定 / 可后续扩展

- 若需展示 big_image / admin / labelme，再补对应页面与桩（本期排除）。
- 演示提示条的具体注入方式（渲染变量 vs `_base.html` 插入）在实施时择一。
- 后续若想彻底无 Python（纯静态、可上 Netlify/GitHub Pages），可在本方案基础上加一步预渲染导出，非本期范围。
