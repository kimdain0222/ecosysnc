# 🚀 구글 코랩에서 스마트 빌딩 에너지 모델 실행 가이드

## 📋 준비사항

### 1. 필요한 파일들
다음 파일들을 준비해주세요:
- `models/Tuned_XGBoost.pkl` (최고 성능 모델)
- `models/scaler.pkl` (특성 스케일러)
- `models/model_performance.csv` (모델 성능 결과)
- `models/feature_importance.csv` (특성 중요도)
- `data/processed/preprocessed_building_data.csv` (전처리된 데이터)

### 2. 구글 코랩 설정
1. [Google Colab](https://colab.research.google.com/) 접속
2. 새 노트북 생성
3. 런타임 → 런타임 유형 변경 → GPU (선택사항)

## 🎯 실행 방법

### 1단계: 라이브러리 설치 및 임포트

```python
# 필요한 라이브러리 설치
!pip install xgboost lightgbm joblib plotly

# 라이브러리 임포트
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
warnings.filterwarnings('ignore')

print("✅ 환경 설정 완료!")
```

### 2단계: 파일 업로드

```python
from google.colab import files
import os

# models 폴더 생성
os.makedirs('models', exist_ok=True)

print("📁 models 폴더가 생성되었습니다.")
print("\n📤 다음 파일들을 업로드해주세요:")
print("   - Tuned_XGBoost.pkl")
print("   - scaler.pkl")
print("   - model_performance.csv")
print("   - feature_importance.csv")

# 파일 업로드
uploaded = files.upload()

# 업로드된 파일들을 models 폴더로 이동
for filename in uploaded.keys():
    if filename.endswith('.pkl') or filename.endswith('.csv'):
        os.rename(filename, f'models/{filename}')
        print(f"✅ {filename} 업로드 완료")

print("\n🎉 모든 파일 업로드 완료!")
```

### 3단계: 모델 로드

```python
# 모델 및 스케일러 로드
try:
    best_model = joblib.load('models/Tuned_XGBoost.pkl')
    scaler = joblib.load('models/scaler.pkl')
    
    print("✅ 모델 로드 완료!")
    print(f"🏆 최고 성능 모델: Tuned XGBoost")
    
except FileNotFoundError:
    print("❌ 모델 파일을 찾을 수 없습니다.")
    best_model = None
    scaler = None
```

### 4단계: 모델 성능 확인

```python
# 모델 성능 결과 확인
try:
    performance_df = pd.read_csv('models/model_performance.csv', index_col=0)
    
    print("📊 모델 성능 비교:")
    print(performance_df[['R2', 'RMSE', 'MAPE']].round(4))
    
    # 성능 시각화
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # R² Score 비교
    axes[0].bar(performance_df.index, performance_df['R2'])
    axes[0].set_title('R² Score 비교')
    axes[0].set_ylabel('R² Score')
    axes[0].tick_params(axis='x', rotation=45)
    
    # RMSE 비교
    axes[1].bar(performance_df.index, performance_df['RMSE'])
    axes[1].set_title('RMSE 비교')
    axes[1].set_ylabel('RMSE')
    axes[1].tick_params(axis='x', rotation=45)
    
    # MAPE 비교
    axes[2].bar(performance_df.index, performance_df['MAPE'])
    axes[2].set_title('MAPE 비교')
    axes[2].set_ylabel('MAPE (%)')
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()
    
except FileNotFoundError:
    print("❌ 성능 결과 파일을 찾을 수 없습니다.")
```

### 5단계: 특성 중요도 분석

```python
# 특성 중요도 확인
try:
    importance_df = pd.read_csv('models/feature_importance.csv')
    
    print("🔍 상위 20개 중요 특성:")
    for i, (_, row) in enumerate(importance_df.head(20).iterrows(), 1):
        print(f"{i:2d}. {row['feature']:<35} | {row['importance']:.4f}")
    
    # 특성 중요도 시각화
    top_20 = importance_df.head(20)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    bars = ax.barh(range(len(top_20)), top_20['importance'])
    ax.set_yticks(range(len(top_20)))
    ax.set_yticklabels(top_20['feature'], fontsize=10)
    ax.set_xlabel('특성 중요도', fontsize=12)
    ax.set_title('상위 20개 중요 특성', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
except FileNotFoundError:
    print("❌ 특성 중요도 파일을 찾을 수 없습니다.")
```

### 6단계: 예측 함수 정의

```python
# 예측 함수 정의
def predict_power_consumption(model, scaler, features):
    """전력 사용량 예측"""
    # 특성 스케일링
    features_scaled = scaler.transform([features])
    
    # 예측
    prediction = model.predict(features_scaled)[0]
    
    return prediction

print("✅ 예측 함수 정의 완료!")
```

### 7단계: 대화형 예측

```python
# 대화형 예측 함수
def interactive_prediction():
    """사용자 입력을 받아 예측하는 대화형 함수"""
    
    if best_model is None or scaler is None:
        print("❌ 모델이 로드되지 않았습니다.")
        return
    
    print("\n🎯 대화형 전력 사용량 예측")
    print("=" * 50)
    
    try:
        # 사용자 입력 받기
        print("\n📝 예측 조건을 입력하세요:")
        
        occupancy = float(input("공실률 (0-100%): "))
        temperature = float(input("온도 (°C): "))
        humidity = float(input("습도 (%): "))
        hour = int(input("시간 (0-23): "))
        
        # 기본 특성 벡터 생성 (평균값으로 초기화)
        features = np.zeros(67)  # 특성 개수에 맞게 조정
        
        # 주요 특성 설정
        features[0] = occupancy
        features[1] = temperature
        features[2] = humidity
        features[3] = hour
        
        # 예측
        prediction = predict_power_consumption(best_model, scaler, features)
        
        print("\n🔮 예측 결과:")
        print(f"   공실률: {occupancy:.1f}%")
        print(f"   온도: {temperature:.1f}°C")
        print(f"   습도: {humidity:.1f}%")
        print(f"   시간: {hour:.0f}시")
        print(f"   예상 전력 사용량: {prediction:.2f} kWh")
        
        # 사용량 수준 분류
        if prediction < 10:
            level = "매우 낮음"
        elif prediction < 30:
            level = "낮음"
        elif prediction < 60:
            level = "보통"
        elif prediction < 100:
            level = "높음"
        else:
            level = "매우 높음"
        
        print(f"   사용량 수준: {level}")
        
    except ValueError:
        print("❌ 잘못된 입력입니다. 숫자를 입력해주세요.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")

# 대화형 예측 실행
interactive_prediction()
```

## 🎉 완료!

이제 구글 코랩에서 스마트 빌딩 에너지 예측 모델을 실행할 수 있습니다!

### 주요 기능:
- ✅ 모델 성능 확인
- ✅ 특성 중요도 분석
- ✅ 대화형 예측
- ✅ 시각화

### 다음 단계:
- 웹 대시보드 개발
- 실시간 API 구축
- IoT 센서 연동
- 자동 제어 시스템 구현

## 📞 문제 해결

### 자주 발생하는 오류:

1. **모델 파일을 찾을 수 없음**
   - 파일이 올바른 위치에 업로드되었는지 확인
   - 파일명이 정확한지 확인

2. **라이브러리 설치 오류**
   - 런타임 재시작 후 다시 설치
   - GPU 런타임 사용 시 CUDA 버전 확인

3. **메모리 부족**
   - 런타임 유형을 GPU로 변경
   - 불필요한 변수 삭제

## 🔗 추가 리소스

- [Google Colab 공식 문서](https://colab.research.google.com/)
- [XGBoost 공식 문서](https://xgboost.readthedocs.io/)
- [LightGBM 공식 문서](https://lightgbm.readthedocs.io/)


