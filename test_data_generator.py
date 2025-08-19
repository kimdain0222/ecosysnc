#!/usr/bin/env python3
"""
테스트용 센서 데이터 생성기
"""

import sqlite3
import random
from datetime import datetime, timedelta
import json

def init_database():
    """데이터베이스 초기화"""
    db_path = "iot_sensors/sensor_data/sensor_readings.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 센서 읽기 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
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
            CREATE TABLE IF NOT EXISTS sensor_status (
                sensor_id TEXT PRIMARY KEY,
                sensor_type TEXT NOT NULL,
                status TEXT NOT NULL,
                last_reading REAL,
                last_update DATETIME
            )
        ''')
        
        # 알림 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
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
        print("✅ 데이터베이스 초기화 완료")

def generate_test_data():
    """테스트 데이터 생성"""
    sensors = [
        {"id": "temp_001", "name": "1층 로비 온도센서", "type": "temperature", "building_id": "B001", "floor": 1, "room_type": "lobby"},
        {"id": "temp_002", "name": "2층 사무실 온도센서", "type": "temperature", "building_id": "B001", "floor": 2, "room_type": "office"},
        {"id": "temp_003", "name": "3층 회의실 온도센서", "type": "temperature", "building_id": "B001", "floor": 3, "room_type": "meeting_room"},
        {"id": "hum_001", "name": "1층 로비 습도센서", "type": "humidity", "building_id": "B001", "floor": 1, "room_type": "lobby"},
        {"id": "hum_002", "name": "2층 사무실 습도센서", "type": "humidity", "building_id": "B001", "floor": 2, "room_type": "office"},
        {"id": "occ_001", "name": "1층 로비 인원센서", "type": "occupancy", "building_id": "B001", "floor": 1, "room_type": "lobby"},
        {"id": "occ_002", "name": "2층 사무실 인원센서", "type": "occupancy", "building_id": "B001", "floor": 2, "room_type": "office"},
        {"id": "occ_003", "name": "3층 회의실 인원센서", "type": "occupancy", "building_id": "B001", "floor": 3, "room_type": "meeting_room"},
        {"id": "power_001", "name": "1층 전력소비센서", "type": "power", "building_id": "B001", "floor": 1, "room_type": "lobby"},
        {"id": "power_002", "name": "2층 전력소비센서", "type": "power", "building_id": "B001", "floor": 2, "room_type": "office"},
        {"id": "power_003", "name": "3층 전력소비센서", "type": "power", "building_id": "B001", "floor": 3, "room_type": "meeting_room"}
    ]
    
    db_path = "iot_sensors/sensor_data/sensor_readings.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 최근 24시간 동안의 데이터 생성
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        for sensor in sensors:
            print(f"📊 {sensor['name']} 데이터 생성 중...")
            
            current_time = start_time
            while current_time <= end_time:
                # 센서 타입별 데이터 생성
                if sensor['type'] == 'temperature':
                    base_temp = 22 + random.uniform(-3, 3)
                    # 시간대별 변화
                    hour = current_time.hour
                    if 6 <= hour <= 9:  # 출근 시간
                        temp = base_temp + random.uniform(1, 3)
                    elif 12 <= hour <= 13:  # 점심 시간
                        temp = base_temp + random.uniform(2, 4)
                    elif 18 <= hour <= 20:  # 퇴근 시간
                        temp = base_temp + random.uniform(0, 2)
                    else:
                        temp = base_temp + random.uniform(-1, 1)
                    
                    value = round(temp, 1)
                    unit = "celsius"
                    
                elif sensor['type'] == 'humidity':
                    base_humidity = 50 + random.uniform(-10, 10)
                    value = round(max(30, min(70, base_humidity)), 1)
                    unit = "percent"
                    
                elif sensor['type'] == 'occupancy':
                    hour = current_time.hour
                    if 9 <= hour <= 18:  # 업무 시간
                        if sensor['room_type'] == 'office':
                            value = random.randint(5, 15)
                        elif sensor['room_type'] == 'meeting_room':
                            value = random.randint(0, 8)
                        else:  # lobby
                            value = random.randint(10, 25)
                    else:
                        value = random.randint(0, 3)
                    unit = "count"
                    
                elif sensor['type'] == 'power':
                    base_power = 30 + random.uniform(-10, 10)
                    hour = current_time.hour
                    if 9 <= hour <= 18:  # 업무 시간
                        power = base_power + random.uniform(10, 20)
                    else:
                        power = base_power + random.uniform(-5, 5)
                    value = round(max(5, power), 1)
                    unit = "kwh"
                
                # 데이터베이스에 저장
                cursor.execute('''
                    INSERT INTO sensor_readings 
                    (sensor_id, sensor_type, value, unit, timestamp, status, confidence, building_id, floor, room_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sensor['id'],
                    sensor['type'],
                    value,
                    unit,
                    current_time.isoformat(),
                    'normal',
                    0.95 + random.uniform(0, 0.05),
                    sensor['building_id'],
                    sensor['floor'],
                    sensor['room_type']
                ))
                
                # 센서 상태 업데이트
                cursor.execute('''
                    INSERT OR REPLACE INTO sensor_status 
                    (sensor_id, sensor_type, status, last_reading, last_update)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    sensor['id'],
                    sensor['type'],
                    'online',
                    value,
                    current_time.isoformat()
                ))
                
                current_time += timedelta(minutes=15)  # 15분 간격
        
        # 알림 데이터 생성
        alerts = [
            ("temp_001", "온도 임계값 초과", "1층 로비 온도가 28°C를 초과했습니다.", "warning"),
            ("power_002", "전력 소비 증가", "2층 사무실 전력 소비가 평소보다 20% 증가했습니다.", "warning"),
            ("hum_001", "습도 낮음", "1층 로비 습도가 30% 미만입니다.", "info")
        ]
        
        for sensor_id, alert_type, message, severity in alerts:
            cursor.execute('''
                INSERT INTO alerts 
                (sensor_id, alert_type, message, severity, timestamp, resolved)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                sensor_id,
                alert_type,
                message,
                severity,
                (datetime.now() - timedelta(hours=random.randint(1, 6))).isoformat(),
                0
            ))
        
        conn.commit()
        print("✅ 테스트 데이터 생성 완료!")

if __name__ == "__main__":
    print("🚀 테스트 데이터 생성기 시작")
    init_database()
    generate_test_data()
    
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
