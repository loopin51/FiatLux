# 📁 최종 프로젝트 구조 - 신입 개발자 가이드

## 🎯 정리 완료된 디렉토리 구조

```
2025유연화/
├── 📄 프로젝트 문서
│   ├── README.md                    # 프로젝트 메인 문서
│   ├── PROJECT_OVERVIEW.md          # 신입 개발자 가이드 (이 문서)
│   ├── .env.example                 # 환경 변수 예시
│   └── requirements.txt             # Python 의존성
│
├── 🔧 백엔드 서비스
│   └── backend/
│       ├── README.md                # 백엔드 상세 문서
│       ├── api/                     # REST API 엔드포인트
│       ├── controllers/             # 비즈니스 로직 (ESP32, Gemini 등)
│       ├── database/                # 데이터베이스 관리
│       ├── mcp/                     # MCP 서버 구현
│       ├── models/                  # 데이터 모델
│       └── tests/                   # 테스트 코드
│
├── 🎨 프론트엔드 서비스
│   └── frontend/
│       ├── README.md                # 프론트엔드 상세 문서
│       ├── nextjs-inventory/        # Next.js 웹 애플리케이션
│       │   ├── src/                 # React 소스 코드
│       │   ├── public/              # 정적 파일
│       │   └── package.json         # Node.js 의존성
│       ├── intelligent_chatbot_client.py    # 🤖 메인 AI 챗봇
│       └── intelligent_chatbot_simple.py   # 📝 간단 버전 챗봇
│
├── ⚡ 하드웨어 제어
│   └── hardware/
│       ├── README.md                # 하드웨어 상세 문서
│       ├── esp32_neopixel_server.ino # ESP32 펌웨어
│       ├── arduino_uno_neopixel.ino  # Arduino 펌웨어
│       └── library.properties       # 라이브러리 정보
│
├── 🚀 실행 스크립트
│   └── scripts/
│       ├── README.md                # 스크립트 상세 문서
│       ├── setup_system.sh          # 시스템 초기 설정
│       ├── start_all.sh             # 전체 시스템 시작
│       ├── start_backend.sh         # 백엔드만 시작
│       ├── start_frontend.sh        # Next.js 앱 시작
│       ├── start_dev.sh             # Streamlit 챗봇 시작
│       ├── stop_all.sh              # 모든 서비스 중지
│       ├── health_check.sh          # 시스템 상태 확인
│       ├── add_sample_tools.py      # 샘플 데이터 추가
│       └── pids/                    # 프로세스 ID 저장
│
├── 📚 문서 저장소
│   └── docs/
│       ├── README.md                # 문서 가이드
│       ├── INSTALL.md               # 설치 가이드
│       └── (기타 문서들)
│
├── 🗄️ 데이터 및 로그
│   ├── items.db                     # SQLite 데이터베이스
│   ├── logs/                        # 시스템 로그
│   ├── archive/                     # 아카이브 파일
│   └── venv/                        # Python 가상환경
│
└── 📋 시스템 파일
    ├── .env                         # 환경 변수 (보안 정보)
    ├── .gitignore                   # Git 무시 파일
    └── start_system.sh              # 시스템 시작 스크립트
```

## 🔄 서비스 실행 플로우

### 1. 개발 환경 시작
```bash
# 1단계: 환경 설정 (최초 1회)
./scripts/setup_system.sh

# 2단계: 전체 시스템 시작
./scripts/start_all.sh

# 또는 개별 서비스 시작
./scripts/start_backend.sh    # 백엔드 API 서버
./scripts/start_frontend.sh   # Next.js 웹 앱
./scripts/start_dev.sh        # Streamlit AI 챗봇
```

### 2. 사용자 접속 정보
```
🌐 Next.js 웹 앱 (관리자):     http://localhost:3000
🤖 Streamlit 챗봇 (사용자):    http://localhost:8501
📡 백엔드 API (개발자):        http://localhost:8000
📊 API 문서 (개발자):          http://localhost:8000/docs
```

## 🎯 각 컴포넌트 역할

### 📱 사용자 인터페이스
- **Next.js 웹 앱**: 관리자용 물품 관리 시스템
  - 물품 CRUD 작업
  - 검색 및 필터링
  - 그리드 시각화
  - 대시보드 및 통계

- **Streamlit AI 챗봇**: 사용자용 대화형 검색
  - 자연어 질문 처리
  - 교육적 응답 제공
  - 음성 인식 지원
  - 실시간 LED 제어

### 🔧 백엔드 서비스
- **FastAPI 서버**: 핵심 비즈니스 로직
  - RESTful API 제공
  - 데이터베이스 관리
  - AI 엔진 통합
  - 하드웨어 제어

- **SQLite 데이터베이스**: 물품 정보 저장
  - 물품 정보 (이름, 설명, 위치, 카테고리)
  - 사용자 설정
  - 시스템 로그

### 🤖 AI 엔진
- **Gemini API**: 고급 자연어 처리
  - 의도 분석
  - 답변 생성
  - 컨텍스트 이해

- **도구 지식 베이스**: 교육적 정보
  - 도구 분류 및 설명
  - 사용법 안내
  - 관련 도구 추천

### ⚡ 하드웨어 제어
- **ESP32/Arduino**: LED 매트릭스 제어
  - WiFi 통신
  - NeoPixel LED 제어
  - 실시간 위치 표시

## 🛠️ 개발 워크플로우

### 신입 개발자 학습 순서
1. **1주차**: 전체 시스템 실행 및 체험
2. **2주차**: 각 컴포넌트 구조 이해
3. **3주차**: 코드 분석 및 간단한 수정
4. **4주차**: 새로운 기능 추가

### 개발 환경 설정
```bash
# Python 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# Node.js 패키지 설치
cd frontend/nextjs-inventory
npm install

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정하여 API 키 등 설정
```

## 🔍 주요 파일 설명

### 🤖 AI 챗봇 (`frontend/intelligent_chatbot_client.py`)
- **역할**: 사용자와 대화하며 물품 검색 및 안내
- **주요 기능**:
  - 자연어 질문 이해
  - 교육적 답변 생성
  - 음성 인식 처리
  - LED 위치 표시

### 🌐 웹 애플리케이션 (`frontend/nextjs-inventory/`)
- **역할**: 관리자용 물품 관리 인터페이스
- **주요 기능**:
  - 물품 CRUD 작업
  - 검색 및 필터링
  - 그리드 시각화
  - 대시보드

### 📡 백엔드 API (`backend/`)
- **역할**: 시스템의 핵심 비즈니스 로직
- **주요 기능**:
  - 데이터베이스 관리
  - AI 엔진 통합
  - 하드웨어 제어
  - API 제공

### ⚡ 하드웨어 제어 (`hardware/`)
- **역할**: 물리적 LED 매트릭스 제어
- **주요 기능**:
  - WiFi 통신
  - LED 제어
  - 위치 표시

## 🚀 배포 및 운영

### 개발 환경
```bash
# 개발 서버 시작
./scripts/start_all.sh

# 개별 서비스 시작
./scripts/start_backend.sh
./scripts/start_frontend.sh
./scripts/start_dev.sh
```

### 프로덕션 환경
```bash
# 시스템 상태 확인
./scripts/health_check.sh

# 로그 확인
./scripts/manage_logs.sh view

# 시스템 중지
./scripts/stop_all.sh
```

## 🤝 기여 가이드

### 새로운 기능 추가
1. **기능 설계**: 어떤 기능인지 명확히 정의
2. **구현 위치**: 어느 컴포넌트에 구현할지 결정
3. **개발**: 코드 작성 및 테스트
4. **문서화**: README.md 업데이트
5. **리뷰**: 다른 개발자와 코드 리뷰

### 버그 수정
1. **문제 파악**: 로그 확인 및 재현
2. **원인 분석**: 디버깅 도구 활용
3. **수정**: 최소한의 변경으로 수정
4. **테스트**: 수정 후 전체 시스템 테스트

## 📞 지원 및 문의

### 문제 해결
- **로그 확인**: `logs/` 디렉토리
- **시스템 상태**: `./scripts/health_check.sh`
- **문서 참조**: 각 디렉토리의 README.md

### 도움 요청
- **이슈 생성**: GitHub Issues
- **문서 개선**: 문서 수정 PR
- **기능 제안**: 새로운 아이디어 제안

---

> 💡 **최종 정리**: 
> - 모든 파일이 적절한 디렉토리에 정리되었습니다
> - 중복 파일들이 제거되었습니다
> - 스크립트들이 올바른 경로를 참조합니다
> - 각 디렉토리에 상세한 README.md가 있습니다
> 
> 이제 `./scripts/start_all.sh`로 전체 시스템을 시작할 수 있습니다! 🚀
