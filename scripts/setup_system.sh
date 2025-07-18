#!/bin/bash
# 스마트 물품 관리 시스템 - 초기 설정 스크립트
# =============================================

set -e  # 에러 발생 시 스크립트 종료

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== 🚀 스마트 물품 관리 시스템 초기 설정 ==="
echo "프로젝트 경로: $PROJECT_ROOT"
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 1. 시스템 요구사항 확인
print_status "시스템 요구사항 확인 중..."

# Python 버전 확인
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION 감지됨"
else
    print_error "Python 3이 설치되지 않았습니다. Python 3.8 이상을 설치해주세요."
    exit 1
fi

# Node.js 버전 확인
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION 감지됨"
else
    print_error "Node.js가 설치되지 않았습니다. Node.js 18 이상을 설치해주세요."
    exit 1
fi

# npm 확인
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION 감지됨"
else
    print_error "npm이 설치되지 않았습니다."
    exit 1
fi

echo ""

# 2. Python 가상환경 설정
print_status "Python 가상환경 설정 중..."

cd "$PROJECT_ROOT"

if [ ! -d "venv" ]; then
    print_status "가상환경 생성 중..."
    python3 -m venv venv
    print_success "가상환경이 생성되었습니다."
else
    print_warning "가상환경이 이미 존재합니다."
fi

# 가상환경 활성화
source venv/bin/activate
print_success "가상환경이 활성화되었습니다."

# pip 업그레이드
print_status "pip 업그레이드 중..."
python -m pip install --upgrade pip

echo ""

# 3. Python 종속성 설치
print_status "Python 종속성 설치 중..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python 종속성이 설치되었습니다."
else
    print_error "requirements.txt 파일을 찾을 수 없습니다."
    exit 1
fi

echo ""

# 4. Next.js 프로젝트 설정
print_status "Next.js 프로젝트 설정 중..."

NEXTJS_PATH="$PROJECT_ROOT/frontend/nextjs-inventory"

if [ -d "$NEXTJS_PATH" ]; then
    cd "$NEXTJS_PATH"
    
    print_status "Node.js 종속성 설치 중..."
    npm install
    print_success "Node.js 종속성이 설치되었습니다."
    
    # Next.js 프로젝트 빌드
    print_status "Next.js 프로젝트 빌드 중..."
    npm run build
    print_success "Next.js 프로젝트가 빌드되었습니다."
else
    print_error "Next.js 프로젝트 디렉토리를 찾을 수 없습니다: $NEXTJS_PATH"
    exit 1
fi

echo ""

# 5. 데이터베이스 초기화
print_status "데이터베이스 초기화 중..."

cd "$PROJECT_ROOT"
python database.py

if [ $? -eq 0 ]; then
    print_success "데이터베이스가 초기화되었습니다."
else
    print_error "데이터베이스 초기화에 실패했습니다."
    exit 1
fi

echo ""

# 6. 환경 변수 설정
print_status "환경 변수 설정 중..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env 파일이 생성되었습니다."
        print_warning "필요시 .env 파일을 수정해주세요."
    else
        print_warning ".env.example 파일이 없습니다. 수동으로 .env 파일을 생성해주세요."
    fi
else
    print_warning ".env 파일이 이미 존재합니다."
fi

echo ""

# 7. 필요한 디렉토리 생성
print_status "필요한 디렉토리 생성 중..."

mkdir -p logs
mkdir -p scripts/pids

# 로그 파일 초기화
touch logs/mcp_server.log
touch logs/fastapi_server.log
touch logs/streamlit_client.log
touch logs/nextjs_server.log
touch logs/fastapi_dev.log
touch logs/mcp_dev.log
touch logs/streamlit_dev.log
touch logs/nextjs_dev.log

print_success "디렉토리 및 로그 파일이 생성되었습니다."

echo ""

# 8. 권한 설정
print_status "실행 스크립트 권한 설정 중..."

chmod +x "$SCRIPT_DIR/start_system.sh"
chmod +x "$SCRIPT_DIR/start_backend.sh"
chmod +x "$SCRIPT_DIR/start_frontend.sh"
chmod +x "$SCRIPT_DIR/start_all.sh"
chmod +x "$SCRIPT_DIR/stop_all.sh"

# 8. 권한 설정
print_status "실행 스크립트 권한 설정 중..."

chmod +x "$SCRIPT_DIR/start_system.sh"
chmod +x "$SCRIPT_DIR/start_backend.sh"
chmod +x "$SCRIPT_DIR/start_frontend.sh"
chmod +x "$SCRIPT_DIR/start_all.sh"
chmod +x "$SCRIPT_DIR/stop_all.sh"

print_success "스크립트 권한이 설정되었습니다."

echo ""

# 9. 설정 완료
print_success "🎉 시스템 설정이 완료되었습니다!"
echo ""
echo "다음 명령어로 시스템을 시작할 수 있습니다:"
echo "  • 전체 시스템 시작: ./scripts/start_all.sh"
echo "  • 백엔드만 시작: ./scripts/start_backend.sh"
echo "  • 프론트엔드만 시작: ./scripts/start_frontend.sh"
echo "  • 시스템 종료: ./scripts/stop_all.sh"
echo ""
echo "웹 인터페이스:"
echo "  • Next.js 앱: http://localhost:3000"
echo "  • Streamlit 챗봇: http://localhost:8501"
echo "  • FastAPI 문서: http://localhost:8001/docs"
echo ""
