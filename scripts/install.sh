#!/bin/bash

# =============================================================================
# 스마트 물품 관리 시스템 - 통합 설치 스크립트
# =============================================================================
# 이 스크립트는 프로젝트의 모든 종속성을 자동으로 설치합니다:
# - Python 백엔드 의존성
# - Node.js 프론트엔드 의존성  
# - Arduino IDE 라이브러리 설치 가이드
# - 시스템 도구 설치
# =============================================================================

set -e  # 오류 발생 시 스크립트 중단

# 색상 코드 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 로고 출력
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║              스마트 물품 관리 시스템 설치 스크립트                     ║"
echo "║                     Smart Inventory System                       ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 함수 정의
print_step() {
    echo -e "\n${BLUE}[단계 $1]${WHITE} $2${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ 오류: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  경고: $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  정보: $1${NC}"
}

# 운영체제 확인
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
        else
            PACKAGE_MANAGER="unknown"
        fi
    else
        OS="windows"
        PACKAGE_MANAGER="unknown"
    fi
    
    print_info "감지된 운영체제: $OS"
    print_info "패키지 매니저: $PACKAGE_MANAGER"
}

# 시스템 도구 설치
install_system_tools() {
    print_step "1" "시스템 도구 설치"
    
    case $PACKAGE_MANAGER in
        "brew")
            print_info "Homebrew를 사용하여 필수 도구를 설치합니다..."
            
            # Homebrew 업데이트
            echo "Homebrew 업데이트 중..."
            brew update
            
            # 필수 도구들 설치
            tools=("wget" "curl" "git" "python3" "node" "npm")
            for tool in "${tools[@]}"; do
                if ! command -v $tool &> /dev/null; then
                    echo "설치 중: $tool"
                    brew install $tool
                else
                    print_success "$tool 이미 설치됨"
                fi
            done
            ;;
            
        "apt")
            print_info "APT를 사용하여 필수 도구를 설치합니다..."
            sudo apt update
            sudo apt install -y wget curl git python3 python3-pip nodejs npm build-essential
            ;;
            
        "yum")
            print_info "YUM을 사용하여 필수 도구를 설치합니다..."
            sudo yum update -y
            sudo yum install -y wget curl git python3 python3-pip nodejs npm gcc gcc-c++ make
            ;;
            
        *)
            print_warning "알 수 없는 패키지 매니저입니다. 수동으로 다음 도구들을 설치해주세요:"
            echo "- Python 3.8+"
            echo "- Node.js 18+"
            echo "- npm"
            echo "- git"
            ;;
    esac
    
    print_success "시스템 도구 설치 완료"
}

# Python 버전 확인
check_python_version() {
    print_step "2" "Python 환경 확인"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
        print_success "Python 설치됨: $PYTHON_VERSION"
        
        # Python 3.8 이상 확인
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python 버전이 요구사항을 충족합니다 (3.8+)"
        else
            print_error "Python 3.8 이상이 필요합니다. 현재: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python이 설치되지 않았습니다."
        exit 1
    fi
}

# Node.js 버전 확인
check_nodejs_version() {
    print_step "3" "Node.js 환경 확인"
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d 'v' -f 2)
        print_success "Node.js 설치됨: $NODE_VERSION"
        
        # Node.js 18 이상 확인
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d '.' -f 1)
        
        if [ "$NODE_MAJOR" -ge 18 ]; then
            print_success "Node.js 버전이 요구사항을 충족합니다 (18+)"
        else
            print_error "Node.js 18 이상이 필요합니다. 현재: $NODE_VERSION"
            exit 1
        fi
    else
        print_error "Node.js가 설치되지 않았습니다."
        exit 1
    fi
    
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm 설치됨: $NPM_VERSION"
    else
        print_error "npm이 설치되지 않았습니다."
        exit 1
    fi
}

# Python 가상환경 설정
setup_python_venv() {
    print_step "4" "Python 가상환경 설정"
    
    # 가상환경 존재 확인
    if [ ! -d "venv" ]; then
        print_info "Python 가상환경을 생성합니다..."
        python3 -m venv venv
        print_success "가상환경 생성 완료"
    else
        print_success "가상환경이 이미 존재합니다"
    fi
    
    # 가상환경 활성화
    print_info "가상환경을 활성화합니다..."
    source venv/bin/activate
    
    # pip 업그레이드
    print_info "pip를 최신 버전으로 업그레이드합니다..."
    pip install --upgrade pip
    
    print_success "Python 가상환경 설정 완료"
}

# Python 백엔드 의존성 설치
install_python_dependencies() {
    print_step "5" "Python 백엔드 의존성 설치"
    
    if [ -f "requirements.txt" ]; then
        print_info "requirements.txt에서 의존성을 설치합니다..."
        pip install -r requirements.txt
        print_success "Python 의존성 설치 완료"
    else
        print_warning "requirements.txt 파일이 없습니다. 수동으로 의존성을 설치합니다..."
        
        # 필수 패키지들 직접 설치
        essential_packages=(
            "fastapi==0.104.1"
            "uvicorn[standard]==0.24.0"
            "streamlit==1.28.1"
            "fastmcp==0.1.0"
            "google-generativeai==0.3.2"
            "pydantic==2.5.0"
            "sqlite3"
            "requests==2.31.0"
            "python-dotenv==1.0.0"
            "aiofiles==23.2.1"
            "python-multipart==0.0.6"
        )
        
        for package in "${essential_packages[@]}"; do
            print_info "설치 중: $package"
            pip install "$package"
        done
        
        print_success "필수 Python 패키지 설치 완료"
    fi
    
    # 설치된 패키지 목록 출력
    print_info "설치된 주요 패키지들:"
    pip list | grep -E "(fastapi|streamlit|fastmcp|google-generativeai|pydantic)"
}

# Node.js 프론트엔드 의존성 설치
install_nodejs_dependencies() {
    print_step "6" "Node.js 프론트엔드 의존성 설치"
    
    if [ -d "frontend/nextjs-inventory" ]; then
        cd frontend/nextjs-inventory
        
        print_info "Next.js 프로젝트 의존성을 설치합니다..."
        
        # package-lock.json이 있으면 npm ci 사용, 없으면 npm install
        if [ -f "package-lock.json" ]; then
            npm ci
        else
            npm install
        fi
        
        print_success "Next.js 의존성 설치 완료"
        
        # 프로젝트 루트로 돌아가기
        cd ../..
    else
        print_error "Next.js 프로젝트 디렉토리를 찾을 수 없습니다: frontend/nextjs-inventory"
        exit 1
    fi
    
    # 설치된 주요 패키지 정보 출력
    cd frontend/nextjs-inventory
    print_info "설치된 주요 패키지들:"
    npm list --depth=0 | grep -E "(next|react|typescript|tailwindcss|framer-motion)" || true
    cd ../..
}

# 환경 변수 파일 설정
setup_environment() {
    print_step "7" "환경 변수 설정"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_info ".env.example을 복사하여 .env 파일을 생성합니다..."
            cp .env.example .env
            print_success ".env 파일 생성 완료"
            print_warning "⚠️  중요: .env 파일에서 다음 항목들을 실제 값으로 수정해주세요:"
            echo "   - GOOGLE_API_KEY: Gemini API 키"
            echo "   - ESP32_SERVER_URL: ESP32 하드웨어 IP 주소 (실제 하드웨어 사용 시)"
        else
            print_warning ".env.example 파일이 없습니다. 수동으로 .env 파일을 생성해주세요."
        fi
    else
        print_success ".env 파일이 이미 존재합니다"
    fi
}

# 데이터베이스 초기화
setup_database() {
    print_step "8" "데이터베이스 초기화"
    
    if [ ! -f "items.db" ]; then
        print_info "SQLite 데이터베이스를 초기화합니다..."
        python3 backend/database/database.py
        print_success "데이터베이스 초기화 완료"
    else
        print_success "데이터베이스 파일이 이미 존재합니다"
    fi
}

# Arduino IDE 라이브러리 설치 가이드
show_arduino_guide() {
    print_step "9" "Arduino 라이브러리 설치 가이드"
    
    echo -e "${YELLOW}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    Arduino IDE 라이브러리 설치                      ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_info "ESP32 하드웨어를 사용하려면 다음 라이브러리들을 Arduino IDE에서 설치해주세요:"
    echo ""
    echo -e "${WHITE}1. ESP32 보드 패키지:${NC}"
    echo "   - Arduino IDE > 파일 > 환경설정"
    echo "   - 추가 보드 매니저 URLs: https://dl.espressif.com/dl/package_esp32_index.json"
    echo "   - 도구 > 보드 > 보드 매니저에서 'ESP32' 검색 후 설치"
    echo ""
    echo -e "${WHITE}2. 필수 라이브러리들:${NC}"
    echo "   - Adafruit NeoPixel (by Adafruit)"
    echo "   - ArduinoJson (by Benoit Blanchon)"
    echo "   - AsyncTCP (by dvarrel)"
    echo "   - ESPAsyncWebServer (by lacamera)"
    echo ""
    echo -e "${WHITE}3. 라이브러리 설치 방법:${NC}"
    echo "   - Arduino IDE > 스케치 > 라이브러리 포함하기 > 라이브러리 관리"
    echo "   - 각 라이브러리 이름으로 검색 후 설치"
    echo ""
    echo -e "${WHITE}4. 하드웨어 연결:${NC}"
    echo "   - ESP32 DevKit 보드"
    echo "   - NeoPixel LED 스트립 (5x5 = 25개)"
    echo "   - GPIO 2번 핀에 LED 데이터 핀 연결"
    echo "   - 적절한 전원 공급 (5V, 충분한 전류)"
    echo ""
    print_warning "자동 설치가 불가능하므로 수동으로 설치해주세요."
}

# 시스템 테스트
run_system_test() {
    print_step "10" "시스템 테스트"
    
    print_info "시스템 구성 요소를 테스트합니다..."
    
    # Python 모듈 테스트
    echo "Python 모듈 테스트:"
    python3 -c "
import sys
modules = ['fastapi', 'streamlit', 'fastmcp', 'google.generativeai', 'pydantic', 'requests', 'dotenv']
for module in modules:
    try:
        __import__(module)
        print(f'  ✅ {module}')
    except ImportError:
        print(f'  ❌ {module}')
        sys.exit(1)
"
    
    # Node.js 모듈 테스트
    echo "Node.js 모듈 테스트:"
    cd frontend/nextjs-inventory
    node -e "
const modules = ['next', 'react', 'typescript', 'tailwindcss'];
modules.forEach(module => {
    try {
        require.resolve(module);
        console.log(\`  ✅ \${module}\`);
    } catch (e) {
        console.log(\`  ❌ \${module}\`);
        process.exit(1);
    }
});
"
    cd ../..
    
    print_success "모든 구성 요소가 올바르게 설치되었습니다!"
}

# 설치 완료 안내
show_completion_guide() {
    print_step "11" "설치 완료 및 사용 안내"
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                        설치 완료! 🎉                            ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_success "모든 의존성이 성공적으로 설치되었습니다!"
    echo ""
    echo -e "${WHITE}다음 단계:${NC}"
    echo ""
    echo -e "${CYAN}1. 환경 변수 설정:${NC}"
    echo "   vi .env  # Gemini API 키 설정"
    echo ""
    echo -e "${CYAN}2. 시스템 시작:${NC}"
    echo "   ./scripts/start_system.sh"
    echo ""
    echo -e "${CYAN}3. 웹 인터페이스 접속:${NC}"
    echo "   - Next.js 웹앱: http://localhost:3000"
    echo "   - AI 챗봇: http://localhost:8501"
    echo "   - API 문서: http://localhost:8001/docs"
    echo ""
    echo -e "${CYAN}4. Arduino 펌웨어 업로드:${NC}"
    echo "   - hardware/esp32_neopixel_server.ino 파일을 Arduino IDE로 열기"
    echo "   - WiFi 설정 수정 후 ESP32에 업로드"
    echo ""
    echo -e "${YELLOW}⚠️  중요 사항:${NC}"
    echo "   - .env 파일의 API 키를 실제 값으로 수정해주세요"
    echo "   - ESP32 하드웨어 없이도 시뮬레이션 모드로 테스트 가능합니다"
    echo "   - 문제 발생 시 README.md의 트러블슈팅 섹션을 참고하세요"
    echo ""
    print_info "설치 스크립트가 완료되었습니다. 즐거운 개발 되세요! 🚀"
}

# 메인 실행 함수
main() {
    # 시작 시간 기록
    start_time=$(date +%s)
    
    # 프로젝트 루트 디렉토리로 이동
    if [ ! -f "requirements.txt" ] && [ ! -d "backend" ]; then
        print_error "프로젝트 루트 디렉토리에서 실행해주세요."
        exit 1
    fi
    
    print_info "설치를 시작합니다..."
    
    # 운영체제 감지
    detect_os
    
    # 사용자 확인
    echo -e "\n${YELLOW}계속 진행하시겠습니까? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_info "설치가 취소되었습니다."
        exit 0
    fi
    
    # 설치 단계들 실행
    install_system_tools
    check_python_version
    check_nodejs_version
    setup_python_venv
    install_python_dependencies
    install_nodejs_dependencies
    setup_environment
    setup_database
    show_arduino_guide
    run_system_test
    show_completion_guide
    
    # 완료 시간 계산
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    print_success "총 설치 시간: ${duration}초"
}

# 스크립트 실행
main "$@"
