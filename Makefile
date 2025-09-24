# =============================================================================
# Energy Management System - Makefile
# 에너지 관리 시스템 자동화 스크립트
# =============================================================================

.PHONY: help install install-dev run test clean setup venv deps

# 기본 타겟
help: ## 도움말 표시
	@echo "에너지 관리 시스템 - 사용 가능한 명령어:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 설치 관련
install: venv deps ## 전체 시스템 설치 (가상환경 + 패키지)
	@echo "✅ 설치 완료!"

install-dev: venv deps-dev ## 개발 환경 설치 (개발용 패키지 포함)
	@echo "✅ 개발 환경 설치 완료!"

venv: ## 가상환경 생성
	@echo "🔧 가상환경 생성 중..."
	@python3 -m venv venv
	@echo "✅ 가상환경 생성 완료"

deps: venv ## 기본 패키지 설치
	@echo "📦 패키지 설치 중..."
	@venv/bin/pip install --upgrade pip
	@venv/bin/pip install -r requirements.txt
	@echo "✅ 기본 패키지 설치 완료"

deps-dev: venv ## 개발용 패키지 설치
	@echo "📦 개발용 패키지 설치 중..."
	@venv/bin/pip install --upgrade pip
	@venv/bin/pip install -r requirements-dev.txt
	@echo "✅ 개발용 패키지 설치 완료"

# 실행 관련
run: ## 웹 대시보드 실행
	@echo "🚀 에너지 관리 시스템 시작 중..."
	@venv/bin/python app.py

run-iot: ## IoT 센서 시뮬레이터 실행
	@echo "📡 IoT 센서 시뮬레이터 시작 중..."
	@venv/bin/python iot_sensors/sensor_simulator.py

run-collector: ## 센서 데이터 수집기 실행
	@echo "📊 센서 데이터 수집기 시작 중..."
	@venv/bin/python iot_sensors/sensor_collector.py

# 개발 관련
test: ## 테스트 실행
	@echo "🧪 테스트 실행 중..."
	@venv/bin/pytest tests/ -v

test-cov: ## 커버리지 포함 테스트 실행
	@echo "🧪 커버리지 테스트 실행 중..."
	@venv/bin/pytest tests/ --cov=. --cov-report=html

lint: ## 코드 린팅
	@echo "🔍 코드 린팅 중..."
	@venv/bin/flake8 .
	@venv/bin/mypy .

format: ## 코드 포맷팅
	@echo "✨ 코드 포맷팅 중..."
	@venv/bin/black .
	@venv/bin/isort .

# 데이터 관련
data-prep: ## 데이터 전처리 실행
	@echo "📊 데이터 전처리 중..."
	@venv/bin/python scripts/data_preprocessor.py

data-collect: ## 데이터 수집 실행
	@echo "📥 데이터 수집 중..."
	@venv/bin/python scripts/data_collector.py

model-train: ## 머신러닝 모델 훈련
	@echo "🤖 모델 훈련 중..."
	@venv/bin/python scripts/ml_model_developer.py

# 정리 관련
clean: ## 임시 파일 정리
	@echo "🧹 임시 파일 정리 중..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .pytest_cache/
	@rm -rf htmlcov/
	@echo "✅ 정리 완료"

clean-venv: ## 가상환경 삭제
	@echo "🗑️ 가상환경 삭제 중..."
	@rm -rf venv/
	@echo "✅ 가상환경 삭제 완료"

clean-data: ## 생성된 데이터 파일 정리
	@echo "🗑️ 데이터 파일 정리 중..."
	@rm -rf data/processed/*.csv
	@rm -rf models/*.pkl
	@echo "✅ 데이터 파일 정리 완료"

# 전체 재설치
reinstall: clean-venv install ## 전체 재설치 (가상환경 삭제 후 재설치)
	@echo "✅ 재설치 완료"

# 개발 환경 전체 설정
setup: install-dev ## 개발 환경 전체 설정
	@echo "🔧 개발 환경 설정 중..."
	@venv/bin/pre-commit install
	@echo "✅ 개발 환경 설정 완료"

# Docker 관련 (선택사항)
docker-build: ## Docker 이미지 빌드
	@echo "🐳 Docker 이미지 빌드 중..."
	@docker build -t energy-management-system .

docker-run: ## Docker 컨테이너 실행
	@echo "🐳 Docker 컨테이너 실행 중..."
	@docker run -p 5000:5000 energy-management-system

# 배포 관련
deploy-check: ## 배포 전 체크
	@echo "🔍 배포 전 체크 중..."
	@venv/bin/python -m pytest tests/ -v
	@venv/bin/flake8 .
	@venv/bin/mypy .
	@echo "✅ 배포 체크 완료"

# 잔디밭 관련
grass: ## GitHub 잔디밭 커밋 생성
	@echo "🌱 GitHub 잔디밭 커밋 생성 중..."
	@venv/bin/python scripts/git_grass.py

grass-commit: ## 잔디밭 커밋 생성 후 자동 커밋
	@echo "🌱 잔디밭 커밋 생성 및 푸시 중..."
	@venv/bin/python scripts/git_grass.py
	@git add daily_activity.log
	@git commit -m "$$(venv/bin/python scripts/git_grass.py | grep '커밋 메시지:' | cut -d':' -f2- | xargs)"
	@git push

# 도움말
help-install: ## 설치 관련 도움말
	@echo "설치 관련 명령어:"
	@echo "  make install      - 기본 설치"
	@echo "  make install-dev  - 개발 환경 설치"
	@echo "  make reinstall    - 전체 재설치"
	@echo "  make clean-venv   - 가상환경 삭제"

help-run: ## 실행 관련 도움말
	@echo "실행 관련 명령어:"
	@echo "  make run          - 웹 대시보드 실행"
	@echo "  make run-iot      - IoT 센서 시뮬레이터"
	@echo "  make run-collector- 센서 데이터 수집기"

help-dev: ## 개발 관련 도움말
	@echo "개발 관련 명령어:"
	@echo "  make test         - 테스트 실행"
	@echo "  make lint         - 코드 린팅"
	@echo "  make format       - 코드 포맷팅"
	@echo "  make clean        - 임시 파일 정리"

help-grass: ## 잔디밭 관련 도움말
	@echo "잔디밭 관련 명령어:"
	@echo "  make grass        - 잔디밭 커밋 메시지 생성"
	@echo "  make grass-commit - 잔디밭 커밋 생성 후 자동 푸시"
