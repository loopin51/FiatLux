# 📋 스크립트 빠른 참조 가이드

## 🚀 기본 명령어

### 시스템 시작
```bash
# 전체 시스템 시작
./scripts/start_all.sh

# 백엔드만 시작
./scripts/start_backend.sh

# 프론트엔드만 시작
./scripts/start_frontend.sh

# 개발 모드 시작
./scripts/start_dev.sh
```

### 시스템 관리
```bash
# 모든 서비스 중지
./scripts/stop_all.sh

# 시스템 상태 확인
./scripts/health_check.sh

# 초기 설정
./scripts/setup_system.sh
```

## 📊 로그 관리

### 기본 로그 명령어
```bash
# 로그 초기화
./scripts/manage_logs.sh init

# 로그 상태 확인
./scripts/manage_logs.sh status

# 특정 서비스 로그 보기
./scripts/manage_logs.sh view fastapi

# 실시간 로그 추적
./scripts/manage_logs.sh follow streamlit

# 모든 로그 초기화
./scripts/manage_logs.sh clear

# 로그 백업
./scripts/manage_logs.sh backup
```

## 🌐 접속 주소

- **Next.js 앱**: <http://localhost:3000>
- **Streamlit 챗봇**: <http://localhost:8501>
- **FastAPI 문서**: <http://localhost:8001/docs>

## 📁 로그 파일 위치

### 운영 모드
- `logs/mcp_server.log` - MCP 서버
- `logs/fastapi_server.log` - FastAPI 서버
- `logs/streamlit_client.log` - Streamlit 클라이언트
- `logs/nextjs_server.log` - Next.js 서버

### 개발 모드
- `logs/fastapi_dev.log` - FastAPI 개발
- `logs/mcp_dev.log` - MCP 개발
- `logs/streamlit_dev.log` - Streamlit 개발
- `logs/nextjs_dev.log` - Next.js 개발

## 🔧 문제 해결

### 포트 충돌 해결
```bash
# 포트 사용 프로세스 확인
lsof -i :3000
lsof -i :8001
lsof -i :8501

# 프로세스 종료
kill -9 [PID]
```

### 권한 문제 해결
```bash
# 스크립트 권한 설정
chmod +x scripts/*.sh

# 로그 디렉토리 권한 설정
chmod -R 755 logs/
```

### 서비스 재시작
```bash
# 안전한 재시작
./scripts/stop_all.sh
./scripts/start_all.sh
```

## 🎯 일반적인 사용 시나리오

### 1. 처음 설치
```bash
./scripts/setup_system.sh
./scripts/manage_logs.sh init
./scripts/start_all.sh
```

### 2. 개발 환경
```bash
./scripts/start_dev.sh
./scripts/manage_logs.sh follow fastapi
```

### 3. 문제 해결
```bash
./scripts/health_check.sh
./scripts/manage_logs.sh status
./scripts/manage_logs.sh view fastapi
```

---

상세한 내용은 `scripts/README.md`를 참조하세요.
