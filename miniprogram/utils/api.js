const config = require("./config");

function parseUploadResponse(data) {
  if (typeof data === "string") {
    return JSON.parse(data);
  }
  return data;
}

function detectBlueberries(filePath, conf) {
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${config.baseUrl}/api/mini/detect`,
      filePath,
      name: "image",
      formData: {
        conf: String(conf || 0.5)
      },
      success(response) {
        let payload;
        try {
          payload = parseUploadResponse(response.data);
        } catch (error) {
          reject(new Error("服务器返回格式错误"));
          return;
        }

        if (response.statusCode >= 200 && response.statusCode < 300 && payload.success) {
          resolve(payload);
          return;
        }

        reject(new Error(payload.message || "检测失败"));
      },
      fail() {
        reject(new Error("无法连接检测服务"));
      }
    });
  });
}

module.exports = {
  detectBlueberries
};
