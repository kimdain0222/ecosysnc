#!/bin/bash

# GitHub 잔디밭 자동 생성 스크립트 (Linux/macOS)

echo "========================================"
echo "GitHub 잔디밭 자동 생성 스크립트"
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

# 잔디밭 스크립트 실행
echo -e "${BLUE}🌱 잔디밭 커밋 생성 중...${NC}"
python scripts/git_grass.py

echo
echo -e "${YELLOW}📝 다음 명령어로 커밋하세요:${NC}"
echo "git add daily_activity.log"
echo "git commit -m \"커밋 메시지\""
echo "git push"
echo
