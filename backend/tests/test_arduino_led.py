#!/usr/bin/env python3
"""
Arduino Uno LED 컨트롤러 테스트 스크립트
Arduino와 시리얼 통신을 테스트하고 LED 제어를 확인합니다.
"""

import sys
import os
import time
import logging

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.controllers.arduino_controller import (
    arduino_controller,
    LEDColor,
    LEDPosition,
    test_arduino_connection,
    get_controller_status
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_connection():
    """기본 연결 테스트"""
    print("=" * 50)
    print("Arduino 기본 연결 테스트")
    print("=" * 50)
    
    status = get_controller_status()
    print(f"연결 상태: {status}")
    
    if status['connected']:
        print("✅ Arduino 연결 성공!")
        return True
    else:
        print("⚠️ Arduino 연결 실패 - 시뮬레이션 모드로 동작")
        return False

def test_single_led():
    """단일 LED 테스트"""
    print("\n" + "=" * 50)
    print("단일 LED 테스트")
    print("=" * 50)
    
    # A1 위치에 빨간색 LED 켜기
    color = LEDColor(r=255, g=0, b=0)
    result = arduino_controller.highlight_position("A1", color, 3)
    
    if result:
        print("✅ A1 위치에 빨간색 LED 켜기 성공")
        time.sleep(1)
        return True
    else:
        print("❌ 단일 LED 테스트 실패")
        return False

def test_multiple_leds():
    """다중 LED 테스트"""
    print("\n" + "=" * 50)
    print("다중 LED 테스트")
    print("=" * 50)
    
    # 여러 위치에 다양한 색상 LED 켜기
    positions = ["A1", "B2", "C3", "D4", "E5"]
    colors = [
        LEDColor(r=255, g=0, b=0),    # 빨강
        LEDColor(r=0, g=255, b=0),    # 초록
        LEDColor(r=0, g=0, b=255),    # 파랑
        LEDColor(r=255, g=255, b=0),  # 노랑
        LEDColor(r=255, g=0, b=255)   # 마젠타
    ]
    
    result = arduino_controller.highlight_multiple_positions(positions, colors, 3)
    
    if result:
        print("✅ 다중 LED 테스트 성공")
        print(f"켜진 위치: {positions}")
        time.sleep(1)
        return True
    else:
        print("❌ 다중 LED 테스트 실패")
        return False

def test_sequential_pattern():
    """순차적 패턴 테스트"""
    print("\n" + "=" * 50)
    print("순차적 패턴 테스트")
    print("=" * 50)
    
    # 행별로 순차적으로 LED 켜기
    for row in range(5):
        row_char = chr(ord('A') + row)
        positions = [f"{row_char}{col}" for col in range(1, 9)]
        colors = [LEDColor(r=50, g=50, b=255) for _ in range(8)]
        
        print(f"행 {row_char} 켜기...")
        arduino_controller.highlight_multiple_positions(positions, colors, 1)
        time.sleep(1.2)
    
    print("✅ 순차적 패턴 테스트 완료")
    return True

def test_rainbow_pattern():
    """무지개 패턴 테스트"""
    print("\n" + "=" * 50)
    print("무지개 패턴 테스트")
    print("=" * 50)
    
    # 무지개 색상 배열
    rainbow_colors = [
        LEDColor(r=255, g=0, b=0),    # 빨강
        LEDColor(r=255, g=127, b=0),  # 주황
        LEDColor(r=255, g=255, b=0),  # 노랑
        LEDColor(r=0, g=255, b=0),    # 초록
        LEDColor(r=0, g=0, b=255),    # 파랑
        LEDColor(r=75, g=0, b=130),   # 남색
        LEDColor(r=148, g=0, b=211),  # 보라
        LEDColor(r=255, g=0, b=255)   # 마젠타
    ]
    
    # 각 열에 무지개 색상 적용
    for col in range(1, 9):
        positions = [f"{chr(ord('A') + row)}{col}" for row in range(5)]
        colors = [rainbow_colors[col - 1] for _ in range(5)]
        
        print(f"열 {col} 무지개 색상 적용...")
        arduino_controller.highlight_multiple_positions(positions, colors, 1)
        time.sleep(0.5)
    
    print("✅ 무지개 패턴 테스트 완료")
    return True

def test_clear_all():
    """모든 LED 끄기 테스트"""
    print("\n" + "=" * 50)
    print("모든 LED 끄기 테스트")
    print("=" * 50)
    
    result = arduino_controller.turn_off_all_leds()
    
    if result:
        print("✅ 모든 LED 끄기 성공")
        return True
    else:
        print("❌ 모든 LED 끄기 실패")
        return False

def test_led_status():
    """LED 상태 확인 테스트"""
    print("\n" + "=" * 50)
    print("LED 상태 확인 테스트")
    print("=" * 50)
    
    # 몇 개 LED 켜기
    positions = ["A1", "C3", "E5"]
    colors = [LEDColor(r=255, g=100, b=0) for _ in range(3)]
    arduino_controller.highlight_multiple_positions(positions, colors, 5)
    
    # 상태 확인
    led_states = arduino_controller.get_led_status()
    print(f"현재 켜진 LED 개수: {len(led_states)}")
    
    for position, color in led_states.items():
        print(f"  {position}: RGB({color.r}, {color.g}, {color.b})")
    
    return True

def run_interactive_test():
    """대화형 테스트"""
    print("\n" + "=" * 50)
    print("대화형 테스트")
    print("=" * 50)
    print("LED 위치와 색상을 직접 입력하세요.")
    print("형식: A1 255 0 0 (위치 R G B)")
    print("종료하려면 'quit' 입력")
    
    while True:
        try:
            user_input = input("\n명령 입력: ").strip()
            
            if user_input.lower() == 'quit':
                break
            
            if user_input.lower() == 'clear':
                arduino_controller.turn_off_all_leds()
                print("모든 LED 끄기 완료")
                continue
            
            if user_input.lower() == 'status':
                led_states = arduino_controller.get_led_status()
                print(f"현재 켜진 LED: {len(led_states)}개")
                for pos, color in led_states.items():
                    print(f"  {pos}: RGB({color.r}, {color.g}, {color.b})")
                continue
            
            # LED 제어 명령 파싱
            parts = user_input.split()
            if len(parts) != 4:
                print("잘못된 형식입니다. 예: A1 255 0 0")
                continue
            
            position = parts[0].upper()
            r, g, b = map(int, parts[1:4])
            
            # 위치 유효성 검사
            if len(position) != 2 or position[0] not in 'ABCDE' or position[1] not in '12345678':
                print("잘못된 위치입니다. A1-E8 범위로 입력하세요.")
                continue
            
            # 색상 유효성 검사
            if not all(0 <= val <= 255 for val in [r, g, b]):
                print("색상 값은 0-255 범위여야 합니다.")
                continue
            
            # LED 켜기
            color = LEDColor(r=r, g=g, b=b)
            result = arduino_controller.highlight_position(position, color, 10)
            
            if result:
                print(f"✅ {position} 위치에 RGB({r},{g},{b}) 색상 적용 성공")
            else:
                print(f"❌ {position} 위치 LED 제어 실패")
                
        except KeyboardInterrupt:
            print("\n테스트 종료")
            break
        except Exception as e:
            print(f"오류 발생: {e}")

def main():
    """메인 테스트 함수"""
    print("🔧 Arduino Uno LED 컨트롤러 테스트 시작")
    print("=" * 60)
    
    try:
        # 기본 연결 테스트
        if not test_basic_connection():
            print("⚠️ Arduino가 연결되지 않았지만 시뮬레이션 모드로 계속 진행합니다.")
        
        # 일련의 테스트 실행
        tests = [
            ("단일 LED", test_single_led),
            ("다중 LED", test_multiple_leds),
            ("순차적 패턴", test_sequential_pattern),
            ("무지개 패턴", test_rainbow_pattern),
            ("모든 LED 끄기", test_clear_all),
            ("LED 상태 확인", test_led_status),
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n🧪 {test_name} 테스트 시작...")
                result = test_func()
                if result:
                    print(f"✅ {test_name} 테스트 통과")
                else:
                    print(f"❌ {test_name} 테스트 실패")
                time.sleep(0.5)
            except Exception as e:
                print(f"❌ {test_name} 테스트 중 오류: {e}")
        
        # 대화형 테스트 제안
        print("\n" + "=" * 60)
        response = input("대화형 테스트를 시작하시겠습니까? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            run_interactive_test()
        
        # 정리
        print("\n🧹 테스트 종료 - 모든 LED 끄기...")
        arduino_controller.turn_off_all_leds()
        
        print("\n✅ 모든 테스트 완료!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트 중단됨")
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
    finally:
        # 연결 정리
        arduino_controller.disconnect()
        print("Arduino 연결 종료")

if __name__ == "__main__":
    main()
