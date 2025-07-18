# 📋 스마트 물품 관리 시스템 - 스크립트 가이드

## 🚀 개요

이 문서는 스마트 물품 관리 시스템의 모든 스크립트들에 대한 완전한 사용 가이드입니다. 
시스템 설정부터 실행, 관리, 디버깅까지 모든 과정을 신입 개발자도 쉽게 이해할 수 있도록 설명합니다.

## 🏗️ 시스템 실행 플로우

```
1. 최초 설정    2. 시스템 시작    3. 서비스 확인    4. 사용자 접속
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ setup_      │ │ start_all.  │ │ health_     │ │ http://     │
│ system.sh   │→│ sh          │→│ check.sh    │→│ localhost   │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
     ↓               ↓               ↓               ↓
   환경 구성       서비스 시작       상태 확인       웹 접속
```

## 📁 스크립트 구조

```
scripts/
├── README.md                    # 스크립트 가이드 (이 파일)
├── QUICK_REFERENCE.md          # 빠른 참조 가이드
│
├── 🚀 시스템 관리
│   ├── setup_system.sh         # 시스템 초기 설정
│   ├── start_all.sh            # 전체 시스템 시작
│   ├── start_system.sh         # 시스템 시작 (별칭)
│   ├── stop_all.sh             # 모든 서비스 중지
│   └── health_check.sh         # 시스템 상태 확인
│
├── 🔧 개별 서비스
│   ├── start_backend.sh        # 백엔드 서비스 시작
│   ├── start_frontend.sh       # Next.js 앱 시작
│   ├── start_nextjs_only.sh    # Next.js 앱만 시작
│   └── start_dev.sh            # Streamlit 챗봇 시작
│
├── 📦 설치 및 설정
│   ├── install.sh              # 종속성 설치
│   ├── quick_install.sh        # 빠른 설치
│   └── add_sample_tools.py     # 샘플 데이터 추가
│
├── 📊 모니터링
│   ├── manage_logs.sh          # 로그 관리
│   └── pids/                   # 프로세스 ID 저장
│
└── 🔍 디버깅 도구
    └── (각 스크립트 내 디버깅 기능)
```

---

## 🛠️ 주요 스크립트 상세 가이드

### 1. 시스템 설정 스크립트

#### `setup_system.sh` - 시스템 초기 설정
**목적**: 시스템 최초 설정 및 환경 구성

**실행 내용**:
```bash
# 1. 가상환경 생성
python3 -m venv venv

# 2. 가상환경 활성화
source venv/bin/activate

# 3. Python 패키지 설치
pip install -r requirements.txt

# 4. Node.js 패키지 설치
cd frontend/nextjs-inventory && npm install

# 5. 환경 변수 설정
cp .env.example .env

# 6. 디렉토리 생성
mkdir -p logs scripts/pids

# 7. 권한 설정
chmod +x scripts/*.sh
```

**사용법**:
```bash
# 최초 1회만 실행
./scripts/setup_system.sh

# 성공 시 출력
✅ 시스템 설정 완료
🌐 웹 앱: http://localhost:3000
🤖 챗봇: http://localhost:8501
```

---

### 2. 서비스 시작 스크립트

#### `start_all.sh`
**목적**: 전체 시스템 통합 시작

**기능**:
- 백엔드 서비스 시작 (MCP, FastAPI, Streamlit)
- 프론트엔드 서비스 시작 (Next.js)
- 서비스 상태 확인
- 실행 결과 종합 보고

**사용법**:
```bash
./scripts/start_all.sh
```

**접속 URL**:
- Next.js 앱: http://localhost:3000
- Streamlit 챗봇: http://localhost:8501
- FastAPI 문서: http://localhost:8001/docs

#### `start_backend.sh`
**목적**: 백엔드 서비스만 시작

**기능**:
- MCP 서버 시작 (포트 8000)
- FastAPI 서버 시작 (포트 8001)
- Streamlit 클라이언트 시작 (포트 8501)
- 각 서비스 PID 관리
- 로그 파일 자동 생성

**사용법**:
```bash
./scripts/start_backend.sh
```

**생성되는 로그 파일**:
- `logs/mcp_server.log`
- `logs/fastapi_server.log`
- `logs/streamlit_client.log`

#### `start_frontend.sh`
**목적**: Next.js 웹 애플리케이션 시작

**기능**:
- Next.js 개발 서버 시작
- 종속성 자동 설치
- 백엔드 서비스 상태 확인
- 3000 포트에서 서비스 제공

**사용법**:
```bash
./scripts/start_frontend.sh
```

**생성되는 로그 파일**:
- `logs/nextjs_server.log`

#### `start_nextjs_only.sh`
**목적**: Next.js 웹 애플리케이션만 시작 (Streamlit, MCP 서버 제외)

**기능**:
- Next.js 개발 서버 시작
- 필요한 FastAPI 백엔드만 자동 시작
- Streamlit AI 챗봇 제외
- MCP 서버 제외
- 경량화된 실행 환경

**사용법**:
```bash
./scripts/start_nextjs_only.sh
```

**생성되는 로그 파일**:
- `logs/nextjs_server.log`
- `logs/fastapi_server.log`

**주요 특징**:
- 🚀 빠른 시작 (필요한 서비스만 실행)
- 💡 관리자 인터페이스 전용
- 🔧 개발 및 테스트에 적합
- 📊 물품 관리 기능 완전 지원

#### `start_dev.sh`
**목적**: 개발 모드로 모든 서비스 시작

**기능**:
- tmux/screen 세션 관리
- 개발 환경 최적화
- 모든 서비스 동시 실행
- 실시간 로그 모니터링

**사용법**:
```bash
./scripts/start_dev.sh
```

**세션 관리**:
```bash
# tmux 사용시
tmux list-sessions
tmux attach-session -t inventory-fastapi

# screen 사용시
screen -ls
screen -r inventory-fastapi
```

**생성되는 로그 파일**:
- `logs/fastapi_dev.log`
- `logs/mcp_dev.log`
- `logs/streamlit_dev.log`
- `logs/nextjs_dev.log`

---

### 3. 서비스 관리 스크립트

#### `stop_all.sh`
**목적**: 모든 서비스 안전하게 중지

**기능**:
- 실행 중인 모든 서비스 감지
- PID 파일 기반 프로세스 종료
- 포트 점유 프로세스 정리
- 임시 파일 및 세션 정리

**사용법**:
```bash
./scripts/stop_all.sh
```

**중지되는 서비스**:
- MCP 서버
- FastAPI 서버
- Streamlit 클라이언트
- Next.js 서버
- tmux/screen 세션

#### `health_check.sh`
**목적**: 시스템 상태 종합 점검

**기능**:
- 서비스 실행 상태 확인
- 포트 점유 상태 확인
- 로그 파일 상태 확인
- 종속성 설치 상태 확인
- 데이터베이스 연결 상태 확인

**사용법**:
```bash
./scripts/health_check.sh
```

**체크 항목**:
- ✅ Python 가상환경
- ✅ Node.js 환경
- ✅ 서비스 프로세스
- ✅ 네트워크 포트
- ✅ 로그 파일
- ✅ 데이터베이스

---

### 4. 설치 스크립트

#### `install.sh`
**목적**: 종속성 완전 설치

**기능**:
- Python 패키지 설치
- Node.js 모듈 설치
- 시스템 종속성 확인
- 환경 검증

**사용법**:
```bash
./scripts/install.sh
```

#### `quick_install.sh`
**목적**: 빠른 설치 (최소 종속성)

**기능**:
- 핵심 패키지만 설치
- 빠른 환경 구성
- 개발 환경 우선 설정

**사용법**:
```bash
./scripts/quick_install.sh
```

---

## 📊 로그 관리 시스템

### `manage_logs.sh`
**목적**: 종합적인 로그 관리 도구

#### 주요 기능

##### 1. 로그 초기화
```bash
./scripts/manage_logs.sh init
```
- 로그 디렉토리 생성
- 모든 로그 파일 생성
- 권한 설정

##### 2. 로그 상태 확인
```bash
./scripts/manage_logs.sh status
```
- 로그 파일 크기 확인
- 수정 시간 확인
- 전체 통계 제공

출력 예시:
```
📊 로그 파일 상태
위치: /path/to/logs

mcp_server.log         2.34 MB  2024-01-15 14:30:25
fastapi_server.log     1.87 MB  2024-01-15 14:30:20
streamlit_client.log   0.95 MB  2024-01-15 14:30:15
nextjs_server.log      5.23 MB  2024-01-15 14:30:10

총 4 개의 로그 파일, 전체 크기: 10.39 MB
```

##### 3. 로그 보기
```bash
./scripts/manage_logs.sh view [서비스명]
```
- 특정 서비스의 최근 로그 확인
- 마지막 50줄 표시
- 자동 로그 파일 감지

사용 예시:
```bash
./scripts/manage_logs.sh view fastapi
./scripts/manage_logs.sh view mcp
./scripts/manage_logs.sh view streamlit
./scripts/manage_logs.sh view nextjs
```

##### 4. 실시간 로그 추적
```bash
./scripts/manage_logs.sh follow [서비스명]
```
- 실시간 로그 스트리밍
- 새로운 로그 항목 즉시 표시
- Ctrl+C로 종료

사용 예시:
```bash
./scripts/manage_logs.sh follow fastapi
```

##### 5. 로그 초기화
```bash
./scripts/manage_logs.sh clear
```
- 모든 로그 파일 내용 삭제
- 파일 구조는 유지
- 디스크 공간 확보

##### 6. 로그 백업
```bash
./scripts/manage_logs.sh backup
```
- 타임스탬프 기반 백업
- 자동 압축 (tar.gz)
- 백업 파일 위치: `logs_backup/`

백업 파일 예시:
```
logs_backup/
├── logs_20240115_143025.tar.gz
├── logs_20240114_091230.tar.gz
└── logs_20240113_154500.tar.gz
```

---

## 🔧 로그 파일 구조

### 운영 모드 로그
```
logs/
├── mcp_server.log          # MCP 서버 로그
├── fastapi_server.log      # FastAPI 서버 로그
├── streamlit_client.log    # Streamlit 클라이언트 로그
├── nextjs_server.log       # Next.js 서버 로그
├── system.log              # 시스템 로그
└── error.log               # 에러 로그
```

### 개발 모드 로그
```
logs/
├── fastapi_dev.log         # FastAPI 개발 로그
├── mcp_dev.log             # MCP 개발 로그
├── streamlit_dev.log       # Streamlit 개발 로그
└── nextjs_dev.log          # Next.js 개발 로그
```

---

## 🚀 사용 시나리오

### 1. 처음 설치
```bash
# 1. 시스템 설정
./scripts/setup_system.sh

# 2. 로그 초기화
./scripts/manage_logs.sh init

# 3. 전체 시스템 시작
./scripts/start_all.sh
```

### 2. 개발 환경 구성
```bash
# 1. 개발 모드 시작
./scripts/start_dev.sh

# 2. 실시간 로그 모니터링
./scripts/manage_logs.sh follow fastapi
```

### 3. 문제 해결
```bash
# 1. 시스템 상태 확인
./scripts/health_check.sh

# 2. 로그 확인
./scripts/manage_logs.sh status
./scripts/manage_logs.sh view fastapi

# 3. 서비스 재시작
./scripts/stop_all.sh
./scripts/start_all.sh
```

### 4. 정기 유지보수
```bash
# 1. 로그 백업
./scripts/manage_logs.sh backup

# 2. 로그 초기화
./scripts/manage_logs.sh clear

# 3. 시스템 점검
./scripts/health_check.sh
```

---

## 🛡️ 안전 기능

### 1. 중복 실행 방지
- PID 파일 기반 프로세스 체크
- 포트 점유 상태 확인
- 안전한 재시작 메커니즘

### 2. 자동 복구
- 실패한 서비스 자동 재시작
- 로그 파일 자동 생성
- 권한 문제 자동 해결

### 3. 상태 모니터링
- 실시간 서비스 상태 확인
- 자원 사용량 모니터링
- 에러 로그 자동 분석

---

## 📞 문제 해결

### 일반적인 문제

#### 1. 포트 충돌
```bash
# 포트 사용 프로세스 확인
lsof -i :3000
lsof -i :8000
lsof -i :8001
lsof -i :8501

# 프로세스 종료
kill -9 [PID]
```

#### 2. 권한 문제
```bash
# 스크립트 권한 설정
chmod +x scripts/*.sh

# 로그 디렉토리 권한 설정
chmod -R 755 logs/
```

#### 3. 종속성 문제
```bash
# 재설치
./scripts/install.sh

# 또는 빠른 설치
./scripts/quick_install.sh
```

#### 4. 로그 파일 문제
```bash
# 로그 재초기화
./scripts/manage_logs.sh init

# 로그 권한 수정
chmod 644 logs/*.log
```

### 디버깅 도구

#### 1. 상세 로그 확인
```bash
# 실시간 로그 추적
./scripts/manage_logs.sh follow fastapi

# 에러 로그 확인
./scripts/manage_logs.sh view error
```

#### 2. 시스템 진단
```bash
# 전체 시스템 상태 확인
./scripts/health_check.sh

# 특정 서비스 상태 확인
ps aux | grep python
ps aux | grep node
```

#### 3. 네트워크 확인
```bash
# 포트 상태 확인
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001
netstat -tulpn | grep :8501
```

---

## 🔄 업데이트 가이드

### 스크립트 업데이트
```bash
# 기존 서비스 중지
./scripts/stop_all.sh

# 새 스크립트 적용
git pull origin main

# 권한 재설정
chmod +x scripts/*.sh

# 시스템 재시작
./scripts/start_all.sh
```

### 로그 관리 업데이트
```bash
# 로그 백업
./scripts/manage_logs.sh backup

# 로그 초기화
./scripts/manage_logs.sh clear

# 새 로그 구조 적용
./scripts/manage_logs.sh init
```

---

## 📈 성능 최적화

### 1. 로그 관리
- 정기적 로그 백업 및 초기화
- 로그 크기 모니터링
- 불필요한 로그 레벨 조정

### 2. 프로세스 관리
- 메모리 사용량 모니터링
- CPU 사용률 확인
- 좀비 프로세스 정리

### 3. 디스크 관리
- 로그 파일 크기 제한
- 임시 파일 정리
- 백업 파일 관리

---

## 📝 로그 활용 팁

### 1. 효율적인 로그 분석
```bash
# 에러 메시지 검색
grep -i "error" logs/fastapi_server.log

# 특정 시간대 로그 확인
grep "2024-01-15 14:" logs/fastapi_server.log

# 로그 통계
wc -l logs/*.log
```

### 2. 로그 모니터링
```bash
# 여러 로그 동시 모니터링
multitail logs/fastapi_server.log logs/mcp_server.log

# 로그 필터링
tail -f logs/fastapi_server.log | grep "INFO"
```

### 3. 로그 분석 도구
```bash
# 로그 압축 및 분석
gzip logs/old_logs/*.log

# 로그 검색 최적화
grep -r "pattern" logs/
```

---

## 🎯 결론

이 스크립트 시스템은 스마트 물품 관리 시스템의 완전한 자동화를 제공합니다. 개발부터 운영까지 모든 단계에서 안정적이고 효율적인 관리를 위해 설계되었습니다.

**핵심 장점**:
- 🚀 원클릭 시스템 시작
- 📊 실시간 모니터링
- 🛡️ 안전한 프로세스 관리
- 📋 완전한 로그 관리
- 🔧 쉬운 문제 해결

**새로운 기능**:
- 📱 `start_nextjs_only.sh`: Next.js 앱만 실행하는 경량화된 스크립트
- 💡 관리자 인터페이스 전용 실행 모드
- 🔧 개발 및 테스트에 최적화된 환경

**지원 연락처**:
- 문제 발생시: GitHub Issues
- 기능 제안: GitHub Discussions
- 긴급 지원: 시스템 관리자

---

*마지막 업데이트: 2025년 1월 15일*
*버전: 1.0.0*
