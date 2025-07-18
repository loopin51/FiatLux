#!/bin/bash
# 스마트 물품 관리 시스템 - 개발 모드 시작 스크립트
# ================================================

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

print_header "
╔══════════════════════════════════════════════════════╗
║            🛠️ 개발 모드 시작                          ║
║                                                      ║
║  • 자동 리로드 활성화                                ║
║  • 상세한 로그 출력                                  ║
║  • 개발 도구 접근 가능                               ║
╚══════════════════════════════════════════════════════╝
"

echo ""

# 개발 모드 확인
print_status "개발 모드 설정 확인 중..."
export NODE_ENV=development
export FASTAPI_ENV=development
export STREAMLIT_ENV=development

echo ""

# 1. 시스템 준비
print_header "=== 시스템 준비 ==="

# 로그 디렉토리 생성
mkdir -p "$PROJECT_ROOT/logs"
print_success "로그 디렉토리가 준비되었습니다."

# PID 디렉토리 생성
mkdir -p "$PROJECT_ROOT/scripts/pids"
print_success "PID 디렉토리가 준비되었습니다."

# 가상환경 활성화
cd "$PROJECT_ROOT"
if [ -d "venv" ]; then
    source venv/bin/activate
    print_success "가상환경이 활성화되었습니다."
else
    print_error "가상환경을 찾을 수 없습니다. setup_system.sh를 먼저 실행해주세요."
    exit 1
fi

echo ""

# 2. 개발 도구 설치 확인
print_header "=== 개발 도구 확인 ==="

# nodemon 설치 확인 (Next.js 자동 리로드)
cd "$PROJECT_ROOT/frontend/nextjs-inventory"
if ! npm list nodemon > /dev/null 2>&1; then
    print_status "nodemon 설치 중..."
    npm install --save-dev nodemon
    print_success "nodemon이 설치되었습니다."
else
    print_success "nodemon이 이미 설치되어 있습니다."
fi

# watchdog 설치 확인 (Python 파일 감시)
cd "$PROJECT_ROOT"
if ! python -c "import watchdog" 2>/dev/null; then
    print_status "watchdog 설치 중..."
    pip install watchdog
    print_success "watchdog가 설치되었습니다."
else
    print_success "watchdog가 이미 설치되어 있습니다."
fi

echo ""

# 3. 개발 서버 시작
print_header "=== 개발 서버 시작 ==="

# tmux 또는 screen 세션 사용 (사용 가능한 경우)
if command -v tmux &> /dev/null; then
    print_status "tmux를 사용하여 개발 서버를 시작합니다."
    
    # 기존 세션 종료
    tmux kill-session -t inventory-dev 2>/dev/null || true
    
    # 새 세션 시작
    tmux new-session -d -s inventory-dev -n main
    
    # 백엔드 서비스 창
    tmux new-window -t inventory-dev -n backend
    tmux send-keys -t inventory-dev:backend "cd '$PROJECT_ROOT'" Enter
    tmux send-keys -t inventory-dev:backend "source venv/bin/activate" Enter
    tmux send-keys -t inventory-dev:backend "uvicorn rest_api:app --host 0.0.0.0 --port 8001 --reload" Enter
    
    # MCP 서버 창
    tmux new-window -t inventory-dev -n mcp
    tmux send-keys -t inventory-dev:mcp "cd '$PROJECT_ROOT'" Enter
    tmux send-keys -t inventory-dev:mcp "source venv/bin/activate" Enter
    tmux send-keys -t inventory-dev:mcp "python mcp_server.py" Enter
    
    # Streamlit 창
    tmux new-window -t inventory-dev -n streamlit
    tmux send-keys -t inventory-dev:streamlit "cd '$PROJECT_ROOT'" Enter
    tmux send-keys -t inventory-dev:streamlit "source venv/bin/activate" Enter
    tmux send-keys -t inventory-dev:streamlit "streamlit run frontend/intelligent_chatbot_client.py --server.port 8501" Enter
    
    # Next.js 창
    tmux new-window -t inventory-dev -n nextjs
    tmux send-keys -t inventory-dev:nextjs "cd '$PROJECT_ROOT/frontend/nextjs-inventory'" Enter
    tmux send-keys -t inventory-dev:nextjs "npm run dev" Enter
    
    print_success "tmux 세션 'inventory-dev'가 시작되었습니다."
    print_status "세션 연결: tmux attach-session -t inventory-dev"
    print_status "세션 종료: tmux kill-session -t inventory-dev"
    
elif command -v screen &> /dev/null; then
    print_status "screen을 사용하여 개발 서버를 시작합니다."
    
    # FastAPI 서버
    screen -dmS inventory-fastapi bash -c "cd '$PROJECT_ROOT'; source venv/bin/activate; uvicorn rest_api:app --host 0.0.0.0 --port 8001 --reload"
    
    # MCP 서버
    screen -dmS inventory-mcp bash -c "cd '$PROJECT_ROOT'; source venv/bin/activate; python mcp_server.py"
    
    # Streamlit
    screen -dmS inventory-streamlit bash -c "cd '$PROJECT_ROOT'; source venv/bin/activate; streamlit run frontend/intelligent_chatbot_client.py --server.port 8501"
    
    # Next.js
    screen -dmS inventory-nextjs bash -c "cd '$PROJECT_ROOT/frontend/nextjs-inventory'; npm run dev"
    
    print_success "screen 세션들이 시작되었습니다."
    print_status "세션 목록: screen -ls"
    print_status "세션 연결: screen -r inventory-[서비스명]"
    
else
    print_warning "tmux 또는 screen이 설치되지 않았습니다. 백그라운드 모드로 실행합니다."
    
    # 백그라운드에서 서비스 시작
    cd "$PROJECT_ROOT"
    
    # 로그 디렉토리 및 파일 생성
    mkdir -p logs
    touch logs/fastapi_dev.log
    touch logs/mcp_dev.log
    touch logs/streamlit_dev.log
    touch logs/nextjs_dev.log
    
    # FastAPI 서버 시작
    nohup uvicorn rest_api:app --host 0.0.0.0 --port 8001 --reload > logs/fastapi_dev.log 2>&1 &
    echo $! > scripts/pids/fastapi_dev.pid
    
    # MCP 서버 시작
    nohup python mcp_server.py > logs/mcp_dev.log 2>&1 &
    echo $! > scripts/pids/mcp_dev.pid
    
    # Streamlit 시작
    nohup streamlit run frontend/intelligent_chatbot_client.py --server.port 8501 > logs/streamlit_dev.log 2>&1 &
    echo $! > scripts/pids/streamlit_dev.pid
    
    # Next.js 시작
    cd "$PROJECT_ROOT/frontend/nextjs-inventory"
    nohup npm run dev > "$PROJECT_ROOT/logs/nextjs_dev.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/scripts/pids/nextjs_dev.pid"
    
    print_success "모든 서비스가 백그라운드에서 시작되었습니다."
fi

echo ""

# 4. 개발 도구 정보
print_header "=== 개발 도구 정보 ==="
echo ""
echo "🌐 웹 인터페이스:"
echo "  • 메인 애플리케이션: http://localhost:3000"
echo "  • AI 챗봇: http://localhost:8501"
echo "  • API 문서: http://localhost:8001/docs"
echo "  • API 대화형 문서: http://localhost:8001/redoc"
echo ""

echo "🔧 개발 도구:"
echo "  • Hot Reload: 코드 변경 시 자동 새로고침"
echo "  • 로그 파일: $PROJECT_ROOT/logs/"
echo "  • 개발자 도구: 브라우저 F12"
echo "  • API 테스트: http://localhost:8001/docs"
echo ""

echo "📊 모니터링:"
echo "  • 실시간 로그: tail -f logs/[서비스명].log"
echo "  • 서비스 상태: ps aux | grep [서비스명]"
echo "  • 포트 상태: netstat -tlnp | grep ':300[01]\\|:850[01]'"
echo ""

echo "🚀 개발 워크플로우:"
echo "  1. 코드 수정"
echo "  2. 자동 리로드 확인"
echo "  3. 브라우저에서 테스트"
echo "  4. API 문서에서 백엔드 테스트"
echo "  5. 로그 파일에서 디버깅"
echo ""

# 5. 서비스 상태 확인
print_header "=== 서비스 상태 확인 ==="
sleep 5  # 서비스 시작 대기

echo ""
print_status "서비스 상태 확인 중..."

# 포트 확인
if command -v curl &> /dev/null; then
    # FastAPI 확인
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "FastAPI 서버: 실행 중"
    else
        print_warning "FastAPI 서버: 시작 중 또는 오류"
    fi
    
    # Next.js 확인
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Next.js 서버: 실행 중"
    else
        print_warning "Next.js 서버: 시작 중 또는 오류"
    fi
    
    # Streamlit 확인
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        print_success "Streamlit 앱: 실행 중"
    else
        print_warning "Streamlit 앱: 시작 중 또는 오류"
    fi
else
    print_warning "curl이 없어서 서비스 상태를 확인할 수 없습니다."
fi

echo ""

# 6. 완료 메시지
print_success "🎉 개발 모드가 시작되었습니다!"
echo ""
print_status "개발 작업을 시작하세요!"
echo "  • 코드 변경 시 자동으로 새로고침됩니다"
echo "  • 로그를 확인하여 오류를 디버깅하세요"
echo "  • 종료하려면 ./scripts/stop_all.sh를 실행하세요"
echo ""

if command -v tmux &> /dev/null; then
    print_status "tmux 세션에 연결하려면: tmux attach-session -t inventory-dev"
fi
