#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Energy Management System - Database Configuration
에너지 관리 시스템 데이터베이스 설정
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import redis
from influxdb_client import InfluxDBClient
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# 환경 변수 설정
# =============================================================================

# PostgreSQL 설정
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'energy_management')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'energy_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'energy_password_2024')

# InfluxDB 설정
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'energy_admin_token_2024')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'energy_org')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'energy_data')

# Redis 설정
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'energy_password_2024')
REDIS_DB = int(os.getenv('REDIS_DB', '0'))

# =============================================================================
# PostgreSQL 설정
# =============================================================================

# 데이터베이스 URL 생성
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # 프로덕션에서는 False로 설정
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스 생성
Base = declarative_base()

# 메타데이터 생성
metadata = MetaData()

# =============================================================================
# InfluxDB 설정
# =============================================================================

class InfluxDBManager:
    """InfluxDB 관리 클래스"""
    
    def __init__(self):
        self.client = None
        self.write_api = None
        self.query_api = None
        self.connect()
    
    def connect(self):
        """InfluxDB 연결"""
        try:
            self.client = InfluxDBClient(
                url=INFLUXDB_URL,
                token=INFLUXDB_TOKEN,
                org=INFLUXDB_ORG
            )
            self.write_api = self.client.write_api()
            self.query_api = self.client.query_api()
            logger.info("✅ InfluxDB 연결 성공")
        except Exception as e:
            logger.error(f"❌ InfluxDB 연결 실패: {e}")
            self.client = None
    
    def write_sensor_data(self, measurement, tags, fields, timestamp=None):
        """센서 데이터 쓰기"""
        if not self.write_api:
            logger.error("InfluxDB가 연결되지 않았습니다")
            return False
        
        try:
            from influxdb_client import Point
            
            point = Point(measurement)
            
            # 태그 추가
            for key, value in tags.items():
                point = point.tag(key, value)
            
            # 필드 추가
            for key, value in fields.items():
                point = point.field(key, value)
            
            # 타임스탬프 설정
            if timestamp:
                point = point.time(timestamp)
            
            self.write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            return True
        except Exception as e:
            logger.error(f"센서 데이터 쓰기 실패: {e}")
            return False
    
    def query_sensor_data(self, query):
        """센서 데이터 쿼리"""
        if not self.query_api:
            logger.error("InfluxDB가 연결되지 않았습니다")
            return None
        
        try:
            result = self.query_api.query(org=INFLUXDB_ORG, query=query)
            return result
        except Exception as e:
            logger.error(f"센서 데이터 쿼리 실패: {e}")
            return None
    
    def close(self):
        """연결 종료"""
        if self.client:
            self.client.close()

# InfluxDB 인스턴스 생성
influxdb = InfluxDBManager()

# =============================================================================
# Redis 설정
# =============================================================================

class RedisManager:
    """Redis 관리 클래스"""
    
    def __init__(self):
        self.client = None
        self.connect()
    
    def connect(self):
        """Redis 연결"""
        try:
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # 연결 테스트
            self.client.ping()
            logger.info("✅ Redis 연결 성공")
        except Exception as e:
            logger.error(f"❌ Redis 연결 실패: {e}")
            self.client = None
    
    def set(self, key, value, expire=None):
        """값 설정"""
        if not self.client:
            return False
        try:
            return self.client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis SET 실패: {e}")
            return False
    
    def get(self, key):
        """값 조회"""
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET 실패: {e}")
            return None
    
    def delete(self, key):
        """값 삭제"""
        if not self.client:
            return False
        try:
            return self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE 실패: {e}")
            return False
    
    def exists(self, key):
        """키 존재 확인"""
        if not self.client:
            return False
        try:
            return self.client.exists(key)
        except Exception as e:
            logger.error(f"Redis EXISTS 실패: {e}")
            return False
    
    def set_session(self, session_id, user_data, expire=3600):
        """세션 설정"""
        key = f"session:{session_id}"
        return self.set(key, user_data, expire)
    
    def get_session(self, session_id):
        """세션 조회"""
        key = f"session:{session_id}"
        return self.get(key)
    
    def delete_session(self, session_id):
        """세션 삭제"""
        key = f"session:{session_id}"
        return self.delete(key)
    
    def set_cache(self, key, data, expire=300):
        """캐시 설정"""
        cache_key = f"cache:{key}"
        return self.set(cache_key, data, expire)
    
    def get_cache(self, key):
        """캐시 조회"""
        cache_key = f"cache:{key}"
        return self.get(cache_key)
    
    def delete_cache(self, key):
        """캐시 삭제"""
        cache_key = f"cache:{key}"
        return self.delete(cache_key)

# Redis 인스턴스 생성
redis_client = RedisManager()

# =============================================================================
# 데이터베이스 의존성 함수
# =============================================================================

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_influxdb():
    """InfluxDB 클라이언트 의존성"""
    return influxdb

def get_redis():
    """Redis 클라이언트 의존성"""
    return redis_client

# =============================================================================
# 데이터베이스 연결 테스트
# =============================================================================

def test_connections():
    """모든 데이터베이스 연결 테스트"""
    results = {}
    
    # PostgreSQL 연결 테스트
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        results['postgresql'] = True
        logger.info("✅ PostgreSQL 연결 테스트 성공")
    except Exception as e:
        results['postgresql'] = False
        logger.error(f"❌ PostgreSQL 연결 테스트 실패: {e}")
    
    # InfluxDB 연결 테스트
    try:
        if influxdb.client:
            influxdb.client.ping()
            results['influxdb'] = True
            logger.info("✅ InfluxDB 연결 테스트 성공")
        else:
            results['influxdb'] = False
    except Exception as e:
        results['influxdb'] = False
        logger.error(f"❌ InfluxDB 연결 테스트 실패: {e}")
    
    # Redis 연결 테스트
    try:
        if redis_client.client:
            redis_client.client.ping()
            results['redis'] = True
            logger.info("✅ Redis 연결 테스트 성공")
        else:
            results['redis'] = False
    except Exception as e:
        results['redis'] = False
        logger.error(f"❌ Redis 연결 테스트 실패: {e}")
    
    return results

# =============================================================================
# 초기화 함수
# =============================================================================

def init_databases():
    """데이터베이스 초기화"""
    logger.info("🚀 데이터베이스 초기화 시작")
    
    # 연결 테스트
    results = test_connections()
    
    # 결과 출력
    for db_name, status in results.items():
        if status:
            logger.info(f"✅ {db_name.upper()} 연결 성공")
        else:
            logger.warning(f"⚠️ {db_name.upper()} 연결 실패")
    
    # 모든 연결이 성공했는지 확인
    all_connected = all(results.values())
    
    if all_connected:
        logger.info("🎉 모든 데이터베이스 연결 성공!")
    else:
        logger.warning("⚠️ 일부 데이터베이스 연결 실패")
    
    return all_connected

if __name__ == "__main__":
    # 연결 테스트 실행
    init_databases()



