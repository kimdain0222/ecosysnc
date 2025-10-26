# 🏢 스마트 빌딩 에너지 관리 시스템 (SBEMS)

교내 건물의 전력 사용 데이터를 분석하여 공실 시 자동으로 조명/에어컨을 제어하는 시스템입니다.

## 📋 프로젝트 개요

### 목표
- 건물 전력 사용 패턴 분석
- 공실률 예측 모델 개발
- 자동 제어 로직 구현
- 에너지 절약 효과 시뮬레이션

### 주요 기능
- 📊 **데이터 분석**: 전력 사용량 시계열 분석 및 시각화
- 🤖 **예측 모델**: 공실률 및 전력 사용량 예측
- ⚡ **자동 제어**: 공실 시 최적 제어 로직
- 📈 **대시보드**: 실시간 모니터링 및 결과 시각화

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   프론트엔드    │    │   백엔드 API    │    │   ML 파이프라인 │
│   (React.js)    │◄──►│   (FastAPI)     │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   대시보드      │    │   PostgreSQL    │    │   데이터 저장소 │
│   (차트)        │    │   (데이터베이스) │    │   (CSV/JSON)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 프로젝트 구조

```
smart-building-ems/
├── 📊 data/                    # 데이터 저장소
│   ├── raw/                   # 원본 데이터
│   ├── processed/             # 전처리된 데이터
│   └── data_summary.json      # 데이터 요약 정보
├── 🔧 scripts/                # 데이터 수집 스크립트
│   └── data_collector.py      # 데이터 수집기
├── 📓 notebooks/              # Jupyter 노트북
│   └── 01_data_exploration.ipynb  # 데이터 탐색
├── 🖥️ backend/                # 백엔드 서버
│   └── app/                   # FastAPI 애플리케이션
├── 🎨 frontend/               # 프론트엔드 (React)
├── 📚 docs/                   # 문서
└── 📦 requirements.txt        # Python 패키지 목록
```

## 🚀 시작하기

### 1. 환경 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd smart-building-ems

# Python 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. 데이터 수집

```bash
# 데이터 수집 스크립트 실행
python scripts/data_collector.py
```

이 스크립트는 다음을 수행합니다:
- UCI 공개 데이터셋 다운로드 (가능한 경우)
- 가상 건물 데이터 생성
- 데이터 전처리 및 정제
- 데이터 요약 정보 생성

### 3. 데이터 분석

```bash
# Jupyter 노트북 실행
jupyter notebook notebooks/01_data_exploration.ipynb
```

노트북에서 다음을 확인할 수 있습니다:
- 데이터 기본 정보 및 통계
- 시계열 데이터 시각화
- 공실률과 전력 사용량 상관관계
- 온도/습도 분석
- 데이터 품질 검사

## 📊 데이터 설명

### 가상 건물 데이터
- **기간**: 2023년 1월 1일 ~ 12월 31일 (1년)
- **건물 수**: 5개 건물
- **데이터 포인트**: 시간별 (총 43,800개)
- **특성**:
  - `building_id`: 건물 식별자 (B001~B005)
  - `timestamp`: 시간 정보
  - `power_consumption`: 전력 사용량 (kWh)
  - `temperature`: 온도 (°C)
  - `humidity`: 습도 (%)
  - `occupancy`: 공실률 (%)
  - `floor`: 층수
  - `room_type`: 공간 유형

### 데이터 패턴
- **시간대별**: 업무시간(8-18시) 사용량 증가
- **요일별**: 평일 vs 주말 차이
- **계절별**: 여름(에어컨), 겨울(난방) 사용량 증가
- **공실률**: 업무시간 평일 80%, 주말/심야 10%

## 🛠️ 기술 스택

### Backend
- **언어**: Python 3.9+
- **프레임워크**: FastAPI
- **데이터 분석**: pandas, numpy, scikit-learn
- **머신러닝**: tensorflow/pytorch
- **데이터베이스**: PostgreSQL
- **시각화**: matplotlib, seaborn, plotly

### Frontend
- **프레임워크**: React.js
- **차트 라이브러리**: Chart.js, D3.js
- **UI 라이브러리**: Material-UI

### DevOps
- **컨테이너**: Docker
- **배포**: AWS EC2 또는 Heroku
- **버전 관리**: Git

## 📈 예상 성과

### 기술적 성과
- 데이터 정확도: 90% 이상
- 예측 모델 정확도: 85% 이상
- 시스템 응답 시간: 1초 이내

### 비즈니스 성과
- 에너지 절약 효과: 20-30% 절감 시뮬레이션
- 비용 절감: 연간 예상 절약액 계산
- ROI: 투자 대비 수익률 분석

## 🔄 개발 일정

### Phase 1: 기획 및 설계 (1-2주)
- [x] 프로젝트 요구사항 분석
- [x] 시스템 아키텍처 설계
- [x] 기술 스택 선정

### Phase 2: 데이터 및 분석 엔진 (3-4주)
- [x] 데이터 시뮬레이션 모듈 개발
- [ ] 기본 데이터 분석 및 시각화

### Phase 3: 예측 모델 개발 (5-6주)
- [ ] 공실률 예측 모델 개발
- [ ] 전력 사용량 예측 모델 개발

### Phase 4: 제어 시스템 (7-8주)
- [ ] 자동 제어 로직 구현
- [ ] 시뮬레이션 및 최적화

### Phase 5: 웹 대시보드 (9-10주)
- [ ] 백엔드 API 개발
- [ ] 프론트엔드 대시보드 개발

### Phase 6: 통합 및 배포 (11-12주)
- [ ] 시스템 통합 및 테스트
- [ ] 배포 및 문서화

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 연락처

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해주세요.

---

**참고**: 이 프로젝트는 개인 포트폴리오 목적으로 개발되었으며, 실제 하드웨어 제어는 포함되지 않습니다.
