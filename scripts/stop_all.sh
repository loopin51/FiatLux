#!/bin/bash
# 스마트 물품 관리 시스템 - 전체 서비스 종료 스크립트
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

# 프로세스 종료 함수
kill_process() {
    local pid=$1
    local service_name=$2
    
    if [ -z "$pid" ]; then
        print_warning "$service_name: PID가 없습니다."
        return 1
    fi
    
    if ps -p $pid > /dev/null 2>&1; then
        print_status "$service_name 종료 중... (PID: $pid)"
        kill $pid
        
        # 종료 확인 (최대 10초 대기)
        local count=0
        while ps -p $pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        if ps -p $pid > /dev/null 2>&1; then
            print_warning "$service_name이 정상적으로 종료되지 않았습니다. 강제 종료합니다."
            kill -9 $pid
            sleep 1
        fi
        
        if ps -p $pid > /dev/null 2>&1; then
            print_error "$service_name 종료에 실패했습니다."
            return 1
        else
            print_success "$service_name이 종료되었습니다."
            return 0
        fi
    else
        print_warning "$service_name이 실행 중이 아닙니다."
        return 1
    fi
}

print_header "
╔══════════════════════════════════════════════════════╗
║            🛑 시스템 종료 중...                      ║
╚══════════════════════════════════════════════════════╝
"

echo ""

# PID 파일 디렉토리
PID_DIR="$PROJECT_ROOT/scripts/pids"

if [ ! -d "$PID_DIR" ]; then
    print_warning "PID 디렉토리가 없습니다. 실행 중인 서비스가 없을 수 있습니다."
    exit 0
fi

# 1. Next.js 서버 종료
print_header "=== 프론트엔드 서비스 종료 ==="
if [ -f "$PID_DIR/nextjs_server.pid" ]; then
    NEXTJS_PID=$(cat "$PID_DIR/nextjs_server.pid")
    kill_process $NEXTJS_PID "Next.js 서버"
    rm -f "$PID_DIR/nextjs_server.pid"
fi

echo ""

# 2. 백엔드 서비스 종료
print_header "=== 백엔드 서비스 종료 ==="

# Streamlit 클라이언트 종료
if [ -f "$PID_DIR/streamlit_client.pid" ]; then
    STREAMLIT_PID=$(cat "$PID_DIR/streamlit_client.pid")
    kill_process $STREAMLIT_PID "Streamlit 클라이언트"
    rm -f "$PID_DIR/streamlit_client.pid"
fi

# FastAPI 서버 종료
if [ -f "$PID_DIR/fastapi_server.pid" ]; then
    FASTAPI_PID=$(cat "$PID_DIR/fastapi_server.pid")
    kill_process $FASTAPI_PID "FastAPI 서버"
    rm -f "$PID_DIR/fastapi_server.pid"
fi

# MCP 서버 종료
if [ -f "$PID_DIR/mcp_server.pid" ]; then
    MCP_PID=$(cat "$PID_DIR/mcp_server.pid")
    kill_process $MCP_PID "MCP 서버"
    rm -f "$PID_DIR/mcp_server.pid"
fi

echo ""

# 3. 추가 프로세스 정리
print_header "=== 추가 프로세스 정리 ==="

# 포트 기반으로 남은 프로세스 찾기
print_status "포트 기반 프로세스 확인 중..."

# 포트 3000 (Next.js)
if command -v lsof &> /dev/null; then
    NEXTJS_PROCESSES=$(lsof -ti:3000 2>/dev/null || true)
    if [ -n "$NEXTJS_PROCESSES" ]; then
        print_warning "포트 3000에서 실행 중인 프로세스를 발견했습니다."
        echo $NEXTJS_PROCESSES | xargs kill -9 2>/dev/null || true
        print_success "포트 3000의 프로세스가 종료되었습니다."
    fi
    
    # 포트 8001 (FastAPI)
    FASTAPI_PROCESSES=$(lsof -ti:8001 2>/dev/null || true)
    if [ -n "$FASTAPI_PROCESSES" ]; then
        print_warning "포트 8001에서 실행 중인 프로세스를 발견했습니다."
        echo $FASTAPI_PROCESSES | xargs kill -9 2>/dev/null || true
        print_success "포트 8001의 프로세스가 종료되었습니다."
    fi
    
    # 포트 8501 (Streamlit)
    STREAMLIT_PROCESSES=$(lsof -ti:8501 2>/dev/null || true)
    if [ -n "$STREAMLIT_PROCESSES" ]; then
        print_warning "포트 8501에서 실행 중인 프로세스를 발견했습니다."
        echo $STREAMLIT_PROCESSES | xargs kill -9 2>/dev/null || true
        print_success "포트 8501의 프로세스가 종료되었습니다."
    fi
fi

echo ""

# 4. 임시 파일 정리
print_header "=== 임시 파일 정리 ==="

# PID 디렉토리 정리
if [ -d "$PID_DIR" ]; then
    print_status "PID 파일 정리 중..."
    rm -rf "$PID_DIR"
    print_success "PID 파일이 정리되었습니다."
fi

# 로그 파일 압축 (선택사항)
if [ -d "$PROJECT_ROOT/logs" ]; then
    print_status "로그 파일 정리 중..."
    
    # 오래된 로그 파일 압축
    find "$PROJECT_ROOT/logs" -name "*.log" -mtime +7 -exec gzip {} \; 2>/dev/null || true
    
    # 압축된 로그 파일 중 30일 이상 된 것 삭제
    find "$PROJECT_ROOT/logs" -name "*.log.gz" -mtime +30 -delete 2>/dev/null || true
    
    print_success "로그 파일이 정리되었습니다."
fi

echo ""

# 5. 서비스 상태 최종 확인
print_header "=== 서비스 상태 최종 확인 ==="

print_status "포트 상태 확인 중..."

if command -v lsof &> /dev/null; then
    echo "포트 사용 상태:"
    
    # 포트 3000 확인
    if lsof -ti:3000 > /dev/null 2>&1; then
        echo "  ❌ 포트 3000: 여전히 사용 중"
    else
        echo "  ✅ 포트 3000: 사용 가능"
    fi
    
    # 포트 8001 확인
    if lsof -ti:8001 > /dev/null 2>&1; then
        echo "  ❌ 포트 8001: 여전히 사용 중"
    else
        echo "  ✅ 포트 8001: 사용 가능"
    fi
    
    # 포트 8501 확인
    if lsof -ti:8501 > /dev/null 2>&1; then
        echo "  ❌ 포트 8501: 여전히 사용 중"
    else
        echo "  ✅ 포트 8501: 사용 가능"
    fi
else
    print_warning "lsof 명령어가 없어서 포트 상태를 확인할 수 없습니다."
fi

echo ""

# 6. 완료 메시지
print_success "🎉 모든 서비스가 성공적으로 종료되었습니다!"
echo ""
echo "다음 명령어로 시스템을 다시 시작할 수 있습니다:"
echo "  • 전체 시스템: ./scripts/start_all.sh"
echo "  • 백엔드만: ./scripts/start_backend.sh"
echo "  • 프론트엔드만: ./scripts/start_frontend.sh"
echo ""

# 7. 시스템 정보 표시
print_header "=== 시스템 정보 ==="
echo ""
echo "📁 프로젝트 디렉토리: $PROJECT_ROOT"
echo "📄 로그 파일: $PROJECT_ROOT/logs/"
echo "🔧 스크립트 디렉토리: $SCRIPT_DIR"
echo "🗄️ 데이터베이스: $PROJECT_ROOT/items.db"
echo ""

print_status "시스템 종료가 완료되었습니다."
