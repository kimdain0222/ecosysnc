@echo off
echo ========================================
echo 에너지 관리 시스템 시작
echo ========================================
echo.

REM 가상환경 활성화
if not exist "venv" (
    echo ❌ 가상환경이 없습니다. 먼저 install.bat을 실행하세요.
    pause
    exit /b 1
)

echo 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM 앱 실행
echo 에너지 관리 시스템 시작 중...
echo 웹 브라우저에서 http://localhost:5000 으로 접속하세요.
echo.
python app.py

pause
