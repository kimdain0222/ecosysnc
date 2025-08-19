#!/usr/bin/env python3
"""
스마트 빌딩 에너지 관리 시스템 (SBEMS) - 머신러닝 모델 개발
최적화된 전처리 데이터를 활용한 예측 모델 개발
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 머신러닝 라이브러리
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb

# 시계열 특화 모델
from sklearn.ensemble import IsolationForest
import joblib
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartBuildingMLModels:
    """스마트 빌딩 에너지 예측 모델 클래스"""
    
    def __init__(self, data_path='data/processed/preprocessed_building_data.csv'):
        self.data_path = data_path
        self.models = {}
        self.model_scores = {}
        self.feature_importance = {}
        self.best_model = None
        self.scaler = StandardScaler()
        
    def load_and_prepare_data(self):
        """데이터 로드 및 모델 학습 준비"""
        logger.info("데이터 로드 및 모델 학습 준비 중...")
        
        # 전처리된 데이터 로드
        self.df = pd.read_csv(self.data_path)
        
        # 수치형 특성만 선택
        numeric_features = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 타겟 변수 분리
        self.target = 'power_consumption'
        if self.target in numeric_features:
            numeric_features.remove(self.target)
        
        # 특성과 타겟 분리
        self.X = self.df[numeric_features]
        self.y = self.df[self.target]
        
        # 무한값 처리
        self.X = self.X.replace([np.inf, -np.inf], np.nan)
        self.X = self.X.fillna(self.X.median())
        
        # 훈련/테스트 분할 (시계열 고려)
        train_size = int(len(self.X) * 0.8)
        self.X_train = self.X[:train_size]
        self.X_test = self.X[train_size:]
        self.y_train = self.y[:train_size]
        self.y_test = self.y[train_size:]
        
        # 특성 스케일링
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        logger.info(f"데이터 준비 완료: {self.X_train.shape[0]} 훈련, {self.X_test.shape[0]} 테스트")
        logger.info(f"특성 개수: {self.X_train.shape[1]}")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def evaluate_model(self, model, X_train, X_test, y_train, y_test, model_name):
        """모델 평가"""
        # 훈련 및 예측
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # 평가 지표 계산
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # 상대 오차 계산
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        # 교차 검증
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
        
        results = {
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2,
            'MAPE': mape,
            'CV_R2_mean': cv_scores.mean(),
            'CV_R2_std': cv_scores.std()
        }
        
        logger.info(f"{model_name} 성능:")
        logger.info(f"  RMSE: {rmse:.4f}")
        logger.info(f"  MAE: {mae:.4f}")
        logger.info(f"  R²: {r2:.4f}")
        logger.info(f"  MAPE: {mape:.2f}%")
        logger.info(f"  CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        return model, results, y_pred
    
    def train_linear_models(self):
        """선형 모델 훈련"""
        logger.info("=== 선형 모델 훈련 시작 ===")
        
        # 1. Linear Regression
        logger.info("Linear Regression 훈련 중...")
        lr_model, lr_results, lr_pred = self.evaluate_model(
            LinearRegression(), self.X_train_scaled, self.X_test_scaled, 
            self.y_train, self.y_test, "Linear Regression"
        )
        self.models['Linear_Regression'] = lr_model
        self.model_scores['Linear_Regression'] = lr_results
        
        # 2. Ridge Regression
        logger.info("Ridge Regression 훈련 중...")
        ridge_model, ridge_results, ridge_pred = self.evaluate_model(
            Ridge(alpha=1.0), self.X_train_scaled, self.X_test_scaled, 
            self.y_train, self.y_test, "Ridge Regression"
        )
        self.models['Ridge_Regression'] = ridge_model
        self.model_scores['Ridge_Regression'] = ridge_results
        
        # 3. Lasso Regression
        logger.info("Lasso Regression 훈련 중...")
        lasso_model, lasso_results, lasso_pred = self.evaluate_model(
            Lasso(alpha=0.1), self.X_train_scaled, self.X_test_scaled, 
            self.y_train, self.y_test, "Lasso Regression"
        )
        self.models['Lasso_Regression'] = lasso_model
        self.model_scores['Lasso_Regression'] = lasso_results
        
        return lr_pred, ridge_pred, lasso_pred
    
    def train_ensemble_models(self):
        """앙상블 모델 훈련"""
        logger.info("=== 앙상블 모델 훈련 시작 ===")
        
        # 1. Random Forest
        logger.info("Random Forest 훈련 중...")
        rf_model, rf_results, rf_pred = self.evaluate_model(
            RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            self.X_train, self.X_test, self.y_train, self.y_test, "Random Forest"
        )
        self.models['Random_Forest'] = rf_model
        self.model_scores['Random_Forest'] = rf_results
        self.feature_importance['Random_Forest'] = rf_model.feature_importances_
        
        # 2. Gradient Boosting
        logger.info("Gradient Boosting 훈련 중...")
        gb_model, gb_results, gb_pred = self.evaluate_model(
            GradientBoostingRegressor(n_estimators=100, random_state=42),
            self.X_train, self.X_test, self.y_train, self.y_test, "Gradient Boosting"
        )
        self.models['Gradient_Boosting'] = gb_model
        self.model_scores['Gradient_Boosting'] = gb_results
        self.feature_importance['Gradient_Boosting'] = gb_model.feature_importances_
        
        # 3. XGBoost
        logger.info("XGBoost 훈련 중...")
        xgb_model, xgb_results, xgb_pred = self.evaluate_model(
            xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            self.X_train, self.X_test, self.y_train, self.y_test, "XGBoost"
        )
        self.models['XGBoost'] = xgb_model
        self.model_scores['XGBoost'] = xgb_results
        self.feature_importance['XGBoost'] = xgb_model.feature_importances_
        
        # 4. LightGBM
        logger.info("LightGBM 훈련 중...")
        lgb_model, lgb_results, lgb_pred = self.evaluate_model(
            lgb.LGBMRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            self.X_train, self.X_test, self.y_train, self.y_test, "LightGBM"
        )
        self.models['LightGBM'] = lgb_model
        self.model_scores['LightGBM'] = lgb_results
        self.feature_importance['LightGBM'] = lgb_model.feature_importances_
        
        return rf_pred, gb_pred, xgb_pred, lgb_pred
    
    def train_svm_model(self):
        """SVM 모델 훈련"""
        logger.info("=== SVM 모델 훈련 시작 ===")
        
        # SVM (커널 트릭 사용)
        logger.info("SVM 훈련 중...")
        svm_model, svm_results, svm_pred = self.evaluate_model(
            SVR(kernel='rbf', C=1.0, gamma='scale'),
            self.X_train_scaled, self.X_test_scaled, 
            self.y_train, self.y_test, "SVM"
        )
        self.models['SVM'] = svm_model
        self.model_scores['SVM'] = svm_results
        
        return svm_pred
    
    def hyperparameter_tuning(self, model_name='XGBoost'):
        """하이퍼파라미터 튜닝"""
        logger.info(f"=== {model_name} 하이퍼파라미터 튜닝 시작 ===")
        
        if model_name == 'XGBoost':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0],
                'colsample_bytree': [0.8, 0.9, 1.0]
            }
            base_model = xgb.XGBRegressor(random_state=42)
        
        elif model_name == 'Random_Forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            base_model = RandomForestRegressor(random_state=42, n_jobs=-1)
        
        # Grid Search
        grid_search = GridSearchCV(
            base_model, param_grid, cv=5, scoring='r2', n_jobs=-1, verbose=1
        )
        grid_search.fit(self.X_train, self.y_train)
        
        # 최적 모델 평가
        best_model = grid_search.best_estimator_
        best_model, best_results, best_pred = self.evaluate_model(
            best_model, self.X_train, self.X_test, 
            self.y_train, self.y_test, f"Tuned {model_name}"
        )
        
        logger.info(f"최적 파라미터: {grid_search.best_params_}")
        
        self.models[f'Tuned_{model_name}'] = best_model
        self.model_scores[f'Tuned_{model_name}'] = best_results
        
        return best_model, best_results, best_pred
    
    def compare_models(self):
        """모델 성능 비교"""
        logger.info("=== 모델 성능 비교 ===")
        
        # 결과 테이블 생성
        results_df = pd.DataFrame(self.model_scores).T
        
        # 성능 순위
        results_df['Rank'] = results_df['R2'].rank(ascending=False)
        results_df = results_df.sort_values('Rank')
        
        logger.info("\n모델 성능 순위:")
        for idx, (model_name, row) in enumerate(results_df.iterrows(), 1):
            logger.info(f"{idx:2d}. {model_name:<20} | R²: {row['R2']:.4f} | RMSE: {row['RMSE']:.4f} | MAPE: {row['MAPE']:.2f}%")
        
        # 최고 성능 모델 선택
        best_model_name = results_df.index[0]
        self.best_model = self.models[best_model_name]
        
        logger.info(f"\n🏆 최고 성능 모델: {best_model_name}")
        logger.info(f"   R² Score: {results_df.loc[best_model_name, 'R2']:.4f}")
        logger.info(f"   RMSE: {results_df.loc[best_model_name, 'RMSE']:.4f}")
        logger.info(f"   MAPE: {results_df.loc[best_model_name, 'MAPE']:.2f}%")
        
        return results_df
    
    def analyze_feature_importance(self, model_name='XGBoost'):
        """특성 중요도 분석"""
        logger.info(f"=== {model_name} 특성 중요도 분석 ===")
        
        if model_name in self.feature_importance:
            importance = self.feature_importance[model_name]
            feature_names = self.X_train.columns
            
            # 중요도 데이터프레임 생성
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            # 상위 20개 특성 출력
            logger.info("상위 20개 중요 특성:")
            for i, (_, row) in enumerate(importance_df.head(20).iterrows(), 1):
                logger.info(f"{i:2d}. {row['feature']:<35} | {row['importance']:.4f}")
            
            return importance_df
        
        else:
            logger.warning(f"{model_name}의 특성 중요도 정보가 없습니다.")
            return None
    
    def save_models(self, output_dir='models/'):
        """모델 저장"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("모델 저장 중...")
        
        # 각 모델 저장
        for model_name, model in self.models.items():
            model_path = os.path.join(output_dir, f'{model_name}.pkl')
            joblib.dump(model, model_path)
            logger.info(f"  {model_name} 저장: {model_path}")
        
        # 스케일러 저장
        scaler_path = os.path.join(output_dir, 'scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"  Scaler 저장: {scaler_path}")
        
        # 모델 성능 결과 저장
        results_df = pd.DataFrame(self.model_scores).T
        results_path = os.path.join(output_dir, 'model_performance.csv')
        results_df.to_csv(results_path)
        logger.info(f"  성능 결과 저장: {results_path}")
        
        # 특성 중요도 저장
        if self.feature_importance:
            importance_df = self.analyze_feature_importance('XGBoost')
            if importance_df is not None:
                importance_path = os.path.join(output_dir, 'feature_importance.csv')
                importance_df.to_csv(importance_path, index=False)
                logger.info(f"  특성 중요도 저장: {importance_path}")
    
    def run_full_pipeline(self):
        """전체 머신러닝 파이프라인 실행"""
        logger.info("=== 스마트 빌딩 에너지 머신러닝 파이프라인 시작 ===")
        
        # 1. 데이터 준비
        self.load_and_prepare_data()
        
        # 2. 선형 모델 훈련
        self.train_linear_models()
        
        # 3. 앙상블 모델 훈련
        self.train_ensemble_models()
        
        # 4. SVM 모델 훈련
        self.train_svm_model()
        
        # 5. 하이퍼파라미터 튜닝 (XGBoost)
        self.hyperparameter_tuning('XGBoost')
        
        # 6. 모델 성능 비교
        results_df = self.compare_models()
        
        # 7. 특성 중요도 분석
        self.analyze_feature_importance('XGBoost')
        
        # 8. 모델 저장
        self.save_models()
        
        logger.info("=== 머신러닝 파이프라인 완료 ===")
        
        return results_df

if __name__ == "__main__":
    # 머신러닝 파이프라인 실행
    ml_pipeline = SmartBuildingMLModels()
    results = ml_pipeline.run_full_pipeline()
    
    print(f"\n🎉 머신러닝 모델 개발 완료!")
    print(f"🏆 최고 성능 모델: {results.index[0]}")
    print(f"📊 R² Score: {results.iloc[0]['R2']:.4f}")
    print(f"📈 RMSE: {results.iloc[0]['RMSE']:.4f}")
    print(f"📉 MAPE: {results.iloc[0]['MAPE']:.2f}%")
    print(f"💾 모델 저장 위치: models/")


