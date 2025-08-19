#!/usr/bin/env python3
"""
IoT 센서 데이터 수집기
실시간 센서 데이터를 수집하고 처리하는 시스템
"""

import json
import sqlite3
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
from dataclasses import dataclass
import joblib
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('iot_sensors/sensor_data/sensor_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SensorReading:
    """센서 읽기 데이터 클래스"""
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    building_id: str
    floor: int
    room_type: str
    status: str = "normal"
    confidence: float = 1.0

class SensorDatabase:
    """센서 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
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
                        building_id TEXT NOT NULL,
                        floor INTEGER NOT NULL,
                        room_type TEXT NOT NULL,
                        status TEXT DEFAULT 'normal',
                        confidence REAL DEFAULT 1.0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 센서 상태 테이블 생성
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sensor_status (
                        sensor_id TEXT PRIMARY KEY,
                        sensor_type TEXT NOT NULL,
                        last_reading REAL,
                        last_timestamp DATETIME,
                        status TEXT DEFAULT 'online',
                        error_count INTEGER DEFAULT 0,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                conn.commit()
                logger.info("✅ 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 초기화 오류: {e}")
    
    def save_reading(self, reading: SensorReading):
        """센서 읽기 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO sensor_readings 
                    (sensor_id, sensor_type, value, unit, timestamp, building_id, floor, room_type, status, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    reading.sensor_id, reading.sensor_type, reading.value, reading.unit,
                    reading.timestamp, reading.building_id, reading.floor, reading.room_type,
                    reading.status, reading.confidence
                ))
                
                # 센서 상태 업데이트
                cursor.execute('''
                    INSERT OR REPLACE INTO sensor_status 
                    (sensor_id, sensor_type, last_reading, last_timestamp, status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    reading.sensor_id, reading.sensor_type, reading.value,
                    reading.timestamp, reading.status, datetime.now()
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ 센서 읽기 저장 오류: {e}")
    
    def save_alert(self, sensor_id: str, alert_type: str, message: str, severity: str):
        """알림 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO alerts (sensor_id, alert_type, message, severity)
                    VALUES (?, ?, ?, ?)
                ''', (sensor_id, alert_type, message, severity))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ 알림 저장 오류: {e}")
    
    def get_recent_readings(self, sensor_id: str = None, hours: int = 24) -> pd.DataFrame:
        """최근 센서 읽기 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT * FROM sensor_readings 
                    WHERE timestamp >= datetime('now', '-{} hours')
                '''.format(hours)
                
                if sensor_id:
                    query += f" AND sensor_id = '{sensor_id}'"
                
                query += " ORDER BY timestamp DESC"
                
                df = pd.read_sql_query(query, conn)
                return df
                
        except Exception as e:
            logger.error(f"❌ 센서 읽기 조회 오류: {e}")
            return pd.DataFrame()
    
    def get_sensor_status(self) -> pd.DataFrame:
        """센서 상태 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("SELECT * FROM sensor_status", conn)
                return df
                
        except Exception as e:
            logger.error(f"❌ 센서 상태 조회 오류: {e}")
            return pd.DataFrame()

class MQTTClient:
    """MQTT 클라이언트 클래스"""
    
    def __init__(self, config: Dict, on_message_callback):
        self.config = config
        self.on_message_callback = on_message_callback
        self.client = None
        self.connected = False
        
    def connect(self):
        """MQTT 브로커 연결"""
        try:
            self.client = mqtt.Client(client_id=self.config['client_id'])
            self.client.username_pw_set(self.config['username'], self.config['password'])
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            
            self.client.connect(self.config['broker'], self.config['port'], self.config['keepalive'])
            self.client.loop_start()
            
            logger.info("✅ MQTT 브로커 연결 완료")
            
        except Exception as e:
            logger.error(f"❌ MQTT 연결 오류: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        """연결 콜백"""
        if rc == 0:
            self.connected = True
            logger.info("✅ MQTT 연결 성공")
            
            # 모든 센서 토픽 구독
            topics = [
                "building/+/+/+/temperature",
                "building/+/+/+/humidity", 
                "building/+/+/+/occupancy",
                "building/+/+/+/power"
            ]
            
            for topic in topics:
                client.subscribe(topic, qos=self.config['qos'])
                logger.info(f"📡 토픽 구독: {topic}")
        else:
            logger.error(f"❌ MQTT 연결 실패: {rc}")
    
    def on_message(self, client, userdata, msg):
        """메시지 수신 콜백"""
        try:
            payload = json.loads(msg.payload.decode())
            self.on_message_callback(msg.topic, payload)
            
        except Exception as e:
            logger.error(f"❌ 메시지 처리 오류: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """연결 해제 콜백"""
        self.connected = False
        logger.warning("⚠️ MQTT 연결 해제")
    
    def disconnect(self):
        """연결 해제"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

class HTTPClient:
    """HTTP 클라이언트 클래스"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config['timeout']
    
    def get_sensor_data(self, endpoint: str) -> Optional[Dict]:
        """센서 데이터 HTTP 요청"""
        for attempt in range(self.config['retry_attempts']):
            try:
                response = self.session.get(endpoint)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ HTTP 요청 실패 (시도 {attempt + 1}): {e}")
                if attempt < self.config['retry_attempts'] - 1:
                    time.sleep(self.config['retry_delay'])
        
        return None

class SensorCollector:
    """IoT 센서 데이터 수집기 메인 클래스"""
    
    def __init__(self, config_path: str = "iot_sensors/config/sensor_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        
        # 컴포넌트 초기화
        self.db = SensorDatabase(self.config['data_storage']['file_path'])
        self.mqtt_client = MQTTClient(self.config['mqtt_config'], self.on_mqtt_message)
        self.http_client = HTTPClient(self.config['http_config'])
        
        # ML 모델 로드
        self.model = None
        self.scaler = None
        self.load_ml_model()
        
        # 스레드 관리
        self.running = False
        self.threads = []
        
        logger.info("🚀 IoT 센서 데이터 수집기 초기화 완료")
    
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
    
    def load_ml_model(self):
        """ML 모델 로드"""
        try:
            model_path = self.config['prediction']['model_path']
            scaler_path = self.config['prediction']['scaler_path']
            
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            
            logger.info("✅ ML 모델 로드 완료")
            
        except Exception as e:
            logger.warning(f"⚠️ ML 모델 로드 실패: {e}")
    
    def on_mqtt_message(self, topic: str, payload: Dict):
        """MQTT 메시지 처리"""
        try:
            # 토픽에서 센서 정보 추출
            parts = topic.split('/')
            if len(parts) >= 5:
                building_id = parts[1]
                floor = int(parts[2].replace('floor', ''))
                room_type = parts[3]
                sensor_type = parts[4]
                
                # 센서 ID 찾기
                sensor_id = self.find_sensor_id(building_id, floor, room_type, sensor_type)
                
                if sensor_id:
                    reading = SensorReading(
                        sensor_id=sensor_id,
                        sensor_type=sensor_type,
                        value=float(payload.get('value', 0)),
                        unit=payload.get('unit', ''),
                        timestamp=datetime.fromisoformat(payload.get('timestamp', datetime.now().isoformat())),
                        building_id=building_id,
                        floor=floor,
                        room_type=room_type,
                        status=payload.get('status', 'normal'),
                        confidence=payload.get('confidence', 1.0)
                    )
                    
                    self.process_sensor_reading(reading)
                    
        except Exception as e:
            logger.error(f"❌ MQTT 메시지 처리 오류: {e}")
    
    def find_sensor_id(self, building_id: str, floor: int, room_type: str, sensor_type: str) -> Optional[str]:
        """센서 ID 찾기"""
        sensor_key = f"{sensor_type}_sensors"
        if sensor_key in self.config['sensors']:
            for sensor in self.config['sensors'][sensor_key]:
                if (sensor['building_id'] == building_id and 
                    sensor['floor'] == floor and 
                    sensor['room_type'] == room_type):
                    return sensor['id']
        return None
    
    def process_sensor_reading(self, reading: SensorReading):
        """센서 읽기 처리"""
        try:
            # 임계값 검사
            self.check_thresholds(reading)
            
            # 데이터베이스 저장
            self.db.save_reading(reading)
            
            # 실시간 예측 (전력 센서인 경우)
            if reading.sensor_type == 'power':
                self.predict_power_consumption(reading)
            
            logger.info(f"📊 센서 데이터 처리: {reading.sensor_id} = {reading.value} {reading.unit}")
            
        except Exception as e:
            logger.error(f"❌ 센서 읽기 처리 오류: {e}")
    
    def check_thresholds(self, reading: SensorReading):
        """임계값 검사 및 알림"""
        try:
            sensor_config = self.get_sensor_config(reading.sensor_id)
            if not sensor_config:
                return
            
            thresholds = sensor_config['thresholds']
            value = reading.value
            
            # 임계값 검사
            if value < thresholds['critical_min']:
                self.db.save_alert(
                    reading.sensor_id, 
                    'critical_low', 
                    f"센서 값이 임계값 아래: {value} {reading.unit}",
                    'critical'
                )
                reading.status = 'critical_low'
                
            elif value > thresholds['critical_max']:
                self.db.save_alert(
                    reading.sensor_id,
                    'critical_high',
                    f"센서 값이 임계값 위: {value} {reading.unit}",
                    'critical'
                )
                reading.status = 'critical_high'
                
            elif value < thresholds['min']:
                self.db.save_alert(
                    reading.sensor_id,
                    'warning_low',
                    f"센서 값이 경고 임계값 아래: {value} {reading.unit}",
                    'warning'
                )
                reading.status = 'warning_low'
                
            elif value > thresholds['max']:
                self.db.save_alert(
                    reading.sensor_id,
                    'warning_high',
                    f"센서 값이 경고 임계값 위: {value} {reading.unit}",
                    'warning'
                )
                reading.status = 'warning_high'
                
        except Exception as e:
            logger.error(f"❌ 임계값 검사 오류: {e}")
    
    def get_sensor_config(self, sensor_id: str) -> Optional[Dict]:
        """센서 설정 조회"""
        for sensor_type, sensors in self.config['sensors'].items():
            for sensor in sensors:
                if sensor['id'] == sensor_id:
                    return sensor
        return None
    
    def predict_power_consumption(self, reading: SensorReading):
        """전력 소비 예측"""
        try:
            if not self.model or not self.scaler:
                return
            
            # 최근 센서 데이터 수집
            recent_data = self.db.get_recent_readings(hours=1)
            
            if recent_data.empty:
                return
            
            # 예측을 위한 특성 생성
            features = self.create_prediction_features(recent_data, reading)
            
            if features is not None:
                # 예측 수행
                prediction = self.model.predict([features])[0]
                confidence = self.model.predict_proba([features])[0].max() if hasattr(self.model, 'predict_proba') else 1.0
                
                # 예측 결과 저장
                prediction_reading = SensorReading(
                    sensor_id=f"{reading.sensor_id}_prediction",
                    sensor_type="power_prediction",
                    value=prediction,
                    unit="kwh",
                    timestamp=datetime.now(),
                    building_id=reading.building_id,
                    floor=reading.floor,
                    room_type=reading.room_type,
                    status="prediction",
                    confidence=confidence
                )
                
                self.db.save_reading(prediction_reading)
                
                logger.info(f"🔮 전력 소비 예측: {prediction:.2f} kWh (신뢰도: {confidence:.2f})")
                
        except Exception as e:
            logger.error(f"❌ 전력 소비 예측 오류: {e}")
    
    def create_prediction_features(self, recent_data: pd.DataFrame, current_reading: SensorReading) -> Optional[List]:
        """예측을 위한 특성 생성"""
        try:
            # 현재 시간 정보
            now = datetime.now()
            
            # 기본 특성
            features = [
                now.hour,
                now.weekday(),
                now.month,
                current_reading.floor,
                1 if current_reading.room_type == 'office' else 0,
                1 if current_reading.room_type == 'meeting_room' else 0,
                1 if current_reading.room_type == 'lobby' else 0
            ]
            
            # 최근 센서 데이터 평균
            for sensor_type in ['temperature', 'humidity', 'occupancy']:
                sensor_data = recent_data[
                    (recent_data['sensor_type'] == sensor_type) & 
                    (recent_data['building_id'] == current_reading.building_id) &
                    (recent_data['floor'] == current_reading.floor)
                ]
                
                if not sensor_data.empty:
                    features.append(sensor_data['value'].mean())
                else:
                    features.append(0.0)
            
            # 전력 소비 특성
            power_data = recent_data[
                (recent_data['sensor_type'] == 'power') & 
                (recent_data['building_id'] == current_reading.building_id) &
                (recent_data['floor'] == current_reading.floor)
            ]
            
            if not power_data.empty:
                features.extend([
                    power_data['value'].mean(),
                    power_data['value'].std(),
                    power_data['value'].max(),
                    power_data['value'].min()
                ])
            else:
                features.extend([0.0, 0.0, 0.0, 0.0])
            
            # 특성 스케일링
            features_scaled = self.scaler.transform([features])
            return features_scaled[0]
            
        except Exception as e:
            logger.error(f"❌ 특성 생성 오류: {e}")
            return None
    
    def http_polling_worker(self):
        """HTTP 폴링 워커"""
        while self.running:
            try:
                for sensor_type, sensors in self.config['sensors'].items():
                    for sensor in sensors:
                        if 'http_endpoint' in sensor:
                            data = self.http_client.get_sensor_data(sensor['http_endpoint'])
                            if data:
                                reading = SensorReading(
                                    sensor_id=sensor['id'],
                                    sensor_type=sensor_type.replace('_sensors', ''),
                                    value=float(data.get('value', 0)),
                                    unit=data.get('unit', sensor['unit']),
                                    timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
                                    building_id=sensor['building_id'],
                                    floor=sensor['floor'],
                                    room_type=sensor['room_type'],
                                    status=data.get('status', 'normal'),
                                    confidence=data.get('confidence', 1.0)
                                )
                                self.process_sensor_reading(reading)
                
                time.sleep(60)  # 1분 대기
                
            except Exception as e:
                logger.error(f"❌ HTTP 폴링 오류: {e}")
                time.sleep(60)
    
    def start(self):
        """센서 수집기 시작"""
        try:
            self.running = True
            
            # MQTT 연결 시도 (선택사항)
            try:
                self.mqtt_client.connect()
                logger.info("✅ MQTT 연결 성공")
            except Exception as e:
                logger.info("ℹ️ MQTT 브로커 없음, HTTP 방식만 사용")
            
            # HTTP 폴링 스레드 시작
            http_thread = threading.Thread(target=self.http_polling_worker, daemon=True)
            http_thread.start()
            self.threads.append(http_thread)
            
            logger.info("🚀 IoT 센서 데이터 수집기 시작됨")
            
        except Exception as e:
            logger.error(f"❌ 센서 수집기 시작 오류: {e}")
    
    def stop(self):
        """센서 수집기 중지"""
        try:
            self.running = False
            
            # MQTT 연결 해제
            self.mqtt_client.disconnect()
            
            # 스레드 대기
            for thread in self.threads:
                thread.join(timeout=5)
            
            logger.info("🛑 IoT 센서 데이터 수집기 중지됨")
            
        except Exception as e:
            logger.error(f"❌ 센서 수집기 중지 오류: {e}")

def main():
    """메인 함수"""
    try:
        collector = SensorCollector()
        collector.start()
        
        # 무한 루프로 실행
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            collector.stop()
            
    except Exception as e:
        logger.error(f"❌ 메인 실행 오류: {e}")

if __name__ == "__main__":
    main()
