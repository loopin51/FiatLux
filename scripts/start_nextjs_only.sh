#!/bin/bash
# 스마트 물품 관리 시스템 - Next.js 앱만 시작하는 스크립트
# ====================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[정보]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[성공]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[경고]${NC} $1"
}

print_error() {
    echo -e "${RED}[오류]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# 로고 출력
print_header "
╔══════════════════════════════════════════════════════╗
║            🌐 Next.js 웹 애플리케이션 시작           ║
║                                                      ║
║  • 관리자용 웹 인터페이스                            ║
║  • 물품 관리 및 검색                                 ║
║  • 실시간 LED 제어                                   ║
║  • FastAPI 백엔드 연동                               ║
╚══════════════════════════════════════════════════════╝
"

echo ""

# 1. 시스템 초기화 확인
print_status "시스템 초기화 상태 확인 중..."

if [ ! -d "$PROJECT_ROOT/venv" ]; then
    print_error "가상환경이 설정되지 않았습니다."
    print_status "시스템을 초기화하는 중..."
    "$SCRIPT_DIR/setup_system.sh"
    if [ $? -ne 0 ]; then
        print_error "시스템 초기화에 실패했습니다."
        exit 1
    fi
else
    print_success "시스템이 이미 초기화되어 있습니다."
fi

echo ""

# 2. 백엔드 서비스 상태 확인
print_header "=== 백엔드 서비스 상태 확인 ==="

PID_DIR="$PROJECT_ROOT/scripts/pids"

print_status "필요한 백엔드 서비스 상태 확인 중..."

# FastAPI 서버 확인
FASTAPI_RUNNING=false
if [ -f "$PID_DIR/fastapi_server.pid" ]; then
    FASTAPI_PID=$(cat "$PID_DIR/fastapi_server.pid")
    if ps -p $FASTAPI_PID > /dev/null 2>&1; then
        print_success "FastAPI 서버가 실행 중입니다. (PID: $FASTAPI_PID)"
        FASTAPI_RUNNING=true
    else
        print_warning "FastAPI 서버가 실행되지 않았습니다."
    fi
else
    print_warning "FastAPI 서버가 실행되지 않았습니다."
fi

# FastAPI 서버가 실행되지 않았으면 시작
if [ "$FASTAPI_RUNNING" = false ]; then
    print_status "FastAPI 서버를 시작합니다..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # 로그 디렉토리 생성
    mkdir -p logs
    mkdir -p scripts/pids
    
    # FastAPI 서버 시작
    nohup uvicorn backend.api.rest_api:app --host 0.0.0.0 --port 8001 --reload > logs/fastapi_server.log 2>&1 &
    FASTAPI_PID=$!
    echo $FASTAPI_PID > "$PID_DIR/fastapi_server.pid"
    
    # 서버 시작 확인
    sleep 3
    if ps -p $FASTAPI_PID > /dev/null 2>&1; then
        print_success "FastAPI 서버가 시작되었습니다. (PID: $FASTAPI_PID)"
    else
        print_error "FastAPI 서버 시작에 실패했습니다."
        rm -f "$PID_DIR/fastapi_server.pid"
        exit 1
    fi
fi

echo ""

# 3. Next.js 애플리케이션 시작
print_header "=== Next.js 애플리케이션 시작 ==="

cd "$PROJECT_ROOT/frontend/nextjs-inventory"

# Node.js 종속성 확인
if [ ! -d "node_modules" ]; then
    print_status "Node.js 종속성 설치 중..."
    npm install
    if [ $? -ne 0 ]; then
        print_error "Node.js 종속성 설치에 실패했습니다."
        exit 1
    fi
else
    print_success "Node.js 종속성이 이미 설치되어 있습니다."
fi

# 기존 Next.js 프로세스 종료
if [ -f "$PID_DIR/nextjs_server.pid" ]; then
    NEXTJS_PID=$(cat "$PID_DIR/nextjs_server.pid")
    if ps -p $NEXTJS_PID > /dev/null 2>&1; then
        print_warning "기존 Next.js 서버를 종료합니다. (PID: $NEXTJS_PID)"
        kill $NEXTJS_PID
        sleep 2
    fi
    rm -f "$PID_DIR/nextjs_server.pid"
fi

# Next.js 서버 시작
print_status "Next.js 서버를 시작합니다..."

# 로그 파일 생성
mkdir -p "$PROJECT_ROOT/logs"
touch "$PROJECT_ROOT/logs/nextjs_server.log"

# Next.js 서버 실행
nohup npm run dev > "$PROJECT_ROOT/logs/nextjs_server.log" 2>&1 &
NEXTJS_PID=$!
echo $NEXTJS_PID > "$PID_DIR/nextjs_server.pid"

print_success "Next.js 서버가 시작되었습니다. (PID: $NEXTJS_PID)"

echo ""

# 4. 서비스 시작 확인
print_header "=== 서비스 시작 확인 ==="

# 서비스 시작 대기
print_status "서비스 시작을 확인하는 중..."
sleep 10

# 포트 확인
if command -v curl &> /dev/null; then
    # FastAPI 확인
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "✅ FastAPI 서버: http://localhost:8001 (실행 중)"
    else
        print_warning "⚠️  FastAPI 서버: 시작 중이거나 오류 발생"
    fi
    
    # Next.js 확인
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "✅ Next.js 서버: http://localhost:3000 (실행 중)"
    else
        print_warning "⚠️  Next.js 서버: 시작 중이거나 오류 발생"
    fi
else
    print_warning "curl이 설치되어 있지 않아 서비스 상태를 확인할 수 없습니다."
fi

echo ""

# 5. 웹 인터페이스 정보
print_header "=== 웹 인터페이스 정보 ==="
echo ""
echo "🌐 사용 가능한 웹 인터페이스:"
echo "  • 메인 애플리케이션 (Next.js): http://localhost:3000"
echo "  • API 문서 (FastAPI): http://localhost:8001/docs"
echo "  • API 대화형 문서: http://localhost:8001/redoc"
echo ""

# 6. 개발 도구 정보
print_header "=== 개발 도구 정보 ==="
echo ""
echo "🛠️ 개발 및 디버깅:"
echo "  • Next.js 로그: $PROJECT_ROOT/logs/nextjs_server.log"
echo "  • FastAPI 로그: $PROJECT_ROOT/logs/fastapi_server.log"
echo "  • PID 파일: $PROJECT_ROOT/scripts/pids/"
echo "  • 서비스 종료: $SCRIPT_DIR/stop_all.sh"
echo "  • 전체 시스템 시작: $SCRIPT_DIR/start_all.sh"
echo ""

# 7. 주요 기능 안내
print_header "=== 주요 기능 안내 ==="
echo ""
echo "📋 Next.js 웹 애플리케이션 기능:"
echo "  • 물품 관리 (추가, 수정, 삭제)"
echo "  • 실시간 검색 및 필터링"
echo "  • 그리드 뷰로 물품 현황 확인"
echo "  • LED 위치 표시 테스트"
echo "  • 카테고리별 물품 분류"
echo ""

# 8. 참고 사항
print_header "=== 참고 사항 ==="
echo ""
echo "ℹ️  이 스크립트는 Next.js 앱만 시작합니다:"
echo "  • Streamlit AI 챗봇은 시작되지 않습니다"
echo "  • MCP 서버는 시작되지 않습니다"
echo "  • AI 챗봇이 필요한 경우 ./scripts/start_all.sh 를 사용하세요"
echo ""

# 9. 완료 메시지
print_success "🎉 Next.js 애플리케이션이 성공적으로 시작되었습니다!"
print_success "🚀 브라우저에서 http://localhost:3000 을 열어서 시스템을 사용하세요!"
echo ""

# 10. 실행 옵션
echo "실행 옵션:"
echo "  • 백그라운드 실행: 이 터미널을 그대로 두고 다른 작업을 하세요"
echo "  • 종료: Ctrl+C를 누르거나 ./scripts/stop_all.sh를 실행하세요"
echo "  • 로그 확인: tail -f $PROJECT_ROOT/logs/nextjs_server.log"
echo ""

# 11. 키보드 인터럽트 처리
trap 'echo ""; print_warning "Next.js 서비스 종료 신호를 받았습니다."; print_status "완전히 종료하려면 ./scripts/stop_all.sh를 실행하세요."; exit 0' INT

print_status "Next.js 서비스가 백그라운드에서 실행 중입니다..."
print_status "종료하려면 Ctrl+C를 누르거나 ./scripts/stop_all.sh를 실행하세요."
echo ""

# 무한 대기 (사용자가 종료할 때까지)
while true; do
    sleep 1
done
