/*
 * Arduino Uno NeoPixel LED 제어 시스템
 * 시리얼 통신을 통해 컴퓨터와 연결되어 5x8 그리드 LED를 제어합니다.
 * 
 * 하드웨어 구성:
 * - Arduino Uno
 * - 디지털 핀 2~6번에 각각 NeoPixel LED 스트립 연결
 * - 각 핀당 24개 LED (8개 위치 × 3개 LED)
 * - 총 120개 LED로 5x8 그리드 구성
 * 
 * 필요한 라이브러리:
 * - Adafruit NeoPixel
 * 
 * 시리얼 통신 프로토콜:
 * - 보드레이트: 115200
 * - 형식: "A1:255,0,0" (위치:R,G,B) 또는 "A1:0,0,0" (끄기)
 * - 복수 명령: "A1:255,0,0|B2:0,255,0|C3:0,0,255"
 */

#include <Adafruit_NeoPixel.h>

// 핀 설정
#define PIN_A 2  // A열 (A1-A8)
#define PIN_B 3  // B열 (B1-B8)
#define PIN_C 4  // C열 (C1-C8)
#define PIN_D 5  // D열 (D1-D8)
#define PIN_E 6  // E열 (E1-E8)

// LED 설정
#define LEDS_PER_POSITION 3  // 각 위치당 LED 개수
#define POSITIONS_PER_ROW 8  // 행당 위치 개수
#define TOTAL_LEDS_PER_STRIP 24  // 스트립당 총 LED 개수 (8 × 3)
#define BRIGHTNESS 100  // 밝기 (0-255)

// NeoPixel 스트립 객체들
Adafruit_NeoPixel stripA(TOTAL_LEDS_PER_STRIP, PIN_A, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel stripB(TOTAL_LEDS_PER_STRIP, PIN_B, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel stripC(TOTAL_LEDS_PER_STRIP, PIN_C, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel stripD(TOTAL_LEDS_PER_STRIP, PIN_D, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel stripE(TOTAL_LEDS_PER_STRIP, PIN_E, NEO_GRB + NEO_KHZ800);

// 스트립 배열 (인덱스 접근용)
Adafruit_NeoPixel* strips[] = {&stripA, &stripB, &stripC, &stripD, &stripE};

// LED 상태 저장 배열 (5행 × 8열)
uint32_t ledStates[5][8] = {0};

// 시리얼 통신 버퍼
String serialBuffer = "";

void setup() {
  Serial.begin(115200);
  
  // 모든 NeoPixel 스트립 초기화
  stripA.begin();
  stripB.begin();
  stripC.begin();
  stripD.begin();
  stripE.begin();
  
  // 밝기 설정
  stripA.setBrightness(BRIGHTNESS);
  stripB.setBrightness(BRIGHTNESS);
  stripC.setBrightness(BRIGHTNESS);
  stripD.setBrightness(BRIGHTNESS);
  stripE.setBrightness(BRIGHTNESS);
  
  // 모든 LED 끄기
  clearAllLEDs();
  
  Serial.println("Arduino Uno NeoPixel Controller Ready");
  Serial.println("Format: A1:255,0,0 or A1:255,0,0|B2:0,255,0");
  Serial.println("Positions: A1-E8 (5x8 grid)");
  
  // 시작 테스트 (무지개 패턴)
  startupTest();
}

void loop() {
  // 시리얼 데이터 읽기
  if (Serial.available()) {
    char c = Serial.read();
    
    if (c == '\n' || c == '\r') {
      // 명령 처리
      if (serialBuffer.length() > 0) {
        processSerialCommand(serialBuffer);
        serialBuffer = "";
      }
    } else {
      serialBuffer += c;
    }
  }
  
  // 주기적으로 LED 상태 업데이트
  updateAllLEDs();
  delay(50);
}

void processSerialCommand(String command) {
  Serial.print("Received: ");
  Serial.println(command);
  
  // 여러 명령 처리 (|로 구분)
  int startPos = 0;
  int pipePos = command.indexOf('|');
  
  while (pipePos != -1) {
    String singleCommand = command.substring(startPos, pipePos);
    processSingleCommand(singleCommand);
    
    startPos = pipePos + 1;
    pipePos = command.indexOf('|', startPos);
  }
  
  // 마지막 명령 처리
  String singleCommand = command.substring(startPos);
  processSingleCommand(singleCommand);
}

void processSingleCommand(String command) {
  // 형식: "A1:255,0,0" 또는 "CLEAR" 또는 "STATUS"
  command.trim();
  
  if (command == "CLEAR") {
    clearAllLEDs();
    Serial.println("All LEDs cleared");
    return;
  }
  
  if (command == "STATUS") {
    printLEDStatus();
    return;
  }
  
  // 위치와 색상 분리
  int colonPos = command.indexOf(':');
  if (colonPos == -1) {
    Serial.println("Error: Invalid format");
    return;
  }
  
  String position = command.substring(0, colonPos);
  String colorStr = command.substring(colonPos + 1);
  
  // 위치 파싱 (A1-E8)
  int row, col;
  if (!parsePosition(position, row, col)) {
    Serial.println("Error: Invalid position");
    return;
  }
  
  // 색상 파싱 (R,G,B)
  int r, g, b;
  if (!parseColor(colorStr, r, g, b)) {
    Serial.println("Error: Invalid color");
    return;
  }
  
  // LED 상태 업데이트
  uint32_t color = strips[0]->Color(r, g, b);
  ledStates[row][col] = color;
  
  Serial.print("Set ");
  Serial.print(position);
  Serial.print(" to RGB(");
  Serial.print(r);
  Serial.print(",");
  Serial.print(g);
  Serial.print(",");
  Serial.print(b);
  Serial.println(")");
}

bool parsePosition(String position, int &row, int &col) {
  if (position.length() != 2) return false;
  
  char rowChar = position.charAt(0);
  char colChar = position.charAt(1);
  
  // 행 파싱 (A-E)
  if (rowChar >= 'A' && rowChar <= 'E') {
    row = rowChar - 'A';
  } else {
    return false;
  }
  
  // 열 파싱 (1-8)
  if (colChar >= '1' && colChar <= '8') {
    col = colChar - '1';
  } else {
    return false;
  }
  
  return true;
}

bool parseColor(String colorStr, int &r, int &g, int &b) {
  // 형식: "255,0,0"
  int firstComma = colorStr.indexOf(',');
  int secondComma = colorStr.indexOf(',', firstComma + 1);
  
  if (firstComma == -1 || secondComma == -1) return false;
  
  r = colorStr.substring(0, firstComma).toInt();
  g = colorStr.substring(firstComma + 1, secondComma).toInt();
  b = colorStr.substring(secondComma + 1).toInt();
  
  // 범위 확인
  if (r < 0 || r > 255 || g < 0 || g > 255 || b < 0 || b > 255) {
    return false;
  }
  
  return true;
}

void updateAllLEDs() {
  // 모든 LED 스트립 업데이트
  for (int row = 0; row < 5; row++) {
    for (int col = 0; col < 8; col++) {
      uint32_t color = ledStates[row][col];
      
      // 해당 위치의 3개 LED 모두 같은 색상으로 설정
      int startIndex = col * LEDS_PER_POSITION;
      for (int i = 0; i < LEDS_PER_POSITION; i++) {
        strips[row]->setPixelColor(startIndex + i, color);
      }
    }
    
    // 스트립 업데이트
    strips[row]->show();
  }
}

void clearAllLEDs() {
  // 모든 LED 상태 초기화
  for (int row = 0; row < 5; row++) {
    for (int col = 0; col < 8; col++) {
      ledStates[row][col] = 0;
    }
  }
  
  // 모든 LED 끄기
  for (int i = 0; i < 5; i++) {
    strips[i]->clear();
    strips[i]->show();
  }
}

void printLEDStatus() {
  Serial.println("=== LED Status ===");
  for (int row = 0; row < 5; row++) {
    char rowChar = 'A' + row;
    for (int col = 0; col < 8; col++) {
      uint32_t color = ledStates[row][col];
      if (color != 0) {
        // 색상 분해
        uint8_t r = (color >> 16) & 0xFF;
        uint8_t g = (color >> 8) & 0xFF;
        uint8_t b = color & 0xFF;
        
        Serial.print(rowChar);
        Serial.print(col + 1);
        Serial.print(": RGB(");
        Serial.print(r);
        Serial.print(",");
        Serial.print(g);
        Serial.print(",");
        Serial.print(b);
        Serial.println(")");
      }
    }
  }
  Serial.println("==================");
}

void startupTest() {
  Serial.println("Running startup test...");
  
  // 무지개 색상 배열
  uint32_t rainbowColors[] = {
    stripA.Color(255, 0, 0),    // 빨강
    stripA.Color(255, 127, 0),  // 주황
    stripA.Color(255, 255, 0),  // 노랑
    stripA.Color(0, 255, 0),    // 초록
    stripA.Color(0, 0, 255),    // 파랑
    stripA.Color(75, 0, 130),   // 남색
    stripA.Color(148, 0, 211)   // 보라
  };
  
  // 각 행을 순차적으로 켜기
  for (int row = 0; row < 5; row++) {
    for (int col = 0; col < 8; col++) {
      ledStates[row][col] = rainbowColors[col % 7];
    }
    updateAllLEDs();
    delay(200);
  }
  
  delay(1000);
  
  // 모든 LED 끄기
  clearAllLEDs();
  
  Serial.println("Startup test completed");
}

// 디버깅용 함수
void debugPrintGrid() {
  Serial.println("=== LED Grid Debug ===");
  for (int row = 0; row < 5; row++) {
    char rowChar = 'A' + row;
    Serial.print(rowChar);
    Serial.print(": ");
    
    for (int col = 0; col < 8; col++) {
      if (ledStates[row][col] != 0) {
        Serial.print("●");
      } else {
        Serial.print("○");
      }
      Serial.print(" ");
    }
    Serial.println();
  }
  Serial.println("====================");
}
