#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Energy Management System - SQLite to PostgreSQL Migration
SQLite에서 PostgreSQL로 데이터 마이그레이션
"""

import sys
import os
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SQLiteToPostgreSQLMigrator:
    """SQLite에서 PostgreSQL로 데이터 마이그레이션 클래스"""
    
    def __init__(self, sqlite_path="backup/sensor_readings_backup.db"):
        self.sqlite_path = sqlite_path
        self.postgres_connection = None
        
    def connect_sqlite(self):
        """SQLite 연결"""
        try:
            if not os.path.exists(self.sqlite_path):
                logger.error(f"SQLite 파일을 찾을 수 없습니다: {self.sqlite_path}")
                return None
            
            conn = sqlite3.connect(self.sqlite_path)
            logger.info(f"✅ SQLite 연결 성공: {self.sqlite_path}")
            return conn
        except Exception as e:
            logger.error(f"❌ SQLite 연결 실패: {e}")
            return None
    
    def connect_postgresql(self):
        """PostgreSQL 연결"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='energy_management',
                user='energy_user',
                password='energy_password_2024'
            )
            logger.info("✅ PostgreSQL 연결 성공")
            return conn
        except Exception as e:
            logger.error(f"❌ PostgreSQL 연결 실패: {e}")
            logger.error("💡 Docker를 실행하세요: docker-compose up -d postgres")
            return None
    
    def get_sqlite_tables(self, conn):
        """SQLite 테이블 목록 조회"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"📊 SQLite 테이블: {tables}")
            return tables
        except Exception as e:
            logger.error(f"❌ 테이블 목록 조회 실패: {e}")
            return []
    
    def get_table_data(self, conn, table_name):
        """테이블 데이터 조회"""
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            logger.info(f"📊 {table_name} 테이블: {len(df)}개 레코드")
            return df
        except Exception as e:
            logger.error(f"❌ {table_name} 테이블 데이터 조회 실패: {e}")
            return None
    
    def migrate_sensor_readings(self, sqlite_df, postgres_conn):
        """센서 읽기 데이터 마이그레이션"""
        try:
            cursor = postgres_conn.cursor()
            
            # 기본 테넌트와 건물 생성 (없는 경우)
            self.create_default_tenant_and_building(postgres_conn)
            
            # 센서 타입 생성
            self.create_sensor_types(postgres_conn)
            
            # 센서 데이터를 PostgreSQL 형식으로 변환
            for _, row in sqlite_df.iterrows():
                # 센서 데이터 삽입
                insert_query = """
                INSERT INTO sensors (
                    building_id, sensor_id, name, sensor_type_id,
                    status, last_reading, created_at
                ) VALUES (
                    (SELECT id FROM buildings WHERE name = 'Default Building' LIMIT 1),
                    %s, %s, 
                    (SELECT id FROM sensor_types WHERE name = %s LIMIT 1),
                    %s, %s, %s
                ) ON CONFLICT (building_id, sensor_id) DO NOTHING;
                """
                
                # 센서 타입 매핑
                sensor_type_map = {
                    'temperature': 'temperature',
                    'humidity': 'humidity',
                    'power': 'power_consumption',
                    'occupancy': 'occupancy'
                }
                
                sensor_type = sensor_type_map.get(row.get('sensor_type', 'temperature'), 'temperature')
                
                cursor.execute(insert_query, (
                    row.get('sensor_id', f"sensor_{row.get('id', 'unknown')}"),
                    row.get('sensor_id', f"Sensor {row.get('id', 'Unknown')}"),
                    sensor_type,
                    row.get('status', 'active'),
                    row.get('timestamp'),
                    datetime.now()
                ))
            
            postgres_conn.commit()
            logger.info(f"✅ 센서 읽기 데이터 마이그레이션 완료: {len(sqlite_df)}개 레코드")
            
        except Exception as e:
            logger.error(f"❌ 센서 읽기 데이터 마이그레이션 실패: {e}")
            postgres_conn.rollback()
    
    def migrate_sensor_status(self, sqlite_df, postgres_conn):
        """센서 상태 데이터 마이그레이션"""
        try:
            cursor = postgres_conn.cursor()
            
            for _, row in sqlite_df.iterrows():
                # 센서 상태 업데이트
                update_query = """
                UPDATE sensors 
                SET status = %s, last_reading = %s, updated_at = %s
                WHERE sensor_id = %s;
                """
                
                cursor.execute(update_query, (
                    row.get('status', 'active'),
                    row.get('last_timestamp'),
                    datetime.now(),
                    row.get('sensor_id')
                ))
            
            postgres_conn.commit()
            logger.info(f"✅ 센서 상태 데이터 마이그레이션 완료: {len(sqlite_df)}개 레코드")
            
        except Exception as e:
            logger.error(f"❌ 센서 상태 데이터 마이그레이션 실패: {e}")
            postgres_conn.rollback()
    
    def migrate_alerts(self, sqlite_df, postgres_conn):
        """알림 데이터 마이그레이션"""
        try:
            cursor = postgres_conn.cursor()
            
            for _, row in sqlite_df.iterrows():
                # 알림 데이터 삽입
                insert_query = """
                INSERT INTO notifications (
                    tenant_id, building_id, sensor_id, notification_type,
                    title, message, severity, status, created_at
                ) VALUES (
                    (SELECT id FROM tenants WHERE name = 'Energy Management Demo' LIMIT 1),
                    (SELECT id FROM buildings WHERE name = 'Default Building' LIMIT 1),
                    (SELECT id FROM sensors WHERE sensor_id = %s LIMIT 1),
                    %s, %s, %s, %s, %s, %s
                );
                """
                
                cursor.execute(insert_query, (
                    row.get('sensor_id'),
                    row.get('alert_type', 'sensor_alert'),
                    f"Alert: {row.get('alert_type', 'Unknown')}",
                    row.get('message', 'Sensor alert'),
                    row.get('severity', 'warning'),
                    'unread',
                    row.get('timestamp', datetime.now())
                ))
            
            postgres_conn.commit()
            logger.info(f"✅ 알림 데이터 마이그레이션 완료: {len(sqlite_df)}개 레코드")
            
        except Exception as e:
            logger.error(f"❌ 알림 데이터 마이그레이션 실패: {e}")
            postgres_conn.rollback()
    
    def create_default_tenant_and_building(self, postgres_conn):
        """기본 테넌트와 건물 생성"""
        try:
            cursor = postgres_conn.cursor()
            
            # 기본 테넌트 생성
            cursor.execute("""
                INSERT INTO tenants (name, domain, subscription_plan)
                VALUES ('Energy Management Demo', 'demo.energy.com', 'Professional')
                ON CONFLICT (domain) DO NOTHING;
            """)
            
            # 기본 건물 생성
            cursor.execute("""
                INSERT INTO buildings (tenant_id, name, address, building_type, total_floors)
                SELECT 
                    t.id,
                    'Default Building',
                    '123 Energy Street, Seoul, Korea',
                    'office',
                    5
                FROM tenants t 
                WHERE t.name = 'Energy Management Demo'
                ON CONFLICT DO NOTHING;
            """)
            
            postgres_conn.commit()
            logger.info("✅ 기본 테넌트와 건물 생성 완료")
            
        except Exception as e:
            logger.error(f"❌ 기본 테넌트와 건물 생성 실패: {e}")
            postgres_conn.rollback()
    
    def create_sensor_types(self, postgres_conn):
        """센서 타입 생성"""
        try:
            cursor = postgres_conn.cursor()
            
            sensor_types = [
                ('temperature', 'celsius', 'float', -50, 100, '온도 센서'),
                ('humidity', 'percent', 'float', 0, 100, '습도 센서'),
                ('power_consumption', 'kwh', 'float', 0, 10000, '전력 사용량 센서'),
                ('occupancy', 'percent', 'float', 0, 100, '공실률 센서'),
                ('light_level', 'lux', 'float', 0, 100000, '조도 센서'),
                ('co2', 'ppm', 'float', 0, 5000, 'CO2 농도 센서')
            ]
            
            for sensor_type in sensor_types:
                cursor.execute("""
                    INSERT INTO sensor_types (name, unit, data_type, min_value, max_value, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO NOTHING;
                """, sensor_type)
            
            postgres_conn.commit()
            logger.info("✅ 센서 타입 생성 완료")
            
        except Exception as e:
            logger.error(f"❌ 센서 타입 생성 실패: {e}")
            postgres_conn.rollback()
    
    def run_migration(self):
        """전체 마이그레이션 실행"""
        logger.info("🚀 SQLite to PostgreSQL 마이그레이션 시작")
        
        # SQLite 연결
        sqlite_conn = self.connect_sqlite()
        if not sqlite_conn:
            return False
        
        # PostgreSQL 연결
        postgres_conn = self.connect_postgresql()
        if not postgres_conn:
            sqlite_conn.close()
            return False
        
        try:
            # SQLite 테이블 목록 조회
            tables = self.get_sqlite_tables(sqlite_conn)
            
            # 각 테이블별 마이그레이션
            for table in tables:
                if table == 'sqlite_sequence':
                    continue
                
                logger.info(f"📊 {table} 테이블 마이그레이션 시작")
                df = self.get_table_data(sqlite_conn, table)
                
                if df is not None and not df.empty:
                    if table == 'sensor_readings':
                        self.migrate_sensor_readings(df, postgres_conn)
                    elif table == 'sensor_status':
                        self.migrate_sensor_status(df, postgres_conn)
                    elif table == 'alerts':
                        self.migrate_alerts(df, postgres_conn)
                    else:
                        logger.warning(f"⚠️ 알 수 없는 테이블: {table}")
            
            logger.info("🎉 마이그레이션 완료!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 마이그레이션 실패: {e}")
            return False
        finally:
            sqlite_conn.close()
            postgres_conn.close()

def main():
    """메인 함수"""
    print("=" * 60)
    print("🔄 SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    migrator = SQLiteToPostgreSQLMigrator()
    
    if migrator.run_migration():
        print("✅ 마이그레이션이 성공적으로 완료되었습니다!")
        print("\n다음 단계:")
        print("1. Docker로 PostgreSQL 시작: docker-compose up -d postgres")
        print("2. 데이터 확인: python scripts/test_database_connection.py")
    else:
        print("❌ 마이그레이션이 실패했습니다.")
        print("\n문제 해결:")
        print("1. Docker 설치: DOCKER_SETUP.md 참조")
        print("2. PostgreSQL 시작: docker-compose up -d postgres")

if __name__ == "__main__":
    main()
