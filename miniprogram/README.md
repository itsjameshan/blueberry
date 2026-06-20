# 蓝莓成熟度识别小程序

## 本地运行

1. 启动 Flask 后端：`python app.py`。
2. 用微信开发者工具打开本目录 `miniprogram/`。
3. 本地开发时关闭微信开发者工具里的合法域名校验。
4. 如后端不是 `http://127.0.0.1:5000`，修改 `utils/config.js` 的 `baseUrl`。

## 真机或上线

小程序正式访问必须使用 HTTPS 后端域名。部署 Flask 后，将 HTTPS 域名配置到微信公众平台的小程序 request、uploadFile、downloadFile 合法域名中，再修改 `utils/config.js`。
