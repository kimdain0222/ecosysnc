# 🏢 스마트 빌딩 에너지 관리 시스템

AI 기반의 스마트 빌딩 에너지 관리 시스템으로, 건물의 전력 사용 패턴을 분석하고 공실률을 예측하여 에너지를 절약합니다.

## ✨ 주요 기능

- 📊 **실시간 모니터링**: 건물별 전력 사용량 및 환경 데이터 시각화
- 🤖 **AI 예측**: 머신러닝을 통한 공실률 및 전력 사용량 예측
- ⚡ **자동 제어**: 공실 시 최적 제어 로직으로 에너지 절약
- 📈 **웹 대시보드**: 직관적인 인터페이스로 데이터 분석 및 제어
- 🔌 **IoT 연동**: 센서 데이터 실시간 수집 및 분석

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   웹 대시보드    │    │   Flask API     │    │   ML 파이프라인 │
│   (HTML/CSS)    │◄──►│   (Python)      │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   IoT 센서      │    │   PostgreSQL    │    │   InfluxDB      │
│   (실시간 데이터) │    │   (메인 DB)     │    │   (시계열 DB)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis         │    │   Docker        │    │   모니터링      │
│   (캐시/세션)    │    │   (컨테이너)     │    │   (Grafana)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 프로젝트 구조

```
energy_sys/
├── 📊 data/                    # 데이터 저장소
├── 🔧 scripts/                # 데이터 처리 스크립트
├── 📓 notebooks/              # Jupyter 노트북
├── 🖥️ backend/                # 백엔드 API
├── 🎨 frontend/               # 프론트엔드
├── 🔌 iot_sensors/            # IoT 센서 연동
├── 🤖 models/                 # 훈련된 ML 모델
├── 📱 templates/              # 웹 템플릿
├── 🐳 docker-compose.yml      # Docker 컨테이너 설정
├── 🗄️ database/               # 데이터베이스 초기화 스크립트
├── ⚙️ config/                 # 설정 파일
├── 📦 requirements.txt        # 패키지 목록
├── 🚀 install.py              # 자동 설치 스크립트
└── 📚 INSTALL.md              # 상세 설치 가이드
```

## 🚀 시작하기

### 🎯 빠른 설치 (추천)

#### 자동 설치 스크립트 사용
```bash
# 프로젝트 클론
git clone <repository-url>
cd energy_sys

# 자동 설치 (Python 3.8+ 필요)
python install.py
```

#### 운영체제별 설치 스크립트
```bash
# Windows
install.bat

# macOS/Linux
chmod +x install.sh
./install.sh
```

#### Makefile 사용 (Linux/macOS)
```bash
make install        # 기본 설치
make install-dev    # 개발 환경 설치
make run           # 실행
```

### 🔧 수동 설치

#### 1. 환경 설정
```bash
# 프로젝트 클론
git clone <repository-url>
cd energy_sys

# Python 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필요한 패키지 설치
pip install -r requirements.txt
```

#### 2. 개발 환경 설치 (선택사항)
```bash
# 개발용 패키지 포함 설치
pip install -r requirements-dev.txt

# 또는 setup.py 사용
pip install -e ".[dev]"
```

### 📚 상세 설치 가이드
자세한 설치 방법과 문제 해결은 [INSTALL.md](INSTALL.md)를 참조하세요.

### 3. Docker 설치 및 데이터베이스 시작

#### Docker Desktop 설치
```bash
# Windows: DOCKER_SETUP.md 참조
# macOS: Docker Desktop 다운로드
# Linux: docker 설치
```

#### 데이터베이스 시작
```bash
# 1단계: 기본 데이터베이스 (PostgreSQL, InfluxDB, Redis)
python scripts/start_databases.py start stage1

# 2단계: 전체 스택 (Elasticsearch, MinIO 포함)
python scripts/start_databases.py start stage2

# 또는 Docker Compose 직접 사용
docker-compose up -d postgres influxdb redis
```

#### 데이터베이스 연결 테스트
```bash
# 모든 데이터베이스 연결 상태 확인
python scripts/test_database_connection.py
```

### 4. 실행

```bash
# 웹 대시보드 실행
python app.py

# 또는 실행 스크립트 사용
# Windows: run.bat
# macOS/Linux: ./run.sh
```

웹 브라우저에서 `http://localhost:5000`으로 접속하여 대시보드를 확인하세요.

## 🗄️ 데이터베이스 시스템

### 1단계: MVP (현재 실행 중)
- **PostgreSQL** (포트 5432): 메인 비즈니스 데이터
  - 사용자 정보, 건물 정보, 세입자 정보
  - 에너지 사용량 기록, 시스템 설정
- **InfluxDB** (포트 8086): 시계열 센서 데이터
  - IoT 센서 측정값, 실시간 모니터링
  - 시간 기반 데이터 분석
- **Redis** (포트 6379): 캐시 및 세션
  - 사용자 로그인 세션, 자주 사용되는 데이터 캐시

### 2단계: 성장 (필요시 활성화)
- **Elasticsearch** (포트 9200): 검색 및 분석
- **MinIO** (포트 9000): 파일 저장소
- **Prometheus + Grafana**: 시스템 모니터링

### 데이터베이스 관리 도구
- **pgAdmin** (포트 5050): PostgreSQL 관리
- **InfluxDB UI** (포트 8086): 시계열 데이터 관리
- **Grafana** (포트 3000): 대시보드 및 모니터링

## 📊 데이터 및 모델

### 데이터
- **건물 데이터**: 5개 건물, 1년간 시간별 데이터
- **특성**: 전력 사용량, 온도, 습도, 공실률, 층수, 공간 유형
- **패턴**: 업무시간/주말, 계절별 사용량 차이 분석

### AI 모델
- **XGBoost**: 최고 성능 예측 모델
- **다양한 알고리즘**: Random Forest, LightGBM, SVM 등
- **정확도**: 공실률 예측 85% 이상

## 🛠️ 기술 스택

- **Backend**: Python, Flask, FastAPI
- **ML/AI**: scikit-learn, XGBoost, TensorFlow
- **데이터베이스**: PostgreSQL, InfluxDB, Redis
- **컨테이너**: Docker, Docker Compose
- **데이터**: pandas, numpy, matplotlib, plotly
- **IoT**: MQTT, 센서 데이터 수집
- **웹**: HTML, CSS, JavaScript, Bootstrap
- **모니터링**: Prometheus, Grafana

## 📈 성과

- **예측 정확도**: 85% 이상
- **에너지 절약**: 20-30% 절감 시뮬레이션
- **실시간 모니터링**: 1초 이내 응답
- **확장성**: Docker 기반으로 무한 확장 가능

## 🌱 GitHub 잔디밭

이 프로젝트는 GitHub Actions를 통해 자동으로 잔디밭을 생성합니다:

- **매일 자동 커밋**: 다양한 개발 활동 시뮬레이션
- **주말 활동**: 주말 사이드 프로젝트 및 학습 활동
- **랜덤 커밋**: 주중 추가 개발 활동

### 로컬에서 잔디밭 생성
```bash
# Windows
grass.bat

# macOS/Linux
./grass.sh

# 또는 Makefile 사용
make grass
```

## 🤝 기여하기

1. 프로젝트 Fork
2. 기능 브랜치 생성 (`git checkout -b feature/새기능`)
3. 변경사항 커밋 (`git commit -m '새 기능 추가'`)
4. 브랜치에 푸시 (`git push origin feature/새기능`)
5. Pull Request 생성

## 📝 라이선스

MIT 라이선스 하에 배포됩니다.

---

**💡 팁**: 설치나 사용 중 문제가 있으면 [INSTALL.md](INSTALL.md)의 문제 해결 섹션을 참조하세요.
