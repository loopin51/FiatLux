#!/usr/bin/env python3
"""
샘플 도구 데이터베이스 추가 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.database import ItemDatabase

def add_sample_tools():
    """엔지니어링 도구 샘플 데이터 추가"""
    db = ItemDatabase()
    
    # 전선 작업 도구
    wire_tools = [
        ("와이어 커터", "전선을 자르는 도구, 다양한 굵기의 전선에 사용 가능", "A1", "전선작업도구"),
        ("니퍼", "전선 절단 및 피복 제거용 도구", "A2", "전선작업도구"),
        ("와이어 스트리퍼", "전선 피복을 벗기는 전용 도구", "A3", "전선작업도구"),
        ("압착 펜치", "터미널 압착용 도구", "A4", "전선작업도구"),
        ("스트리핑 툴", "정밀한 전선 피복 제거 도구", "A5", "전선작업도구"),
    ]
    
    # 나사 작업 도구
    screw_tools = [
        ("십자 드라이버", "십자 나사 체결용 드라이버", "B1", "나사작업도구"),
        ("일자 드라이버", "일자 나사 체결용 드라이버", "B2", "나사작업도구"),
        ("육각 드라이버", "육각 나사 체결용 드라이버", "B3", "나사작업도구"),
        ("토크 드라이버", "정밀한 토크 제어가 가능한 드라이버", "B4", "나사작업도구"),
        ("전동 드라이버", "전동식 나사 체결 도구", "B5", "나사작업도구"),
        ("드라이버 세트", "다양한 크기의 드라이버 세트", "B6-B8", "나사작업도구"),
    ]
    
    # 측정 도구
    measure_tools = [
        ("디지털 멀티미터", "전압, 전류, 저항 측정 도구", "C1", "측정도구"),
        ("아날로그 멀티미터", "아날로그 방식 전기 측정 도구", "C2", "측정도구"),
        ("오실로스코프", "전기 신호 파형 관찰 도구", "C3-C4", "측정도구"),
        ("디지털 캘리퍼스", "정밀 길이 측정 도구", "C5", "측정도구"),
        ("버니어 캘리퍼스", "아날로그 방식 정밀 측정 도구", "C6", "측정도구"),
        ("전압계", "전압 측정 전용 도구", "C7", "측정도구"),
        ("전류계", "전류 측정 전용 도구", "C8", "측정도구"),
    ]
    
    # 납땜 도구
    solder_tools = [
        ("납땜기", "전자 부품 납땜용 도구", "D1", "납땜도구"),
        ("솔더링 아이언", "정밀 납땜 작업용 도구", "D2", "납땜도구"),
        ("납땜 와이어", "납땜용 솔더 와이어", "D3", "납땜도구"),
        ("플럭스", "납땜 보조제", "D4", "납땜도구"),
        ("디솔더링 펌프", "납땜 제거용 도구", "D5", "납땜도구"),
        ("납땜 팁", "납땜기 교체용 팁", "D6", "납땜도구"),
        ("납땜 스탠드", "납땜기 거치대", "D7", "납땜도구"),
    ]
    
    # 절단 도구
    cutting_tools = [
        ("커터", "일반 절단용 도구", "E1", "절단도구"),
        ("정밀 커터", "정밀 절단 작업용 도구", "E2", "절단도구"),
        ("가위", "종이, 천 등 절단용 도구", "E3", "절단도구"),
        ("금속 절단기", "금속 절단용 도구", "E4", "절단도구"),
        ("드릴", "구멍 뚫기용 도구", "E5", "절단도구"),
        ("드릴 비트 세트", "다양한 크기의 드릴 비트", "E6-E8", "절단도구"),
    ]
    
    # 조립 도구
    assembly_tools = [
        ("핀셋", "작은 부품 조작용 도구", "F1", "조립도구"),
        ("정밀 핀셋", "정밀 작업용 핀셋", "F2", "조립도구"),
        ("집게", "부품 잡기용 도구", "F3", "조립도구"),
        ("바이스", "작업물 고정용 도구", "F4-F5", "조립도구"),
        ("클램프", "임시 고정용 도구", "F6", "조립도구"),
        ("고정 클립", "작은 부품 고정용 클립", "F7", "조립도구"),
    ]
    
    # 전원 및 연결 도구
    power_tools = [
        ("전원 공급 장치", "가변 전압 전원 공급 장치", "G1-G2", "전원도구"),
        ("배터리 팩", "휴대용 전원 공급 장치", "G3", "전원도구"),
        ("USB 케이블", "USB 연결 케이블", "G4", "연결도구"),
        ("점퍼 와이어", "브레드보드용 연결 와이어", "G5", "연결도구"),
        ("브레드보드", "회로 프로토타입용 보드", "G6", "연결도구"),
        ("커넥터 세트", "다양한 전기 커넥터", "G7-G8", "연결도구"),
    ]
    
    # 모든 도구 데이터 합치기
    all_tools = (wire_tools + screw_tools + measure_tools + solder_tools + 
                cutting_tools + assembly_tools + power_tools)
    
    # 기존 데이터 확인
    existing_items = db.get_all_items()
    existing_names = {item.name for item in existing_items}
    
    # 새로운 도구만 추가
    new_tools = [tool for tool in all_tools if tool[0] not in existing_names]
    
    if new_tools:
        # 데이터베이스에 추가
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.executemany("""
            INSERT INTO items (name, description, grid_position, category)
            VALUES (?, ?, ?, ?)
        """, new_tools)
        
        conn.commit()
        conn.close()
        
        print(f"✅ {len(new_tools)}개의 새로운 도구를 데이터베이스에 추가했습니다.")
        
        # 추가된 도구 목록 출력
        print("\n📦 추가된 도구 목록:")
        for tool in new_tools:
            print(f"  • {tool[0]} - {tool[1]} ({tool[2]})")
    else:
        print("ℹ️  모든 도구가 이미 데이터베이스에 존재합니다.")
    
    # 전체 통계 출력
    all_items = db.get_all_items()
    categories = db.get_categories()
    
    print(f"\n📊 데이터베이스 통계:")
    print(f"  • 총 물품 수: {len(all_items)}")
    print(f"  • 카테고리 수: {len(categories)}")
    print(f"  • 카테고리: {', '.join(categories)}")

if __name__ == "__main__":
    add_sample_tools()
