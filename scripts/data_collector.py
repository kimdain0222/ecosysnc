"""
스마트 빌딩 에너지 관리 시스템 - 데이터 수집기
공개 데이터셋을 수집하고 전처리하는 스크립트
"""

import os
import pandas as pd
import numpy as np
import requests
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import logging
from tqdm import tqdm

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 데이터 저장 경로 설정
        self.raw_data_dir = self.data_dir / "raw"  # 원본 데이터 저장소
        self.processed_data_dir = self.data_dir / "processed"  # 전처리된 데이터 저장소
        self.raw_data_dir.mkdir(exist_ok=True)
        self.processed_data_dir.mkdir(exist_ok=True)
    
    def download_uci_household_data(self):
        """UCI 개별 가정 전력 소비 데이터 다운로드"""
        logger.info("UCI Household Electric Power Consumption 데이터 다운로드 시작...")
        
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip"
        zip_path = self.raw_data_dir / "household_power_consumption.zip"
        
        try:
            # 데이터 다운로드 (스트리밍 방식으로 메모리 효율적 처리)
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                for chunk in tqdm(response.iter_content(chunk_size=8192), desc="다운로드 중"):
                    f.write(chunk)
            
            # 압축 파일 해제
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.raw_data_dir)
            
            logger.info("UCI 데이터 다운로드 완료!")
            return True
            
        except Exception as e:
            logger.error(f"UCI 데이터 다운로드 실패: {e}")
            return False
    
    def generate_synthetic_building_data(self, num_buildings=5, days=365):
        """가상 건물 데이터 생성 (공개 데이터가 부족할 경우 사용)"""
        logger.info("가상 건물 데이터 생성 시작...")
        
        # 기본 설정 - 2023년 1월 1일부터 시작
        start_date = datetime(2023, 1, 1)
        timestamps = [start_date + timedelta(hours=i) for i in range(days * 24)]
        
        buildings_data = []
        
        for building_id in range(1, num_buildings + 1):
            logger.info(f"건물 {building_id} 데이터 생성 중...")
            
            for timestamp in tqdm(timestamps, desc=f"건물 {building_id}"):
                # 계절성 패턴 분석 (겨울/여름에 에어컨/난방 사용 증가)
                month = timestamp.month
                hour = timestamp.hour
                weekday = timestamp.weekday()
                
                # 기본 전력 사용량 (kWh) - 건물별 차이 반영
                base_consumption = 50 + np.random.normal(0, 10)
                
                # 시간대별 패턴 (업무시간에 사용량 증가)
                if 8 <= hour <= 18:  # 업무시간
                    time_multiplier = 1.5
                elif 19 <= hour <= 22:  # 저녁시간
                    time_multiplier = 1.2
                else:  # 심야시간
                    time_multiplier = 0.3
                
                # 요일별 패턴 (주말에 사용량 감소)
                if weekday < 5:  # 평일
                    day_multiplier = 1.0
                else:  # 주말
                    day_multiplier = 0.4
                
                # 계절별 패턴 (에어컨/난방 사용량 반영)
                if month in [12, 1, 2]:  # 겨울 (난방)
                    season_multiplier = 1.3
                elif month in [6, 7, 8]:  # 여름 (에어컨)
                    season_multiplier = 1.4
                else:  # 봄/가을 (적정 온도)
                    season_multiplier = 0.8
                
                # 공실률 계산 (0-100%)
                if 8 <= hour <= 18 and weekday < 5:  # 업무시간 평일
                    occupancy = np.random.normal(80, 15)
                else:  # 비업무시간 또는 주말
                    occupancy = np.random.normal(10, 5)
                occupancy = max(0, min(100, occupancy))  # 0-100% 범위 제한
                
                # 온도 데이터 (계절별 변화 반영)
                if month in [12, 1, 2]:  # 겨울
                    temperature = np.random.normal(5, 3)
                elif month in [6, 7, 8]:  # 여름
                    temperature = np.random.normal(28, 3)
                else:  # 봄/가을
                    temperature = np.random.normal(18, 5)
                
                # 습도 데이터 (20-80% 범위)
                humidity = np.random.normal(50, 15)
                humidity = max(20, min(80, humidity))
                
                # 최종 전력 사용량 계산 (공실률 반영)
                power_consumption = base_consumption * time_multiplier * day_multiplier * season_multiplier
                power_consumption *= (occupancy / 100) * 0.7 + 0.3  # 공실률 반영 (기본 30% 유지)
                power_consumption += np.random.normal(0, 5)  # 노이즈 추가 (현실성 향상)
                power_consumption = max(0, power_consumption)  # 음수 방지
                
                # 데이터 포인트 생성
                buildings_data.append({
                    'building_id': f'B{building_id:03d}',  # 건물 ID (B001, B002, ...)
                    'timestamp': timestamp,  # 시간 정보
                    'power_consumption': round(power_consumption, 2),  # 전력 사용량 (kWh)
                    'temperature': round(temperature, 1),  # 온도 (°C)
                    'humidity': round(humidity, 1),  # 습도 (%)
                    'occupancy': round(occupancy, 1),  # 공실률 (%)
                    'floor': building_id,  # 층수
                    'room_type': 'office'  # 공간 유형
                })
        
        # DataFrame으로 변환
        df = pd.DataFrame(buildings_data)
        
        # CSV 파일로 저장
        output_path = self.processed_data_dir / "synthetic_building_data.csv"
        df.to_csv(output_path, index=False)
        
        logger.info(f"가상 건물 데이터 생성 완료! 저장 위치: {output_path}")
        logger.info(f"총 {len(df)} 개의 데이터 포인트 생성")
        
        return df
    
    def preprocess_uci_data(self):
        """UCI 데이터 전처리 및 정제"""
        logger.info("UCI 데이터 전처리 시작...")
        
        try:
            # 원본 데이터 로드
            data_path = self.raw_data_dir / "household_power_consumption.txt"
            df = pd.read_csv(data_path, sep=';', na_values=['?'])
            
            # 결측값 처리
            df = df.dropna()
            
            # 날짜/시간 데이터 변환
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
            df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
            df['timestamp'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))
            
            # 컬럼명을 한국어 친화적으로 변경
            df = df.rename(columns={
                'Global_active_power': 'power_consumption',  # 전력 사용량
                'Global_reactive_power': 'reactive_power',  # 무효 전력
                'Voltage': 'voltage',  # 전압
                'Global_intensity': 'current',  # 전류
                'Sub_metering_1': 'kitchen',  # 주방 전력
                'Sub_metering_2': 'laundry',  # 세탁실 전력
                'Sub_metering_3': 'heating_cooling'  # 냉난방 전력
            })
            
            # 필요한 컬럼만 선택
            columns_to_keep = ['timestamp', 'power_consumption', 'reactive_power', 
                             'voltage', 'current', 'kitchen', 'laundry', 'heating_cooling']
            df = df[columns_to_keep]
            
            # 데이터 타입 변환 (문자열 → 숫자)
            numeric_columns = ['power_consumption', 'reactive_power', 'voltage', 
                             'current', 'kitchen', 'laundry', 'heating_cooling']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 결측값 제거
            df = df.dropna()
            
            # 전처리된 데이터 저장
            output_path = self.processed_data_dir / "uci_processed_data.csv"
            df.to_csv(output_path, index=False)
            
            logger.info(f"UCI 데이터 전처리 완료! 저장 위치: {output_path}")
            return df
            
        except Exception as e:
            logger.error(f"UCI 데이터 전처리 실패: {e}")
            return None
    
    def create_data_summary(self):
        """데이터 요약 정보 생성 및 저장"""
        logger.info("데이터 요약 정보 생성...")
        
        summary = {
            'timestamp': datetime.now().isoformat(),  # 생성 시간
            'data_sources': [],  # 데이터 소스 목록
            'total_records': 0,  # 총 레코드 수
            'date_range': {},  # 날짜 범위
            'statistics': {}  # 통계 정보
        }
        
        # 처리된 데이터 파일들 확인
        processed_files = list(self.processed_data_dir.glob("*.csv"))
        
        for file_path in processed_files:
            try:
                df = pd.read_csv(file_path)
                file_name = file_path.stem
                
                # 파일별 요약 정보 생성
                file_summary = {
                    'file_name': file_name,  # 파일명
                    'records': len(df),  # 레코드 수
                    'columns': list(df.columns),  # 컬럼 목록
                    'date_range': {
                        'start': str(df['timestamp'].min()) if 'timestamp' in df.columns else 'N/A',
                        'end': str(df['timestamp'].max()) if 'timestamp' in df.columns else 'N/A'
                    },
                    'numeric_stats': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {}
                }
                
                summary['data_sources'].append(file_summary)
                summary['total_records'] += len(df)
                
            except Exception as e:
                logger.error(f"파일 {file_path} 처리 중 오류: {e}")
        
        # 요약 정보를 JSON 파일로 저장
        summary_path = self.data_dir / "data_summary.json"
        import json
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"데이터 요약 정보 저장 완료: {summary_path}")
        return summary

def main():
    """메인 실행 함수 - 데이터 수집 파이프라인"""
    collector = DataCollector()
    
    # 1. UCI 공개 데이터셋 다운로드 시도
    uci_success = collector.download_uci_household_data()
    
    if uci_success:
        # UCI 데이터 전처리
        collector.preprocess_uci_data()
    
    # 2. 가상 건물 데이터 생성 (항상 실행)
    collector.generate_synthetic_building_data()
    
    # 3. 데이터 요약 정보 생성
    collector.create_data_summary()
    
    logger.info("데이터 수집 완료!")

if __name__ == "__main__":
    main()
