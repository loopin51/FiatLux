#!/bin/bash
# 스마트 물품 관리 시스템 - 시스템 헬스체크 스크립트
# ==================================================

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

# 헬스체크 결과 저장
HEALTH_SCORE=0
TOTAL_CHECKS=0

check_result() {
    local status=$1
    local service=$2
    local details=$3
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ "$status" = "ok" ]; then
        HEALTH_SCORE=$((HEALTH_SCORE + 1))
        print_success "$service: 정상"
        if [ -n "$details" ]; then
            echo "    $details"
        fi
    elif [ "$status" = "warning" ]; then
        print_warning "$service: 경고"
        if [ -n "$details" ]; then
            echo "    $details"
        fi
    else
        print_error "$service: 오류"
        if [ -n "$details" ]; then
            echo "    $details"
        fi
    fi
}

print_header "
╔══════════════════════════════════════════════════════╗
║            🏥 시스템 헬스체크                        ║
║                                                      ║
║  • 모든 서비스 상태 확인                             ║
║  • 리소스 사용량 모니터링                            ║
║  • 연결 상태 진단                                   ║
╚══════════════════════════════════════════════════════╝
"

echo ""

# 1. 시스템 기본 정보
print_header "=== 시스템 정보 ==="
echo ""
echo "🖥️ 시스템 정보:"
echo "  • 운영체제: $(uname -s)"
echo "  • 아키텍처: $(uname -m)"
echo "  • 커널: $(uname -r)"
echo "  • 날짜: $(date)"
echo "  • 업타임: $(uptime | cut -d',' -f1 | cut -d' ' -f3-)"
echo ""

# 2. 프로세스 상태 확인
print_header "=== 프로세스 상태 확인 ==="
echo ""

PID_DIR="$PROJECT_ROOT/scripts/pids"

# MCP 서버 확인
if [ -f "$PID_DIR/mcp_server.pid" ]; then
    MCP_PID=$(cat "$PID_DIR/mcp_server.pid")
    if ps -p $MCP_PID > /dev/null 2>&1; then
        CPU_USAGE=$(ps -p $MCP_PID -o %cpu --no-headers | tr -d ' ')
        MEM_USAGE=$(ps -p $MCP_PID -o %mem --no-headers | tr -d ' ')
        check_result "ok" "MCP 서버 프로세스" "PID: $MCP_PID, CPU: ${CPU_USAGE}%, MEM: ${MEM_USAGE}%"
    else
        check_result "error" "MCP 서버 프로세스" "PID 파일은 있지만 프로세스가 실행되지 않음"
    fi
else
    check_result "warning" "MCP 서버 프로세스" "PID 파일이 없음"
fi

# FastAPI 서버 확인
if [ -f "$PID_DIR/fastapi_server.pid" ]; then
    FASTAPI_PID=$(cat "$PID_DIR/fastapi_server.pid")
    if ps -p $FASTAPI_PID > /dev/null 2>&1; then
        CPU_USAGE=$(ps -p $FASTAPI_PID -o %cpu --no-headers | tr -d ' ')
        MEM_USAGE=$(ps -p $FASTAPI_PID -o %mem --no-headers | tr -d ' ')
        check_result "ok" "FastAPI 서버 프로세스" "PID: $FASTAPI_PID, CPU: ${CPU_USAGE}%, MEM: ${MEM_USAGE}%"
    else
        check_result "error" "FastAPI 서버 프로세스" "PID 파일은 있지만 프로세스가 실행되지 않음"
    fi
else
    check_result "warning" "FastAPI 서버 프로세스" "PID 파일이 없음"
fi

# Streamlit 클라이언트 확인
if [ -f "$PID_DIR/streamlit_client.pid" ]; then
    STREAMLIT_PID=$(cat "$PID_DIR/streamlit_client.pid")
    if ps -p $STREAMLIT_PID > /dev/null 2>&1; then
        CPU_USAGE=$(ps -p $STREAMLIT_PID -o %cpu --no-headers | tr -d ' ')
        MEM_USAGE=$(ps -p $STREAMLIT_PID -o %mem --no-headers | tr -d ' ')
        check_result "ok" "Streamlit 클라이언트 프로세스" "PID: $STREAMLIT_PID, CPU: ${CPU_USAGE}%, MEM: ${MEM_USAGE}%"
    else
        check_result "error" "Streamlit 클라이언트 프로세스" "PID 파일은 있지만 프로세스가 실행되지 않음"
    fi
else
    check_result "warning" "Streamlit 클라이언트 프로세스" "PID 파일이 없음"
fi

# Next.js 서버 확인
if [ -f "$PID_DIR/nextjs_server.pid" ]; then
    NEXTJS_PID=$(cat "$PID_DIR/nextjs_server.pid")
    if ps -p $NEXTJS_PID > /dev/null 2>&1; then
        CPU_USAGE=$(ps -p $NEXTJS_PID -o %cpu --no-headers | tr -d ' ')
        MEM_USAGE=$(ps -p $NEXTJS_PID -o %mem --no-headers | tr -d ' ')
        check_result "ok" "Next.js 서버 프로세스" "PID: $NEXTJS_PID, CPU: ${CPU_USAGE}%, MEM: ${MEM_USAGE}%"
    else
        check_result "error" "Next.js 서버 프로세스" "PID 파일은 있지만 프로세스가 실행되지 않음"
    fi
else
    check_result "warning" "Next.js 서버 프로세스" "PID 파일이 없음"
fi

echo ""

# 3. 네트워크 연결 확인
print_header "=== 네트워크 연결 확인 ==="
echo ""

if command -v curl &> /dev/null; then
    # FastAPI 서버 확인
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health | grep -q "200"; then
        RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" http://localhost:8001/health)
        check_result "ok" "FastAPI 서버 연결" "응답 시간: ${RESPONSE_TIME}초"
    else
        check_result "error" "FastAPI 서버 연결" "서버가 응답하지 않음"
    fi
    
    # Next.js 서버 확인
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
        RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" http://localhost:3000)
        check_result "ok" "Next.js 서버 연결" "응답 시간: ${RESPONSE_TIME}초"
    else
        check_result "error" "Next.js 서버 연결" "서버가 응답하지 않음"
    fi
    
    # Streamlit 앱 확인
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200"; then
        RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" http://localhost:8501)
        check_result "ok" "Streamlit 앱 연결" "응답 시간: ${RESPONSE_TIME}초"
    else
        check_result "error" "Streamlit 앱 연결" "앱이 응답하지 않음"
    fi
else
    check_result "warning" "네트워크 연결 확인" "curl이 설치되지 않음"
fi

echo ""

# 4. 포트 상태 확인
print_header "=== 포트 상태 확인 ==="
echo ""

if command -v netstat &> /dev/null; then
    # 포트 3000 확인
    if netstat -tlnp 2>/dev/null | grep -q ":3000 "; then
        check_result "ok" "포트 3000 (Next.js)" "포트가 리스닝 중"
    else
        check_result "error" "포트 3000 (Next.js)" "포트가 리스닝하지 않음"
    fi
    
    # 포트 8001 확인
    if netstat -tlnp 2>/dev/null | grep -q ":8001 "; then
        check_result "ok" "포트 8001 (FastAPI)" "포트가 리스닝 중"
    else
        check_result "error" "포트 8001 (FastAPI)" "포트가 리스닝하지 않음"
    fi
    
    # 포트 8501 확인
    if netstat -tlnp 2>/dev/null | grep -q ":8501 "; then
        check_result "ok" "포트 8501 (Streamlit)" "포트가 리스닝 중"
    else
        check_result "error" "포트 8501 (Streamlit)" "포트가 리스닝하지 않음"
    fi
elif command -v lsof &> /dev/null; then
    # 포트 3000 확인
    if lsof -i :3000 > /dev/null 2>&1; then
        check_result "ok" "포트 3000 (Next.js)" "포트가 리스닝 중"
    else
        check_result "error" "포트 3000 (Next.js)" "포트가 리스닝하지 않음"
    fi
    
    # 포트 8001 확인
    if lsof -i :8001 > /dev/null 2>&1; then
        check_result "ok" "포트 8001 (FastAPI)" "포트가 리스닝 중"
    else
        check_result "error" "포트 8001 (FastAPI)" "포트가 리스닝하지 않음"
    fi
    
    # 포트 8501 확인
    if lsof -i :8501 > /dev/null 2>&1; then
        check_result "ok" "포트 8501 (Streamlit)" "포트가 리스닝 중"
    else
        check_result "error" "포트 8501 (Streamlit)" "포트가 리스닝하지 않음"
    fi
else
    check_result "warning" "포트 상태 확인" "netstat 또는 lsof가 설치되지 않음"
fi

echo ""

# 5. 파일 시스템 확인
print_header "=== 파일 시스템 확인 ==="
echo ""

# 데이터베이스 파일 확인
if [ -f "$PROJECT_ROOT/items.db" ]; then
    DB_SIZE=$(du -h "$PROJECT_ROOT/items.db" | cut -f1)
    check_result "ok" "데이터베이스 파일" "크기: $DB_SIZE"
else
    check_result "error" "데이터베이스 파일" "items.db 파일이 없음"
fi

# 가상환경 확인
if [ -d "$PROJECT_ROOT/venv" ]; then
    VENV_SIZE=$(du -sh "$PROJECT_ROOT/venv" | cut -f1)
    check_result "ok" "Python 가상환경" "크기: $VENV_SIZE"
else
    check_result "error" "Python 가상환경" "venv 디렉토리가 없음"
fi

# Next.js 빌드 확인
if [ -d "$PROJECT_ROOT/frontend/nextjs-inventory/.next" ]; then
    NEXT_SIZE=$(du -sh "$PROJECT_ROOT/frontend/nextjs-inventory/.next" | cut -f1)
    check_result "ok" "Next.js 빌드" "크기: $NEXT_SIZE"
else
    check_result "warning" "Next.js 빌드" ".next 디렉토리가 없음 (빌드 필요)"
fi

# 로그 디렉토리 확인
if [ -d "$PROJECT_ROOT/logs" ]; then
    LOG_COUNT=$(find "$PROJECT_ROOT/logs" -name "*.log" | wc -l)
    check_result "ok" "로그 디렉토리" "로그 파일 수: $LOG_COUNT"
else
    check_result "warning" "로그 디렉토리" "logs 디렉토리가 없음"
fi

echo ""

# 6. 디스크 사용량 확인
print_header "=== 리소스 사용량 확인 ==="
echo ""

# 디스크 사용량
DISK_USAGE=$(df -h "$PROJECT_ROOT" | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USAGE" -lt 80 ]; then
    check_result "ok" "디스크 사용량" "${DISK_USAGE}% 사용 중"
elif [ "$DISK_USAGE" -lt 90 ]; then
    check_result "warning" "디스크 사용량" "${DISK_USAGE}% 사용 중 (주의 필요)"
else
    check_result "error" "디스크 사용량" "${DISK_USAGE}% 사용 중 (위험)"
fi

# 메모리 사용량
if command -v free &> /dev/null; then
    MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
    if [ "$(echo "$MEM_USAGE < 80" | bc -l 2>/dev/null || echo "0")" -eq 1 ]; then
        check_result "ok" "메모리 사용량" "${MEM_USAGE}% 사용 중"
    elif [ "$(echo "$MEM_USAGE < 90" | bc -l 2>/dev/null || echo "0")" -eq 1 ]; then
        check_result "warning" "메모리 사용량" "${MEM_USAGE}% 사용 중 (주의 필요)"
    else
        check_result "error" "메모리 사용량" "${MEM_USAGE}% 사용 중 (위험)"
    fi
else
    check_result "warning" "메모리 사용량" "free 명령어가 없음"
fi

echo ""

# 7. 로그 파일 분석
print_header "=== 로그 파일 분석 ==="
echo ""

if [ -d "$PROJECT_ROOT/logs" ]; then
    # 최근 오류 확인
    ERROR_COUNT=$(find "$PROJECT_ROOT/logs" -name "*.log" -exec grep -i "error\|exception\|fail" {} \; 2>/dev/null | wc -l)
    if [ "$ERROR_COUNT" -eq 0 ]; then
        check_result "ok" "로그 오류" "최근 오류 없음"
    elif [ "$ERROR_COUNT" -lt 5 ]; then
        check_result "warning" "로그 오류" "최근 오류 ${ERROR_COUNT}건 발견"
    else
        check_result "error" "로그 오류" "최근 오류 ${ERROR_COUNT}건 발견 (확인 필요)"
    fi
    
    # 로그 파일 크기 확인
    LARGE_LOGS=$(find "$PROJECT_ROOT/logs" -name "*.log" -size +100M | wc -l)
    if [ "$LARGE_LOGS" -eq 0 ]; then
        check_result "ok" "로그 파일 크기" "모든 로그 파일 크기 정상"
    else
        check_result "warning" "로그 파일 크기" "${LARGE_LOGS}개의 대용량 로그 파일 발견"
    fi
else
    check_result "warning" "로그 파일 분석" "logs 디렉토리가 없음"
fi

echo ""

# 8. 헬스체크 결과 요약
print_header "=== 헬스체크 결과 요약 ==="
echo ""

HEALTH_PERCENTAGE=$((HEALTH_SCORE * 100 / TOTAL_CHECKS))

echo "📊 헬스체크 결과:"
echo "  • 총 체크 항목: $TOTAL_CHECKS"
echo "  • 정상 항목: $HEALTH_SCORE"
echo "  • 시스템 건강도: $HEALTH_PERCENTAGE%"
echo ""

if [ "$HEALTH_PERCENTAGE" -ge 90 ]; then
    print_success "🎉 시스템 상태가 매우 양호합니다!"
elif [ "$HEALTH_PERCENTAGE" -ge 70 ]; then
    print_warning "⚠️ 시스템 상태가 양호하지만 일부 주의가 필요합니다."
else
    print_error "🚨 시스템 상태가 좋지 않습니다. 확인이 필요합니다."
fi

echo ""

# 9. 권장 사항
print_header "=== 권장 사항 ==="
echo ""

if [ "$HEALTH_PERCENTAGE" -lt 100 ]; then
    echo "🔧 다음 사항을 확인해보세요:"
    echo "  • 실행되지 않은 서비스가 있다면 재시작해보세요"
    echo "  • 로그 파일에서 오류 메시지를 확인해보세요"
    echo "  • 시스템 리소스가 부족한지 확인해보세요"
    echo "  • 필요하다면 서비스를 재시작해보세요"
    echo ""
    echo "명령어:"
    echo "  • 서비스 재시작: ./scripts/stop_all.sh && ./scripts/start_all.sh"
    echo "  • 로그 확인: tail -f logs/[서비스명].log"
    echo "  • 시스템 정리: ./scripts/cleanup.sh"
else
    echo "✅ 시스템이 정상적으로 작동하고 있습니다."
fi

echo ""

# 10. 실시간 모니터링 정보
print_header "=== 실시간 모니터링 ==="
echo ""
echo "🔍 지속적인 모니터링을 위해 다음 명령어를 사용하세요:"
echo "  • 실시간 로그 확인: tail -f logs/*.log"
echo "  • 프로세스 모니터링: watch -n 5 'ps aux | grep -E \"node|python|uvicorn|streamlit\"'"
echo "  • 포트 상태 확인: watch -n 5 'netstat -tlnp | grep -E \":300[01]|:850[01]\"'"
echo "  • 시스템 리소스: top 또는 htop"
echo ""

print_status "헬스체크가 완료되었습니다."
