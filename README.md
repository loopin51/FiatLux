# 🤖 스마트 물품 관리 시스템 (2025 유연화 프로젝트)

## 📋 프로젝트 개요

스마트 물품 관리 시스템은 **AI 기반 챗봇**과 **웹 인터페이스**를 통해 물품을 효율적으로 관리하는 통합 시스템입니다. 
초보자도 쉽게 도구를 찾고 사용할 수 있도록 교육적 안내와 실시간 LED 위치 표시 기능을 제공합니다.

## 🏗️ 시스템 아키텍처

### 전체 시스템 구성
```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 인터페이스                           │
├─────────────────────┬───────────────────────────────────────┤
│   Next.js 웹 앱     │      Streamlit AI 챗봇               │
│   (재고 관리)       │      (대화형 검색)                    │
│   Port: 3000       │      Port: 8501/8502                 │
└─────────────────────┴───────────────────────────────────────┘
                              │
                    ┌─────────────────┐
                    │   백엔드 API    │
                    │   (Python)      │
                    └─────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
    ┌───────────────┐  ┌─────────────┐  ┌─────────────┐
    │   데이터베이스   │  │    AI 엔진   │  │  하드웨어    │
    │   (SQLite)     │  │   (Gemini)   │  │  (ESP32)     │
    └───────────────┘  └─────────────┘  └─────────────┘
```

## 🚀 빠른 시작 가이드

### 1. 시스템 초기 설정
```bash
# 저장소 클론
git clone <repository-url>
cd 2025유연화

# 시스템 설정 (최초 1회)
./scripts/setup_system.sh
```시스템

AI 기반 물품 검색 및 관리, 실시간 LED 위치 표시, 웹 기반 인터페이스를 제공하는 통합 시스템입니다.

## � 빠른 시작

### 1. 시스템 초기 설정
```bash
# 저장소 클론
git clone <repository-url>
cd 2025유연화

# 시스템 설정 (최초 1회)
./scripts/setup_system.sh
```

### 2. 전체 시스템 시작
```bash
# 모든 서비스 시작
./scripts/start_all.sh
```

### 3. 웹 인터페이스 접속
- **메인 애플리케이션**: http://localhost:3000
- **AI 챗봇**: http://localhost:8501
- **API 문서**: http://localhost:8001/docs

## � 사용 가능한 스크립트

### 🔧 시스템 관리
- `./scripts/setup_system.sh` - 시스템 초기 설정
- `./scripts/start_all.sh` - 전체 시스템 시작
- `./scripts/stop_all.sh` - 전체 시스템 종료
- `./scripts/health_check.sh` - 시스템 상태 확인

### 🎯 개별 서비스 관리
- `./scripts/start_backend.sh` - 백엔드 서비스만 시작
- `./scripts/start_frontend.sh` - 프론트엔드 서비스만 시작
- `./scripts/start_dev.sh` - 개발 모드로 시작

### 🔍 디버깅 및 모니터링
- `./scripts/health_check.sh` - 전체 시스템 건강도 확인
- `tail -f logs/*.log` - 실시간 로그 확인
- `ps aux | grep -E "node|python|uvicorn|streamlit"` - 프로세스 상태 확인

## 🎯 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js Web   │    │  Streamlit AI   │    │   ESP32 LED     │
│   Frontend      │    │   Chatbot       │    │   Controller    │
│  localhost:3000 │    │  localhost:8501 │    │   (Hardware)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          │ HTTP REST              │ MCP stdio             │ HTTP
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   MCP Server    │    │   SQLite DB     │
│   REST Server   │◄──►│   FastMCP       │◄──►│   Database      │
│ backend/api/    │    │ backend/mcp/    │    │   items.db      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 시스템 시작 가이드

### 📋 시작 순서

1. **백엔드 서버들 시작**

   ```bash
   cd smart-inventory-system
   
   # 1. REST API 서버 (포트 8001)
   python backend/api/rest_api.py &
   
   # 2. MCP 서버 (포트 8000)
   python backend/mcp/mcp_server.py &
   
   # 3. Streamlit 챗봇 (포트 8501)
   streamlit run frontend/streamlit_client.py &
   ```

2. **Next.js 프론트엔드 시작**

   ```bash
   cd frontend/nextjs-inventory
   npm run dev
   ```

3. **전체 시스템 자동 시작**

   ```bash
   ./scripts/start_system.sh
   ```

### 🌐 접속 URL

| 서비스 | URL | 설명 |
|--------|-----|------|
| 🌐 Next.js 웹앱 | <http://localhost:3000> | 메인 시각적 관리 인터페이스 |
| 🤖 AI 챗봇 | <http://localhost:8501> | Streamlit 자연어 대화 인터페이스 |
| 📚 API 문서 | <http://localhost:8001/docs> | FastAPI Swagger 문서 |
| 🔍 Health Check | <http://localhost:8001/health> | 시스템 상태 확인 |

## 📋 주요 컴포넌트 역할

### 🖥️ 백엔드 서비스 (`backend/`)

| 디렉토리 | 파일 | 역할 | 포트 |
|----------|------|------|------|
| `api/` | `rest_api.py` | FastAPI REST 서버 | 8001 |
| `mcp/` | `mcp_server.py` | FastMCP 프로토콜 서버 | 8000 |
| `database/` | `database.py` | SQLite 데이터베이스 관리 | - |
| `models/` | `models.py` | Pydantic 데이터 모델 | - |
| `controllers/` | `gemini_agent.py` | Gemini LLM AI 에이전트 | - |
| `controllers/` | `esp32_controller.py` | ESP32 LED 제어 | - |
| `tests/` | `test_*.py` | 단위 및 통합 테스트 | - |

### 🌐 프론트엔드 (`frontend/`)

| 디렉토리 | 파일/폴더 | 역할 | 포트 |
|----------|-----------|------|------|
| `nextjs-inventory/` | Next.js 프로젝트 | 시각적 웹 관리 인터페이스 | 3000 |
| `.` | `streamlit_client.py` | AI 챗봇 인터페이스 | 8501 |

## 🔧 하드웨어 연결 (`hardware/`)

| 디렉토리 | 파일 | 역할 |
|----------|------|------|
| `hardware/` | `arduino_uno_neopixel.ino` | Arduino Uno 펌웨어 |
| `hardware/` | `esp32_neopixel_server.ino` | ESP32 펌웨어 (백업용) |
| `hardware/` | `library.properties` | Arduino 라이브러리 종속성 |

### 📟 Arduino Uno 하드웨어 설정

- **Arduino Uno** 보드
- **NeoPixel LED 스트립** (WS2812B)
- **5개 디지털 핀** (2~6번)에 각각 24개 LED 연결
- **5x8 그리드 구성** (총 120개 LED)
- **USB 시리얼 통신** (115200 baud)

### 🔌 연결 방법

```
Arduino Uno
├── 디지털 핀 2 → A행 LED (A1-A8, 24개)
├── 디지털 핀 3 → B행 LED (B1-B8, 24개)  
├── 디지털 핀 4 → C행 LED (C1-C8, 24개)
├── 디지털 핀 5 → D행 LED (D1-D8, 24개)
└── 디지털 핀 6 → E행 LED (E1-E8, 24개)
```

각 위치당 3개 LED가 묶여서 동시에 켜집니다.

## 🔧 개발 환경 설정

### Python 환경

```bash
# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt
```

### Node.js 환경

```bash
# Next.js 프로젝트로 이동
cd frontend/nextjs-inventory

# 의존성 설치
npm install
```

### 환경 변수 설정

```bash
# .env 파일 생성 (루트 디렉토리에)
cp .env.example .env

# Gemini API 키 설정
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 🔍 시스템 상태 확인

### 실행 중인 서비스 확인

```bash
# 포트 사용 확인
lsof -i :3000  # Next.js
lsof -i :8000  # MCP 서버  
lsof -i :8001  # REST API
lsof -i :8501  # Streamlit

# 프로세스 확인
ps aux | grep python
ps aux | grep node
```

### 접속 테스트

- ✅ Next.js: 브라우저에서 그리드 화면 확인
- ✅ REST API: FastAPI 문서 페이지 접속
- ✅ Streamlit: AI 챗봇 인터페이스 확인
- ✅ Health: `{"status": "healthy"}` 응답 확인

## 🛠️ 트러블슈팅

### 포트 충돌 해결

```bash
# 사용 중인 프로세스 종료
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:8001 | xargs kill -9
sudo lsof -ti:8501 | xargs kill -9
```

### 데이터베이스 초기화

```bash
# SQLite 데이터베이스 재생성
rm items.db
python backend/database/database.py
```

### 의존성 재설치

```bash
# Python 의존성
pip install -r requirements.txt --force-reinstall

# Node.js 의존성  
cd frontend/nextjs-inventory
rm -rf node_modules package-lock.json
npm install
```

## 📈 향후 개선사항

- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인 구축
- [ ] 로깅 시스템 개선
- [ ] 모니터링 대시보드 추가
- [ ] 데이터베이스 마이그레이션 스크립트
- [ ] 단위 테스트 커버리지 확대

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

**개발팀**: 2025년 유연화 프로젝트팀  
**라이센스**: MIT License
