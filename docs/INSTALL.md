# 설치 가이드 - 스마트 물품 관리 시스템

## 🚀 빠른 시작

### 자동 설치 (권장)

```bash
# 전체 시스템 자동 설치
./scripts/install.sh

# 빠른 설치 (최소한의 확인)
./scripts/quick_install.sh
```

### 수동 설치

#### 1. 사전 요구사항 확인

```bash
# Python 3.8+ 확인
python3 --version

# Node.js 18+ 확인
node --version

# npm 확인
npm --version
```

#### 2. Python 백엔드 설치

```bash
# 가상환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate

# Python 의존성 설치
pip install -r requirements.txt
```

#### 3. Node.js 프론트엔드 설치

```bash
# Next.js 프로젝트로 이동
cd frontend/nextjs-inventory

# 의존성 설치
npm install

# 프로젝트 루트로 돌아가기
cd ../..
```

#### 4. 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp .env.example .env

# Gemini API 키 설정
vi .env  # GOOGLE_API_KEY를 실제 값으로 수정
```

#### 5. 데이터베이스 초기화

```bash
# SQLite 데이터베이스 생성
python3 backend/database/database.py
```

## 📱 Arduino 라이브러리 설치

### ESP32 보드 설치

1. Arduino IDE 열기
2. **파일** > **환경설정**
3. **추가 보드 매니저 URLs**에 추가:
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
4. **도구** > **보드** > **보드 매니저**
5. "ESP32" 검색 후 설치

### 필수 라이브러리 설치

Arduino IDE에서 다음 라이브러리들을 설치하세요:

| 라이브러리 | 작성자 | 설명 |
|------------|--------|------|
| Adafruit NeoPixel | Adafruit | LED 스트립 제어 |
| ArduinoJson | Benoit Blanchon | JSON 데이터 처리 |
| AsyncTCP | dvarrel | 비동기 TCP 통신 |
| ESPAsyncWebServer | lacamera | 비동기 웹 서버 |

### 라이브러리 설치 방법

1. Arduino IDE에서 **스케치** > **라이브러리 포함하기** > **라이브러리 관리**
2. 각 라이브러리 이름으로 검색
3. 올바른 작성자의 라이브러리 선택 후 설치

## 🔧 시스템 시작

```bash
# 전체 시스템 시작
./scripts/start_system.sh

# 또는 개별 서비스 시작
python backend/api/rest_api.py &          # REST API (포트 8001)
python backend/mcp/mcp_server.py &        # MCP 서버 (포트 8000)  
streamlit run frontend/streamlit_client.py &  # AI 챗봇 (포트 8501)
cd frontend/nextjs-inventory && npm run dev   # Next.js (포트 3000)
```

## 🌐 접속 주소

| 서비스 | URL | 설명 |
|--------|-----|------|
| **Next.js 웹앱** | http://localhost:3000 | 메인 관리 인터페이스 |
| **AI 챗봇** | http://localhost:8501 | Streamlit 대화형 인터페이스 |
| **API 문서** | http://localhost:8001/docs | FastAPI Swagger 문서 |
| **Health Check** | http://localhost:8001/health | 시스템 상태 확인 |

## 🔍 설치 확인

### Python 모듈 테스트

```python
# Python에서 실행
import fastapi, streamlit, fastmcp, google.generativeai
print("✅ 모든 Python 모듈이 정상적으로 설치되었습니다!")
```

### Node.js 모듈 테스트

```bash
# Next.js 프로젝트에서 실행
cd frontend/nextjs-inventory
npm run build
```

### 전체 시스템 테스트

```bash
# 모든 서비스 시작 후
curl http://localhost:8001/health     # API 서버 확인
curl http://localhost:3000           # Next.js 확인
```

## 🛠️ 트러블슈팅

### 포트 충돌

```bash
# 사용 중인 포트 확인
lsof -i :3000 -i :8000 -i :8001 -i :8501

# 프로세스 종료
sudo lsof -ti:포트번호 | xargs kill -9
```

### Python 의존성 오류

```bash
# pip 업그레이드
pip install --upgrade pip

# 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

### Node.js 의존성 오류

```bash
# Node.js 캐시 정리
cd frontend/nextjs-inventory
rm -rf node_modules package-lock.json
npm install
```

### 데이터베이스 오류

```bash
# 데이터베이스 재생성
rm items.db
python3 backend/database/database.py
```

### 환경 변수 오류

```bash
# .env 파일 확인
cat .env

# 예시 파일과 비교
diff .env .env.example
```

## 📋 시스템 요구사항

### 소프트웨어

- **Python**: 3.8 이상
- **Node.js**: 18 이상
- **npm**: 최신 버전
- **Arduino IDE**: 1.8.19 이상 (ESP32 사용 시)

### 하드웨어 (선택사항)

- **ESP32 DevKit** 보드
- **NeoPixel LED 스트립** (WS2812B, 5x5 = 25개)
- **적절한 전원 공급** (5V, 2A 이상)
- **점퍼 와이어** 및 **브레드보드**

### 운영체제

- **macOS**: 10.15 이상
- **Linux**: Ubuntu 18.04 이상
- **Windows**: 10 이상 (WSL 권장)

## 🔐 보안 고려사항

1. **API 키 보안**: `.env` 파일을 절대 공개 저장소에 올리지 마세요
2. **방화벽 설정**: 개발 서버는 로컬 네트워크에서만 접근 가능하도록 설정
3. **HTTPS 사용**: 프로덕션 환경에서는 HTTPS 사용 권장
4. **의존성 업데이트**: 정기적으로 보안 업데이트 확인

## 📞 지원

문제가 발생하면:

1. **로그 확인**: 각 서비스의 터미널 출력 확인
2. **문서 참조**: `docs/README.md` 참조
3. **이슈 등록**: GitHub Issues에 상세한 오류 정보와 함께 등록
4. **토론**: GitHub Discussions에서 질문

---

**Happy Coding! 🚀**
