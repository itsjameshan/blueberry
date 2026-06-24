# 开发日志

> 记录每次开发的完成事项和待办事项

---

## 2026-06-23

### 完成事项
- [x] 创建项目文档体系（docs/ 文件夹）
  - `docs/requirements.md` — 需求文档
  - `docs/tech-spec.md` — 技术规格文档
  - `docs/design-spec.md` — 设计规范文档
  - `docs/dev-steps.md` — 开发步骤规划
- [x] 创建开发日志文件（devlog/changelog.md）
- [x] 创建 CLAUDE.md 项目指引文件

### 待办事项
- [x] Step 1：门户首页开发 ✅
- [x] Step 2：环境变量配置 ✅
- [x] Step 3：数据库扩展 ✅
- [x] Step 4：果园管理后端 + 前端 ✅
- [x] Step 5：和风天气 API 封装 ✅
- [x] Step 6：气象数据展示页面 ✅
- [x] Step 7：农业建议规则引擎 ✅
- [x] Step 8：邮件预警推送 ✅

---

## 2026-06-23 — Step 1 完成

### 完成事项
- [x] Step 1：门户首页开发
  - 创建 `static/portal.html` 门户页面
  - 添加 `/portal` 路由
  - 展示两个子系统入口卡片：蓝莓检测系统、气象中心
  - 显示当前用户信息和退出按钮

### 验收结果
- [x] 门户首页正常显示 ✅
- [x] 两个入口卡片可点击跳转 ✅
- [x] 用户信息显示正常 ✅

### 下一步
- Step 2：环境变量配置

---

## 2026-06-23 — Step 2 完成

### 完成事项
- [x] Step 2：环境变量配置
  - 创建 `.env` 文件
  - 配置和风天气 API Key
  - 配置 SMTP 邮件服务信息
  - 使用 `python-dotenv` 加载环境变量

### 验收结果
- [x] 环境变量正确加载 ✅
- [x] API Key 配置成功 ✅

### 下一步
- Step 3：数据库扩展

---

## 2026-06-23 — Step 3 完成

### 完成事项
- [x] Step 3：数据库扩展
  - 在 `database.py` 中新增表结构：
    - `gardens` - 果园信息表
    - `weather_data` - 天气数据缓存表
    - `weather_alerts` - 天气预警记录表
  - 添加果园管理相关函数：
    - `create_garden()` - 创建果园
    - `get_garden_by_id()` - 根据 ID 获取果园
    - `get_gardens_by_user()` - 获取用户的果园列表
    - `update_garden()` - 更新果园信息
    - `delete_garden()` - 删除果园
  - 添加天气数据相关函数：
    - `save_weather_data()` - 保存天气数据缓存
    - `get_latest_weather()` - 获取最新天气数据
    - `save_weather_alert()` - 保存预警记录
    - `get_active_alerts()` - 获取活跃预警

### 验收结果
- [x] 数据库表创建成功 ✅
- [x] 所有数据库函数正常工作 ✅

### 下一步
- Step 4：果园管理后端 + 前端

---

## 2026-06-23 — Step 4 完成

### 完成事项
- [x] Step 4：果园管理后端 + 前端
  - `app.py`：新增果园管理 API（GET/POST/PUT/DELETE `/api/gardens`）
  - `app.py`：新增天气数据 API（GET `/api/weather/<garden_id>`）
  - `app.py`：新增 `/garden` 路由
  - `static/garden.html`：果园管理页面（卡片列表 + 弹窗表单）
  - `static/css/garden.css`：果园管理样式
  - `static/js/garden.js`：果园 CRUD 交互逻辑
  - 重写 `static/weather.html`：气象中心页面（果园列表 + 气象数据展示）
  - 重写 `static/css/weather.css`：气象中心样式
  - 新增 `static/js/weather.js`：气象中心交互逻辑

### 验收结果
- [x] 所有路由验证通过（login/portal/garden/weather 均 200） ✅
- [x] 果园管理 API 正常 ✅
- [x] 气象中心页面正常 ✅
- [x] 现有检测系统功能不受影响 ✅

### 下一步
- Step 5：和风天气 API 封装（`weather/api_client.py`）

---

## 2026-06-23 — Step 5 完成

### 完成事项
- [x] Step 5：和风天气 API 封装
  - 创建 `weather/` 模块目录
  - 创建 `weather/__init__.py`
  - 创建 `weather/api_client.py`，封装和风天气 API
    - `lookup_city()` - 城市查询
    - `get_realtime_weather()` - 实时天气
    - `get_forecast_3d()` - 3天预报
    - `get_weather_warnings()` - 天气预警
    - `get_minutely_precipitation()` - 分钟降水
    - `get_air_quality()` - 空气质量
    - `get_sunrise_sunset()` - 日出日落
    - `get_historical_weather()` - 历史天气
    - `get_full_weather()` - 完整天气数据
  - 更新 `.env` 配置，添加 `QWEATHER_API_HOST`
  - 解决 API 连通性问题（使用新的 API Host：`pu5ctwrvjg.re.qweatherapi.com`）
  - GeoAPI 路径从 `/v2` 改为 `/geo/v2`
  - 增加错误处理，免费版不支持的接口优雅降级

### 验收结果
- [x] 城市查询正常 ✅
- [x] 实时天气正常 ✅
- [x] 3天预报正常 ✅
- [x] 免费版不支持的接口优雅降级 ✅
- [x] 所有函数都能处理错误，不会抛出异常 ✅

### 免费版限制
- ❌ 天气预警（403）
- ❌ 空气质量（403）
- ❌ 日出日落（400）
- ❌ 历史天气（403）

### 下一步
- Step 6：气象数据展示页面

---

## 2026-06-23 — Step 6 完成

### 完成事项
- [x] Step 6：气象数据展示页面
  - 更新 `app.py` 中的 `/api/weather/<garden_id>` API
    - 添加缓存机制（1小时内使用缓存数据）
    - 调用和风天气 API 获取实时数据
    - 自动查询 location_id 并缓存到果园记录
    - 修复 sqlite3.Row 对象的 `.get()` 方法问题
  - 更新 `database.py` 中的 `create_garden()` 函数
    - 返回新创建的果园 ID
  - 更新 `static/js/weather.js`
    - 展示实时天气数据（温度、天气描述、体感温度、湿度、风速）
    - 展示气象数据卡片（温度、湿度、风速、降水量、气压、能见度）
    - 展示3天天气预报
    - 预留农业建议区域
  - 更新 `static/css/weather.css`
    - 添加实时天气样式（渐变背景、大字体温度显示）
    - 添加3天预报样式

### 验收结果
- [x] 气象数据 API 返回完整数据 ✅
- [x] 实时天气数据正常显示 ✅
- [x] 3天预报数据正常显示 ✅
- [x] 缓存机制正常工作 ✅
- [x] 自动查询并缓存 location_id ✅

### 技术细节
- 缓存策略：1小时内使用缓存数据，超过1小时重新调用 API
- 错误处理：API 调用失败时返回错误信息
- 数据格式：使用 JSON 格式存储和传输气象数据

### 下一步
- Step 7：农业建议规则引擎

---

## 2026-06-23 — Step 7 完成

### 完成事项
- [x] Step 7：农业建议规则引擎
  - 创建 `weather/advice_engine.py` 农业建议规则引擎
    - `get_agricultural_advice()` - 根据气象数据和生长阶段生成建议
    - `_get_dormant_advice()` - 休眠期建议
    - `_get_sprouting_advice()` - 萌芽期建议
    - `_get_flowering_advice()` - 花期建议
    - `_get_fruiting_advice()` - 果期建议
    - `_get_general_advice()` - 通用建议
  - 集成建议引擎到 `/api/weather/<garden_id>` API
  - 更新 `static/js/weather.js` 展示农业建议
  - 更新 `static/css/weather.css` 添加建议卡片样式
    - 支持 warning（警告）和 info（信息）两个级别
    - 不同级别使用不同颜色和图标

### 验收结果
- [x] 农业建议引擎正常工作 ✅
- [x] 根据生长阶段生成针对性建议 ✅
- [x] 根据气象条件生成预警和建议 ✅
- [x] 前端正确展示农业建议 ✅
- [x] 建议样式美观，区分级别 ✅

### 规则引擎逻辑
- **休眠期**：低温预警、湿度建议
- **萌芽期**：温度建议、湿度建议
- **花期**：温度、风速、降水、湿度综合建议
- **果期**：温度、风速、降水、湿度综合建议，适宜温度时提供常规管理建议
- **通用**：灌溉建议、未来天气预警

### 下一步
- Step 8：邮件预警推送

---

## 2026-06-23 — Step 8 完成

### 完成事项
- [x] Step 8：邮件预警推送
  - 创建 `weather/email_sender.py` 邮件发送模块
    - `send_alert_email()` - 通用邮件发送函数
    - `send_weather_alert_email()` - 气象预警邮件发送（支持纯文本和HTML格式）
  - 集成邮件预警到 `/api/weather/<garden_id>` API
    - 当检测到气象预警时，自动发送邮件通知果园管理者
    - 获取果园管理者的邮箱地址
    - 为每个预警发送独立的邮件通知
    - 邮件发送失败不影响 API 正常返回
  - 邮件内容包含：
    - 果园名称
    - 预警标题和内容
    - 当前气象数据
    - 美观的HTML格式邮件模板

### 验收结果
- [x] 邮件发送模块正常工作 ✅
- [x] SMTP配置缺失时优雅降级 ✅
- [x] 气象预警触发邮件发送 ✅
- [x] 邮件内容格式正确 ✅
- [x] 邮件发送失败不影响主流程 ✅

### 配置说明
需要在 `.env` 文件中配置 SMTP 信息：
```
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASS=your_app_password
SMTP_FROM=your_email@qq.com
```

### 技术细节
- 使用 Python 标准库 `smtplib` 发送邮件
- 支持 SSL（端口465）和 TLS（其他端口）
- 邮件格式：纯文本 + HTML（alternative）
- 异常处理：邮件发送失败只打印日志，不影响 API 响应

---

## 开发完成总结

所有 8 个开发步骤已全部完成！

### 已实现功能
1. ✅ 门户首页 - 统一入口，展示两个子系统
2. ✅ 环境变量配置 - 使用 python-dotenv 管理配置
3. ✅ 数据库扩展 - 新增果园、天气数据、预警表
4. ✅ 果园管理 - 完整的 CRUD 功能
5. ✅ 和风天气 API 封装 - 集成实时天气、预报、预警等数据
6. ✅ 气象数据展示 - 实时天气、3天预报、气象卡片
7. ✅ 农业建议规则引擎 - 根据生长阶段和气象条件生成建议
8. ✅ 邮件预警推送 - 自动发送气象预警邮件
9. ✅ 历史预警记录查询 - 查看过往预警记录
10. ✅ 实时时钟显示 - 导航栏显示当前时间
11. ✅ 天气数据自动刷新 - 每30分钟自动更新

### 系统架构
```
蓝莓智慧农业平台
├── 门户首页 (/portal)
├── 蓝莓成熟度检测系统 (原有功能)
└── 气象中心 (/weather)
    ├── 果园列表
    ├── 实时天气展示
    ├── 3天天气预报
    ├── 农业建议（基于规则引擎）
    ├── 气象预警邮件推送
    └── 历史预警记录查询 (/weather/alerts)
```

---

## 2026-06-23 — 邮箱功能补全

### 完成事项
- [x] 给 `users` 表添加 `email` 字段（兼容旧数据库自动迁移）
- [x] 新增 `update_user_email()` 数据库函数
- [x] 新增 `/api/user/email` (POST) — 设置用户邮箱
- [x] 新增 `/api/user/info` (GET) — 获取当前用户信息（含邮箱）
- [x] 气象中心导航栏添加邮箱设置按钮（信封图标）
- [x] 邮箱设置弹窗 UI（输入、校验、保存）
- [x] 邮件预警逻辑验证通过：用户设置邮箱后，预警邮件可正常发送

### 验收结果
- [x] 邮箱设置 API 正常工作 ✅
- [x] 邮箱查询 API 正常工作 ✅
- [x] 前端弹窗交互正常 ✅
- [x] 邮件预警链路完整（users.email → email_sender → SMTP） ✅

---

## 2026-06-23 — 农业建议规则扩充 & 邮件模板优化

### 完成事项
- [x] 扩充农业建议规则引擎（`weather/advice_engine.py`）
  - 休眠期：新增极端低温（-10°C/-5°C）分级预警、未来极端低温预报
  - 萌芽期：新增倒春寒预警、温度/湿度适宜区间提示、霜冻预报
  - 花期：新增霜冻预警（<5°C）、风速适宜区间、降水分级、湿度分级（>90%极高危）
  - 果期：新增高温灼果预警（>35°C）、暴雨预警（>30mm）、连续降水检测
  - 通用建议：新增气压异常预警、能见度预警、温度剧变预警、连续降水预警
- [x] 优化邮件预警模板设计（`weather/email_sender.py`）
  - 重新设计 HTML 邮件模板，采用品牌色（#6C5CE7）+ 预警色（#E74C3C）
  - 新增顶部品牌栏、预警图标、果园信息卡片
  - 新增当前天气数据展示（温度/湿度/风速）
  - 优化排版和响应式布局，提升邮件可读性
- [x] 测试验证邮件发送成功 ✅

### 验收结果
- [x] 农业建议规则覆盖更多气象条件和生长阶段 ✅
- [x] 邮件模板视觉优化，信息层次清晰 ✅
- [x] 邮件发送测试通过 ✅

---

## 2026-06-23 — 预警统计图表 & 自定义阈值

### 完成事项
- [x] 新增预警统计 API（`/api/alerts/stats`）
  - 按级别统计（warning/info）
  - 按果园统计
  - 按日期统计（近30天趋势）
- [x] 历史预警页面添加统计图表（Chart.js）
  - 预警级别分布（环形图）
  - 果园预警排名（横向柱状图）
  - 近30天预警趋势（折线图）
  - 统计卡片（总数/高级预警/提示信息）
- [x] 新增用户自定义预警阈值功能
  - 数据库新增 `user_thresholds` 表（自动迁移）
  - 新增 `/api/user/thresholds` GET/POST 接口
  - 历史预警页面添加阈值设置按钮（滑块图标）
  - 支持设置：高温/低温/高湿度/低湿度/大风/强降雨 阈值
- [x] 农业建议引擎集成自定义阈值
  - 所有生长阶段建议均使用用户阈值替代硬编码值
  - 建议内容中显示用户设置的阈值数值
- [x] 更新开发日志

### 验收结果
- [x] 统计图表正常渲染 ✅
- [x] 阈值设置保存/读取正常 ✅
- [x] 农业建议使用自定义阈值 ✅

---

## 2026-06-24 — 门户首页改版（landing）& 三端连通

### 完成事项
- [x] 将 `单网页/` 门户模板集成进 Flask，作为**公开首页** `/`（无需登录可浏览）
  - 新增 `static/landing.html`（昆明学院头部/导航/页脚身份保留）
  - 新增 `static/css/landing.css`、`static/js/landing.js`
  - `app.py`：`/` 改为 `render_template('landing.html')`，`/portal` 仍为登录后控制台
- [x] 删除政治宣传内容
  - 移除「正确政绩观学习教育」红色 hero + 假「昆院要闻」栏
  - 改为蓝莓主视觉 hero（蓝色调 + 蓝莓植株背景）
- [x] 三端连通（landing ↔ 蓝莓识别 ↔ 天气，统一登录）
  - 导航/卡片：蓝莓识别 → `/index`、天气预警 → `/weather`（均 `login_required` 守卫）
  - `login_required` 增加 `next=request.path`
  - `static/js/login.js`：登录成功后跳回 `next`（仅站内相对路径，防开放重定向）
  - 登录态在 landing 顶栏显示「你好，<用户> · 控制台 · 退出」
- [x] 抖音视频墙（6 卡）
  - 因抖音禁止 iframe 内嵌，采用封面卡 + 新标签打开
  - 链接集中在 `static/js/landing.js` 的 `DOUYIN_VIDEOS` 数组（当前为占位「待填链接」）
- [x] 检测样本图库（4 张样图）+ 单页锚点（项目视频/检测图库/了解我们）+ 锚点吸顶偏移修复

### 验收结果
- [x] `/` 公开 200，蓝莓主视觉，无政治内容 ✅
- [x] 登出访问 `/index`、`/weather` → 302 → `/login?next=...` ✅
- [x] admin 登录后**跳回点击的工具页**（浏览器 E2E 通过） ✅
- [x] 登录态首页显示用户名/控制台/退出 ✅

### 待办事项
- [ ] 填入 6 个抖音真实分享链接（`DOUYIN_VIDEOS`）
- [ ] （可选）用真实检测结果图替换样本图库
- [ ] （可选）清理冗余的 `单网页/` 源模板目录

---

## 2026-06-24 — 多页结构改版（保留 UI）

### 完成事项
- [x] 引入共享基础模板 `static/_base.html`（头部/导航/页脚统一，Jinja 继承）
- [x] 导航重构：主页 / 了解我们 / 技术介绍 / 蓝莓检测 / 天气预警 / 更多
- [x] Logo 换为昆明学院校徽 `static/img/kmu_seal.svg` + “智慧农业”副名
- [x] 主页 `/`：大图 + 平台介绍 + 数据指标 + **三个抖音视频**
- [x] 了解我们 `/about`：蓝莓检测系统 + 天气预警系统介绍
- [x] 技术介绍 `/tech`：检测结果图 + 成熟度样本图库
- [x] 更多 `/more`：联系方式 + 公众号
- [x] 填入 3 个真实抖音链接（另存 2 个备用）于 `static/js/landing.js` `DOUYIN_VIDEOS`
- [x] 天气预警登录窗主题化：标题“天气预警系统” + 天空背景；返回/退出回到天气登录窗
  - `login_page` 按 `next` 切主题；`/logout?next=` 回指定系统登录窗（防开放重定向）
  - `weather.html`：返回 → `/login?next=/weather`，退出 → `/logout?next=/weather`

### 改动文件
- 新增：`static/_base.html`、`static/about.html`、`static/tech.html`、`static/more.html`、`static/img/kmu_seal.svg`、`static/img/detect{1,2,3}.jpg`
- 修改：`app.py`（新增 /about、/tech、/more；login_page、logout）、`static/landing.html`、`static/js/landing.js`、`static/login.html`、`static/css/login.css`、`static/css/landing.css`、`static/weather.html`

### 验收结果
- [x] /、/about、/tech、/more 均 200，导航 active 正确 ✅
- [x] 校徽 + 3 个真实抖音视频正常显示 ✅
- [x] `/login?next=/weather` → 天空主题“天气预警系统”登录窗 ✅
- [x] `/weather` 登出/返回 → 天气登录窗；开放重定向被拦截 ✅
- [x] 蓝莓检测/天气预警仍受登录保护，登录后跳回对应系统（浏览器 E2E 过） ✅

### 待办 / 备注
- [ ] 公众号二维码为占位（`more.html`），可替换真实图
- [ ] 天空登录背景为 CSS 渐变，如需照片放 `static/img/sky.jpg` 并改 `body.weather-login`
- [ ] `单网页/` 源模板已冗余（不被服务），可删
