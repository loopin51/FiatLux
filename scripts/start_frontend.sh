#!/bin/bash
# 스마트 물품 관리 시스템 - 프론트엔드 서비스 시작 스크립트
# ========================================================

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

echo "=== 🎨 프론트엔드 서비스 시작 ==="
echo ""

# PID 파일 저장 디렉토리
PID_DIR="$PROJECT_ROOT/scripts/pids"
mkdir -p "$PID_DIR"

# Next.js 프로젝트 경로
NEXTJS_PATH="$PROJECT_ROOT/frontend/nextjs-inventory"

# 1. Next.js 프로젝트 확인
print_status "Next.js 프로젝트 확인 중..."
if [ ! -d "$NEXTJS_PATH" ]; then
    print_error "Next.js 프로젝트를 찾을 수 없습니다: $NEXTJS_PATH"
    exit 1
fi

cd "$NEXTJS_PATH"

# 2. Node.js 종속성 확인
print_status "Node.js 종속성 확인 중..."
if [ ! -d "node_modules" ]; then
    print_status "Node.js 종속성 설치 중..."
    npm install
    if [ $? -eq 0 ]; then
        print_success "Node.js 종속성이 설치되었습니다."
    else
        print_error "Node.js 종속성 설치에 실패했습니다."
        exit 1
    fi
else
    print_success "Node.js 종속성이 이미 설치되어 있습니다."
fi

echo ""

# 3. 백엔드 서비스 상태 확인
print_status "백엔드 서비스 상태 확인 중..."
BACKEND_OK=true

# FastAPI 서버 확인
if command -v curl &> /dev/null; then
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "FastAPI 서버가 실행 중입니다."
    else
        print_warning "FastAPI 서버가 실행되지 않았습니다."
        BACKEND_OK=false
    fi
else
    print_warning "curl 명령어가 없어서 백엔드 상태를 확인할 수 없습니다."
fi

if [ "$BACKEND_OK" = false ]; then
    print_warning "백엔드 서비스를 먼저 시작해주세요: ./scripts/start_backend.sh"
    echo ""
fi

# 4. Next.js 개발 서버 시작
print_status "Next.js 개발 서버 시작 중..."

# 기존 Next.js 프로세스 확인
if [ -f "$PID_DIR/nextjs_server.pid" ]; then
    NEXTJS_PID=$(cat "$PID_DIR/nextjs_server.pid")
    if ps -p $NEXTJS_PID > /dev/null 2>&1; then
        print_warning "Next.js 서버가 이미 실행 중입니다. (PID: $NEXTJS_PID)"
        print_success "Next.js 앱: http://localhost:3000"
        exit 0
    else
        rm -f "$PID_DIR/nextjs_server.pid"
    fi
fi

# 로그 디렉토리 생성
mkdir -p "$PROJECT_ROOT/logs"

# Next.js 개발 서버 시작
print_status "Next.js 서버를 시작합니다..."
nohup npm run dev > "$PROJECT_ROOT/logs/nextjs_server.log" 2>&1 &
NEXTJS_PID=$!
echo $NEXTJS_PID > "$PID_DIR/nextjs_server.pid"

# 서버 시작 확인
print_status "서버 시작 확인 중..."
sleep 10

if ps -p $NEXTJS_PID > /dev/null 2>&1; then
    print_success "Next.js 서버가 시작되었습니다. (PID: $NEXTJS_PID)"
    print_success "Next.js 앱: http://localhost:3000"
else
    print_error "Next.js 서버 시작에 실패했습니다."
    rm -f "$PID_DIR/nextjs_server.pid"
    
    # 로그 확인
    if [ -f "$PROJECT_ROOT/logs/nextjs_server.log" ]; then
        print_error "오류 로그:"
        tail -n 20 "$PROJECT_ROOT/logs/nextjs_server.log"
    fi
    exit 1
fi

echo ""

# 5. 서비스 상태 요약
print_status "프론트엔드 서비스 상태:"
echo ""
echo "실행 중인 프론트엔드 서비스:"
echo "  • Next.js 개발 서버: http://localhost:3000 (PID: $(cat "$PID_DIR/nextjs_server.pid" 2>/dev/null || echo "없음"))"
echo ""

print_success "🎉 프론트엔드 서비스가 시작되었습니다!"
echo ""
echo "로그 파일:"
echo "  • Next.js 서버: logs/nextjs_server.log"
echo ""
echo "개발 도구:"
echo "  • 브라우저에서 http://localhost:3000 을 열어주세요"
echo "  • 코드 변경 시 자동으로 새로고침됩니다"
echo ""
echo "서비스 종료: ./scripts/stop_all.sh"
echo ""
