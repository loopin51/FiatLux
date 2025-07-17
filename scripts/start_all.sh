#!/bin/bash
# 스마트 물품 관리 시스템 - 전체 서비스 시작 스크립트
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
║            🤖 스마트 물품 관리 시스템                ║
║                                                      ║
║  • AI 기반 물품 검색 및 관리                         ║
║  • 실시간 LED 위치 표시                              ║
║  • 웹 기반 인터페이스                                ║
║  • MCP 서버 기반 확장 가능한 아키텍처                ║
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

# 2. 백엔드 서비스 시작
print_header "=== 백엔드 서비스 시작 ==="
"$SCRIPT_DIR/start_backend.sh"

if [ $? -ne 0 ]; then
    print_error "백엔드 서비스 시작에 실패했습니다."
    exit 1
fi

echo ""

# 3. 프론트엔드 서비스 시작
print_header "=== 프론트엔드 서비스 시작 ==="
"$SCRIPT_DIR/start_frontend.sh"

if [ $? -ne 0 ]; then
    print_error "프론트엔드 서비스 시작에 실패했습니다."
    print_warning "백엔드 서비스는 계속 실행 중입니다."
    exit 1
fi

echo ""

# 4. 시스템 상태 확인
print_header "=== 시스템 상태 확인 ==="

PID_DIR="$PROJECT_ROOT/scripts/pids"

print_status "실행 중인 모든 서비스:"
echo ""

# 백엔드 서비스 상태
echo "📡 백엔드 서비스:"
if [ -f "$PID_DIR/mcp_server.pid" ]; then
    MCP_PID=$(cat "$PID_DIR/mcp_server.pid")
    if ps -p $MCP_PID > /dev/null 2>&1; then
        echo "  ✅ MCP 서버 (PID: $MCP_PID)"
    else
        echo "  ❌ MCP 서버 (실행 중이 아님)"
    fi
else
    echo "  ❌ MCP 서버 (PID 파일 없음)"
fi

if [ -f "$PID_DIR/fastapi_server.pid" ]; then
    FASTAPI_PID=$(cat "$PID_DIR/fastapi_server.pid")
    if ps -p $FASTAPI_PID > /dev/null 2>&1; then
        echo "  ✅ FastAPI 서버 (PID: $FASTAPI_PID)"
    else
        echo "  ❌ FastAPI 서버 (실행 중이 아님)"
    fi
else
    echo "  ❌ FastAPI 서버 (PID 파일 없음)"
fi

if [ -f "$PID_DIR/streamlit_client.pid" ]; then
    STREAMLIT_PID=$(cat "$PID_DIR/streamlit_client.pid")
    if ps -p $STREAMLIT_PID > /dev/null 2>&1; then
        echo "  ✅ Streamlit 클라이언트 (PID: $STREAMLIT_PID)"
    else
        echo "  ❌ Streamlit 클라이언트 (실행 중이 아님)"
    fi
else
    echo "  ❌ Streamlit 클라이언트 (PID 파일 없음)"
fi

echo ""

# 프론트엔드 서비스 상태
echo "🎨 프론트엔드 서비스:"
if [ -f "$PID_DIR/nextjs_server.pid" ]; then
    NEXTJS_PID=$(cat "$PID_DIR/nextjs_server.pid")
    if ps -p $NEXTJS_PID > /dev/null 2>&1; then
        echo "  ✅ Next.js 서버 (PID: $NEXTJS_PID)"
    else
        echo "  ❌ Next.js 서버 (실행 중이 아님)"
    fi
else
    echo "  ❌ Next.js 서버 (PID 파일 없음)"
fi

echo ""

# 5. 웹 인터페이스 정보
print_header "=== 웹 인터페이스 ==="
echo ""
echo "🌐 사용 가능한 웹 인터페이스:"
echo "  • 메인 애플리케이션 (Next.js): http://localhost:3000"
echo "  • AI 챗봇 (Streamlit): http://localhost:8501"
echo "  • API 문서 (FastAPI): http://localhost:8001/docs"
echo "  • API 대화형 문서: http://localhost:8001/redoc"
echo ""

# 6. 개발 도구 정보
print_header "=== 개발 도구 ==="
echo ""
echo "🛠️ 개발 및 디버깅:"
echo "  • 로그 파일: $PROJECT_ROOT/logs/"
echo "  • PID 파일: $PROJECT_ROOT/scripts/pids/"
echo "  • 서비스 종료: $SCRIPT_DIR/stop_all.sh"
echo "  • 서비스 재시작: $SCRIPT_DIR/start_all.sh"
echo ""

# 7. 하드웨어 연결 정보
print_header "=== 하드웨어 연결 ==="
echo ""
echo "🔌 Arduino/ESP32 연결:"
echo "  • 시리얼 포트를 확인하고 Arduino IDE 또는 ESP32 펌웨어를 업로드하세요"
echo "  • LED 매트릭스 테스트: python test_system.py"
echo "  • 하드웨어 설정: hardware/ 디렉토리 참조"
echo ""

# 8. 완료 메시지
print_success "🎉 모든 서비스가 성공적으로 시작되었습니다!"
print_success "🚀 브라우저에서 http://localhost:3000 을 열어서 시스템을 사용하세요!"
echo ""

# 9. 키보드 인터럽트 처리
trap 'echo ""; print_warning "시스템 종료 신호를 받았습니다."; print_status "서비스를 종료하려면 ./scripts/stop_all.sh를 실행하세요."; exit 0' INT

print_status "시스템이 백그라운드에서 실행 중입니다."
print_status "종료하려면 Ctrl+C를 누르거나 ./scripts/stop_all.sh를 실행하세요."
echo ""

# 무한 대기 (사용자가 종료할 때까지)
while true; do
    sleep 1
done
