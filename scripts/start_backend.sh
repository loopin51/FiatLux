#!/bin/bash
# 스마트 물품 관리 시스템 - 백엔드 서비스 시작 스크립트
# ======================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

echo "=== 🔧 백엔드 서비스 시작 ==="
echo ""

cd "$PROJECT_ROOT"

# PID 파일 저장 디렉토리
PID_DIR="$PROJECT_ROOT/scripts/pids"
mkdir -p "$PID_DIR"

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
    print_success "가상환경이 활성화되었습니다."
else
    print_error "가상환경을 찾을 수 없습니다. setup_system.sh를 먼저 실행해주세요."
    exit 1
fi

# 1. 데이터베이스 상태 확인
print_status "데이터베이스 상태 확인 중..."
if [ -f "items.db" ]; then
    print_success "데이터베이스 파일이 존재합니다."
else
    print_status "데이터베이스 초기화 중..."
    python database.py
    if [ $? -eq 0 ]; then
        print_success "데이터베이스가 초기화되었습니다."
    else
        print_error "데이터베이스 초기화에 실패했습니다."
        exit 1
    fi
fi

echo ""

# 2. MCP 서버 시작
print_status "MCP 서버 시작 중..."
if [ -f "$PID_DIR/mcp_server.pid" ]; then
    MCP_PID=$(cat "$PID_DIR/mcp_server.pid")
    if ps -p $MCP_PID > /dev/null 2>&1; then
        print_warning "MCP 서버가 이미 실행 중입니다. (PID: $MCP_PID)"
    else
        rm -f "$PID_DIR/mcp_server.pid"
    fi
fi

if [ ! -f "$PID_DIR/mcp_server.pid" ]; then
    # 로그 디렉토리 및 파일 생성
    mkdir -p logs
    touch logs/mcp_server.log
    
    nohup python mcp_server.py > logs/mcp_server.log 2>&1 &
    MCP_PID=$!
    echo $MCP_PID > "$PID_DIR/mcp_server.pid"
    
    # 서버 시작 확인
    sleep 3
    if ps -p $MCP_PID > /dev/null 2>&1; then
        print_success "MCP 서버가 시작되었습니다. (PID: $MCP_PID)"
    else
        print_error "MCP 서버 시작에 실패했습니다."
        rm -f "$PID_DIR/mcp_server.pid"
        exit 1
    fi
fi

echo ""

# 3. FastAPI 서버 시작
print_status "FastAPI 서버 시작 중..."
if [ -f "$PID_DIR/fastapi_server.pid" ]; then
    FASTAPI_PID=$(cat "$PID_DIR/fastapi_server.pid")
    if ps -p $FASTAPI_PID > /dev/null 2>&1; then
        print_warning "FastAPI 서버가 이미 실행 중입니다. (PID: $FASTAPI_PID)"
    else
        rm -f "$PID_DIR/fastapi_server.pid"
    fi
fi

if [ ! -f "$PID_DIR/fastapi_server.pid" ]; then
    # 로그 디렉토리 및 파일 생성
    mkdir -p logs
    touch logs/fastapi_server.log
    
    nohup uvicorn rest_api:app --host 0.0.0.0 --port 8001 --reload > logs/fastapi_server.log 2>&1 &
    FASTAPI_PID=$!
    echo $FASTAPI_PID > "$PID_DIR/fastapi_server.pid"
    
    # 서버 시작 확인
    sleep 3
    if ps -p $FASTAPI_PID > /dev/null 2>&1; then
        print_success "FastAPI 서버가 시작되었습니다. (PID: $FASTAPI_PID)"
        print_success "API 문서: http://localhost:8001/docs"
    else
        print_error "FastAPI 서버 시작에 실패했습니다."
        rm -f "$PID_DIR/fastapi_server.pid"
        exit 1
    fi
fi

echo ""

# 4. Streamlit 클라이언트 시작
print_status "Streamlit 클라이언트 시작 중..."
if [ -f "$PID_DIR/streamlit_client.pid" ]; then
    STREAMLIT_PID=$(cat "$PID_DIR/streamlit_client.pid")
    if ps -p $STREAMLIT_PID > /dev/null 2>&1; then
        print_warning "Streamlit 클라이언트가 이미 실행 중입니다. (PID: $STREAMLIT_PID)"
    else
        rm -f "$PID_DIR/streamlit_client.pid"
    fi
fi

if [ ! -f "$PID_DIR/streamlit_client.pid" ]; then
    # 로그 디렉토리 및 파일 생성
    mkdir -p logs
    touch logs/streamlit_client.log
    
    nohup streamlit run intelligent_chatbot_client.py --server.port 8501 > logs/streamlit_client.log 2>&1 &
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > "$PID_DIR/streamlit_client.pid"
    
    # 서버 시작 확인
    sleep 5
    if ps -p $STREAMLIT_PID > /dev/null 2>&1; then
        print_success "Streamlit 클라이언트가 시작되었습니다. (PID: $STREAMLIT_PID)"
        print_success "Streamlit 앱: http://localhost:8501"
    else
        print_error "Streamlit 클라이언트 시작에 실패했습니다."
        rm -f "$PID_DIR/streamlit_client.pid"
        exit 1
    fi
fi

echo ""

# 5. 서비스 상태 확인
print_status "서비스 상태 확인 중..."
echo ""
echo "실행 중인 백엔드 서비스:"
echo "  • MCP 서버: http://localhost:8000 (PID: $(cat "$PID_DIR/mcp_server.pid" 2>/dev/null || echo "없음"))"
echo "  • FastAPI 서버: http://localhost:8001 (PID: $(cat "$PID_DIR/fastapi_server.pid" 2>/dev/null || echo "없음"))"
echo "  • Streamlit 클라이언트: http://localhost:8501 (PID: $(cat "$PID_DIR/streamlit_client.pid" 2>/dev/null || echo "없음"))"
echo ""

print_success "🎉 백엔드 서비스가 모두 시작되었습니다!"
echo ""
echo "로그 파일:"
echo "  • MCP 서버: logs/mcp_server.log"
echo "  • FastAPI 서버: logs/fastapi_server.log"
echo "  • Streamlit 클라이언트: logs/streamlit_client.log"
echo ""
echo "서비스 종료: ./scripts/stop_all.sh"
echo ""
