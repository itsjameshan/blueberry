# CLAUDE.md — 项目指引

> 本文档为 AI 编程助手提供项目上下文和工作指引

---

## 项目概述

**蓝莓成熟度检测系统** — 基于 Flask + YOLO11 + ONNX Runtime 的蓝莓成熟度检测 Web 应用，正在扩展气象预警与农业建议模块。

---

## 文档索引

| 文档 | 路径 | 用途 |
|------|------|------|
| 需求文档 | `docs/requirements.md` | 功能需求、页面结构、权限设计 |
| 技术规格 | `docs/tech-spec.md` | 技术栈、API 规格、数据库设计、文件结构 |
| 设计规范 | `docs/design-spec.md` | UI 颜色、组件、布局、响应式规范 |
| 开发步骤 | `docs/dev-steps.md` | 分步开发计划、验收标准 |
| 开发日志 | `devlog/changelog.md` | 完成事项和待办事项记录 |

**每次开发前请先阅读 `docs/dev-steps.md` 确认当前步骤。**

---

## 工作规则

### 开发流程

1. 查看 `devlog/changelog.md` 确认当前待办事项
2. 阅读 `docs/dev-steps.md` 中对应步骤的详细说明
3. 按步骤开发，完成后更新 `devlog/changelog.md`
4. 每个 Step 完成后验证功能正常再进入下一步

### 代码规范

- 遵循 `docs/design-spec.md` 中的 UI 设计规范
- 遵循 `docs/tech-spec.md` 中的技术规格
- 不破坏现有检测系统的任何功能
- 新增代码与现有代码风格保持一致

### 文件组织

```
blueberry/
── docs/              # 项目文档（需求、技术、设计、步骤）
├── devlog/            # 开发日志
├── CLAUDE.md          # 本文件（项目指引）
├── app.py             # Flask 应用入口
├── database.py        # 数据库操作
├── detect_engine.py   # 检测引擎
├── weather/           # 气象模块（新增）
├── static/            # 前端页面、样式、脚本
├── uploads/           # 上传文件
├── results/           # 检测结果
├── onnx_data/         # ONNX 模型文件
└── blueberry1.v4i.yolov11/  # YOLO 训练数据
```

### 关键配置

- 和风天气 API Key：从 `.env` 文件读取（`QWEATHER_API_KEY`）
- 数据库：SQLite（`blueberry.db`）
- 默认管理员：`admin` / `admin123`

---

## 当前开发状态

**阶段**：基础设施搭建  
**当前步骤**：Step 1 — 门户首页  
**下一步**：完成门户首页后进入 Step 2（环境变量配置）
