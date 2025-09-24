#!/usr/bin/env python3
"""
합성 데이터 생성기 - 대용량 원본 데이터 대체
원본 데이터의 통계적 특성을 기반으로 합성 데이터를 생성
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

class SyntheticDataGenerator:
    """합성 데이터 생성기"""
    
    def __init__(self):
        self.random_seed = 42
        np.random.seed(self.random_seed)
        
    def generate_household_power_data(self, num_records=10000):
        """가전제품 전력 소비 합성 데이터 생성"""
        print("🏠 가전제품 전력 소비 합성 데이터 생성 중...")
        
        # 기본 통계 (원본 데이터 기반)
        base_stats = {
            'global_active_power': {'mean': 1.1, 'std': 1.0, 'min': 0.0, 'max': 8.0},
            'global_reactive_power': {'mean': 0.12, 'std': 0.1, 'min': 0.0, 'max': 1.4},
            'voltage': {'mean': 240.0, 'std': 3.0, 'min': 230.0, 'max': 250.0},
            'global_intensity': {'mean': 4.6, 'std': 4.0, 'min': 0.2, 'max': 48.0},
            'sub_metering_1': {'mean': 1.1, 'std': 6.0, 'min': 0.0, 'max': 88.0},
            'sub_metering_2': {'mean': 1.3, 'std': 5.0, 'min': 0.0, 'max': 80.0},
            'sub_metering_3': {'mean': 6.5, 'std': 8.0, 'min': 0.0, 'max': 31.0}
        }
        
        # 날짜 범위 생성
        start_date = datetime(2006, 12, 16, 17, 24, 0)
        dates = [start_date + timedelta(minutes=i) for i in range(num_records)]
        
        # 합성 데이터 생성
        data = []
        for i, date in enumerate(dates):
            # 계절성 및 시간 패턴 반영
            hour = date.hour
            day_of_week = date.weekday()
            
            # 시간대별 전력 사용량 조정
            time_factor = self._get_time_factor(hour, day_of_week)
            
            record = {
                'Date': date.strftime('%d/%m/%Y'),
                'Time': date.strftime('%H:%M:%S'),
                'Global_active_power': max(0, np.random.normal(
                    base_stats['global_active_power']['mean'] * time_factor,
                    base_stats['global_active_power']['std']
                )),
                'Global_reactive_power': max(0, np.random.normal(
                    base_stats['global_reactive_power']['mean'] * time_factor,
                    base_stats['global_reactive_power']['std']
                )),
                'Voltage': np.random.normal(
                    base_stats['voltage']['mean'],
                    base_stats['voltage']['std']
                ),
                'Global_intensity': max(0.2, np.random.normal(
                    base_stats['global_intensity']['mean'] * time_factor,
                    base_stats['global_intensity']['std']
                )),
                'Sub_metering_1': max(0, np.random.normal(
                    base_stats['sub_metering_1']['mean'] * time_factor,
                    base_stats['sub_metering_1']['std']
                )),
                'Sub_metering_2': max(0, np.random.normal(
                    base_stats['sub_metering_2']['mean'] * time_factor,
                    base_stats['sub_metering_2']['std']
                )),
                'Sub_metering_3': max(0, np.random.normal(
                    base_stats['sub_metering_3']['mean'] * time_factor,
                    base_stats['sub_metering_3']['std']
                ))
            }
            
            # 값 범위 제한
            for key, value in record.items():
                if key in ['Date', 'Time']:
                    continue
                if key in base_stats:
                    record[key] = max(
                        base_stats[key]['min'],
                        min(base_stats[key]['max'], value)
                    )
            
            data.append(record)
        
        df = pd.DataFrame(data)
        print(f"✅ {num_records:,}개의 합성 데이터 생성 완료")
        
        return df
    
    def _get_time_factor(self, hour, day_of_week):
        """시간대별 전력 사용량 팩터 계산"""
        # 주말 vs 평일
        weekend_factor = 0.8 if day_of_week >= 5 else 1.0
        
        # 시간대별 패턴 (새벽: 낮음, 저녁: 높음)
        if 0 <= hour <= 6:
            time_factor = 0.3  # 새벽
        elif 7 <= hour <= 11:
            time_factor = 0.8  # 오전
        elif 12 <= hour <= 17:
            time_factor = 1.0  # 오후
        elif 18 <= hour <= 22:
            time_factor = 1.3  # 저녁
        else:
            time_factor = 0.6  # 밤
        
        return time_factor * weekend_factor
    
    def save_synthetic_data(self, df, output_path):
        """합성 데이터 저장"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"💾 합성 데이터 저장: {output_path}")
        
        # 메타데이터 저장
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'num_records': len(df),
            'columns': list(df.columns),
            'data_type': 'synthetic_household_power_consumption',
            'description': '원본 데이터의 통계적 특성을 기반으로 생성된 합성 데이터',
            'note': 'GitHub 파일 크기 제한으로 인해 원본 대용량 파일 대체'
        }
        
        metadata_path = output_path.replace('.csv', '_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📊 메타데이터 저장: {metadata_path}")

def main():
    """메인 실행 함수"""
    print("🚀 합성 데이터 생성기 시작")
    
    generator = SyntheticDataGenerator()
    
    # 합성 데이터 생성 (원본 127MB → 합성 1-2MB)
    synthetic_df = generator.generate_household_power_data(num_records=50000)
    
    # 저장
    output_path = 'data/raw/synthetic_household_power_consumption.csv'
    generator.save_synthetic_data(synthetic_df, output_path)
    
    print("✅ 합성 데이터 생성 완료!")
    print(f"📁 저장 위치: {output_path}")
    print(f"📊 데이터 크기: {len(synthetic_df):,} 행")

if __name__ == "__main__":
    main()
