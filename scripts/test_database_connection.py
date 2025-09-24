#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Energy Management System - Database Connection Test
에너지 관리 시스템 데이터베이스 연결 테스트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_sqlite_connection():
    """SQLite 연결 테스트"""
    print("🔍 SQLite 연결 테스트...")
    try:
        import sqlite3
        
        # 기존 SQLite 파일 확인
        sqlite_files = [
            "iot_sensors/sensor_data/sensor_readings.db",
            "backup/sensor_readings_backup.db"
        ]
        
        for file_path in sqlite_files:
            if os.path.exists(file_path):
                print(f"✅ SQLite 파일 발견: {file_path}")
                try:
                    conn = sqlite3.connect(file_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    print(f"   📊 테이블 수: {len(tables)}")
                    for table in tables:
                        print(f"   - {table[0]}")
                    conn.close()
                except Exception as e:
                    print(f"   ❌ 연결 실패: {e}")
            else:
                print(f"❌ SQLite 파일 없음: {file_path}")
        
        return True
    except ImportError:
        print("❌ sqlite3 모듈을 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f"❌ SQLite 테스트 실패: {e}")
        return False

def test_postgresql_connection():
    """PostgreSQL 연결 테스트"""
    print("\n🔍 PostgreSQL 연결 테스트...")
    try:
        import psycopg2
        
        # 연결 정보
        connection_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'energy_management',
            'user': 'energy_user',
            'password': 'energy_password_2024'
        }
        
        try:
            conn = psycopg2.connect(**connection_params)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL 연결 성공!")
            print(f"   📊 버전: {version[0]}")
            
            # 테이블 확인
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            tables = cursor.fetchall()
            print(f"   📊 테이블 수: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
            
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            print(f"❌ PostgreSQL 연결 실패: {e}")
            print("   💡 Docker가 실행 중인지 확인하세요: docker-compose up -d postgres")
            return False
            
    except ImportError:
        print("❌ psycopg2 모듈을 찾을 수 없습니다.")
        print("   💡 설치: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL 테스트 실패: {e}")
        return False

def test_influxdb_connection():
    """InfluxDB 연결 테스트"""
    print("\n🔍 InfluxDB 연결 테스트...")
    try:
        from influxdb_client import InfluxDBClient
        
        # 연결 정보
        url = "http://localhost:8086"
        token = "energy_admin_token_2024"
        org = "energy_org"
        
        try:
            client = InfluxDBClient(url=url, token=token, org=org)
            
            # 연결 테스트
            health = client.health()
            print(f"✅ InfluxDB 연결 성공!")
            print(f"   📊 상태: {health.status}")
            print(f"   📊 버전: {health.version}")
            
            # 버킷 확인
            buckets_api = client.buckets_api()
            buckets = buckets_api.find_buckets()
            print(f"   📊 버킷 수: {len(buckets.buckets)}")
            for bucket in buckets.buckets:
                print(f"   - {bucket.name}")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"❌ InfluxDB 연결 실패: {e}")
            print("   💡 Docker가 실행 중인지 확인하세요: docker-compose up -d influxdb")
            return False
            
    except ImportError:
        print("❌ influxdb-client 모듈을 찾을 수 없습니다.")
        print("   💡 설치: pip install influxdb-client")
        return False
    except Exception as e:
        print(f"❌ InfluxDB 테스트 실패: {e}")
        return False

def test_redis_connection():
    """Redis 연결 테스트"""
    print("\n🔍 Redis 연결 테스트...")
    try:
        import redis
        
        # 연결 정보
        r = redis.Redis(
            host='localhost',
            port=6379,
            password='energy_password_2024',
            decode_responses=True
        )
        
        try:
            # 연결 테스트
            r.ping()
            print("✅ Redis 연결 성공!")
            
            # 정보 확인
            info = r.info()
            print(f"   📊 버전: {info.get('redis_version', 'Unknown')}")
            print(f"   📊 메모리 사용량: {info.get('used_memory_human', 'Unknown')}")
            print(f"   📊 연결 수: {info.get('connected_clients', 'Unknown')}")
            
            return True
            
        except redis.ConnectionError as e:
            print(f"❌ Redis 연결 실패: {e}")
            print("   💡 Docker가 실행 중인지 확인하세요: docker-compose up -d redis")
            return False
            
    except ImportError:
        print("❌ redis 모듈을 찾을 수 없습니다.")
        print("   💡 설치: pip install redis")
        return False
    except Exception as e:
        print(f"❌ Redis 테스트 실패: {e}")
        return False

def test_docker_status():
    """Docker 상태 확인"""
    print("\n🔍 Docker 상태 확인...")
    try:
        import subprocess
        
        # Docker 버전 확인
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker 설치됨: {result.stdout.strip()}")
        
        # Docker Compose 버전 확인
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker Compose 설치됨: {result.stdout.strip()}")
        
        # 실행 중인 컨테이너 확인
        result = subprocess.run(['docker', 'ps'], 
                              capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:  # 헤더 제외
            print(f"✅ 실행 중인 컨테이너: {len(lines) - 1}개")
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    print(f"   - {parts[1]}")
        else:
            print("⚠️ 실행 중인 컨테이너가 없습니다.")
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Docker 명령어 실행 실패")
        return False
    except FileNotFoundError:
        print("❌ Docker가 설치되지 않았습니다.")
        print("   💡 설치 가이드: DOCKER_SETUP.md 참조")
        return False
    except Exception as e:
        print(f"❌ Docker 상태 확인 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("🏢 Energy Management System - Database Connection Test")
    print("=" * 60)
    
    results = {}
    
    # SQLite 테스트
    results['sqlite'] = test_sqlite_connection()
    
    # Docker 상태 확인
    results['docker'] = test_docker_status()
    
    # PostgreSQL 테스트
    results['postgresql'] = test_postgresql_connection()
    
    # InfluxDB 테스트
    results['influxdb'] = test_influxdb_connection()
    
    # Redis 테스트
    results['redis'] = test_redis_connection()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    for db_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {db_name.upper()}")
    
    # 권장사항
    print("\n💡 권장사항:")
    
    if not results.get('docker', False):
        print("1. Docker를 설치하세요: DOCKER_SETUP.md 참조")
    
    if not results.get('postgresql', False):
        print("2. PostgreSQL을 시작하세요: docker-compose up -d postgres")
    
    if not results.get('influxdb', False):
        print("3. InfluxDB를 시작하세요: docker-compose up -d influxdb")
    
    if not results.get('redis', False):
        print("4. Redis를 시작하세요: docker-compose up -d redis")
    
    if all(results.values()):
        print("🎉 모든 데이터베이스가 정상적으로 연결되었습니다!")
    else:
        print("⚠️ 일부 데이터베이스 연결에 문제가 있습니다.")

if __name__ == "__main__":
    main()
