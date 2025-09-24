#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Energy Management System - Database Startup Script
에너지 관리 시스템 데이터베이스 시작 스크립트
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.database import init_databases, test_connections

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.docker_compose_file = self.project_root / "docker-compose.yml"
    
    def check_docker(self):
        """Docker 설치 확인"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"✅ Docker 설치됨: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ Docker가 설치되지 않았습니다.")
            logger.error("Docker를 설치하고 다시 시도하세요: https://www.docker.com/get-started")
            return False
    
    def check_docker_compose(self):
        """Docker Compose 설치 확인"""
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"✅ Docker Compose 설치됨: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ Docker Compose가 설치되지 않았습니다.")
            return False
    
    def start_databases(self, stage="stage1"):
        """데이터베이스 시작"""
        logger.info(f"🚀 {stage} 데이터베이스 시작 중...")
        
        if not self.docker_compose_file.exists():
            logger.error(f"❌ docker-compose.yml 파일을 찾을 수 없습니다: {self.docker_compose_file}")
            return False
        
        try:
            # Docker Compose로 서비스 시작
            if stage == "stage1":
                cmd = ['docker-compose', 'up', '-d', 'postgres', 'influxdb', 'redis']
            elif stage == "stage2":
                cmd = ['docker-compose', '--profile', 'stage2', 'up', '-d']
            else:
                cmd = ['docker-compose', 'up', '-d']
            
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=True, text=True, check=True)
            
            logger.info("✅ 데이터베이스 서비스 시작 완료")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 데이터베이스 시작 실패: {e}")
            logger.error(f"에러 출력: {e.stderr}")
            return False
    
    def wait_for_databases(self, timeout=60):
        """데이터베이스 연결 대기"""
        logger.info("⏳ 데이터베이스 연결 대기 중...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                results = test_connections()
                if all(results.values()):
                    logger.info("✅ 모든 데이터베이스 연결 성공!")
                    return True
                else:
                    failed_dbs = [db for db, status in results.items() if not status]
                    logger.info(f"⏳ 연결 대기 중... (실패: {', '.join(failed_dbs)})")
                    time.sleep(5)
            except Exception as e:
                logger.info(f"⏳ 연결 시도 중... ({e})")
                time.sleep(5)
        
        logger.error("❌ 데이터베이스 연결 타임아웃")
        return False
    
    def stop_databases(self):
        """데이터베이스 중지"""
        logger.info("🛑 데이터베이스 서비스 중지 중...")
        
        try:
            result = subprocess.run(['docker-compose', 'down'], 
                                  cwd=self.project_root,
                                  capture_output=True, text=True, check=True)
            logger.info("✅ 데이터베이스 서비스 중지 완료")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 데이터베이스 중지 실패: {e}")
            return False
    
    def show_status(self):
        """데이터베이스 상태 확인"""
        logger.info("📊 데이터베이스 상태 확인 중...")
        
        try:
            result = subprocess.run(['docker-compose', 'ps'], 
                                  cwd=self.project_root,
                                  capture_output=True, text=True, check=True)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 상태 확인 실패: {e}")
            return False
    
    def show_logs(self, service=None):
        """데이터베이스 로그 확인"""
        logger.info(f"📋 {service or '모든 서비스'} 로그 확인 중...")
        
        try:
            if service:
                cmd = ['docker-compose', 'logs', service]
            else:
                cmd = ['docker-compose', 'logs']
            
            result = subprocess.run(cmd, cwd=self.project_root,
                                  capture_output=True, text=True, check=True)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 로그 확인 실패: {e}")
            return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("🏢 Energy Management System - Database Manager")
    print("=" * 60)
    
    manager = DatabaseManager()
    
    # Docker 설치 확인
    if not manager.check_docker():
        return False
    
    if not manager.check_docker_compose():
        return False
    
    # 명령어 인수 처리
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            stage = sys.argv[2] if len(sys.argv) > 2 else "stage1"
            if manager.start_databases(stage):
                manager.wait_for_databases()
                init_databases()
        
        elif command == "stop":
            manager.stop_databases()
        
        elif command == "status":
            manager.show_status()
        
        elif command == "logs":
            service = sys.argv[2] if len(sys.argv) > 2 else None
            manager.show_logs(service)
        
        elif command == "restart":
            stage = sys.argv[2] if len(sys.argv) > 2 else "stage1"
            manager.stop_databases()
            time.sleep(5)
            if manager.start_databases(stage):
                manager.wait_for_databases()
                init_databases()
        
        else:
            print("사용법:")
            print("  python scripts/start_databases.py start [stage1|stage2]")
            print("  python scripts/start_databases.py stop")
            print("  python scripts/start_databases.py status")
            print("  python scripts/start_databases.py logs [service]")
            print("  python scripts/start_databases.py restart [stage1|stage2]")
    
    else:
        # 대화형 모드
        while True:
            print("\n선택하세요:")
            print("1. 데이터베이스 시작 (1단계)")
            print("2. 데이터베이스 시작 (2단계)")
            print("3. 데이터베이스 중지")
            print("4. 상태 확인")
            print("5. 로그 확인")
            print("6. 연결 테스트")
            print("0. 종료")
            
            choice = input("\n선택 (0-6): ").strip()
            
            if choice == "1":
                if manager.start_databases("stage1"):
                    manager.wait_for_databases()
                    init_databases()
            
            elif choice == "2":
                if manager.start_databases("stage2"):
                    manager.wait_for_databases()
                    init_databases()
            
            elif choice == "3":
                manager.stop_databases()
            
            elif choice == "4":
                manager.show_status()
            
            elif choice == "5":
                service = input("서비스명 (엔터시 모든 서비스): ").strip() or None
                manager.show_logs(service)
            
            elif choice == "6":
                results = test_connections()
                for db, status in results.items():
                    status_icon = "✅" if status else "❌"
                    print(f"{status_icon} {db.upper()}")
            
            elif choice == "0":
                print("👋 종료합니다.")
                break
            
            else:
                print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main()
