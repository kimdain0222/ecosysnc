#!/usr/bin/env python3
"""
IoT 센서 시뮬레이터
실제 센서 데이터를 시뮬레이션하여 테스트용 데이터를 생성
"""

import json
import time
import random
import threading
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List
import paho.mqtt.client as mqtt
import requests
from flask import Flask, jsonify, request
import numpy as np

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('iot_sensors/sensor_data/sensor_simulator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SensorSimulator:
    """센서 시뮬레이터 클래스"""
    
    def __init__(self, config_path: str = "iot_sensors/config/sensor_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        
        # MQTT 클라이언트
        self.mqtt_client = None
        self.mqtt_connected = False
        
        # HTTP 서버
        self.http_server = None
        
        # 시뮬레이션 상태
        self.running = False
        self.threads = []
        
        # 센서 상태 저장
        self.sensor_states = {}
        
        # 데이터베이스 초기화
        self.db_path = "iot_sensors/sensor_data/sensor_readings.db"
        self.init_database()
        
        logger.info("🚀 IoT 센서 시뮬레이터 초기화 완료")
    
    def load_config(self) -> Dict:
        """설정 파일 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info("✅ 설정 파일 로드 완료")
            return config
        except Exception as e:
            logger.error(f"❌ 설정 파일 로드 오류: {e}")
            return {}
    
    def init_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
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
                        last_update DATETIME NOT NULL
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
                logger.info("✅ 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 초기화 오류: {e}")
    
    def save_sensor_data(self, sensor_config: Dict, data: Dict):
        """센서 데이터를 데이터베이스에 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 센서 읽기 저장
                cursor.execute('''
                    INSERT INTO sensor_readings 
                    (sensor_id, sensor_type, value, unit, timestamp, status, confidence, building_id, floor, room_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sensor_config['id'],
                    sensor_config.get('sensor_type', 'unknown'),
                    data['value'],
                    data['unit'],
                    data['timestamp'],
                    data['status'],
                    data.get('confidence', 1.0),
                    sensor_config.get('building_id', ''),
                    sensor_config.get('floor', 0),
                    sensor_config.get('room_type', '')
                ))
                
                # 센서 상태 업데이트
                cursor.execute('''
                    INSERT OR REPLACE INTO sensor_status 
                    (sensor_id, sensor_type, status, last_reading, last_update)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    sensor_config['id'],
                    sensor_config.get('sensor_type', 'unknown'),
                    'online',
                    data['value'],
                    data['timestamp']
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 저장 오류: {e}")
    
    def setup_mqtt(self):
        """MQTT 설정"""
        try:
            mqtt_config = self.config['mqtt_config']
            
            self.mqtt_client = mqtt.Client(client_id=f"simulator_{random.randint(1000, 9999)}")
            self.mqtt_client.username_pw_set(mqtt_config['username'], mqtt_config['password'])
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            
            self.mqtt_client.connect(mqtt_config['broker'], mqtt_config['port'], mqtt_config['keepalive'])
            self.mqtt_client.loop_start()
            
            logger.info("✅ MQTT 설정 완료")
            
        except Exception as e:
            logger.error(f"❌ MQTT 설정 오류: {e}")

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT 연결 콜백"""
        if rc == 0:
            self.mqtt_connected = True
            logger.info("✅ MQTT 연결 성공")
        else:
            logger.error(f"❌ MQTT 연결 실패: {rc}")

    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT 연결 해제 콜백"""
        self.mqtt_connected = False
        logger.warning("⚠️ MQTT 연결 해제")

    def setup_http_server(self):
        """HTTP 서버 설정"""
        try:
            app = Flask(__name__)
            
            # 기본 경로 추가
            @app.route('/')
            def index():
                return {
                    "status": "running", 
                    "service": "IoT Sensor Simulator",
                    "message": "센서 데이터는 /api/sensors 에서 확인할 수 있습니다",
                    "endpoints": {
                        "all_sensors": "/api/sensors",
                        "individual_sensor": "/api/sensors/{sensor_id}",
                        "sensor_control": "/api/sensors/{sensor_id}/control"
                    },
                    "available_sensors": [
                        "temp_b001_1_office",
                        "temp_b001_2_office", 
                        "hum_b001_1_office",
                        "occ_b001_1_office",
                        "power_b001_1_office"
                    ]
                }
            
            @app.route('/api/sensors/<sensor_id>', methods=['GET'])
            def get_sensor_data(sensor_id):
                """센서 데이터 HTTP 엔드포인트"""
                if sensor_id in self.sensor_states:
                    return jsonify(self.sensor_states[sensor_id])
                else:
                    return jsonify({"error": "Sensor not found"}), 404
            
            @app.route('/api/sensors', methods=['GET'])
            def get_all_sensors():
                """모든 센서 데이터 조회"""
                return jsonify(self.sensor_states)
            
            @app.route('/api/sensors/<sensor_id>/control', methods=['POST'])
            def control_sensor(sensor_id):
                """센서 제어"""
                data = request.get_json()
                if sensor_id in self.sensor_states:
                    self.sensor_states[sensor_id].update(data)
                    return jsonify({"message": "Sensor updated", "sensor": self.sensor_states[sensor_id]})
                else:
                    return jsonify({"error": "Sensor not found"}), 404
            
            # 레거시 엔드포인트 추가 (기존 코드와 호환성을 위해)
            @app.route('/sensor_data', methods=['GET'])
            def sensor_data_legacy():
                """레거시 센서 데이터 엔드포인트"""
                return jsonify(self.sensor_states)
            
            @app.route('/sensor_status', methods=['GET'])
            def sensor_status_legacy():
                """레거시 센서 상태 엔드포인트"""
                return jsonify({
                    "status": "running",
                    "active_sensors": len(self.sensor_states),
                    "sensors": list(self.sensor_states.keys()),
                    "timestamp": "2025-10-26T16:17:13.953728"
                })
            
            def run_server():
                app.run(host='0.0.0.0', port=8081, debug=False)
            
            # HTTP 서버 스레드 시작
            http_thread = threading.Thread(target=run_server, daemon=True)
            http_thread.start()
            self.threads.append(http_thread)
            
            logger.info("✅ HTTP 서버 설정 완료 (포트: 8081)")
            
        except Exception as e:
            logger.error(f"❌ HTTP 서버 설정 오류: {e}")

    def generate_temperature_data(self, sensor_config: Dict) -> Dict:
        """온도 데이터 생성"""
        try:
            base_temp = 22.0  # 기본 온도
            hour = datetime.now().hour
            
            # 시간대별 온도 변화
            if 6 <= hour <= 9:  # 출근 시간
                base_temp += 2
            elif 12 <= hour <= 14:  # 점심 시간
                base_temp += 1
            elif 18 <= hour <= 20:  # 퇴근 시간
                base_temp += 1.5
            elif 22 <= hour or hour <= 6:  # 야간
                base_temp -= 3
            
            # 요일별 변화
            weekday = datetime.now().weekday()
            if weekday >= 5:  # 주말
                base_temp -= 2
            
            # 랜덤 노이즈 추가
            noise = random.uniform(-1.5, 1.5)
            temperature = base_temp + noise
            
            # 임계값 내로 제한
            thresholds = sensor_config['thresholds']
            temperature = max(thresholds['critical_min'], min(thresholds['critical_max'], temperature))
            
            return {
                "value": round(temperature, 2),
                "unit": "celsius",
                "timestamp": datetime.now().isoformat(),
                "status": "normal",
                "confidence": random.uniform(0.95, 1.0)
            }
            
        except Exception as e:
            logger.error(f"❌ 온도 데이터 생성 오류: {e}")
            return {"value": 22.0, "unit": "celsius", "timestamp": datetime.now().isoformat(), "status": "error"}
    
    def generate_humidity_data(self, sensor_config: Dict) -> Dict:
        """습도 데이터 생성"""
        try:
            base_humidity = 50.0  # 기본 습도
            hour = datetime.now().hour
            
            # 시간대별 습도 변화
            if 6 <= hour <= 9:  # 출근 시간
                base_humidity += 5
            elif 12 <= hour <= 14:  # 점심 시간
                base_humidity += 3
            elif 18 <= hour <= 20:  # 퇴근 시간
                base_humidity += 4
            elif 22 <= hour or hour <= 6:  # 야간
                base_humidity -= 5
            
            # 온도와의 상관관계 (온도가 높으면 습도 감소)
            if 'temp_001' in self.sensor_states:
                temp = self.sensor_states['temp_001'].get('value', 22.0)
                if temp > 25:
                    base_humidity -= (temp - 25) * 2
            
            # 랜덤 노이즈 추가
            noise = random.uniform(-3, 3)
            humidity = base_humidity + noise
            
            # 임계값 내로 제한
            thresholds = sensor_config['thresholds']
            humidity = max(thresholds['critical_min'], min(thresholds['critical_max'], humidity))
            
            return {
                "value": round(humidity, 1),
                "unit": "percent",
                "timestamp": datetime.now().isoformat(),
                "status": "normal",
                "confidence": random.uniform(0.95, 1.0)
            }
            
        except Exception as e:
            logger.error(f"❌ 습도 데이터 생성 오류: {e}")
            return {"value": 50.0, "unit": "percent", "timestamp": datetime.now().isoformat(), "status": "error"}
    
    def generate_occupancy_data(self, sensor_config: Dict) -> Dict:
        """인원 데이터 생성"""
        try:
            hour = datetime.now().hour
            weekday = datetime.now().weekday()
            
            # 기본 인원 수
            if weekday >= 5:  # 주말
                base_occupancy = random.randint(0, 3)
            else:  # 평일
                if 8 <= hour <= 9:  # 출근 시간
                    base_occupancy = random.randint(15, 25)
                elif 12 <= hour <= 13:  # 점심 시간
                    base_occupancy = random.randint(5, 10)
                elif 18 <= hour <= 19:  # 퇴근 시간
                    base_occupancy = random.randint(8, 15)
                elif 22 <= hour or hour <= 7:  # 야간
                    base_occupancy = random.randint(0, 2)
                else:  # 업무 시간
                    base_occupancy = random.randint(10, 20)
            
            # 랜덤 변동
            variation = random.randint(-2, 2)
            occupancy = max(0, base_occupancy + variation)
            
            # 임계값 내로 제한
            thresholds = sensor_config['thresholds']
            occupancy = min(thresholds['critical_max'], occupancy)
            
            return {
                "value": occupancy,
                "unit": "count",
                "timestamp": datetime.now().isoformat(),
                "status": "normal",
                "confidence": random.uniform(0.95, 1.0)
            }
            
        except Exception as e:
            logger.error(f"❌ 인원 데이터 생성 오류: {e}")
            return {"value": 0, "unit": "count", "timestamp": datetime.now().isoformat(), "status": "error"}
    
    def generate_power_data(self, sensor_config: Dict) -> Dict:
        """전력 데이터 생성"""
        try:
            hour = datetime.now().hour
            weekday = datetime.now().weekday()
            
            # 기본 전력 소비
            if weekday >= 5:  # 주말
                base_power = random.uniform(5, 15)
            else:  # 평일
                if 8 <= hour <= 9:  # 출근 시간
                    base_power = random.uniform(25, 35)
                elif 12 <= hour <= 13:  # 점심 시간
                    base_power = random.uniform(15, 25)
                elif 18 <= hour <= 19:  # 퇴근 시간
                    base_power = random.uniform(20, 30)
                elif 22 <= hour or hour <= 7:  # 야간
                    base_power = random.uniform(5, 10)
                else:  # 업무 시간
                    base_power = random.uniform(20, 30)
            
            # 인원 수에 따른 전력 소비 증가
            if 'occ_001' in self.sensor_states:
                occupancy = self.sensor_states['occ_001'].get('value', 0)
                base_power += occupancy * 0.5
            
            # 온도에 따른 전력 소비 (에어컨/난방)
            if 'temp_001' in self.sensor_states:
                temp = self.sensor_states['temp_001'].get('value', 22.0)
                if temp > 25 or temp < 18:
                    base_power += abs(temp - 22) * 2
            
            # 랜덤 변동
            variation = random.uniform(-3, 3)
            power = max(0, base_power + variation)
            
            # 임계값 내로 제한
            thresholds = sensor_config['thresholds']
            power = min(thresholds['critical_max'], power)
            
            return {
                "value": round(power, 2),
                "unit": "kwh",
                "timestamp": datetime.now().isoformat(),
                "status": "normal",
                "confidence": random.uniform(0.95, 1.0)
            }
            
        except Exception as e:
            logger.error(f"❌ 전력 데이터 생성 오류: {e}")
            return {"value": 20.0, "unit": "kwh", "timestamp": datetime.now().isoformat(), "status": "error"}
    
    def simulate_sensor(self, sensor_config: Dict):
        """개별 센서 시뮬레이션"""
        try:
            sensor_id = sensor_config['id']
            sensor_type = sensor_config.get('sensor_type', 'unknown')
            update_interval = sensor_config.get('update_interval', 60)
            
            while self.running:
                try:
                    # 센서 타입별 데이터 생성
                    if 'temperature' in sensor_id or sensor_type == 'temperature':
                        data = self.generate_temperature_data(sensor_config)
                    elif 'humidity' in sensor_id or sensor_type == 'humidity':
                        data = self.generate_humidity_data(sensor_config)
                    elif 'occupancy' in sensor_id or sensor_type == 'occupancy':
                        data = self.generate_occupancy_data(sensor_config)
                    elif 'power' in sensor_id or sensor_type == 'power':
                        data = self.generate_power_data(sensor_config)
                    else:
                        data = {"value": 0, "unit": "unknown", "timestamp": datetime.now().isoformat(), "status": "error"}
                    
                    # 센서 상태 업데이트
                    self.sensor_states[sensor_id] = data
                    
                    # 데이터베이스에 저장
                    self.save_sensor_data(sensor_config, data)
                    
                    # MQTT로 데이터 전송
                    if self.mqtt_connected and 'mqtt_topic' in sensor_config:
                        payload = json.dumps(data)
                        self.mqtt_client.publish(sensor_config['mqtt_topic'], payload, qos=1)
                        logger.debug(f"📡 MQTT 전송: {sensor_config['mqtt_topic']} = {data['value']} {data['unit']}")
                    
                    # 업데이트 간격만큼 대기
                    time.sleep(update_interval)
                    
                except Exception as e:
                    logger.error(f"❌ 센서 시뮬레이션 오류 ({sensor_id}): {e}")
                    time.sleep(update_interval)
                    
        except Exception as e:
            logger.error(f"❌ 센서 시뮬레이션 스레드 오류 ({sensor_id}): {e}")
    
    def start_simulation(self):
        """시뮬레이션 시작"""
        try:
            self.running = True
            
            # MQTT 설정
            self.setup_mqtt()
            
            # HTTP 서버 설정
            self.setup_http_server()
            
            # 모든 센서에 대해 시뮬레이션 스레드 시작
            for sensor_type, sensors in self.config['sensors'].items():
                for sensor in sensors:
                    # 센서 타입 정보 추가
                    sensor['sensor_type'] = sensor_type.replace('_sensors', '')
                    
                    # 시뮬레이션 스레드 시작
                    thread = threading.Thread(
                        target=self.simulate_sensor, 
                        args=(sensor,), 
                        daemon=True,
                        name=f"simulator_{sensor['id']}"
                    )
                    thread.start()
                    self.threads.append(thread)
                    
                    logger.info(f"🚀 센서 시뮬레이션 시작: {sensor['id']} ({sensor['name']})")
            
            logger.info("🎯 IoT 센서 시뮬레이션 시작됨")
            
        except Exception as e:
            logger.error(f"❌ 시뮬레이션 시작 오류: {e}")
    
    def stop_simulation(self):
        """시뮬레이션 중지"""
        try:
            self.running = False
            
            # MQTT 연결 해제
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            
            # 스레드 대기
            for thread in self.threads:
                thread.join(timeout=5)
            
            logger.info("🛑 IoT 센서 시뮬레이션 중지됨")
            
        except Exception as e:
            logger.error(f"❌ 시뮬레이션 중지 오류: {e}")
    
    def get_sensor_status(self) -> Dict:
        """센서 상태 조회"""
        return {
            "running": self.running,
            "mqtt_connected": self.mqtt_connected,
            "sensor_count": len(self.sensor_states),
            "sensors": self.sensor_states
        }

def main():
    """메인 함수"""
    try:
        simulator = SensorSimulator()
        simulator.start_simulation()
        
        # 무한 루프로 실행
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            simulator.stop_simulation()
            
    except Exception as e:
        logger.error(f"❌ 메인 실행 오류: {e}")

if __name__ == "__main__":
    main()
