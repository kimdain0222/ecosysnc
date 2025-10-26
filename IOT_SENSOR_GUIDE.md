# IoT 센서 연동 가이드

## 📋 개요

스마트 빌딩 에너지 관리 시스템(SBEMS)의 IoT 센서 연동 기능은 실시간 센서 데이터 수집, 모니터링, 분석 및 예측을 제공합니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   IoT 센서들    │    │   MQTT 브로커   │    │  데이터 수집기  │
│                 │───▶│                 │───▶│                 │
│ • 온도 센서     │    │ • Mosquitto     │    │ • SensorCollector│
│ • 습도 센서     │    │ • RabbitMQ      │    │ • 실시간 처리    │
│ • 인원 센서     │    │ • HiveMQ        │    │ • 임계값 검사    │
│ • 전력 센서     │    │                 │    │ • 알림 생성      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   웹 대시보드   │◀───│   Flask API     │◀───│  SQLite DB      │
│                 │    │                 │    │                 │
│ • 실시간 모니터링│    │ • RESTful API   │    │ • 센서 읽기     │
│ • 차트 & 그래프 │    │ • 데이터 조회   │    │ • 센서 상태     │
│ • 알림 관리     │    │ • 예측 API      │    │ • 알림 기록     │
│ • 센서 제어     │    │ • 실시간 업데이트│    │ • 예측 결과     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 설치 및 설정

### 1. 필요한 패키지 설치

```bash
pip install paho-mqtt requests flask sqlite3
```

### 2. MQTT 브로커 설정 (선택사항)

실제 IoT 센서를 사용하는 경우 MQTT 브로커가 필요합니다:

#### Mosquitto 설치 (Windows)
```bash
# Chocolatey 사용
choco install mosquitto

# 또는 수동 설치
# https://mosquitto.org/download/
```

#### Mosquitto 설정 파일 (mosquitto.conf)
```conf
# 기본 포트
port 1883

# 사용자 인증
allow_anonymous false
password_file mosquitto_passwd

# 로그 설정
log_type all
log_timestamp true
```

### 3. 센서 설정 파일 확인

`iot_sensors/config/sensor_config.json` 파일을 확인하고 필요에 따라 수정:

```json
{
  "sensors": {
    "temperature_sensors": [
      {
        "id": "temp_001",
        "name": "1층 로비 온도센서",
        "building_id": "B001",
        "floor": 1,
        "room_type": "lobby",
        "mqtt_topic": "building/B001/floor1/lobby/temperature",
        "http_endpoint": "http://sensor-gateway:8080/api/sensors/temp_001",
        "update_interval": 60,
        "unit": "celsius",
        "thresholds": {
          "min": 15,
          "max": 30,
          "critical_min": 10,
          "critical_max": 35
        }
      }
    ]
  }
}
```

## 🚀 실행 방법

### 1. 센서 시뮬레이터 실행 (테스트용)

```bash
# 새 터미널에서 실행
python iot_sensors/sensor_simulator.py
```

### 2. 센서 데이터 수집기 실행 (실제 센서용)

```bash
# 새 터미널에서 실행
python iot_sensors/sensor_collector.py
```

### 3. 웹 대시보드 실행

```bash
# 새 터미널에서 실행
python app.py
```

### 4. 웹 브라우저에서 접속

```
http://localhost:5000/iot-monitoring
```

## 📊 주요 기능

### 1. 실시간 센서 모니터링

- **센서 상태 카드**: 온라인 센서 수, 총 센서 수, 활성 알림, 마지막 업데이트
- **실시간 차트**: 센서 타입별 실시간 데이터 시각화
- **센서 상태 목록**: 개별 센서의 상태 및 최신 값 표시

### 2. 센서 데이터 관리

- **센서 목록**: 모든 센서의 상세 정보 및 최신 데이터
- **센서 상세 정보**: 개별 센서의 24시간 데이터 추이
- **데이터 필터링**: 센서 ID, 타입, 시간 범위별 필터링

### 3. 알림 시스템

- **임계값 기반 알림**: 설정된 임계값을 초과/미달 시 자동 알림
- **알림 심각도**: Critical, Warning 레벨 구분
- **알림 관리**: 해결된 알림 표시 및 관리

### 4. 실시간 예측

- **전력 소비 예측**: ML 모델을 활용한 실시간 전력 소비 예측
- **예측 신뢰도**: 예측 결과의 신뢰도 표시
- **예측 히스토리**: 과거 예측 결과 조회

## 🔌 API 엔드포인트

### 센서 관련 API

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/iot/sensors` | GET | 센서 목록 조회 |
| `/api/iot/readings` | GET | 센서 읽기 데이터 조회 |
| `/api/iot/status` | GET | 센서 상태 조회 |
| `/api/iot/alerts` | GET | 알림 목록 조회 |
| `/api/iot/predictions` | GET | 예측 데이터 조회 |
| `/api/iot/dashboard` | GET | 대시보드 통합 데이터 |

### 쿼리 파라미터

- `sensor_id`: 특정 센서 ID
- `sensor_type`: 센서 타입 (temperature, humidity, occupancy, power)
- `hours`: 조회할 시간 범위 (기본값: 24)
- `severity`: 알림 심각도 (critical, warning)
- `resolved`: 해결된 알림 여부 (true/false)

### 응답 예시

```json
{
  "readings": [
    {
      "sensor_id": "temp_001",
      "sensor_type": "temperature",
      "value": 23.5,
      "unit": "celsius",
      "timestamp": "2024-01-15T10:30:00",
      "building_id": "B001",
      "floor": 1,
      "room_type": "lobby",
      "status": "normal",
      "confidence": 0.98
    }
  ],
  "count": 1,
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🔧 센서 추가 방법

### 1. 설정 파일에 센서 추가

`iot_sensors/config/sensor_config.json`에 새 센서 정보 추가:

```json
{
  "sensors": {
    "temperature_sensors": [
      {
        "id": "temp_new",
        "name": "새 온도센서",
        "building_id": "B001",
        "floor": 4,
        "room_type": "conference",
        "mqtt_topic": "building/B001/floor4/conference/temperature",
        "http_endpoint": "http://sensor-gateway:8080/api/sensors/temp_new",
        "update_interval": 60,
        "unit": "celsius",
        "thresholds": {
          "min": 18,
          "max": 26,
          "critical_min": 15,
          "critical_max": 30
        }
      }
    ]
  }
}
```

### 2. MQTT 토픽 구독

센서 데이터 수집기가 자동으로 새 토픽을 구독합니다:

```
building/+/+/+/temperature
building/+/+/+/humidity
building/+/+/+/occupancy
building/+/+/+/power
```

### 3. HTTP 엔드포인트 추가 (선택사항)

센서 게이트웨이에 HTTP 엔드포인트 추가:

```python
@app.route('/api/sensors/<sensor_id>', methods=['GET'])
def get_sensor_data(sensor_id):
    # 센서 데이터 반환 로직
    return jsonify({
        "value": 23.5,
        "unit": "celsius",
        "timestamp": datetime.now().isoformat(),
        "status": "normal",
        "confidence": 0.98
    })
```

## 🛠️ 문제 해결

### 1. MQTT 연결 오류

**문제**: MQTT 브로커에 연결할 수 없음
**해결책**:
```bash
# MQTT 브로커 상태 확인
netstat -an | findstr 1883

# Mosquitto 서비스 시작
net start mosquitto
```

### 2. 센서 데이터가 표시되지 않음

**문제**: 웹 대시보드에 센서 데이터가 표시되지 않음
**해결책**:
1. 센서 시뮬레이터가 실행 중인지 확인
2. 데이터베이스 파일 존재 확인: `iot_sensors/sensor_data/sensor_readings.db`
3. 로그 파일 확인: `iot_sensors/sensor_data/sensor_collector.log`

### 3. 알림이 생성되지 않음

**문제**: 임계값을 초과해도 알림이 생성되지 않음
**해결책**:
1. 센서 설정의 임계값 확인
2. 알림 테이블 존재 확인
3. 로그에서 임계값 검사 오류 확인

### 4. 웹 대시보드 로딩 오류

**문제**: IoT 모니터링 페이지가 로딩되지 않음
**해결책**:
1. Flask 앱이 실행 중인지 확인
2. 브라우저 개발자 도구에서 JavaScript 오류 확인
3. API 엔드포인트 응답 확인

## 📈 성능 최적화

### 1. 데이터베이스 최적화

```sql
-- 인덱스 생성
CREATE INDEX idx_sensor_readings_timestamp ON sensor_readings(timestamp);
CREATE INDEX idx_sensor_readings_sensor_id ON sensor_readings(sensor_id);
CREATE INDEX idx_sensor_readings_type ON sensor_readings(sensor_type);

-- 오래된 데이터 정리 (30일 이상)
DELETE FROM sensor_readings WHERE timestamp < datetime('now', '-30 days');
```

### 2. 메모리 사용량 최적화

- 센서 데이터 수집 간격 조정
- 차트 데이터 포인트 수 제한
- 불필요한 로그 레벨 조정

### 3. 네트워크 최적화

- MQTT QoS 레벨 조정
- HTTP 요청 타임아웃 설정
- 배치 데이터 전송 구현

## 🔒 보안 고려사항

### 1. MQTT 보안

```conf
# Mosquitto 설정
allow_anonymous false
password_file mosquitto_passwd
listener 8883
certfile /path/to/cert.pem
keyfile /path/to/key.pem
```

### 2. API 보안

```python
# Flask 앱에 인증 추가
from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    # 토큰 검증 로직
    return verify_api_token(token)

@app.route('/api/iot/sensors')
@auth.login_required
def api_iot_sensors():
    # API 로직
```

### 3. 데이터 암호화

- 센서 데이터 전송 시 TLS/SSL 사용
- 데이터베이스 파일 암호화
- API 통신 시 HTTPS 사용

## 📚 추가 리소스

### 1. MQTT 관련

- [MQTT 공식 문서](https://mqtt.org/documentation)
- [Paho MQTT Python 클라이언트](https://pypi.org/project/paho-mqtt/)
- [Mosquitto 브로커](https://mosquitto.org/)

### 2. IoT 센서 관련

- [IoT 센서 표준](https://www.iotone.com/sensors)
- [센서 데이터 시각화](https://plotly.com/python/)
- [실시간 데이터 처리](https://kafka.apache.org/)

### 3. 웹 대시보드 관련

- [Chart.js 문서](https://www.chartjs.org/docs/)
- [Bootstrap 컴포넌트](https://getbootstrap.com/docs/)
- [Flask RESTful API](https://flask-restful.readthedocs.io/)

## 🤝 기여하기

IoT 센서 연동 기능을 개선하려면:

1. 이슈 리포트 생성
2. 기능 요청 제안
3. 코드 풀 리퀘스트 제출
4. 문서 개선 제안

## 📞 지원

문제가 발생하거나 질문이 있으면:

1. 로그 파일 확인
2. 이슈 트래커 검색
3. 개발팀에 문의

---

**IoT 센서 연동 시스템**은 스마트 빌딩의 실시간 모니터링과 예측을 위한 핵심 기능입니다. 이 가이드를 참고하여 효과적으로 시스템을 운영하세요! 🚀
