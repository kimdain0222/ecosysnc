# 에너지 관리 시스템 설치 가이드

이 문서는 에너지 관리 시스템을 설치하고 실행하는 방법을 설명합니다.

## 📋 시스템 요구사항

### 필수 요구사항
- **Python**: 3.8 이상 (권장: 3.9+)
- **메모리**: 최소 4GB RAM (권장: 8GB+)
- **디스크**: 최소 2GB 여유 공간
- **운영체제**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

### 선택적 요구사항
- **GPU**: CUDA 지원 GPU (TensorFlow GPU 가속용)
- **데이터베이스**: PostgreSQL (대용량 데이터용)

## 🚀 빠른 설치 (자동)

가장 쉬운 방법은 자동 설치 스크립트를 사용하는 것입니다:

### Windows
```bash
python install.py
```

### macOS/Linux
```bash
python3 install.py
```

자동 설치 스크립트가 다음을 수행합니다:
- Python 버전 확인
- 가상환경 생성
- 모든 패키지 설치
- 실행 스크립트 생성
- 설치 검증

## 🔧 수동 설치

### 1. 저장소 클론
```bash
git clone https://github.com/your-org/energy-management-system.git
cd energy-management-system
```

### 2. Python 가상환경 생성
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치

#### 방법 1: requirements.txt 사용
```bash
pip install -r requirements.txt
```

#### 방법 2: setup.py 사용 (개발 모드)
```bash
pip install -e .
```

#### 방법 3: 개발용 추가 패키지 포함
```bash
pip install -e ".[dev]"
```

### 4. 설치 검증
```bash
python -c "import pandas, numpy, sklearn, flask; print('설치 성공!')"
```

## 🎯 실행 방법

### 자동 실행 스크립트 사용
```bash
# Windows
run.bat

# macOS/Linux
./run.sh
```

### 수동 실행
```bash
# 가상환경 활성화
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 대시보드 실행
python app.py
```

## 📦 주요 패키지 목록

### 데이터 분석 및 처리
- `pandas==2.1.4` - 데이터 조작 및 분석
- `numpy==1.24.3` - 수치 계산
- `scipy==1.11.4` - 과학 계산

### 머신러닝
- `scikit-learn==1.3.2` - 머신러닝 라이브러리
- `tensorflow==2.15.0` - 딥러닝 프레임워크
- `keras==2.15.0` - 고수준 딥러닝 API

### 데이터 시각화
- `matplotlib==3.8.2` - 기본 플롯팅
- `seaborn==0.13.0` - 통계 시각화
- `plotly==5.17.0` - 인터랙티브 시각화

### 웹 프레임워크
- `Flask==3.0.0` - 웹 애플리케이션
- `gunicorn==21.2.0` - WSGI 서버
- `fastapi==0.104.1` - 고성능 API

### 데이터베이스
- `sqlalchemy==2.0.23` - ORM
- `psycopg2-binary==2.9.9` - PostgreSQL 어댑터

### IoT 및 통신
- `paho-mqtt==2.1.0` - MQTT 클라이언트

## 🛠️ 개발 환경 설정

### 개발용 패키지 설치
```bash
pip install -e ".[dev]"
```

### 코드 포맷팅
```bash
black .
flake8 .
mypy .
```

### 테스트 실행
```bash
pytest
```

## 🔍 문제 해결

### 일반적인 문제들

#### 1. Python 버전 오류
```
❌ Python 3.8 이상이 필요합니다!
```
**해결방법**: [Python 공식 사이트](https://www.python.org/downloads/)에서 최신 버전을 다운로드하세요.

#### 2. pip 설치 오류
```
❌ pip가 설치되어 있지 않습니다.
```
**해결방법**: 
```bash
# Windows
python -m ensurepip --upgrade

# macOS/Linux
python3 -m ensurepip --upgrade
```

#### 3. 패키지 설치 실패
```
❌ 패키지 설치 실패
```
**해결방법**:
1. 인터넷 연결 확인
2. pip 업그레이드: `pip install --upgrade pip`
3. 캐시 클리어: `pip cache purge`
4. 개별 패키지 설치 시도

#### 4. TensorFlow 설치 문제
```
❌ tensorflow 설치 실패
```
**해결방법**:
```bash
# CPU 버전만 설치
pip install tensorflow-cpu

# 또는 특정 버전
pip install tensorflow==2.15.0
```

#### 5. 가상환경 활성화 실패
**Windows**:
```bash
# PowerShell 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux**:
```bash
# 실행 권한 부여
chmod +x activate.sh
chmod +x run.sh
```

### 로그 확인
설치 과정에서 문제가 발생하면 다음 로그를 확인하세요:
- `venv/install.log` - 패키지 설치 로그
- `sensor_data/sensor_collector.log` - 센서 데이터 로그

## 🌐 웹 대시보드 접속

설치 완료 후 웹 브라우저에서 다음 주소로 접속하세요:
- **로컬**: http://localhost:5000
- **네트워크**: http://[서버IP]:5000

## 📱 IoT 센서 설정

### 센서 시뮬레이터 실행
```bash
python iot_sensors/sensor_simulator.py
```

### 실제 센서 연결
1. `iot_sensors/config/sensor_config.json` 파일 수정
2. 센서 데이터 수집기 실행:
```bash
python iot_sensors/sensor_collector.py
```

## 🔄 업데이트

### 프로젝트 업데이트
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### 개별 패키지 업데이트
```bash
pip install --upgrade [패키지명]
```

## 📞 지원

문제가 지속되면 다음을 확인하세요:
1. [Issues](https://github.com/your-org/energy-management-system/issues) 페이지
2. [Wiki](https://github.com/your-org/energy-management-system/wiki) 문서
3. 팀 슬랙 채널: #energy-system-support

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

**설치에 성공하셨나요?** 🎉
이제 [README.md](README.md)를 확인하여 시스템 사용법을 알아보세요!
