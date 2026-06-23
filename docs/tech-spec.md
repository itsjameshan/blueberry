# 技术规格文档

> 版本：v1.0 | 创建日期：2026-06-23

---

## 一、现有系统技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.8+ | 主开发语言 |
| Flask | 3.1.1 | Web 框架 |
| Flask-CORS | 5.0.1 | 跨域支持 |
| Werkzeug | 3.1.4 | 密码哈希 |
| SQLite | Python 内置 | 数据库 |
| ONNX Runtime | 1.21.2 | 模型推理 |
| OpenCV | 4.11.0.86 | 图像处理 |
| Pillow | 11.2.1 | 图像处理 |
| NumPy | 2.2.6 | 数值计算 |

## 二、新增技术组件

| 组件 | 版本 | 用途 |
|------|------|------|
| requests | 2.31+ | HTTP 客户端，调用和风天气 API |
| APScheduler | 3.10+ | 定时任务，定期拉取天气数据 |
| python-dotenv | 1.0+ | 环境变量管理（API Key、邮件配置） |
| smtplib | Python 内置 | 邮件推送 |

## 三、和风天气 API 规格

### 3.1 基础信息

- 文档地址：https://dev.qweather.com/docs/api/
- 请求方式：GET
- 响应格式：JSON
- 认证方式：Query 参数 `key=YOUR_KEY`

### 3.2 使用的 API 接口

| 接口 | 路径 | 用途 |
|------|------|------|
| GeoAPI | `/geo/v2/city/lookup` | 城市查询，获取 location_id |
| 实时天气 | `/v7/weather/now` | 当前天气 |
| 天气预报 | `/v7/weather/3d` | 3天预报 |
| 天气预警 | `/v7/warning/now` | 当前预警 |
| 分钟降水 | `/v7/minutely/5m` | 2小时逐5分钟降水 |
| 天气指数 | `/v7/indices/1d` | 生活/农业指数 |
| 空气质量 | `/v7/air/now` | 实时空气质量 |
| 天文 | `/v7/astronomy/sun` | 日出日落 |
| 历史天气 | `/v7/historical/weather` | 历史天气查询 |

### 3.3 调用限制

- 免费版：8个API，每分钟调用限制需遵守
- 策略：数据缓存到数据库，减少重复调用

## 四、数据库变更

### 4.1 新增表

**gardens 表**
```sql
CREATE TABLE gardens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    location_id VARCHAR(50),
    plant_date DATE,
    growth_stage VARCHAR(20) DEFAULT 'dormant',
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**weather_data 表**
```sql
CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    garden_id INTEGER NOT NULL,
    weather_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    FOREIGN KEY (garden_id) REFERENCES gardens(id)
);
```

**weather_alerts 表**
```sql
CREATE TABLE weather_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    garden_id INTEGER NOT NULL,
    alert_title TEXT NOT NULL,
    alert_level VARCHAR(20),
    alert_content TEXT,
    start_time TEXT,
    end_time TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (garden_id) REFERENCES gardens(id)
);
```

### 4.2 现有表无需修改

## 五、新增文件结构

```
blueberry/
├── weather/                    # 气象模块（新增目录）
│   ├── __init__.py
│   ├── api_client.py           # 和风天气 API 封装
│   ├── advice_engine.py        # 农业建议规则引擎
│   ├── email_sender.py         # 邮件推送
│   ── scheduler.py            # 定时任务
├── static/
│   ├── portal.html             # 门户首页
│   ├── weather.html            # 气象中心首页
│   ├── garden.html             # 果园管理
│   ├── forecast.html           # 天气预报详情
│   ├── advice.html             # 农业建议
│   ├── css/
│   │   ├── portal.css
│   │   ├── weather.css
│   │   ├── garden.css
│   │   ├── forecast.css
│   │   └── advice.css
│   └── js/
│       ├── portal.js
│       ├── weather.js
│       ├── garden.js
│       ├── forecast.js
│       └── advice.js
├── .env                        # 环境变量（API Key、邮件配置）
└── .env.example                # 环境变量模板
```

## 六、环境变量配置

```env
# 和风天气
QWEATHER_API_KEY=5b4b4b0ff8af44a58c20a54dd47c79a1

# 邮件推送（按需配置）
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASS=your_app_password
SMTP_FROM=your_email@qq.com
```
