#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Energy Management System Auto Installer
에너지 관리 시스템 자동 설치 스크립트

이 스크립트는 프로젝트의 모든 의존성을 자동으로 설치하고 환경을 설정합니다.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class Colors:
    """터미널 색상 코드"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message, color=Colors.BLUE):
    """색상이 있는 메시지 출력"""
    print(f"{color}{message}{Colors.END}")

def print_header(message):
    """헤더 메시지 출력"""
    print_colored(f"\n{'='*60}", Colors.BOLD)
    print_colored(f"  {message}", Colors.BOLD)
    print_colored(f"{'='*60}", Colors.BOLD)

def print_step(step, message):
    """단계별 메시지 출력"""
    print_colored(f"\n[단계 {step}] {message}", Colors.YELLOW)

def check_python_version():
    """Python 버전 확인"""
    print_step(1, "Python 버전 확인 중...")
    version = sys.version_info
    print(f"현재 Python 버전: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_colored("❌ Python 3.8 이상이 필요합니다!", Colors.RED)
        print_colored("https://www.python.org/downloads/ 에서 최신 버전을 다운로드하세요.", Colors.YELLOW)
        return False
    
    print_colored("✅ Python 버전이 호환됩니다.", Colors.GREEN)
    return True

def check_pip():
    """pip 설치 확인"""
    print_step(2, "pip 설치 확인 중...")
    try:
        import pip
        print_colored("✅ pip가 설치되어 있습니다.", Colors.GREEN)
        return True
    except ImportError:
        print_colored("❌ pip가 설치되어 있지 않습니다.", Colors.RED)
        print_colored("pip를 설치하세요: https://pip.pypa.io/en/stable/installation/", Colors.YELLOW)
        return False

def upgrade_pip():
    """pip 업그레이드"""
    print_step(3, "pip 업그레이드 중...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print_colored("✅ pip 업그레이드 완료", Colors.GREEN)
        return True
    except subprocess.CalledProcessError:
        print_colored("⚠️ pip 업그레이드 실패 (계속 진행)", Colors.YELLOW)
        return True

def create_virtual_environment():
    """가상환경 생성"""
    print_step(4, "가상환경 생성 중...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print_colored("⚠️ 기존 가상환경이 발견되었습니다.", Colors.YELLOW)
        response = input("기존 가상환경을 삭제하고 새로 만들까요? (y/N): ").lower()
        if response == 'y':
            shutil.rmtree(venv_path)
            print_colored("기존 가상환경을 삭제했습니다.", Colors.YELLOW)
        else:
            print_colored("기존 가상환경을 사용합니다.", Colors.GREEN)
            return True
    
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print_colored("✅ 가상환경 생성 완료", Colors.GREEN)
        return True
    except subprocess.CalledProcessError:
        print_colored("❌ 가상환경 생성 실패", Colors.RED)
        return False

def get_venv_python():
    """가상환경의 Python 경로 반환"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def get_venv_pip():
    """가상환경의 pip 경로 반환"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")

def install_requirements():
    """requirements.txt 설치"""
    print_step(5, "패키지 설치 중...")
    
    venv_python = get_venv_python()
    venv_pip = get_venv_pip()
    
    if not venv_python.exists():
        print_colored("❌ 가상환경 Python을 찾을 수 없습니다.", Colors.RED)
        return False
    
    try:
        # requirements.txt 설치
        if Path("requirements.txt").exists():
            subprocess.check_call([str(venv_pip), "install", "-r", "requirements.txt"])
            print_colored("✅ requirements.txt 패키지 설치 완료", Colors.GREEN)
        else:
            print_colored("⚠️ requirements.txt 파일을 찾을 수 없습니다.", Colors.YELLOW)
        
        # setup.py로 설치 (개발 모드)
        if Path("setup.py").exists():
            subprocess.check_call([str(venv_pip), "install", "-e", "."])
            print_colored("✅ 프로젝트 패키지 설치 완료", Colors.GREEN)
        
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ 패키지 설치 실패: {e}", Colors.RED)
        return False

def create_activation_scripts():
    """활성화 스크립트 생성"""
    print_step(6, "활성화 스크립트 생성 중...")
    
    # Windows용 배치 파일
    if platform.system() == "Windows":
        activate_script = """@echo off
echo 에너지 관리 시스템 가상환경 활성화 중...
call venv\\Scripts\\activate.bat
echo.
echo ✅ 가상환경이 활성화되었습니다!
echo 대시보드 실행: python app.py
echo.
"""
        with open("activate.bat", "w", encoding="utf-8") as f:
            f.write(activate_script)
        print_colored("✅ activate.bat 생성 완료", Colors.GREEN)
    
    # Unix/Linux/macOS용 스크립트
    activate_script = """#!/bin/bash
echo "에너지 관리 시스템 가상환경 활성화 중..."
source venv/bin/activate
echo ""
echo "✅ 가상환경이 활성화되었습니다!"
echo "대시보드 실행: python app.py"
echo ""
"""
    with open("activate.sh", "w", encoding="utf-8") as f:
        f.write(activate_script)
    
    # 실행 권한 부여
    if platform.system() != "Windows":
        os.chmod("activate.sh", 0o755)
    
    print_colored("✅ activate.sh 생성 완료", Colors.GREEN)

def create_run_scripts():
    """실행 스크립트 생성"""
    print_step(7, "실행 스크립트 생성 중...")
    
    # Windows용 실행 스크립트
    if platform.system() == "Windows":
        run_script = """@echo off
echo 에너지 관리 시스템 시작 중...
call venv\\Scripts\\activate.bat
python app.py
pause
"""
        with open("run.bat", "w", encoding="utf-8") as f:
            f.write(run_script)
        print_colored("✅ run.bat 생성 완료", Colors.GREEN)
    
    # Unix/Linux/macOS용 실행 스크립트
    run_script = """#!/bin/bash
echo "에너지 관리 시스템 시작 중..."
source venv/bin/activate
python app.py
"""
    with open("run.sh", "w", encoding="utf-8") as f:
        f.write(run_script)
    
    if platform.system() != "Windows":
        os.chmod("run.sh", 0o755)
    
    print_colored("✅ run.sh 생성 완료", Colors.GREEN)

def verify_installation():
    """설치 검증"""
    print_step(8, "설치 검증 중...")
    
    venv_python = get_venv_python()
    
    try:
        # 주요 패키지 import 테스트
        test_imports = [
            "pandas", "numpy", "sklearn", "flask", "matplotlib", "plotly"
        ]
        
        for package in test_imports:
            result = subprocess.run([
                str(venv_python), "-c", f"import {package}; print('{package} OK')"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print_colored(f"✅ {package} 정상 설치됨", Colors.GREEN)
            else:
                print_colored(f"❌ {package} 설치 문제", Colors.RED)
        
        return True
    except Exception as e:
        print_colored(f"❌ 설치 검증 실패: {e}", Colors.RED)
        return False

def print_completion_message():
    """완료 메시지 출력"""
    print_header("설치 완료!")
    
    print_colored("🎉 에너지 관리 시스템이 성공적으로 설치되었습니다!", Colors.GREEN)
    print_colored("\n📋 다음 단계:", Colors.BOLD)
    
    if platform.system() == "Windows":
        print_colored("1. 가상환경 활성화: activate.bat", Colors.YELLOW)
        print_colored("2. 대시보드 실행: run.bat", Colors.YELLOW)
    else:
        print_colored("1. 가상환경 활성화: source activate.sh", Colors.YELLOW)
        print_colored("2. 대시보드 실행: ./run.sh", Colors.YELLOW)
    
    print_colored("\n또는 수동으로:", Colors.BOLD)
    if platform.system() == "Windows":
        print_colored("  venv\\Scripts\\activate", Colors.YELLOW)
    else:
        print_colored("  source venv/bin/activate", Colors.YELLOW)
    print_colored("  python app.py", Colors.YELLOW)
    
    print_colored("\n📚 추가 정보:", Colors.BOLD)
    print_colored("  - README.md: 프로젝트 개요", Colors.YELLOW)
    print_colored("  - INSTALL.md: 상세 설치 가이드", Colors.YELLOW)
    print_colored("  - docs/: 문서 폴더", Colors.YELLOW)

def main():
    """메인 함수"""
    print_header("에너지 관리 시스템 자동 설치")
    print_colored("이 스크립트는 프로젝트의 모든 의존성을 자동으로 설치합니다.", Colors.BLUE)
    
    # 설치 단계 실행
    steps = [
        check_python_version,
        check_pip,
        upgrade_pip,
        create_virtual_environment,
        install_requirements,
        create_activation_scripts,
        create_run_scripts,
        verify_installation,
    ]
    
    for step in steps:
        if not step():
            print_colored("\n❌ 설치가 실패했습니다. 오류를 확인하고 다시 시도하세요.", Colors.RED)
            sys.exit(1)
    
    print_completion_message()

if __name__ == "__main__":
    main()
