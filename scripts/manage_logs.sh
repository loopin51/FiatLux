#!/bin/bash
# 로그 관리 유틸리티 스크립트
# ================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$PROJECT_ROOT/logs"

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

# 로그 디렉토리 생성 함수
create_logs_directory() {
    print_status "로그 디렉토리 생성 중..."
    
    if [ ! -d "$LOGS_DIR" ]; then
        mkdir -p "$LOGS_DIR"
        print_success "로그 디렉토리가 생성되었습니다: $LOGS_DIR"
    else
        print_warning "로그 디렉토리가 이미 존재합니다: $LOGS_DIR"
    fi
}

# 로그 파일 생성 함수
create_log_files() {
    print_status "로그 파일 생성 중..."
    
    local log_files=(
        "mcp_server.log"
        "fastapi_server.log"
        "streamlit_client.log"
        "nextjs_server.log"
        "fastapi_dev.log"
        "mcp_dev.log"
        "streamlit_dev.log"
        "nextjs_dev.log"
        "system.log"
        "error.log"
    )
    
    for log_file in "${log_files[@]}"; do
        local log_path="$LOGS_DIR/$log_file"
        if [ ! -f "$log_path" ]; then
            touch "$log_path"
            print_success "로그 파일 생성: $log_file"
        else
            print_warning "로그 파일이 이미 존재: $log_file"
        fi
    done
}

# 로그 파일 초기화 함수
clear_logs() {
    print_warning "모든 로그 파일을 초기화합니다..."
    
    if [ -d "$LOGS_DIR" ]; then
        find "$LOGS_DIR" -name "*.log" -type f -exec truncate -s 0 {} \;
        print_success "모든 로그 파일이 초기화되었습니다."
    else
        print_error "로그 디렉토리가 존재하지 않습니다."
    fi
}

# 로그 상태 확인 함수
check_logs_status() {
    print_status "로그 상태 확인 중..."
    
    if [ ! -d "$LOGS_DIR" ]; then
        print_error "로그 디렉토리가 존재하지 않습니다."
        return 1
    fi
    
    echo ""
    print_header "📊 로그 파일 상태"
    echo "위치: $LOGS_DIR"
    echo ""
    
    local total_size=0
    local file_count=0
    
    for log_file in "$LOGS_DIR"/*.log; do
        if [ -f "$log_file" ]; then
            local filename=$(basename "$log_file")
            local size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo "0")
            local size_mb=$(echo "scale=2; $size/1024/1024" | bc)
            local modified=$(stat -f%Sm "$log_file" 2>/dev/null || stat -c%y "$log_file" 2>/dev/null || echo "알 수 없음")
            
            printf "%-25s %8s MB  %s\n" "$filename" "$size_mb" "$modified"
            
            total_size=$((total_size + size))
            file_count=$((file_count + 1))
        fi
    done
    
    if [ $file_count -eq 0 ]; then
        print_warning "로그 파일이 없습니다."
    else
        local total_size_mb=$(echo "scale=2; $total_size/1024/1024" | bc)
        echo ""
        print_success "총 $file_count 개의 로그 파일, 전체 크기: $total_size_mb MB"
    fi
}

# 로그 보기 함수
view_logs() {
    local service="$1"
    
    if [ -z "$service" ]; then
        print_error "서비스명을 입력해주세요."
        echo "사용법: $0 view [서비스명]"
        echo "예시: $0 view fastapi"
        return 1
    fi
    
    local log_file="$LOGS_DIR/${service}.log"
    if [ ! -f "$log_file" ]; then
        # 개발 모드 로그 파일 확인
        log_file="$LOGS_DIR/${service}_dev.log"
        if [ ! -f "$log_file" ]; then
            # 서버 로그 파일 확인
            log_file="$LOGS_DIR/${service}_server.log"
            if [ ! -f "$log_file" ]; then
                print_error "로그 파일을 찾을 수 없습니다: $service"
                return 1
            fi
        fi
    fi
    
    print_status "로그 파일 보기: $log_file"
    echo ""
    
    if [ -s "$log_file" ]; then
        tail -n 50 "$log_file"
    else
        print_warning "로그 파일이 비어있습니다."
    fi
}

# 실시간 로그 추적 함수
follow_logs() {
    local service="$1"
    
    if [ -z "$service" ]; then
        print_error "서비스명을 입력해주세요."
        echo "사용법: $0 follow [서비스명]"
        echo "예시: $0 follow fastapi"
        return 1
    fi
    
    local log_file="$LOGS_DIR/${service}.log"
    if [ ! -f "$log_file" ]; then
        # 개발 모드 로그 파일 확인
        log_file="$LOGS_DIR/${service}_dev.log"
        if [ ! -f "$log_file" ]; then
            # 서버 로그 파일 확인
            log_file="$LOGS_DIR/${service}_server.log"
            if [ ! -f "$log_file" ]; then
                print_error "로그 파일을 찾을 수 없습니다: $service"
                return 1
            fi
        fi
    fi
    
    print_status "실시간 로그 추적: $log_file"
    print_status "중지하려면 Ctrl+C를 누르세요."
    echo ""
    
    tail -f "$log_file"
}

# 로그 백업 함수
backup_logs() {
    print_status "로그 백업 중..."
    
    local backup_dir="$PROJECT_ROOT/logs_backup"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$backup_dir/logs_$timestamp"
    
    if [ ! -d "$LOGS_DIR" ]; then
        print_error "로그 디렉토리가 존재하지 않습니다."
        return 1
    fi
    
    mkdir -p "$backup_path"
    
    # 로그 파일 복사
    cp -r "$LOGS_DIR"/* "$backup_path/" 2>/dev/null || true
    
    # 백업 파일 압축
    cd "$backup_dir"
    tar -czf "logs_$timestamp.tar.gz" "logs_$timestamp"
    rm -rf "logs_$timestamp"
    
    print_success "로그가 백업되었습니다: $backup_dir/logs_$timestamp.tar.gz"
}

# 도움말 표시
show_help() {
    echo "로그 관리 유틸리티 스크립트"
    echo ""
    echo "사용법: $0 [명령어] [옵션]"
    echo ""
    echo "명령어:"
    echo "  init      - 로그 디렉토리 및 파일 생성"
    echo "  status    - 로그 상태 확인"
    echo "  view      - 로그 파일 보기"
    echo "  follow    - 실시간 로그 추적"
    echo "  clear     - 모든 로그 파일 초기화"
    echo "  backup    - 로그 백업"
    echo "  help      - 도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 init"
    echo "  $0 status"
    echo "  $0 view fastapi"
    echo "  $0 follow streamlit"
    echo "  $0 clear"
    echo "  $0 backup"
    echo ""
}

# 메인 함수
main() {
    case "$1" in
        "init")
            create_logs_directory
            create_log_files
            ;;
        "status")
            check_logs_status
            ;;
        "view")
            view_logs "$2"
            ;;
        "follow")
            follow_logs "$2"
            ;;
        "clear")
            clear_logs
            ;;
        "backup")
            backup_logs
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            print_error "알 수 없는 명령어: $1"
            show_help
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"
