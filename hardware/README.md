# ⚡ 하드웨어 제어 시스템 (Hardware)

## 📋 개요

하드웨어 제어 시스템은 **ESP32/Arduino**를 사용하여 **NeoPixel LED 매트릭스**를 제어합니다.
물품 위치를 실시간으로 LED로 표시하여 사용자가 쉽게 찾을 수 있도록 돕습니다.

## 🏗️ 하드웨어 구성

```
물품 저장소
┌─────────────────────────────────────┐
│  A1   A2   A3   A4   A5   A6   A7  │
│  B1   B2   B3   B4   B5   B6   B7  │
│  C1   C2   C3   C4   C5   C6   C7  │
│  D1   D2   D3   D4   D5   D6   D7  │
│  E1   E2   E3   E4   E5   E6   E7  │
└─────────────────────────────────────┘
         ↓ LED 매트릭스
┌─────────────────────────────────────┐
│  🔴   🟢   🔵   ⚫   🟡   🟠   🟣  │
│  ⚫   🔴   ⚫   🟢   ⚫   🔵   ⚫  │
│  🟡   ⚫   🟠   ⚫   🟣   ⚫   🔴  │
│  ⚫   🟢   ⚫   🔵   ⚫   🟡   ⚫  │
│  🟠   ⚫   🟣   ⚫   🔴   ⚫   🟢  │
└─────────────────────────────────────┘
         ↓ 제어 시스템
      ┌─────────────┐
      │   ESP32     │
      │   WiFi      │
      │   HTTP API  │
      └─────────────┘
```

## 🔧 지원 플랫폼

### 1. ESP32 (추천)
- **무선 연결**: WiFi를 통한 원격 제어
- **고성능**: 더 많은 LED 제어 가능
- **실시간 통신**: WebSocket 지원

### 2. Arduino UNO
- **유선 연결**: Serial 통신
- **저비용**: 기본적인 LED 제어
- **간단한 구성**: 초보자에게 적합

## 📁 파일 구조

```
hardware/
├── README.md                    # 하드웨어 문서
├── library.properties           # 라이브러리 정보
├── esp32_neopixel_server.ino   # ESP32 메인 코드
└── arduino_uno_neopixel.ino    # Arduino UNO 코드
```

## 🌐 ESP32 구현

### 주요 기능
- **HTTP API 서버**: RESTful API로 LED 제어
- **WiFi 연결**: 무선 네트워크 통신
- **NeoPixel 제어**: WS2812B LED 스트립 제어
- **실시간 응답**: 즉시 LED 상태 변경

### 회로 연결
```
ESP32 Dev Kit    NeoPixel Strip
┌───────────┐    ┌─────────────┐
│   3V3     │────│     VCC     │
│   GND     │────│     GND     │
│   GPIO 2  │────│     DIN     │
└───────────┘    └─────────────┘
```

### 핀 구성
```cpp
// esp32_neopixel_server.ino
#define LED_PIN 2          // NeoPixel 데이터 핀
#define LED_COUNT 49       // 7x7 매트릭스 (49개 LED)
#define BRIGHTNESS 50      // 밝기 (0-255)

// WiFi 설정
const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";
```

### API 엔드포인트
```cpp
// LED 위치 강조 표시
POST /highlight
{
  "positions": [0, 1, 2],
  "color": {"r": 255, "g": 0, "b": 0},
  "duration": 5
}

// 모든 LED 끄기
POST /off

// 시스템 상태 확인
GET /status
```

### 핵심 코드
```cpp
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>

// NeoPixel 설정
Adafruit_NeoPixel pixels(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
WebServer server(80);

void setup() {
  Serial.begin(115200);
  
  // NeoPixel 초기화
  pixels.begin();
  pixels.clear();
  pixels.show();
  
  // WiFi 연결
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("WiFi 연결 중...");
  }
  
  Serial.println("WiFi 연결됨: " + WiFi.localIP().toString());
  
  // API 엔드포인트 설정
  server.on("/highlight", HTTP_POST, handleHighlight);
  server.on("/off", HTTP_POST, handleOff);
  server.on("/status", HTTP_GET, handleStatus);
  
  server.begin();
  Serial.println("HTTP 서버 시작됨");
}

void loop() {
  server.handleClient();
}

// LED 위치 강조 표시
void handleHighlight() {
  if (server.hasArg("plain")) {
    String json = server.arg("plain");
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, json);
    
    JsonArray positions = doc["positions"];
    JsonObject color = doc["color"];
    int duration = doc["duration"] | 5;
    
    // LED 색상 설정
    uint32_t ledColor = pixels.Color(color["r"], color["g"], color["b"]);
    
    // 지정된 위치의 LED 켜기
    for (int pos : positions) {
      if (pos >= 0 && pos < LED_COUNT) {
        pixels.setPixelColor(pos, ledColor);
      }
    }
    
    pixels.show();
    
    // 지정된 시간 후 LED 끄기
    delay(duration * 1000);
    pixels.clear();
    pixels.show();
    
    server.send(200, "application/json", "{\"success\": true}");
  } else {
    server.send(400, "application/json", "{\"error\": \"Invalid request\"}");
  }
}

// 모든 LED 끄기
void handleOff() {
  pixels.clear();
  pixels.show();
  server.send(200, "application/json", "{\"success\": true}");
}

// 시스템 상태 확인
void handleStatus() {
  DynamicJsonDocument doc(512);
  doc["device"] = "ESP32";
  doc["led_count"] = LED_COUNT;
  doc["wifi_connected"] = WiFi.status() == WL_CONNECTED;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["free_heap"] = ESP.getFreeHeap();
  
  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}
```

## 🔌 Arduino UNO 구현

### 주요 기능
- **Serial 통신**: USB를 통한 명령 수신
- **NeoPixel 제어**: 기본적인 LED 제어
- **간단한 프로토콜**: 텍스트 기반 명령

### 회로 연결
```
Arduino UNO      NeoPixel Strip
┌───────────┐    ┌─────────────┐
│   5V      │────│     VCC     │
│   GND     │────│     GND     │
│   Pin 6   │────│     DIN     │
└───────────┘    └─────────────┘
```

### 명령 프로토콜
```
# LED 위치 강조 표시
HIGHLIGHT:0,1,2:255,0,0:5

# 모든 LED 끄기
OFF

# 상태 확인
STATUS
```

### 핵심 코드
```cpp
#include <Adafruit_NeoPixel.h>

#define LED_PIN 6
#define LED_COUNT 49
#define BRIGHTNESS 50

Adafruit_NeoPixel pixels(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(9600);
  pixels.begin();
  pixels.setBrightness(BRIGHTNESS);
  pixels.clear();
  pixels.show();
  
  Serial.println("Arduino NeoPixel 시스템 준비됨");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    handleCommand(command);
  }
}

void handleCommand(String command) {
  if (command.startsWith("HIGHLIGHT:")) {
    handleHighlight(command);
  } else if (command == "OFF") {
    handleOff();
  } else if (command == "STATUS") {
    handleStatus();
  } else {
    Serial.println("ERROR: Unknown command");
  }
}

void handleHighlight(String command) {
  // 명령 파싱: HIGHLIGHT:0,1,2:255,0,0:5
  int firstColon = command.indexOf(':');
  int secondColon = command.indexOf(':', firstColon + 1);
  int thirdColon = command.indexOf(':', secondColon + 1);
  
  String positionsStr = command.substring(firstColon + 1, secondColon);
  String colorStr = command.substring(secondColon + 1, thirdColon);
  String durationStr = command.substring(thirdColon + 1);
  
  // 위치 파싱
  int positions[LED_COUNT];
  int posCount = 0;
  int pos = 0;
  while (pos < positionsStr.length()) {
    int comma = positionsStr.indexOf(',', pos);
    if (comma == -1) comma = positionsStr.length();
    
    positions[posCount++] = positionsStr.substring(pos, comma).toInt();
    pos = comma + 1;
  }
  
  // 색상 파싱
  int colorComma1 = colorStr.indexOf(',');
  int colorComma2 = colorStr.indexOf(',', colorComma1 + 1);
  
  int r = colorStr.substring(0, colorComma1).toInt();
  int g = colorStr.substring(colorComma1 + 1, colorComma2).toInt();
  int b = colorStr.substring(colorComma2 + 1).toInt();
  
  int duration = durationStr.toInt();
  
  // LED 켜기
  uint32_t color = pixels.Color(r, g, b);
  for (int i = 0; i < posCount; i++) {
    if (positions[i] >= 0 && positions[i] < LED_COUNT) {
      pixels.setPixelColor(positions[i], color);
    }
  }
  pixels.show();
  
  Serial.println("OK: LED highlighted");
  
  // 지정된 시간 후 끄기
  delay(duration * 1000);
  pixels.clear();
  pixels.show();
}

void handleOff() {
  pixels.clear();
  pixels.show();
  Serial.println("OK: All LEDs off");
}

void handleStatus() {
  Serial.println("DEVICE: Arduino UNO");
  Serial.println("LED_COUNT: " + String(LED_COUNT));
  Serial.println("STATUS: Ready");
}
```

## 🔧 설치 및 설정

### 1. 라이브러리 설치
```cpp
// Arduino IDE에서 라이브러리 관리자를 통해 설치
- Adafruit NeoPixel
- ArduinoJson (ESP32만)
- WiFi (ESP32만)
```

### 2. 하드웨어 조립
```
1. NeoPixel 스트립을 7x7 매트릭스로 배열
2. ESP32/Arduino와 연결
3. 전원 공급 (5V, 충분한 전류)
4. 케이스 조립 (선택사항)
```

### 3. 펌웨어 업로드
```bash
# Arduino IDE 사용
1. 적절한 보드 선택 (ESP32 Dev Module 또는 Arduino UNO)
2. 포트 선택
3. 코드 업로드
4. 시리얼 모니터로 동작 확인
```

## 🌐 네트워크 설정

### WiFi 설정 (ESP32)
```cpp
// WiFi 자격 증명 설정
const char* ssid = "your_wifi_name";
const char* password = "your_wifi_password";

// 고정 IP 설정 (선택사항)
IPAddress local_IP(192, 168, 1, 100);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

WiFi.config(local_IP, gateway, subnet);
```

### 방화벽 설정
```bash
# 포트 80 허용 (ESP32)
sudo ufw allow 80

# 시리얼 포트 권한 (Arduino)
sudo chmod 666 /dev/ttyUSB0
```

## 📊 LED 매트릭스 매핑

### 그리드 좌표 → LED 인덱스
```cpp
// 7x7 매트릭스 매핑
int gridToIndex(char row, int col) {
  int rowIndex = row - 'A';  // A=0, B=1, C=2, ...
  int colIndex = col - 1;    // 1=0, 2=1, 3=2, ...
  
  // 지그재그 패턴 (NeoPixel 스트립 연결 방식)
  if (rowIndex % 2 == 0) {
    // 짝수 행: 왼쪽에서 오른쪽
    return rowIndex * 7 + colIndex;
  } else {
    // 홀수 행: 오른쪽에서 왼쪽
    return rowIndex * 7 + (6 - colIndex);
  }
}

// 사용 예시
int ledIndex = gridToIndex('A', 1);  // A1 → LED 0
int ledIndex = gridToIndex('B', 1);  // B1 → LED 13
```

### 색상 정의
```cpp
// 미리 정의된 색상
#define COLOR_RED    pixels.Color(255, 0, 0)
#define COLOR_GREEN  pixels.Color(0, 255, 0)
#define COLOR_BLUE   pixels.Color(0, 0, 255)
#define COLOR_YELLOW pixels.Color(255, 255, 0)
#define COLOR_PURPLE pixels.Color(128, 0, 128)
#define COLOR_WHITE  pixels.Color(255, 255, 255)

// 카테고리별 색상
uint32_t getCategoryColor(String category) {
  if (category == "전선_작업") return COLOR_RED;
  if (category == "나사_작업") return COLOR_GREEN;
  if (category == "측정_도구") return COLOR_BLUE;
  if (category == "납땜_도구") return COLOR_YELLOW;
  return COLOR_WHITE;
}
```

## 🔍 디버깅 및 테스트

### 시리얼 모니터 디버깅
```cpp
// 디버그 메시지 출력
Serial.println("LED 인덱스: " + String(ledIndex));
Serial.println("색상: R=" + String(r) + " G=" + String(g) + " B=" + String(b));
Serial.println("지속 시간: " + String(duration) + "초");
```

### LED 테스트 패턴
```cpp
// 무지개 패턴 테스트
void rainbowTest() {
  for (int i = 0; i < LED_COUNT; i++) {
    pixels.setPixelColor(i, pixels.ColorHSV(i * 65536L / LED_COUNT));
  }
  pixels.show();
  delay(2000);
  pixels.clear();
  pixels.show();
}

// 순차 테스트
void sequentialTest() {
  for (int i = 0; i < LED_COUNT; i++) {
    pixels.setPixelColor(i, COLOR_WHITE);
    pixels.show();
    delay(100);
    pixels.setPixelColor(i, 0);
  }
  pixels.show();
}
```

### 네트워크 테스트 (ESP32)
```bash
# HTTP 요청 테스트
curl -X POST http://192.168.1.100/highlight \
  -H "Content-Type: application/json" \
  -d '{"positions":[0,1,2], "color":{"r":255,"g":0,"b":0}, "duration":5}'

# 상태 확인
curl http://192.168.1.100/status
```

## 🔧 문제 해결

### 자주 발생하는 문제

1. **LED가 켜지지 않음**
   - 전원 공급 확인 (5V, 충분한 전류)
   - 데이터 핀 연결 확인
   - NeoPixel 라이브러리 버전 확인

2. **WiFi 연결 실패 (ESP32)**
   - SSID/비밀번호 확인
   - 신호 강도 확인
   - 라우터 재부팅

3. **색상이 이상함**
   - LED 타입 확인 (WS2812B vs WS2811)
   - 색상 순서 확인 (RGB vs GRB)
   - 밝기 설정 확인

4. **성능 문제**
   - LED 개수 줄이기
   - 업데이트 빈도 조절
   - 메모리 사용량 확인

### 유지보수

```cpp
// 메모리 모니터링 (ESP32)
void checkMemory() {
  Serial.println("Free heap: " + String(ESP.getFreeHeap()));
  Serial.println("Min free heap: " + String(ESP.getMinFreeHeap()));
}

// 온도 모니터링 (ESP32)
void checkTemperature() {
  float temp = temperatureRead();
  Serial.println("CPU 온도: " + String(temp) + "°C");
  
  if (temp > 80.0) {
    Serial.println("경고: 온도가 너무 높습니다!");
  }
}
```

## 🚀 고급 기능

### 애니메이션 효과
```cpp
// 깜빡임 효과
void blinkEffect(int position, uint32_t color, int times) {
  for (int i = 0; i < times; i++) {
    pixels.setPixelColor(position, color);
    pixels.show();
    delay(200);
    pixels.setPixelColor(position, 0);
    pixels.show();
    delay(200);
  }
}

// 페이드 효과
void fadeEffect(int position, uint32_t color, int duration) {
  for (int brightness = 0; brightness <= 255; brightness += 5) {
    uint32_t fadedColor = pixels.Color(
      ((color >> 16) & 0xFF) * brightness / 255,
      ((color >> 8) & 0xFF) * brightness / 255,
      (color & 0xFF) * brightness / 255
    );
    pixels.setPixelColor(position, fadedColor);
    pixels.show();
    delay(duration / 100);
  }
}
```

### 패턴 저장
```cpp
// EEPROM에 패턴 저장
#include <EEPROM.h>

void savePattern(int address, uint32_t pattern[], int size) {
  EEPROM.begin(512);
  for (int i = 0; i < size; i++) {
    EEPROM.put(address + i * 4, pattern[i]);
  }
  EEPROM.commit();
}

void loadPattern(int address, uint32_t pattern[], int size) {
  EEPROM.begin(512);
  for (int i = 0; i < size; i++) {
    EEPROM.get(address + i * 4, pattern[i]);
  }
}
```

---

> ⚡ **하드웨어 팁**: 
> - 전원 공급을 충분히 확보하세요 (LED 개수 × 60mA)
> - 긴 연결선 사용 시 신호 감쇠에 주의하세요
> - 정전기 방지 조치를 취하세요
