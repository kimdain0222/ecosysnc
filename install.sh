#!/bin/bash

# 에너지 관리 시스템 설치 스크립트 (Linux/macOS)

echo "========================================"
echo "에너지 관리 시스템 설치 스크립트"
echo "========================================"
echo

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되어 있지 않습니다.${NC}"
    echo "다음 명령어로 Python3를 설치하세요:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python3"
    exit 1
fi

echo -e "${GREEN}✅ Python3가 설치되어 있습니다.${NC}"
python3 --version
echo

# 가상환경 생성
echo -e "${BLUE}가상환경 생성 중...${NC}"
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 가상환경 생성 실패${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"
echo

# 가상환경 활성화
echo -e "${BLUE}가상환경 활성화 중...${NC}"
source venv/bin/activate

# pip 업그레이드
echo -e "${BLUE}pip 업그레이드 중...${NC}"
python -m pip install --upgrade pip

# 패키지 설치
echo -e "${BLUE}패키지 설치 중...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 패키지 설치 실패${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 패키지 설치 완료${NC}"
echo

# 실행 스크립트 생성
echo -e "${BLUE}실행 스크립트 생성 중...${NC}"
cat > run.sh << 'EOF'
#!/bin/bash
echo "에너지 관리 시스템 시작 중..."
source venv/bin/activate
python app.py
EOF

chmod +x run.sh

# 활성화 스크립트 생성
cat > activate.sh << 'EOF'
#!/bin/bash
echo "에너지 관리 시스템 가상환경 활성화 중..."
source venv/bin/activate
echo ""
echo "✅ 가상환경이 활성화되었습니다!"
echo "대시보드 실행: python app.py"
echo ""
EOF

chmod +x activate.sh

echo -e "${GREEN}✅ 설치 완료!${NC}"
echo
echo -e "${YELLOW}🎉 에너지 관리 시스템이 성공적으로 설치되었습니다!${NC}"
echo
echo -e "${BLUE}실행 방법:${NC}"
echo "1. ./run.sh 실행"
echo "2. 또는 수동으로: source venv/bin/activate && python app.py"
echo
echo -e "${BLUE}가상환경 활성화:${NC}"
echo "source activate.sh"
echo
