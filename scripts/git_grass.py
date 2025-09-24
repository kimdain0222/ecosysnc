#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 잔디밭 자동 생성 스크립트
GitHub Actions와 함께 사용하여 매일 자동으로 커밋을 생성합니다.
"""

import os
import random
import datetime
from pathlib import Path

def create_daily_commit():
    """일일 커밋 생성"""
    
    # 활동 메시지 목록
    activities = [
        "에너지 관리 시스템 코드 리뷰",
        "머신러닝 모델 성능 개선", 
        "IoT 센서 데이터 처리 최적화",
        "웹 대시보드 UI/UX 개선",
        "데이터 전처리 파이프라인 업데이트",
        "API 엔드포인트 성능 튜닝",
        "실시간 모니터링 기능 강화",
        "에너지 예측 알고리즘 개선",
        "데이터베이스 쿼리 최적화",
        "보안 취약점 점검 및 수정",
        "테스트 커버리지 향상",
        "문서화 및 주석 개선",
        "로깅 시스템 강화",
        "에러 핸들링 개선",
        "코드 리팩토링",
        "성능 모니터링 추가",
        "사용자 피드백 반영",
        "배포 자동화 개선",
        "데이터 시각화 업데이트",
        "알고리즘 정확도 향상"
    ]
    
    # 랜덤 활동 선택
    activity = random.choice(activities)
    
    # 현재 시간
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S KST")
    
    # 로그 파일에 추가
    log_file = Path("daily_activity.log")
    
    # 로그 내용 생성
    log_content = f"Daily commit: {timestamp}\n"
    log_content += f"🌱 Daily activity: {activity} - {now.strftime('%Y-%m-%d')}\n\n"
    
    # 파일에 추가 (기존 내용 유지)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_content)
    
    # 커밋 메시지 생성
    commit_message = f"🌱 Daily activity: {activity} - {now.strftime('%Y-%m-%d')}"
    
    print(f"✅ 커밋 생성 완료!")
    print(f"📅 시간: {timestamp}")
    print(f"🌱 활동: {activity}")
    print(f"💬 커밋 메시지: {commit_message}")
    
    return commit_message

def create_weekend_commit():
    """주말 커밋 생성"""
    
    weekend_activities = [
        "주말 사이드 프로젝트 개발",
        "개인 학습 및 연구",
        "코드 리뷰 및 정리",
        "새로운 기술 스택 학습",
        "프로젝트 문서화 작업",
        "성능 최적화 연구",
        "알고리즘 개선 아이디어 검토",
        "사용자 경험 개선 방안 모색",
        "보안 강화 방안 연구",
        "자동화 스크립트 개선"
    ]
    
    activity = random.choice(weekend_activities)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S KST")
    
    log_file = Path("daily_activity.log")
    
    log_content = f"Weekend activity: {timestamp}\n"
    log_content += f"🌅 Weekend: {activity} - {now.strftime('%Y-%m-%d')}\n\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_content)
    
    commit_message = f"🌅 Weekend: {activity} - {now.strftime('%Y-%m-%d')}"
    
    print(f"✅ 주말 커밋 생성 완료!")
    print(f"📅 시간: {timestamp}")
    print(f"🌅 활동: {activity}")
    print(f"💬 커밋 메시지: {commit_message}")
    
    return commit_message

def create_random_commit():
    """랜덤 커밋 생성"""
    
    random_activities = [
        "데이터 분석 스크립트 개선",
        "모델 하이퍼파라미터 튜닝",
        "센서 데이터 검증 로직 추가",
        "대시보드 차트 업데이트",
        "API 응답 시간 최적화",
        "데이터베이스 인덱스 추가",
        "캐싱 메커니즘 구현",
        "실시간 알림 기능 개발",
        "사용자 인증 시스템 강화",
        "데이터 백업 자동화"
    ]
    
    activity = random.choice(random_activities)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S KST")
    
    log_file = Path("daily_activity.log")
    
    log_content = f"Random activity: {timestamp}\n"
    log_content += f"🔧 {activity} - {now.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_content)
    
    commit_message = f"🔧 {activity} - {now.strftime('%Y-%m-%d %H:%M')}"
    
    print(f"✅ 랜덤 커밋 생성 완료!")
    print(f"📅 시간: {timestamp}")
    print(f"🔧 활동: {activity}")
    print(f"💬 커밋 메시지: {commit_message}")
    
    return commit_message

def main():
    """메인 함수"""
    print("🌱 GitHub 잔디밭 자동 생성 스크립트")
    print("=" * 50)
    
    # 현재 요일 확인
    today = datetime.datetime.now().weekday()  # 0=월요일, 6=일요일
    
    if today in [5, 6]:  # 토요일, 일요일
        commit_message = create_weekend_commit()
    else:  # 평일
        # 랜덤하게 일일 커밋 또는 랜덤 커밋 선택
        if random.choice([True, False]):
            commit_message = create_daily_commit()
        else:
            commit_message = create_random_commit()
    
    print("\n" + "=" * 50)
    print("📝 다음 명령어로 커밋하세요:")
    print(f"git add daily_activity.log")
    print(f'git commit -m "{commit_message}"')
    print(f"git push")

if __name__ == "__main__":
    main()
