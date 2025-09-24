#!/bin/bash

# 에너지 관리 시스템 실행 스크립트 (Linux/macOS)

echo "========================================"
echo "에너지 관리 시스템 시작"
echo "========================================"
echo

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 가상환경이 없습니다. 먼저 install.sh을 실행하세요.${NC}"
    exit 1
fi

# 가상환경 활성화
echo -e "${BLUE}가상환경 활성화 중...${NC}"
source venv/bin/activate

# 앱 실행
echo -e "${BLUE}에너지 관리 시스템 시작 중...${NC}"
echo -e "${YELLOW}웹 브라우저에서 http://localhost:5000 으로 접속하세요.${NC}"
echo

python app.py
