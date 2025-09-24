@echo off
echo ========================================
echo 에너지 관리 시스템 설치 스크립트
echo ========================================
echo.

REM Python 버전 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 Python을 설치하세요.
    pause
    exit /b 1
)

echo ✅ Python이 설치되어 있습니다.
echo.

REM 가상환경 생성
echo 가상환경 생성 중...
python -m venv venv
if errorlevel 1 (
    echo ❌ 가상환경 생성 실패
    pause
    exit /b 1
)

echo ✅ 가상환경 생성 완료
echo.

REM 가상환경 활성화
echo 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM pip 업그레이드
echo pip 업그레이드 중...
python -m pip install --upgrade pip

REM 패키지 설치
echo 패키지 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 패키지 설치 실패
    pause
    exit /b 1
)

echo ✅ 패키지 설치 완료
echo.

REM 실행 스크립트 생성
echo 실행 스크립트 생성 중...
echo @echo off > run.bat
echo call venv\Scripts\activate.bat >> run.bat
echo python app.py >> run.bat
echo pause >> run.bat

echo ✅ 설치 완료!
echo.
echo 🎉 에너지 관리 시스템이 성공적으로 설치되었습니다!
echo.
echo 실행 방법:
echo 1. run.bat 더블클릭
echo 2. 또는 명령어: python app.py
echo.
pause
