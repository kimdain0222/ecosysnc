#!/usr/bin/env python3
"""
간단한 테스트 데이터 생성기
"""

import sqlite3
import random
from datetime import datetime, timedelta

def create_database():
    """데이터베이스 생성"""
    db_path = "iot_sensors/sensor_data/sensor_readings.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 기존 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS sensor_readings")
        cursor.execute("DROP TABLE IF EXISTS sensor_status")
        cursor.execute("DROP TABLE IF EXISTS alerts")
        
        # 센서 읽기 테이블 생성
        cursor.execute('''
            CREATE TABLE sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                status TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                building_id TEXT,
                floor INTEGER,
                room_type TEXT
            )
        ''')
        
        # 센서 상태 테이블 생성
        cursor.execute('''
            CREATE TABLE sensor_status (
                sensor_id TEXT PRIMARY KEY,
                sensor_type TEXT NOT NULL,
                status TEXT NOT NULL,
                last_reading REAL,
                last_update DATETIME
            )
        ''')
        
        # 알림 테이블 생성
        cursor.execute('''
            CREATE TABLE alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                resolved INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        print("✅ 데이터베이스 생성 완료")

def insert_sample_data():
    """샘플 데이터 삽입"""
    db_path = "iot_sensors/sensor_data/sensor_readings.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 현재 시간
        now = datetime.now()
        
        # 센서 데이터
        sensors = [
            ("temp_001", "temperature", 24.5, "celsius", "B001", 1, "lobby"),
            ("temp_002", "temperature", 22.8, "celsius", "B001", 2, "office"),
            ("temp_003", "temperature", 23.2, "celsius", "B001", 3, "meeting_room"),
            ("hum_001", "humidity", 45.2, "percent", "B001", 1, "lobby"),
            ("hum_002", "humidity", 48.7, "percent", "B001", 2, "office"),
            ("occ_001", "occupancy", 12, "count", "B001", 1, "lobby"),
            ("occ_002", "occupancy", 8, "count", "B001", 2, "office"),
            ("occ_003", "occupancy", 3, "count", "B001", 3, "meeting_room"),
            ("power_001", "power", 35.6, "kwh", "B001", 1, "lobby"),
            ("power_002", "power", 28.9, "kwh", "B001", 2, "office"),
            ("power_003", "power", 22.3, "kwh", "B001", 3, "meeting_room")
        ]
        
        # 최근 24시간 동안의 데이터 생성
        for i in range(96):  # 15분 간격으로 24시간
            timestamp = now - timedelta(minutes=15 * i)
            
            for sensor_id, sensor_type, base_value, unit, building_id, floor, room_type in sensors:
                # 랜덤 변동 추가
                if sensor_type == "temperature":
                    value = base_value + random.uniform(-2, 2)
                elif sensor_type == "humidity":
                    value = base_value + random.uniform(-5, 5)
                elif sensor_type == "occupancy":
                    value = max(0, base_value + random.randint(-3, 3))
                else:  # power
                    value = max(5, base_value + random.uniform(-5, 5))
                
                cursor.execute('''
                    INSERT INTO sensor_readings 
                    (sensor_id, sensor_type, value, unit, timestamp, status, confidence, building_id, floor, room_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sensor_id, sensor_type, round(value, 1), unit, timestamp.isoformat(),
                    'normal', 0.95, building_id, floor, room_type
                ))
        
        # 센서 상태 데이터
        for sensor_id, sensor_type, base_value, unit, building_id, floor, room_type in sensors:
            cursor.execute('''
                INSERT INTO sensor_status 
                (sensor_id, sensor_type, status, last_reading, last_update)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                sensor_id, sensor_type, 'online', base_value, now.isoformat()
            ))
        
        # 알림 데이터
        alerts = [
            ("temp_001", "온도 임계값 초과", "1층 로비 온도가 28°C를 초과했습니다.", "warning"),
            ("power_002", "전력 소비 증가", "2층 사무실 전력 소비가 평소보다 20% 증가했습니다.", "warning")
        ]
        
        for sensor_id, alert_type, message, severity in alerts:
            cursor.execute('''
                INSERT INTO alerts 
                (sensor_id, alert_type, message, severity, timestamp, resolved)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                sensor_id, alert_type, message, severity, 
                (now - timedelta(hours=random.randint(1, 6))).isoformat(), 0
            ))
        
        conn.commit()
        print("✅ 샘플 데이터 삽입 완료")

if __name__ == "__main__":
    print("🚀 간단한 테스트 데이터 생성기 시작")
    create_database()
    insert_sample_data()
    
    # 결과 확인
    with sqlite3.connect("iot_sensors/sensor_data/sensor_readings.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM sensor_readings')
        readings_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM sensor_status')
        status_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM alerts')
        alerts_count = cursor.fetchone()[0]
        
        print(f"📊 생성된 데이터:")
        print(f"   - 센서 읽기: {readings_count}개")
        print(f"   - 센서 상태: {status_count}개")
        print(f"   - 알림: {alerts_count}개")
