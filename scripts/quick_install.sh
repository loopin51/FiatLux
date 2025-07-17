#!/bin/bash

# =============================================================================
# 스마트 물품 관리 시스템 - 빠른 설치 스크립트
# =============================================================================
# 최소한의 확인으로 빠르게 설치하는 스크립트입니다.
# 자세한 설치는 scripts/install.sh를 사용하세요.
# =============================================================================

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 스마트 물품 관리 시스템 빠른 설치${NC}"
echo "=================================="

# Python 의존성 설치
echo -e "\n${YELLOW}📦 Python 의존성 설치 중...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install fastapi uvicorn streamlit fastmcp google-generativeai pydantic requests python-dotenv
fi

# Node.js 의존성 설치
echo -e "\n${YELLOW}📦 Node.js 의존성 설치 중...${NC}"
if [ -d "frontend/nextjs-inventory" ]; then
    cd frontend/nextjs-inventory
    npm install
    cd ../..
fi

# 환경 변수 설정
echo -e "\n${YELLOW}⚙️ 환경 변수 설정...${NC}"
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo -e "${RED}⚠️ .env 파일에서 GOOGLE_API_KEY를 설정하세요!${NC}"
fi

# 데이터베이스 초기화
echo -e "\n${YELLOW}🗄️ 데이터베이스 초기화...${NC}"
if [ ! -f "items.db" ]; then
    python3 backend/database/database.py
fi

echo -e "\n${GREEN}✅ 빠른 설치 완료!${NC}"
echo -e "${YELLOW}다음 명령으로 시스템을 시작하세요:${NC}"
echo "./scripts/start_system.sh"
