#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "DHT.h"
#include <WiFi.h>
#include <WiFiServer.h>

// ===================== 引脚定义 =====================
// OLED屏幕引脚 (Arduino UNO R4 WiFi I2C)
#define OLED_SDA   A4
#define OLED_SCL   A5
// DHT11温湿度传感器
#define DHT_PIN    2
#define DHT_TYPE   DHT11
// 风扇继电器控制引脚
#define FAN_RELAY  3

// 风扇自动启停温度阈值
const float TEMP_ON  = 28.0;   // 温度高于28℃开风扇
const float TEMP_OFF = 26.0;   // 温度低于26℃关风扇

// ===================== WiFi配置 =====================
const char* ssid = "bei";
const char* password = "88888888";
WiFiServer server(80);
WiFiClient client;

// 创建硬件对象
DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_SSD1306 display(128, 64, &Wire, -1);
bool fanState = false;
bool oledInitOk = false;  // OLED初始化状态标志
bool manualMode = false;  // 手动控制模式标志

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // 等待串口连接
  }
  Serial.println("系统启动中...");

  // 初始化风扇继电器引脚
  pinMode(FAN_RELAY, OUTPUT);
  digitalWrite(FAN_RELAY, LOW);
  fanState = false;

  // 启动DHT温湿度传感器
  dht.begin();
  Serial.println("DHT传感器初始化完成");

  // 扫描I2C总线上的设备
  Serial.println("扫描I2C设备...");
  byte error, address;
  int nDevices = 0;
  
  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    
    if (error == 0) {
      Serial.print("发现I2C设备，地址: 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
      nDevices++;
    }
  }
  
  if (nDevices == 0) {
    Serial.println("未发现任何I2C设备！请检查接线。");
  } else {
    Serial.print("总共发现 ");
    Serial.print(nDevices);
    Serial.println(" 个I2C设备");
  }
  
  // 初始化I2C总线 (Arduino UNO R4 WiFi)
  Wire.begin();
  Serial.println("I2C总线初始化完成");
  
  // OLED初始化，尝试常见地址
  const uint8_t oledAddresses[] = {0x3C, 0x3D};
  
  for (int i = 0; i < 2; i++) {
    Serial.print("尝试初始化OLED，地址: 0x");
    Serial.println(oledAddresses[i], HEX);
    
    oledInitOk = display.begin(SSD1306_SWITCHCAPVCC, oledAddresses[i]);
    if (oledInitOk) {
      Serial.print("OLED初始化成功，地址: 0x");
      Serial.println(oledAddresses[i], HEX);
      break;
    } else {
      Serial.println("OLED初始化失败");
    }
    delay(100);
  }
  
  if (!oledInitOk) {
    Serial.println("【警告】OLED初始化失败！请检查SDA/SCL接线或I2C地址");
    Serial.println("可能的问题：");
    Serial.println("1. SDA/SCL接线错误");
    Serial.println("2. OLED屏幕损坏");
    Serial.println("3. 电源不足");
    Serial.println("4. I2C地址不正确");
  }

  // 开机欢迎画面
  if (oledInitOk) {
    Serial.println("显示开机画面...");
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(0, 0);
    display.println("System Ready");
    display.display();
    Serial.println("开机画面显示完成");
    delay(1000);
  }

  // ===================== WiFi连接 =====================
  Serial.println();
  Serial.print("正在连接WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int wifiAttempts = 0;
  while (WiFi.status() != WL_CONNECTED && wifiAttempts < 20) {
    delay(500);
    Serial.print(".");
    wifiAttempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("WiFi连接成功！");
    Serial.print("IP地址: ");
    Serial.println(WiFi.localIP());
    Serial.print("网关: ");
    Serial.println(WiFi.gatewayIP());
    Serial.print("子网掩码: ");
    Serial.println(WiFi.subnetMask());
    
    // 启动Web服务器
    server.begin();
    Serial.println("Web服务器已启动");
    
    // OLED显示IP地址
    if (oledInitOk) {
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("WiFi Connected");
      display.setCursor(0, 16);
      display.print("IP: ");
      display.println(WiFi.localIP());
      display.display();
      delay(2000);
    }
  } else {
    Serial.println();
    Serial.println("WiFi连接失败！请检查SSID和密码");
    if (oledInitOk) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("WiFi Failed!");
      display.display();
    }
  }
}

// ===================== Web服务器处理函数 =====================

void handleClientRequest(WiFiClient &client) {
  if (!client.connected()) return;
  
  String request = client.readStringUntil('\r');
  
  if (request.startsWith("GET / ")) {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    
    String html = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n";
    html += "<!DOCTYPE HTML><html><head>";
    html += "<meta charset='utf-8'>";
    html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
    html += "<title>温湿度监控</title>";
    html += "<style>";
    html += "body { font-family: Arial, sans-serif; max-width: 400px; margin: 0 auto; padding: 20px; background: #f0f2f5; }";
    html += ".container { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }";
    html += "h1 { text-align: center; color: #333; margin-top: 0; }";
    html += ".sensor-box { background: #e8f5e9; border-radius: 12px; padding: 16px; margin: 12px 0; text-align: center; }";
    html += ".temp { font-size: 48px; font-weight: bold; color: #e53935; }";
    html += ".hum { font-size: 48px; font-weight: bold; color: #1e88e5; }";
    html += ".label { font-size: 14px; color: #666; margin-top: 4px; }";
    html += ".fan-status { text-align: center; padding: 12px; margin: 12px 0; border-radius: 8px; }";
    html += ".fan-on { background: #ffcdd2; color: #c62828; font-weight: bold; }";
    html += ".fan-off { background: #e0e0e0; color: #616161; font-weight: bold; }";
    html += ".mode-status { text-align: center; padding: 8px; margin-bottom: 16px; font-size: 14px; color: #757575; }";
    html += ".btn-group { display: flex; gap: 10px; justify-content: center; }";
    html += ".btn { flex: 1; padding: 12px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: all 0.2s; }";
    html += ".btn-on { background: #4caf50; color: white; }";
    html += ".btn-on:hover { background: #43a047; }";
    html += ".btn-off { background: #f44336; color: white; }";
    html += ".btn-off:hover { background: #d32f2f; }";
    html += ".btn-auto { background: #2196f3; color: white; }";
    html += ".btn-auto:hover { background: #1976d2; }";
    html += "</style></head><body>";
    html += "<div class='container'>";
    html += "<h1>🌡️ 温湿度监控</h1>";
    
    html += "<div class='sensor-box'>";
    html += "<div class='temp'>" + String(temp, 1) + "°C</div>";
    html += "<div class='label'>温度</div>";
    html += "</div>";
    
    html += "<div class='sensor-box'>";
    html += "<div class='hum'>" + String(hum, 1) + "%</div>";
    html += "<div class='label'>湿度</div>";
    html += "</div>";
    
    html += "<div class='fan-status " + String(fanState ? "fan-on" : "fan-off") + "'>";
    html += "风扇状态: " + String(fanState ? "🟢 运行中" : "🔴 已停止");
    html += "</div>";
    
    html += "<div class='mode-status'>";
    html += "当前模式: " + String(manualMode ? "🔧 手动控制" : "🤖 自动控制");
    html += "</div>";
    
    html += "<div class='btn-group'>";
    html += "<button class='btn btn-on' onclick='controlFan(\"on\")'>开启风扇</button>";
    html += "<button class='btn btn-off' onclick='controlFan(\"off\")'>关闭风扇</button>";
    html += "</div>";
    
    html += "<div class='btn-group' style='margin-top: 10px;'>";
    html += "<button class='btn btn-auto' onclick='controlFan(\"auto\")'>自动模式</button>";
    html += "</div>";
    
    html += "</div>";
    
    html += "<script>";
    html += "function controlFan(action) {";
    html += "  fetch('/control?action=' + action);";
    html += "  setTimeout(() => { location.reload(); }, 500);";
    html += "}";
    html += "setInterval(() => { location.reload(); }, 5000);";
    html += "</script>";
    html += "</body></html>";
    
    client.print(html);
  }
  else if (request.startsWith("GET /control?action=on")) {
    digitalWrite(FAN_RELAY, HIGH);
    fanState = true;
    manualMode = true;
    client.print("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n风扇已开启");
    Serial.println("风扇已手动开启（网页控制）");
  }
  else if (request.startsWith("GET /control?action=off")) {
    digitalWrite(FAN_RELAY, LOW);
    fanState = false;
    manualMode = true;
    client.print("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n风扇已关闭");
    Serial.println("风扇已手动关闭（网页控制）");
  }
  else if (request.startsWith("GET /control?action=auto")) {
    manualMode = false;
    client.print("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n已切换到自动模式");
    Serial.println("已切换到自动模式（网页控制）");
  }
  else if (request.startsWith("GET /status")) {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    
    String json = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n";
    json += "{";
    json += "\"temperature\": " + String(temp, 1) + ",";
    json += "\"humidity\": " + String(hum, 1) + ",";
    json += "\"fanState\": " + String(fanState ? "true" : "false") + ",";
    json += "\"manualMode\": " + String(manualMode ? "true" : "false");
    json += "}";
    
    client.print(json);
  }
  else {
    client.print("HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nNot Found");
  }
  
  client.stop();
}

void loop() {
  client = server.available();
  if (client) {
    handleClientRequest(client);
  }
  
  // 读取串口命令（立即响应）
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd == "fan on" || cmd == "FAN ON" || cmd == "1") {
      digitalWrite(FAN_RELAY, HIGH);
      fanState = true;
      manualMode = true;
      Serial.println("风扇已手动开启");
    }
    else if (cmd == "fan off" || cmd == "FAN OFF" || cmd == "0") {
      digitalWrite(FAN_RELAY, LOW);
      fanState = false;
      manualMode = true;
      Serial.println("风扇已手动关闭");
    }
    else if (cmd == "auto" || cmd == "AUTO") {
      manualMode = false;
      Serial.println("已切换到自动模式");
    }
    else if (cmd == "status" || cmd == "STATUS") {
      Serial.print("当前模式: ");
      Serial.println(manualMode ? "手动模式" : "自动模式");
      Serial.print("风扇状态: ");
      Serial.println(fanState ? "开启" : "关闭");
    }
    else if (cmd == "help" || cmd == "HELP") {
      Serial.println("可用命令:");
      Serial.println("  fan on / 1     - 开启风扇（手动模式）");
      Serial.println("  fan off / 0    - 关闭风扇（手动模式）");
      Serial.println("  auto           - 切换到自动模式");
      Serial.println("  status         - 查看当前状态");
      Serial.println("  help           - 显示帮助信息");
    }
    else {
      Serial.println("未知命令，请输入 help 查看可用命令");
    }
  }
  
  // 定时读取传感器和更新显示（每5秒）
  static unsigned long lastTime = 0;
  unsigned long currentTime = millis();
  
  if (currentTime - lastTime >= 5000) {
    lastTime = currentTime;
    
    float temp = dht.readTemperature();
    float hum  = dht.readHumidity();

    if (isnan(temp) || isnan(hum)) {
      if (oledInitOk) {
        display.clearDisplay();
        display.setCursor(0, 0);
        display.println("DHT Sensor Error!");
        display.display();
      }
      Serial.println("DHT读取失败，请检查传感器接线");
      return;
    }

    if (!manualMode) {
      if (temp >= TEMP_ON && fanState == false) {
        digitalWrite(FAN_RELAY, HIGH);
        fanState = true;
        Serial.println("风扇自动开启（温度高于28℃）");
      }
      if (temp <= TEMP_OFF && fanState == true) {
        digitalWrite(FAN_RELAY, LOW);
        fanState = false;
        Serial.println("风扇自动关闭（温度低于26℃）");
      }
    }

    if (oledInitOk) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.print("Temp: ");
      display.print(temp, 1);
      display.println(" C");

      display.setCursor(0, 16);
      display.print("Humi: ");
      display.print(hum, 1);
      display.println(" %");

      display.setCursor(0, 32);
      display.print("Fan: ");
      display.println(fanState ? "ON" : "OFF");
      display.display();
    }

    Serial.print("温度：");
    Serial.print(temp);
    Serial.print("℃ | 湿度：");
    Serial.print(hum);
    Serial.print("% | 风扇：");
    Serial.println(fanState ? "开启" : "关闭");
  }
}