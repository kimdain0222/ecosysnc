# 🗄️ 데이터베이스 시스템 가이드

이 문서는 에너지 관리 시스템의 새로운 데이터베이스 아키텍처에 대해 설명합니다.

## 🏗️ 데이터베이스 아키텍처 개요

우리 시스템은 **3단계 데이터베이스 아키텍처**를 사용합니다:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   InfluxDB      │    │   Redis         │
│   (메인 DB)     │    │   (시계열 DB)   │    │   (캐시/세션)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   비즈니스 데이터│    │   센서 데이터   │    │   세션/캐시     │
│   사용자, 건물   │    │   실시간 모니터링│    │   빠른 접근     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 1단계: MVP 데이터베이스 (현재 실행 중)

### 🐘 PostgreSQL - 메인 데이터베이스

**역할**: 핵심 비즈니스 데이터 저장
**포트**: 5432
**용도**: 관계형 데이터, 트랜잭션 처리

#### 저장되는 데이터
- **사용자 정보**: 회원가입, 로그인, 권한 관리
- **건물 정보**: 주소, 면적, 층수, 건물 유형
- **세입자 정보**: 이름, 연락처, 계약 정보, 입주일
- **에너지 사용량**: 일별/월별 전력 사용량 기록
- **시스템 설정**: 구성 정보, 알림 설정

#### 테이블 구조
```sql
-- 사용자 테이블
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 건물 테이블
CREATE TABLE buildings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    total_area DECIMAL(10,2),
    floors INTEGER,
    building_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 세입자 테이블
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    building_id INTEGER REFERENCES buildings(id),
    name VARCHAR(100) NOT NULL,
    contact_info VARCHAR(100),
    move_in_date DATE,
    contract_end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 센서 데이터 테이블
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    building_id INTEGER REFERENCES buildings(id),
    sensor_type VARCHAR(50) NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 관리 도구
- **pgAdmin**: http://localhost:5050
- **이메일**: admin@energy.com
- **비밀번호**: energy_password_2024

### 📈 InfluxDB - 시계열 데이터베이스

**역할**: IoT 센서 데이터 실시간 저장
**포트**: 8086
**용도**: 시간 기반 데이터, 실시간 분석

#### 저장되는 데이터
- **센서 측정값**: 온도, 습도, 전력 사용량, 조도
- **실시간 모니터링**: 1초 단위 센서 데이터
- **알림 및 이벤트**: 시스템 이벤트, 경고 로그
- **시계열 분석**: 패턴 분석, 예측 데이터

#### 데이터 구조
```json
{
  "measurement": "sensor_readings",
  "tags": {
    "building_id": "building_001",
    "sensor_type": "temperature",
    "floor": "3",
    "room": "office_301"
  },
  "fields": {
    "value": 23.5,
    "unit": "celsius",
    "status": "normal"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 관리 도구
- **InfluxDB UI**: http://localhost:8086
- **사용자명**: admin
- **비밀번호**: energy_password_2024
- **조직**: energy_org
- **버킷**: energy_data

### ⚡ Redis - 캐시 및 세션 저장소

**역할**: 빠른 데이터 접근 및 세션 관리
**포트**: 6379
**용도**: 메모리 기반 고속 데이터 저장

#### 저장되는 데이터
- **사용자 세션**: 로그인 상태, 권한 정보
- **자주 사용되는 데이터**: 건물 목록, 사용자 정보
- **실시간 알림**: 시스템 알림, 경고 메시지
- **임시 계산 결과**: ML 모델 예측 결과

#### 데이터 구조
```redis
# 사용자 세션
session:user_123 = {
  "user_id": 123,
  "username": "admin",
  "role": "admin",
  "login_time": "2024-01-15T10:00:00Z",
  "expires_at": "2024-01-15T18:00:00Z"
}

# 건물 정보 캐시
cache:building_list = [
  {"id": 1, "name": "건물A", "address": "서울시 강남구"},
  {"id": 2, "name": "건물B", "address": "서울시 서초구"}
]

# 실시간 알림
notification:building_001 = {
  "type": "energy_alert",
  "message": "전력 사용량이 임계치를 초과했습니다",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🚀 2단계: 성장 데이터베이스 (필요시 활성화)

### 🔍 Elasticsearch - 검색 및 분석

**역할**: 고급 검색 및 데이터 분석
**포트**: 9200
**용도**: 전문 검색, 로그 분석, 데이터 시각화

#### 저장되는 데이터
- **로그 데이터**: 시스템 로그, 에러 로그, 접근 로그
- **검색 인덱스**: 건물 정보, 사용자 정보, 문서
- **분석 데이터**: 사용 패턴, 성능 메트릭

### 📁 MinIO - 파일 저장소

**역할**: S3 호환 파일 저장소
**포트**: 9000 (API), 9001 (콘솔)
**용도**: 파일 업로드, 백업, 정적 자원

#### 저장되는 데이터
- **사용자 업로드**: 프로필 이미지, 문서
- **시스템 백업**: 데이터베이스 백업, 설정 파일
- **정적 자원**: 이미지, CSS, JavaScript

## 🔧 데이터베이스 관리 명령어

### 기본 명령어
```bash
# 데이터베이스 상태 확인
docker-compose ps

# 특정 데이터베이스 로그 확인
docker-compose logs postgres
docker-compose logs influxdb
docker-compose logs redis

# 데이터베이스 재시작
docker-compose restart postgres
docker-compose restart influxdb
docker-compose restart redis
```

### 데이터베이스 연결 테스트
```bash
# 모든 데이터베이스 연결 상태 확인
python scripts/test_database_connection.py

# 개별 데이터베이스 테스트
python -c "import psycopg2; print('PostgreSQL 연결 성공')"
python -c "import influxdb_client; print('InfluxDB 연결 성공')"
python -c "import redis; print('Redis 연결 성공')"
```

### 데이터 마이그레이션
```bash
# SQLite에서 PostgreSQL로 데이터 마이그레이션
python scripts/migrate_sqlite_to_postgres.py

# 데이터베이스 스키마 업데이트
alembic upgrade head
```

## 📊 데이터 흐름 예시

### 1. 사용자 로그인
```
사용자 → Flask App → Redis (세션 저장) → PostgreSQL (사용자 정보 확인)
```

### 2. 센서 데이터 수집
```
IoT 센서 → InfluxDB (실시간 저장) → Redis (캐시) → 웹 대시보드
```

### 3. 에너지 사용량 조회
```
웹 대시보드 → Redis (캐시 확인) → PostgreSQL (메인 데이터) → InfluxDB (시계열 데이터)
```

### 4. ML 모델 예측
```
PostgreSQL (훈련 데이터) → ML 모델 → Redis (결과 캐시) → 웹 대시보드
```

## 🛠️ 성능 최적화

### PostgreSQL 최적화
```sql
-- 인덱스 생성
CREATE INDEX idx_sensor_data_building_time ON sensor_data(building_id, recorded_at);
CREATE INDEX idx_users_email ON users(email);

-- 쿼리 최적화
EXPLAIN ANALYZE SELECT * FROM sensor_data WHERE building_id = 1 AND recorded_at > '2024-01-01';
```

### InfluxDB 최적화
```json
{
  "retention_policy": "30d",
  "shard_duration": "1d",
  "replication_factor": 1
}
```

### Redis 최적화
```redis
# 메모리 사용량 제한
CONFIG SET maxmemory 512mb
CONFIG SET maxmemory-policy allkeys-lru

# 데이터 만료 시간 설정
EXPIRE session:user_123 3600
```

## 🔄 백업 및 복원

### 자동 백업 스크립트
```bash
# PostgreSQL 백업
docker-compose exec postgres pg_dump -U energy_user energy_management > backup/postgres_$(date +%Y%m%d).sql

# InfluxDB 백업
docker-compose exec influxdb influx backup /backup/influxdb_$(date +%Y%m%d)

# Redis 백업
docker-compose exec redis redis-cli --rdb /backup/redis_$(date +%Y%m%d).rdb
```

### 복원
```bash
# PostgreSQL 복원
docker-compose exec -T postgres psql -U energy_user energy_management < backup/postgres_20240115.sql

# InfluxDB 복원
docker-compose exec influxdb influx restore /backup/influxdb_20240115

# Redis 복원
docker-compose exec redis redis-cli --rdb /backup/redis_20240115.rdb
```

## 📈 모니터링 및 알림

### 데이터베이스 상태 모니터링
```bash
# PostgreSQL 연결 수 확인
docker-compose exec postgres psql -U energy_user -d energy_management -c "SELECT count(*) FROM pg_stat_activity;"

# InfluxDB 데이터 포인트 수 확인
curl -G "http://localhost:8086/query" --data-urlencode "q=SELECT count(*) FROM sensor_readings"

# Redis 메모리 사용량 확인
docker-compose exec redis redis-cli info memory
```

### 알림 설정
```python
# 데이터베이스 연결 실패 알림
def check_database_health():
    try:
        # PostgreSQL 연결 확인
        postgres_conn = psycopg2.connect(...)
        
        # InfluxDB 연결 확인
        influx_client = influxdb_client.InfluxDBClient(...)
        
        # Redis 연결 확인
        redis_client = redis.Redis(...)
        
        return True
    except Exception as e:
        send_alert(f"데이터베이스 연결 실패: {e}")
        return False
```

## 🚨 문제 해결

### 일반적인 문제들

#### 1. PostgreSQL 연결 실패
```bash
# 포트 확인
netstat -ano | findstr :5432

# 컨테이너 재시작
docker-compose restart postgres
```

#### 2. InfluxDB 데이터 손실
```bash
# 데이터 복원
docker-compose exec influxdb influx restore /backup/latest_backup
```

#### 3. Redis 메모리 부족
```bash
# 메모리 사용량 확인
docker-compose exec redis redis-cli info memory

# 캐시 정리
docker-compose exec redis redis-cli FLUSHDB
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Docker 컨테이너 상태: `docker-compose ps`
2. 데이터베이스 로그: `docker-compose logs [service_name]`
3. 연결 테스트: `python scripts/test_database_connection.py`
4. 시스템 리소스: 메모리, 디스크 공간 확인

---

**💡 팁**: 처음 실행 시 데이터베이스 초기화에 시간이 걸릴 수 있습니다. 모든 컨테이너가 "healthy" 상태가 될 때까지 기다려주세요.
