# 蓝莓成熟度检测网页系统

## 功能概述

基于 Flask 框架搭建的蓝莓成熟度检测网页端应用，支持单图检测、批量检测、大图裁剪重建等多种检测模式，采用蓝紫色系浅色设计风格。

## 技术栈

- **框架**: Flask 2.0+
- **数据库**: SQLite
- **模型推理**: ONNX Runtime
- **前端**: HTML5 + CSS3 + JavaScript (ES6+)
- **图标**: Font Awesome
- **样式**: 蓝紫色系浅色主题

## 页面结构

| 页面 | 文件路径 | 功能描述 |
|------|----------|----------|
| 登录页 | `static/login.html` | 用户登录、权限验证 |
| 首页 | `static/index.html` | 功能入口、导航展示 |
| 单图检测页 | `static/single_detect.html` | 单张图片上传检测 |
| 批量检测页 | `static/batch_detect.html` | 多张图片批量检测 |
| 大图检测页 | `static/large_detect.html` | 大图裁剪重建工作流 |
| 检测结果页 | `static/result.html` | 检测结果展示 |
| 管理后台 | `static/admin.html` | 用户管理、数据统计 |

## 核心功能

### 1. 用户认证模块
- 用户名密码登录
- 角色权限管理（普通用户/管理员）
- Session 会话管理

### 2. 检测模块
- 单图上传检测
- 多图批量上传检测
- 大图裁剪检测工作流
- 置信度阈值调节

### 3. 检测标签
- `RipeBlueBerry`: 成熟蓝莓
- `SemiRipeBlueBerry`: 半成熟蓝莓  
- `UnripeBlueBerry`: 未成熟蓝莓

### 4. 结果展示
- 检测结果可视化
- 统计数据汇总
- 检测历史记录

## 文件结构

```
bule/
├── app.py                    # Flask 应用入口
├── models/
│   └── onnx_model.py         # ONNX 模型推理封装
├── routes/
│   ├── auth.py               # 认证路由
│   ├── detect.py             # 检测路由
│   └── admin.py              # 管理后台路由
├── static/
│   ├── css/
│   │   ├── login.css         # 登录页样式
│   │   ├── index.css         # 首页样式
│   │   ├── single_detect.css # 单图检测样式
│   │   ├── batch_detect.css  # 批量检测样式
│   │   └── admin.css         # 管理后台样式
│   ├── js/
│   │   ├── login.js          # 登录页脚本
│   │   ├── single_detect.js  # 单图检测脚本
│   │   └── batch_detect.js   # 批量检测脚本
│   ├── login.html            # 登录页
│   ├── index.html            # 首页
│   ├── single_detect.html    # 单图检测页
│   ├── batch_detect.html     # 批量检测页
│   ├── large_detect.html     # 大图检测页
│   ├── result.html           # 结果页
│   ├── admin.html            # 管理后台
│   └── login.jpg             # 登录页背景图
├── templates/
│   └── base.html             # 模板基类
├── uploads/                  # 上传文件存储
├── results/                  # 检测结果存储
└── database.db               # SQLite 数据库
```

## API 接口

### 认证接口

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/login` | POST | 用户登录 |
| `/api/logout` | GET | 用户登出 |
| `/api/check_login` | GET | 登录状态检查 |

### 检测接口

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/detect` | POST | 单图检测 |
| `/api/batch_detect` | POST | 批量检测（单请求） |
| `/api/batch_detect_multi` | POST | 批量检测（多文件） |
| `/api/crop_detect` | POST | 裁剪检测 |
| `/api/reconstruct` | POST | 结果重建 |

### 管理接口

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/admin/users` | GET | 获取用户列表 |
| `/api/admin/user/<id>` | GET/POST/DELETE | 用户管理 |
| `/api/admin/records` | GET | 获取检测记录 |
| `/api/admin/stats` | GET | 统计数据 |

## 数据库设计

### users 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名 |
| password | VARCHAR(255) | 密码哈希 |
| role | VARCHAR(20) | 角色（user/admin） |
| create_time | DATETIME | 创建时间 |

### records 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| filename | VARCHAR(255) | 文件名 |
| result | TEXT | 检测结果JSON |
| ripe_count | INTEGER | 成熟数量 |
| semi_count | INTEGER | 半成熟数量 |
| unripe_count | INTEGER | 未成熟数量 |
| create_time | DATETIME | 检测时间 |

## 模型推理

```python
# 模型加载
import onnxruntime as ort
session = ort.InferenceSession('models/blueberry_model.onnx')

# 推理流程
def detect(image_path, conf_threshold=0.5):
    # 1. 图像预处理
    # 2. 模型推理
    # 3. 结果后处理
    # 4. 返回检测结果
    pass
```

## 样式规范

### 颜色主题

| 颜色 | 用途 |
|------|------|
| #6C5CE7 | 主色调、按钮高亮 |
| #A29BFE | 次要元素、边框 |
| #F4F2FF | 背景色 |
| #FFFFFF | 卡片背景 |
| #636E72 | 文字颜色 |

### 按钮样式

- 默认状态：白色底 + 蓝紫色文字
- 悬浮状态：紫色高亮
- 圆角：12px
- 阴影：轻微投影

## 部署说明

### 环境要求

- Python 3.8+
- Flask 2.0+
- ONNX Runtime 1.10+
- Pillow 8.0+

### 安装步骤

```bash
# 安装依赖
pip install flask onnxruntime pillow

# 运行应用
python app.py
```

### 配置项

```python
# app.py
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULT_FOLDER'] = 'results/'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['SECRET_KEY'] = 'your-secret-key'
```

## 安全考虑

1. 文件上传校验（类型、大小、重命名）
2. SQL 注入防护（使用 ORM）
3. XSS 防护（HTML 转义）
4. 密码加密存储（bcrypt）
5. 权限控制装饰器
6. Session 安全配置
