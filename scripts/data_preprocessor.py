#!/usr/bin/env python3
"""
스마트 빌딩 에너지 관리 시스템 (SBEMS) - 데이터 전처리 파이프라인
최적화된 특성 엔지니어링 및 데이터 정제를 수행합니다.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.ensemble import IsolationForest
from scipy import stats
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartBuildingPreprocessor:
    """스마트 빌딩 에너지 데이터 전처리 클래스"""
    
    def __init__(self, data_path='data/processed/synthetic_building_data.csv'):
        self.data_path = data_path
        self.scalers = {}
        self.label_encoders = {}
        self.feature_columns = []
        self.target_column = 'power_consumption'
        
    def load_data(self):
        """데이터 로드 및 기본 정보 확인"""
        logger.info("데이터 로드 중...")
        self.df = pd.read_csv(self.data_path)
        logger.info(f"데이터 로드 완료: {self.df.shape}")
        
        # 타임스탬프 변환
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df = self.df.sort_values('timestamp').reset_index(drop=True)
        
        return self.df
    
    def create_time_features(self):
        """시계열 특성 생성"""
        logger.info("시계열 특성 생성 중...")
        
        # 기본 시간 특성
        self.df['hour'] = self.df['timestamp'].dt.hour
        self.df['day_of_week'] = self.df['timestamp'].dt.dayofweek
        self.df['month'] = self.df['timestamp'].dt.month
        self.df['day_of_year'] = self.df['timestamp'].dt.dayofyear
        self.df['week_of_year'] = self.df['timestamp'].dt.isocalendar().week
        
        # 계절 특성
        self.df['season'] = pd.cut(self.df['month'], 
                                  bins=[0, 3, 6, 9, 12], 
                                  labels=['겨울', '봄', '여름', '가을'])
        
        # 업무 관련 특성
        self.df['is_weekend'] = (self.df['day_of_week'] >= 5).astype(int)
        self.df['is_business_hour'] = ((self.df['hour'] >= 8) & (self.df['hour'] <= 18)).astype(int)
        self.df['is_peak_hour'] = ((self.df['hour'] >= 9) & (self.df['hour'] <= 17)).astype(int)
        self.df['is_night'] = ((self.df['hour'] >= 22) | (self.df['hour'] <= 6)).astype(int)
        
        # 시간대별 카테고리
        self.df['time_period'] = pd.cut(self.df['hour'], 
                                       bins=[0, 6, 12, 18, 24], 
                                       labels=['새벽', '오전', '오후', '저녁'])
        
        logger.info("시계열 특성 생성 완료")
        return self.df
    
    def create_temperature_features(self):
        """온도 관련 특성 생성"""
        logger.info("온도 관련 특성 생성 중...")
        
        # 온도 비선형 특성
        self.df['temperature_squared'] = self.df['temperature'] ** 2
        self.df['temperature_cubed'] = self.df['temperature'] ** 3
        
        # 온습도 상호작용
        self.df['temp_humidity_interaction'] = self.df['temperature'] * self.df['humidity']
        
        # 체감온도 (간단한 공식)
        self.df['feels_like_temp'] = (0.5 * self.df['temperature'] + 
                                     0.3 * self.df['humidity'] + 
                                     0.2 * (self.df['temperature'] * self.df['humidity'] / 100))
        
        # 난방/냉방도일
        base_temp = 18  # 기준온도
        self.df['heating_degree_days'] = np.maximum(base_temp - self.df['temperature'], 0)
        self.df['cooling_degree_days'] = np.maximum(self.df['temperature'] - base_temp, 0)
        
        # 쾌적구간
        self.df['comfort_zone'] = ((self.df['temperature'] >= 18) & 
                                  (self.df['temperature'] <= 26)).astype(int)
        
        # 온도 구간별 카테고리
        self.df['temp_category'] = pd.cut(self.df['temperature'], 
                                         bins=[-10, 0, 10, 20, 30, 50], 
                                         labels=['매우추움', '추움', '시원함', '따뜻함', '더움'])
        
        logger.info("온도 관련 특성 생성 완료")
        return self.df
    
    def create_occupancy_features(self):
        """공실률 관련 특성 생성"""
        logger.info("공실률 관련 특성 생성 중...")
        
        # 공실 이진 분류
        self.df['occupancy_binary'] = (self.df['occupancy'] > 0).astype(int)
        
        # 공실 수준 분류
        self.df['occupancy_level'] = pd.cut(self.df['occupancy'], 
                                           bins=[0, 20, 60, 100], 
                                           labels=['낮음', '보통', '높음'])
        
        # 시차 특성 (lag features)
        for lag in [1, 2, 3, 6, 12, 24]:
            self.df[f'occupancy_lag_{lag}h'] = self.df['occupancy'].shift(lag)
        
        # 이동평균
        for window in [3, 6, 12, 24]:
            self.df[f'occupancy_rolling_mean_{window}h'] = self.df['occupancy'].rolling(window=window).mean()
            self.df[f'occupancy_rolling_std_{window}h'] = self.df['occupancy'].rolling(window=window).std()
        
        # 공실 변화율
        self.df['occupancy_change_rate'] = self.df['occupancy'].pct_change()
        
        # 공실 패턴 특성
        self.df['occupancy_trend'] = self.df['occupancy'].rolling(window=6).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
        )
        
        logger.info("공실률 관련 특성 생성 완료")
        return self.df
    
    def create_building_features(self):
        """건물 관련 특성 생성"""
        logger.info("건물 관련 특성 생성 중...")
        
        # 건물별 가상 면적 (층수 기반)
        self.df['building_floor_area'] = self.df['floor'] * 500  # 층당 500m² 가정
        
        # 건물별 에너지 효율성 점수 (가상)
        building_efficiency = {
            'B001': 0.8, 'B002': 0.9, 'B003': 0.7, 'B004': 0.85, 'B005': 0.75
        }
        self.df['building_efficiency_score'] = self.df['building_id'].map(building_efficiency)
        
        # 층수별 특성
        self.df['floor_height_factor'] = self.df['floor'] * 3  # 층당 3m 높이
        self.df['is_ground_floor'] = (self.df['floor'] == 1).astype(int)
        self.df['is_top_floor'] = (self.df['floor'] == 5).astype(int)
        
        # 건물별 평균 전력 사용량
        building_avg_power = self.df.groupby('building_id')['power_consumption'].mean()
        self.df['building_avg_power'] = self.df['building_id'].map(building_avg_power)
        
        # 건물별 전력 사용 패턴 (표준편차)
        building_power_std = self.df.groupby('building_id')['power_consumption'].std()
        self.df['building_power_std'] = self.df['building_id'].map(building_power_std)
        
        logger.info("건물 관련 특성 생성 완료")
        return self.df
    
    def create_power_features(self):
        """전력 사용량 관련 특성 생성"""
        logger.info("전력 사용량 관련 특성 생성 중...")
        
        # 전력 사용량 변화율
        self.df['power_change_rate'] = self.df['power_consumption'].pct_change()
        
        # 전력 사용량 이동평균
        for window in [3, 6, 12, 24]:
            self.df[f'power_rolling_mean_{window}h'] = self.df['power_consumption'].rolling(window=window).mean()
            self.df[f'power_rolling_std_{window}h'] = self.df['power_consumption'].rolling(window=window).std()
        
        # 전력 사용량 트렌드
        self.df['power_trend'] = self.df['power_consumption'].rolling(window=6).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
        )
        
        # 전력 사용량 분위수
        self.df['power_quantile'] = pd.qcut(self.df['power_consumption'], 
                                           q=5, labels=['매우낮음', '낮음', '보통', '높음', '매우높음'])
        
        # 전력 사용량 구간
        self.df['power_category'] = pd.cut(self.df['power_consumption'], 
                                          bins=[0, 10, 30, 60, 100, 200], 
                                          labels=['미사용', '저전력', '보통', '고전력', '최고전력'])
        
        logger.info("전력 사용량 관련 특성 생성 완료")
        return self.df
    
    def handle_missing_values(self):
        """결측값 처리"""
        logger.info("결측값 처리 중...")
        
        initial_missing = self.df.isnull().sum().sum()
        if initial_missing == 0:
            logger.info("결측값이 없습니다.")
            return self.df
        
        # 시계열 데이터의 경우 전진 채우기(forward fill) 사용
        self.df = self.df.fillna(method='ffill')
        
        # 여전히 남은 결측값은 후진 채우기(backward fill) 사용
        self.df = self.df.fillna(method='bfill')
        
        # 숫자형 컬럼의 경우 평균값으로 채우기
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns
        self.df[numeric_columns] = self.df[numeric_columns].fillna(self.df[numeric_columns].mean())
        
        final_missing = self.df.isnull().sum().sum()
        logger.info(f"결측값 처리 완료: {initial_missing} -> {final_missing}")
        
        return self.df
    
    def detect_and_handle_outliers(self, method='isolation_forest'):
        """이상치 탐지 및 처리"""
        logger.info("이상치 탐지 및 처리 중...")
        
        # 전력 사용량 이상치 탐지
        power_consumption = self.df['power_consumption'].values.reshape(-1, 1)
        
        if method == 'isolation_forest':
            # Isolation Forest 사용
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outliers = iso_forest.fit_predict(power_consumption)
            outlier_indices = np.where(outliers == -1)[0]
        
        elif method == 'iqr':
            # IQR 방법
            Q1 = self.df['power_consumption'].quantile(0.25)
            Q3 = self.df['power_consumption'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outlier_indices = self.df[
                (self.df['power_consumption'] < lower_bound) | 
                (self.df['power_consumption'] > upper_bound)
            ].index
        
        elif method == 'zscore':
            # Z-score 방법
            z_scores = np.abs(stats.zscore(power_consumption))
            outlier_indices = np.where(z_scores > 3)[0]
        
        # 이상치를 중앙값으로 대체
        if len(outlier_indices) > 0:
            median_power = self.df['power_consumption'].median()
            self.df.loc[outlier_indices, 'power_consumption'] = median_power
            logger.info(f"이상치 처리 완료: {len(outlier_indices)}개 이상치를 중앙값으로 대체")
        else:
            logger.info("이상치가 발견되지 않았습니다.")
        
        return self.df
    
    def encode_categorical_features(self):
        """범주형 특성 인코딩"""
        logger.info("범주형 특성 인코딩 중...")
        
        categorical_columns = ['building_id', 'room_type', 'season', 'time_period', 
                              'temp_category', 'occupancy_level', 'power_quantile', 'power_category']
        
        for col in categorical_columns:
            if col in self.df.columns:
                # Label Encoding
                le = LabelEncoder()
                self.df[f'{col}_encoded'] = le.fit_transform(self.df[col].astype(str))
                self.label_encoders[col] = le
                
                # One-Hot Encoding (선택적)
                if col in ['building_id', 'season', 'time_period']:
                    dummies = pd.get_dummies(self.df[col], prefix=col)
                    self.df = pd.concat([self.df, dummies], axis=1)
        
        logger.info("범주형 특성 인코딩 완료")
        return self.df
    
    def scale_numerical_features(self, method='standard'):
        """수치형 특성 스케일링"""
        logger.info("수치형 특성 스케일링 중...")
        
        # 스케일링할 수치형 컬럼 선택
        numerical_columns = [
            'temperature', 'humidity', 'occupancy', 'floor',
            'temperature_squared', 'temperature_cubed', 'temp_humidity_interaction',
            'feels_like_temp', 'heating_degree_days', 'cooling_degree_days',
            'building_floor_area', 'building_efficiency_score', 'floor_height_factor',
            'building_avg_power', 'building_power_std'
        ]
        
        # 실제 존재하는 컬럼만 선택
        existing_columns = [col for col in numerical_columns if col in self.df.columns]
        
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        
        # 스케일링 적용
        self.df[existing_columns] = scaler.fit_transform(self.df[existing_columns])
        self.scalers['numerical'] = scaler
        
        logger.info(f"수치형 특성 스케일링 완료: {len(existing_columns)}개 컬럼")
        return self.df
    
    def create_interaction_features(self):
        """상호작용 특성 생성"""
        logger.info("상호작용 특성 생성 중...")
        
        # 온도와 공실률 상호작용
        self.df['temp_occupancy_interaction'] = self.df['temperature'] * self.df['occupancy']
        
        # 시간대와 공실률 상호작용
        self.df['hour_occupancy_interaction'] = self.df['hour'] * self.df['occupancy']
        
        # 건물 효율성과 전력 사용량 상호작용
        self.df['efficiency_power_interaction'] = self.df['building_efficiency_score'] * self.df['power_consumption']
        
        # 업무시간과 공실률 상호작용
        self.df['business_occupancy_interaction'] = self.df['is_business_hour'] * self.df['occupancy']
        
        # 계절과 온도 상호작용
        season_encoded = self.df['season'].astype('category').cat.codes
        self.df['season_temp_interaction'] = season_encoded * self.df['temperature']
        
        logger.info("상호작용 특성 생성 완료")
        return self.df
    
    def select_features(self):
        """최종 특성 선택"""
        logger.info("최종 특성 선택 중...")
        
        # 제거할 컬럼들
        columns_to_drop = [
            'timestamp',  # 시간 정보는 이미 특성으로 추출됨
            'season', 'time_period', 'temp_category', 'occupancy_level',  # 원본 범주형
            'power_quantile', 'power_category'  # 원본 범주형
        ]
        
        # 실제 존재하는 컬럼만 제거
        existing_drop_columns = [col for col in columns_to_drop if col in self.df.columns]
        self.df = self.df.drop(columns=existing_drop_columns)
        
        # 특성 컬럼 목록 저장
        self.feature_columns = [col for col in self.df.columns 
                               if col not in [self.target_column, 'index']]
        
        logger.info(f"최종 특성 선택 완료: {len(self.feature_columns)}개 특성")
        return self.df
    
    def get_feature_importance_preview(self):
        """특성 중요도 미리보기 (상관관계 기반)"""
        logger.info("특성 중요도 분석 중...")
        
        # 수치형 컬럼만 선택하여 상관관계 계산
        numeric_columns = self.df[self.feature_columns].select_dtypes(include=[np.number]).columns.tolist()
        numeric_columns.append(self.target_column)
        
        # 타겟과의 상관관계 계산
        correlations = self.df[numeric_columns].corr()[self.target_column].abs()
        correlations = correlations.sort_values(ascending=False)
        
        # 상위 20개 특성 출력
        top_features = correlations.head(20)
        logger.info("상위 20개 중요 특성:")
        for feature, corr in top_features.items():
            if feature != self.target_column:
                logger.info(f"  {feature}: {corr:.4f}")
        
        return top_features
    
    def save_processed_data(self, output_path='data/processed/preprocessed_building_data.csv'):
        """전처리된 데이터 저장"""
        logger.info("전처리된 데이터 저장 중...")
        
        # 전처리 정보 저장
        preprocessing_info = {
            'timestamp': datetime.now().isoformat(),
            'original_shape': (43800, 8),  # 원본 데이터 크기
            'processed_shape': self.df.shape,
            'feature_count': len(self.feature_columns),
            'target_column': self.target_column,
            'scalers_used': list(self.scalers.keys()),
            'encoders_used': list(self.label_encoders.keys())
        }
        
        # 데이터 저장
        self.df.to_csv(output_path, index=False)
        
        # 전처리 정보를 JSON으로 저장
        import json
        with open('data/processed/preprocessing_info.json', 'w', encoding='utf-8') as f:
            json.dump(preprocessing_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"전처리 완료! 저장 위치: {output_path}")
        logger.info(f"최종 데이터 크기: {self.df.shape}")
        
        return output_path
    
    def run_full_pipeline(self):
        """전체 전처리 파이프라인 실행"""
        logger.info("=== 스마트 빌딩 에너지 데이터 전처리 파이프라인 시작 ===")
        
        # 1. 데이터 로드
        self.load_data()
        
        # 2. 시계열 특성 생성
        self.create_time_features()
        
        # 3. 온도 관련 특성 생성
        self.create_temperature_features()
        
        # 4. 공실률 관련 특성 생성
        self.create_occupancy_features()
        
        # 5. 건물 관련 특성 생성
        self.create_building_features()
        
        # 6. 전력 사용량 관련 특성 생성
        self.create_power_features()
        
        # 7. 상호작용 특성 생성
        self.create_interaction_features()
        
        # 8. 결측값 처리
        self.handle_missing_values()
        
        # 9. 이상치 처리
        self.detect_and_handle_outliers()
        
        # 10. 범주형 특성 인코딩
        self.encode_categorical_features()
        
        # 11. 수치형 특성 스케일링
        self.scale_numerical_features()
        
        # 12. 최종 특성 선택
        self.select_features()
        
        # 13. 특성 중요도 미리보기
        self.get_feature_importance_preview()
        
        # 14. 데이터 저장
        output_path = self.save_processed_data()
        
        logger.info("=== 전처리 파이프라인 완료 ===")
        
        return self.df, output_path

if __name__ == "__main__":
    # 전처리 파이프라인 실행
    preprocessor = SmartBuildingPreprocessor()
    processed_df, output_path = preprocessor.run_full_pipeline()
    
    print(f"\n🎉 전처리 완료!")
    print(f"📊 최종 데이터 크기: {processed_df.shape}")
    print(f"💾 저장 위치: {output_path}")
    print(f"🎯 타겟 변수: {preprocessor.target_column}")
    print(f"🔧 특성 개수: {len(preprocessor.feature_columns)}")
