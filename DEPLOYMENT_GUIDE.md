# 🚀 스마트 빌딩 에너지 관리 시스템 배포 가이드

## 📋 배포 전 준비사항

### 1. GitHub 저장소 준비
- 모든 코드를 GitHub에 업로드
- `main` 브랜치에 최신 코드가 있는지 확인

### 2. 필수 파일 확인
- ✅ `app.py` - 메인 Flask 애플리케이션
- ✅ `requirements.txt` - Python 의존성
- ✅ `Procfile` - 배포 설정
- ✅ `runtime.txt` - Python 버전
- ✅ `templates/` - HTML 템플릿
- ✅ `static/` - CSS, JS, 이미지 파일
- ✅ `models/` - ML 모델 파일들
- ✅ `data/` - 데이터 파일들

---

## 🌟 Render 배포 (추천)

### 1단계: Render 계정 생성
1. [Render.com](https://render.com) 접속
2. GitHub 계정으로 로그인

### 2단계: 새 Web Service 생성
1. **"New +"** 버튼 클릭
2. **"Web Service"** 선택
3. GitHub 저장소 연결

### 3단계: 서비스 설정
```
Name: energy-management-system
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

### 4단계: 환경변수 설정 (선택사항)
```
FLASK_ENV=production
DEBUG=False
```

### 5단계: 배포
- **"Create Web Service"** 클릭
- 자동으로 빌드 및 배포 시작
- 5-10분 후 배포 완료

---

## 🚀 Railway 배포

### 1단계: Railway 계정 생성
1. [Railway.app](https://railway.app) 접속
2. GitHub 계정으로 로그인

### 2단계: 프로젝트 생성
1. **"New Project"** 클릭
2. **"Deploy from GitHub repo"** 선택
3. 저장소 선택

### 3단계: 자동 배포
- Railway가 자동으로 감지하여 배포
- `requirements.txt`와 `Procfile` 기반으로 설정

---

## 🔧 배포 후 확인사항

### 1. 기본 기능 테스트
- [ ] 메인 페이지 로딩
- [ ] 대시보드 차트 표시
- [ ] 예측 기능 작동
- [ ] IoT 모니터링 페이지

### 2. 성능 확인
- [ ] 페이지 로딩 속도
- [ ] API 응답 시간
- [ ] 차트 렌더링

### 3. 오류 로그 확인
- Render/Railway 대시보드에서 로그 확인
- 오류 발생 시 즉시 수정

---

## 🛠️ 문제 해결

### 일반적인 문제들

#### 1. 모듈 Import 오류
```bash
# requirements.txt에 누락된 패키지 추가
pip install [패키지명]
```

#### 2. 포트 오류
```python
# app.py에서 환경변수 사용
port = int(os.environ.get('PORT', 5000))
```

#### 3. 정적 파일 404 오류
```python
# Flask에서 static 폴더 설정 확인
app = Flask(__name__, static_folder='static')
```

#### 4. 데이터베이스 연결 오류
- SQLite 파일 경로 확인
- 파일 권한 설정

---

## 📊 배포 후 모니터링

### 1. 성능 모니터링
- 응답 시간 추적
- 에러율 모니터링
- 사용량 통계

### 2. 로그 분석
- 애플리케이션 로그
- 에러 로그
- 접근 로그

### 3. 백업 및 복구
- 정기적인 데이터 백업
- 코드 버전 관리
- 롤백 계획

---

## 🔄 지속적 배포 (CI/CD)

### GitHub Actions 설정
```yaml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Render
      uses: johnbeynon/render-deploy-action@v1.0.0
      with:
        service-id: ${{ secrets.RENDER_SERVICE_ID }}
        api-key: ${{ secrets.RENDER_API_KEY }}
```

---

## 🎯 최적화 팁

### 1. 성능 최적화
- 정적 파일 압축
- 이미지 최적화
- 캐싱 설정

### 2. 보안 강화
- HTTPS 강제
- 환경변수 사용
- 입력 검증

### 3. 확장성 고려
- 데이터베이스 분리
- CDN 사용
- 로드 밸런싱

---

