@echo off
echo ========================================
echo GitHub 잔디밭 자동 생성 스크립트
echo ========================================
echo.

REM 가상환경 확인
if not exist "venv" (
    echo ❌ 가상환경이 없습니다. 먼저 install.bat을 실행하세요.
    pause
    exit /b 1
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 잔디밭 스크립트 실행
echo 🌱 잔디밭 커밋 생성 중...
python scripts\git_grass.py

echo.
echo 📝 다음 명령어로 커밋하세요:
echo git add daily_activity.log
echo git commit -m "커밋 메시지"
echo git push
echo.
pause
