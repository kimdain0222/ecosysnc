# 🐳 Docker 설치 및 데이터베이스 실행 가이드

## 📋 Docker 설치

### Windows에서 Docker 설치

1. **Docker Desktop 다운로드**
   - [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 방문
   - "Download for Windows" 클릭
   - 설치 파일 다운로드

2. **Docker Desktop 설치**
   - 다운로드한 `Docker Desktop Installer.exe` 실행
   - 설치 과정에서 "Use WSL 2 instead of Hyper-V" 옵션 선택 (권장)
   - 설치 완료 후 재부팅

3. **Docker Desktop 실행**
   - 시작 메뉴에서 "Docker Desktop" 실행
   - 시스템 트레이에 Docker 아이콘이 나타나면 준비 완료

### 설치 확인
```bash
# 명령 프롬프트에서 실행
docker --version
docker-compose --version
```

## 🚀 데이터베이스 실행

### 1단계: 기본 데이터베이스 (PostgreSQL + InfluxDB + Redis)
```bash
# 프로젝트 디렉토리에서 실행
docker-compose up -d postgres influxdb redis
```

### 2단계: 전체 스택 (Elasticsearch + MinIO 포함)
```bash
# 전체 스택 실행
docker-compose --profile stage2 up -d
```

### 3단계: 자동화 스크립트 사용
```bash
# Python 스크립트로 실행
python scripts/start_databases.py start stage1
```

## 📊 데이터베이스 접속 정보

### PostgreSQL (메인 데이터베이스)
- **호스트**: localhost
- **포트**: 5432
- **데이터베이스**: energy_management
- **사용자**: energy_user
- **비밀번호**: energy_password_2024
- **관리 도구**: http://localhost:5050 (pgAdmin)
- **용도**: 사용자 정보, 건물 정보, 세입자 정보, 에너지 사용량 기록

### InfluxDB (시계열 데이터베이스)
- **URL**: http://localhost:8086
- **조직**: energy_org
- **버킷**: energy_data
- **토큰**: energy_admin_token_2024
- **용도**: IoT 센서 데이터, 실시간 모니터링, 시간 기반 분석

### Redis (캐시 및 세션)
- **호스트**: localhost
- **포트**: 6379
- **비밀번호**: energy_password_2024
- **용도**: 사용자 세션, 자주 사용되는 데이터 캐시, 실시간 알림

### Elasticsearch (2단계)
- **URL**: http://localhost:9200
- **Kibana**: http://localhost:5601

### MinIO (2단계)
- **URL**: http://localhost:9000
- **콘솔**: http://localhost:9001
- **사용자**: energy_admin
- **비밀번호**: energy_password_2024

## 🔧 유용한 명령어

### 데이터베이스 상태 확인
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs postgres
docker-compose logs influxdb
docker-compose logs redis
```

### 데이터베이스 중지
```bash
# 모든 서비스 중지
docker-compose down

# 특정 서비스만 중지
docker-compose stop postgres
```

### 데이터베이스 재시작
```bash
# 모든 서비스 재시작
docker-compose restart

# 특정 서비스만 재시작
docker-compose restart postgres
```

### 데이터 초기화
```bash
# 모든 데이터 삭제 후 재시작
docker-compose down -v
docker-compose up -d
```

## 🛠️ 문제 해결

### Docker가 시작되지 않는 경우
1. **WSL 2 설치 확인**
   ```bash
   wsl --list --verbose
   ```

2. **Windows 기능 활성화**
   - 제어판 > 프로그램 > Windows 기능 켜기/끄기
   - "Linux용 Windows 하위 시스템" 체크
   - "가상 머신 플랫폼" 체크

3. **BIOS 설정 확인**
   - 가상화 기술(VT-x/AMD-V) 활성화

### 포트 충돌 문제
```bash
# 포트 사용 중인 프로세스 확인
netstat -ano | findstr :5432
netstat -ano | findstr :8086
netstat -ano | findstr :6379

# 프로세스 종료 (PID는 위 명령어 결과에서 확인)
taskkill /PID [PID번호] /F
```

### 메모리 부족 문제
```bash
# Docker Desktop 설정에서 메모리 할당량 증가
# Docker Desktop > Settings > Resources > Memory
# 권장: 4GB 이상
```

## 📈 성능 최적화

### Docker Desktop 설정
- **메모리**: 4GB 이상 할당
- **CPU**: 2코어 이상 할당
- **디스크**: 충분한 여유 공간 확보

### 데이터베이스 설정
- **PostgreSQL**: shared_buffers = 256MB
- **InfluxDB**: cache-max-memory-size = 1GB
- **Redis**: maxmemory = 512MB

## 🔄 백업 및 복원

### 데이터 백업
```bash
# PostgreSQL 백업
docker-compose exec postgres pg_dump -U energy_user energy_management > backup/postgres_backup.sql

# InfluxDB 백업
docker-compose exec influxdb influx backup /backup/influxdb_backup
```

### 데이터 복원
```bash
# PostgreSQL 복원
docker-compose exec -T postgres psql -U energy_user energy_management < backup/postgres_backup.sql

# InfluxDB 복원
docker-compose exec influxdb influx restore /backup/influxdb_backup
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Docker Desktop이 실행 중인지 확인
2. 포트가 충돌하지 않는지 확인
3. 충분한 메모리가 할당되었는지 확인
4. Windows 기능이 활성화되었는지 확인

---

**💡 팁**: 처음 실행 시 이미지 다운로드로 인해 시간이 걸릴 수 있습니다. 인터넷 연결이 안정적인 환경에서 실행하세요.
