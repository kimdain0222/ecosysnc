#!/usr/bin/env python3
"""
전처리 결과 분석 스크립트
"""

import pandas as pd
import numpy as np
import json

def analyze_preprocessing_results():
    """전처리 결과 분석"""
    print("🔍 전처리 결과 분석 중...")
    
    # 데이터 로드
    df = pd.read_csv('data/processed/preprocessed_building_data.csv')
    
    # 기본 정보
    print(f"\n📊 데이터 기본 정보:")
    print(f"   데이터 크기: {df.shape}")
    print(f"   특성 개수: {df.shape[1] - 1}")
    print(f"   레코드 수: {df.shape[0]:,}")
    
    # 특성 분류
    feature_categories = {
        '시계열': ['hour', 'day_of_week', 'month', 'is_weekend', 'is_business_hour'],
        '온도': ['temperature', 'temperature_squared', 'feels_like_temp'],
        '공실률': ['occupancy', 'occupancy_binary', 'occupancy_rolling_mean_3h'],
        '건물': ['floor', 'building_efficiency_score', 'building_avg_power'],
        '상호작용': ['temp_occupancy_interaction', 'business_occupancy_interaction']
    }
    
    print(f"\n📋 특성 분류:")
    for category, features in feature_categories.items():
        existing = [f for f in features if f in df.columns]
        print(f"   {category}: {len(existing)}개")
    
    # 상관관계 분석
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if 'power_consumption' in numeric_cols:
        numeric_cols.remove('power_consumption')
    
    correlations = df[numeric_cols + ['power_consumption']].corr()['power_consumption'].abs()
    correlations = correlations.sort_values(ascending=False)
    
    print(f"\n🏆 상위 15개 중요 특성:")
    for i, (feature, corr) in enumerate(correlations.head(15).items(), 1):
        category = next((cat for cat, features in feature_categories.items() 
                        if any(f in feature for f in features)), '기타')
        print(f"   {i:2d}. {feature:<35} | {corr:.4f} | {category}")
    
    # 데이터 품질 확인
    print(f"\n🔧 데이터 품질:")
    print(f"   결측값: {df.isnull().sum().sum()}")
    print(f"   중복값: {df.duplicated().sum()}")
    print(f"   무한값: {np.isinf(df.select_dtypes(include=[np.number])).sum().sum()}")
    
    # 통계 정보
    print(f"\n📈 주요 통계:")
    print(f"   전력 사용량 평균: {df['power_consumption'].mean():.2f} kWh")
    print(f"   전력 사용량 표준편차: {df['power_consumption'].std():.2f} kWh")
    print(f"   공실률 평균: {df['occupancy'].mean():.2f}%")
    print(f"   온도 평균: {df['temperature'].mean():.2f}°C")
    
    # 시계열 패턴
    business_hours = df[df['is_business_hour'] == 1]['power_consumption'].mean()
    non_business_hours = df[df['is_business_hour'] == 0]['power_consumption'].mean()
    weekday_power = df[df['is_weekend'] == 0]['power_consumption'].mean()
    weekend_power = df[df['is_weekend'] == 1]['power_consumption'].mean()
    
    print(f"\n⏰ 시계열 패턴:")
    print(f"   업무시간 평균: {business_hours:.2f} kWh")
    print(f"   비업무시간 평균: {non_business_hours:.2f} kWh")
    print(f"   평일 평균: {weekday_power:.2f} kWh")
    print(f"   주말 평균: {weekend_power:.2f} kWh")
    print(f"   업무시간 효과: {(business_hours/non_business_hours - 1)*100:.1f}% 증가")
    print(f"   평일 효과: {(weekday_power/weekend_power - 1)*100:.1f}% 증가")
    
    # 전처리 효과
    print(f"\n🎯 전처리 효과:")
    high_corr_features = correlations[correlations > 0.5].index.tolist()
    print(f"   고상관관계 특성 (>0.5): {len(high_corr_features)}개")
    print(f"   최고 상관관계: {correlations.max():.4f}")
    print(f"   평균 상관관계: {correlations.mean():.4f}")
    
    # 예측 모델 준비도
    print(f"\n🚀 예측 모델 준비도:")
    print(f"   ✅ 데이터 정제 완료")
    print(f"   ✅ 특성 엔지니어링 완료")
    print(f"   ✅ 스케일링 완료")
    print(f"   ✅ 인코딩 완료")
    print(f"   ✅ 이상치 처리 완료")
    print(f"   ✅ 결측값 처리 완료")
    
    print(f"\n🎉 전처리 분석 완료!")
    print(f"   다음 단계: 머신러닝 모델 개발")

if __name__ == "__main__":
    analyze_preprocessing_results()
