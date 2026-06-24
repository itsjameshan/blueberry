# 蓝莓检测系统 微信小程序内网自测 skill\.md

## 项目基础信息

- 后端：Flask \+ MySQL，启动文件：`app.py`，运行端口：5000

- 前端：Flask原生Jinja网页，不重构代码，小程序采用web\-view嵌套访问

- 使用范围：仅本人手机内部测试，不上架、不提交微信审核、不公网发布

- 默认账号：**admin / admin123**

- 运行前提：电脑、手机连接**同一WiFi**

---

## 一、Python环境依赖安装


新增跨域依赖，解决小程序web\-view登录session丢失、跨域拦截问题

```bash
pip install flask flask-cors
```

---

## 
二、app\.py 固定修改（必改，仅两处改动）


### 
2\.1 文件头部新增跨域\+会话配置


直接复制替换头部代码，无需改动原有业务接口

```python
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, Response
from werkzeug.security import check_password_hash
from functools import wraps
import os
import json
import webbrowser
import threading
# 新增跨域模块
from flask_cors import CORS

app = Flask(__name__, template_folder='static')
app.secret_key = 'blueberry_detection_secret_key_2026'
# 全局跨域配置：允许小程序携带Cookie，保留登录态
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
# Session适配小程序，登录7天有效，不丢失登录
app.config['PERMANENT_SESSION_LIFETIME'] = 3600*24*7
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
```

### 
2\.2 尾部启动代码【无需修改】


原有代码已适配局域网访问，直接保留即可，监听全网网卡，手机可访问

```python
if __name__ == '__main__':
    init_db()
    model = get_active_model()
    if model:
        load_model(model['model_path'])
    print("蓝莓检测系统启动中...")
    print("本地地址: http://127.0.0.1:5000")
    print("局域网地址: http://【本机WLANIPv4】:5000")
    print("默认管理员账号: admin / admin123")
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:5000/login')).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## 
三、电脑前置配置


### 
3\.1 获取局域网IP地址


cmd命令行输入：`ipconfig`，复制【无线局域网WLAN】IPv4，例：`192.168.2.106`

### 
3\.2 Windows放行5000端口


1. 控制面板 → Windows防火墙 → 高级设置

2. 入站规则 → 新建规则 → 端口 → TCP端口5000

3. 允许连接，全网络勾选，规则命名：蓝莓检测5000端口

### 
3\.3 预验证


手机浏览器打开：`http://局域网IP:5000`，可正常登录、上传图片即为配置成功

---

## 
四、微信小程序账号注册（免费极简版）

1. 官网地址：[https://mp\.weixin\.qq\.com/](https://mp.weixin.qq.com/) → 立即注册 → 小程序

2. 邮箱注册，绑定个人微信，主体选择：**个人**

3. 开发管理 → 开发设置，复制小程序AppID备用

✅ 自测豁免：无需企业认证、无需类目审核、无需付费、不用提交版本发布

---

## 
五、微信开发者工具配置

### 
5\.1 新建项目


1. 打开微信开发者工具，新建项目

2. 填入项目名、空文件夹、小程序AppID

3. 模板选择：**不使用模板（空白项目）**

### 
5\.2 核心关闭校验（必勾）


右上角详情 → 本地设置 → 勾选：**不校验合法域名、web\-view、TLS、HTTPS证书**

### 
5\.3 小程序极简代码（全覆盖网页）


仅修改首页3个文件，其余代码不动，替换IP为自己电脑局域网IP

**pages/index/index\.wxml**

```xml
<!-- 修改为自己电脑WLAN IPv4地址 -->
<web-view src="http://192.168.2.106:5000"></web-view>
```

**pages/index/index\.json**

```json
{
  "navigationBarTitleText": "蓝莓检测系统",
  "navigationBarHidden": true
}
```

**pages/index/index\.js**

```javascript
Page({})
```

---

## 
六、完整自测流程


1. 终端启动后端：`python app.py`

2. 开发者工具点击【真机调试】，手机微信扫码

3. 小程序内登录admin账号，全功能自测：图片检测、模型管理、数据导出、用户管理

💡 预览模式：点击【预览】扫码，纯体验使用，无调试日志

---

## 
七、外网脱离WiFi测试（可选）

使用cpolar内网穿透，任意网络可用

```bash
cpolar http 5000
```

复制生成公网地址，替换web\-view内src地址即可

---

## 
八、高频问题排查


- 手机打不开页面：未同WiFi、防火墙未放行5000、IP填写错误、app\.py未启动

- 登录后401无权限：未安装flask\-cors、未复制全套跨域配置

- 图片/模型上传失败：单文件≤50MB，项目内uploads/onnx\_data文件夹权限正常

- 页面空白：未关闭开发者工具域名校验、使用了127\.0\.0\.1地址

---

## 
九、硬性安全注意事项


1. 全程禁止：点击【上传代码】【提交审核】，仅本地扫码自测，不会上线外网

2. 仅管理员微信可扫码访问，内网地址外网无法访问，无数据泄露风险

3. 关闭python程序后，小程序直接无法访问，可控性高

4. 所有修改仅适配本地自测，不改动原有蓝莓检测业务逻辑

> （注：部分内容可能由 AI 生成）
