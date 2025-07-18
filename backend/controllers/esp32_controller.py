"""
Arduino Uno 기반 LED 컨트롤러 - ESP32 호환 인터페이스
기존 ESP32 컨트롤러 인터페이스를 유지하면서 Arduino Uno 시리얼 통신으로 동작
"""

# Arduino 컨트롤러 임포트
from .arduino_controller import (
    arduino_controller,
    LEDColor,
    LEDPosition,
    control_led,
    turn_off_all_leds,
    get_controller_status
)

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# 기존 ESP32 인터페이스 유지를 위한 래퍼 함수들

def control_leds(led_indices: List[int], color: Dict[str, int], duration: int = 5) -> bool:
    """
    LED 제어 (기존 ESP32 인터페이스 호환)
    
    Args:
        led_indices: LED 인덱스 리스트 (0-39)
        color: 색상 딕셔너리 {"r": 0-255, "g": 0-255, "b": 0-255}
        duration: 지속 시간 (초)
    
    Returns:
        bool: 성공 여부
    """
    return control_led(led_indices, color, duration)

def highlight_item_location(positions: List[str], color: Dict[str, int] = None, duration: int = 5) -> bool:
    """
    물품 위치 하이라이트 (그리드 위치 기반)
    
    Args:
        positions: 그리드 위치 리스트 (예: ["A1", "B2", "C3"])
        color: 색상 딕셔너리 (기본값: 파란색)
        duration: 지속 시간 (초)
    
    Returns:
        bool: 성공 여부
    """
    try:
        if color is None:
            color = {"r": 0, "g": 0, "b": 255}  # 기본 파란색
        
        # 위치 문자열을 LED 색상으로 변환
        led_colors = []
        for pos in positions:
            led_colors.append(LEDColor(r=color["r"], g=color["g"], b=color["b"]))
        
        return arduino_controller.highlight_multiple_positions(positions, led_colors, duration)
        
    except Exception as e:
        logger.error(f"물품 위치 하이라이트 중 오류: {e}")
        return False

def parse_grid_position(position: str) -> List[int]:
    """
    그리드 위치를 LED 인덱스로 변환
    
    Args:
        position: 그리드 위치 (예: "A1-A3")
    
    Returns:
        List[int]: LED 인덱스 리스트
    """
    try:
        led_indices = []
        
        if "-" in position:
            # 범위 처리 (예: "A1-A3")
            start_pos, end_pos = position.split("-")
            start_row = ord(start_pos[0]) - ord('A')
            start_col = int(start_pos[1]) - 1
            end_row = ord(end_pos[0]) - ord('A')
            end_col = int(end_pos[1]) - 1
            
            # 같은 행에서만 범위 처리
            if start_row == end_row:
                for col in range(start_col, end_col + 1):
                    led_indices.append(start_row * 8 + col)
            else:
                # 다른 행인 경우 각각 처리
                led_indices.append(start_row * 8 + start_col)
                led_indices.append(end_row * 8 + end_col)
        else:
            # 단일 위치 처리
            row = ord(position[0]) - ord('A')
            col = int(position[1]) - 1
            led_indices.append(row * 8 + col)
        
        return led_indices
        
    except Exception as e:
        logger.error(f"그리드 위치 파싱 중 오류: {e}")
        return []

def get_led_status() -> Dict[str, Any]:
    """
    LED 상태 반환 (기존 ESP32 인터페이스 호환)
    
    Returns:
        Dict: LED 상태 정보
    """
    controller_status = get_controller_status()
    led_states = arduino_controller.get_led_status()
    
    return {
        "device": "Arduino Uno NeoPixel Controller",
        "connected": controller_status["connected"],
        "simulation_mode": controller_status["simulation_mode"],
        "port": controller_status["port"],
        "total_leds": 120,  # 5x8x3 = 120개
        "active_positions": len(led_states),
        "led_states": {pos: {"r": color.r, "g": color.g, "b": color.b} 
                      for pos, color in led_states.items()}
    }

def test_led_connection() -> bool:
    """
    LED 연결 테스트
    
    Returns:
        bool: 연결 상태
    """
    try:
        status = get_controller_status()
        if status["connected"]:
            # 테스트 패턴 전송
            test_positions = ["A1", "C3", "E5"]
            test_color = {"r": 255, "g": 0, "b": 0}
            
            result = highlight_item_location(test_positions, test_color, 2)
            logger.info(f"LED 연결 테스트 {'성공' if result else '실패'}")
            return result
        else:
            logger.warning("Arduino가 연결되지 않음 - 시뮬레이션 모드")
            return True  # 시뮬레이션 모드에서는 True 반환
            
    except Exception as e:
        logger.error(f"LED 연결 테스트 중 오류: {e}")
        return False

# 그리드 위치 변환 유틸리티
def grid_position_to_led_indices(position: str) -> List[int]:
    """그리드 위치를 LED 인덱스로 변환"""
    return parse_grid_position(position)

def led_index_to_grid_position(index: int) -> str:
    """LED 인덱스를 그리드 위치로 변환"""
    if not 0 <= index < 40:
        raise ValueError(f"LED 인덱스는 0-39 범위여야 합니다: {index}")
    
    row = index // 8
    col = index % 8
    row_char = chr(ord('A') + row)
    return f"{row_char}{col + 1}"

# 호환성을 위한 기존 함수 별칭
def control_led_grid(positions: List[str], color: Dict[str, int], duration: int = 5) -> bool:
    """그리드 위치 기반 LED 제어"""
    return highlight_item_location(positions, color, duration)

def turn_off_led_grid(positions: List[str] = None) -> bool:
    """그리드 위치 기반 LED 끄기"""
    if positions is None:
        return turn_off_all_leds()
    else:
        # 특정 위치만 끄기
        return highlight_item_location(positions, {"r": 0, "g": 0, "b": 0}, 0)

# 컨트롤러 정보
CONTROLLER_INFO = {
    "name": "Arduino Uno NeoPixel Controller",
    "type": "serial",
    "grid_size": "5x8",
    "total_positions": 40,
    "leds_per_position": 3,
    "total_leds": 120,
    "supported_colors": "RGB (0-255)",
    "communication": "USB Serial",
    "baudrate": 115200
}

# 시뮬레이션 모드 확인
def is_simulation_mode() -> bool:
    """시뮬레이션 모드 여부 확인"""
    return arduino_controller.simulation_mode

def get_controller_info() -> Dict[str, Any]:
    """컨트롤러 정보 반환"""
    status = get_controller_status()
    return {
        **CONTROLLER_INFO,
        "connected": status["connected"],
        "simulation_mode": status["simulation_mode"],
        "port": status["port"],
        "active_leds": status["active_leds"]
    }

import json
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from ..models.models import LEDControl

class ESP32Controller:
    """ESP32 NeoPixel LED 제어 클래스"""
    
    def __init__(self, esp32_ip: str = "192.168.1.100", port: int = 80):
        self.esp32_ip = esp32_ip
        self.port = port
        self.base_url = f"http://{esp32_ip}:{port}"
        
        # 그리드 설정 (예: 5x5 그리드)
        self.grid_rows = 5
        self.grid_cols = 5
        self.grid_mapping = self._create_grid_mapping()
    
    def _create_grid_mapping(self) -> Dict[str, int]:
        """그리드 위치를 LED 인덱스로 매핑"""
        mapping = {}
        led_index = 0
        
        for row in range(self.grid_rows):
            row_letter = chr(ord('A') + row)  # A, B, C, D, E
            for col in range(1, self.grid_cols + 1):
                position = f"{row_letter}{col}"  # A1, A2, ..., E5
                mapping[position] = led_index
                led_index += 1
        
        return mapping
    
    def position_to_led_index(self, position: str) -> Optional[int]:
        """그리드 위치를 LED 인덱스로 변환"""
        return self.grid_mapping.get(position.upper())
    
    def color_name_to_rgb(self, color_name: str) -> tuple:
        """색상 이름을 RGB 값으로 변환"""
        colors = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "purple": (255, 0, 255),
            "cyan": (0, 255, 255),
            "white": (255, 255, 255),
            "orange": (255, 165, 0),
            "pink": (255, 192, 203),
            "off": (0, 0, 0)
        }
        return colors.get(color_name.lower(), (0, 0, 255))  # 기본값: 파란색
    
    async def highlight_position(self, led_control: LEDControl) -> Dict[str, Any]:
        """특정 위치의 LED를 하이라이트"""
        try:
            # 위치 문자열을 리스트로 변환
            positions = []
            if '-' in led_control.grid_position:
                # 범위 위치 (예: "A1-A4")
                start, end = led_control.grid_position.split('-')
                start_row = start[0]
                start_col = int(start[1:])
                end_row = end[0]
                end_col = int(end[1:])
                
                for row in range(ord(start_row), ord(end_row) + 1):
                    for col in range(start_col, end_col + 1):
                        positions.append(f"{chr(row)}{col}")
            else:
                # 단일 위치 (예: "A1")
                positions.append(led_control.grid_position)
            
            # 위치를 LED 인덱스로 변환
            led_indices = []
            for position in positions:
                led_index = self.position_to_led_index(position)
                if led_index is not None:
                    led_indices.append(led_index)
            
            if not led_indices:
                return {
                    "success": False,
                    "error": "No valid LED positions found",
                    "message": "유효한 LED 위치를 찾을 수 없습니다."
                }
            
            # RGB 색상 변환
            rgb_color = self.color_name_to_rgb(led_control.color)
            
            # ESP32로 전송할 명령 구성
            command = {
                "action": "highlight",
                "led_indices": led_indices,
                "color": {
                    "r": rgb_color[0],
                    "g": rgb_color[1],
                    "b": rgb_color[2]
                },
                "duration": led_control.duration,
                "positions": positions
            }
            
            # ESP32로 HTTP 요청 전송
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/led_control",
                    json=command,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": {
                                "command": command,
                                "esp32_response": result
                            },
                            "message": f"LED 제어 완료: {len(led_indices)}개 LED가 {led_control.color} 색상으로 {led_control.duration}초간 켜집니다."
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"ESP32 응답 오류: {response.status}",
                            "message": f"ESP32에서 오류가 발생했습니다: {error_text}"
                        }
        
        except aiohttp.ClientTimeout:
            return {
                "success": False,
                "error": "Timeout",
                "message": "ESP32 연결 시간 초과"
            }
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "message": f"ESP32 연결 오류: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "message": f"예상치 못한 오류: {str(e)}"
            }
    
    async def control_leds(self, led_control: LEDControl) -> Dict[str, Any]:
        """LED 제어 명령을 ESP32로 전송"""
        try:
            # 위치를 LED 인덱스로 변환
            led_indices = []
            for position in led_control.positions:
                led_index = self.position_to_led_index(position)
                if led_index is not None:
                    led_indices.append(led_index)
            
            if not led_indices:
                return {
                    "success": False,
                    "error": "No valid LED positions found",
                    "message": "유효한 LED 위치를 찾을 수 없습니다."
                }
            
            # RGB 색상 변환
            rgb_color = self.color_name_to_rgb(led_control.color)
            
            # ESP32로 전송할 명령 구성
            command = {
                "action": "highlight",
                "led_indices": led_indices,
                "color": {
                    "r": rgb_color[0],
                    "g": rgb_color[1],
                    "b": rgb_color[2]
                },
                "duration": led_control.duration,
                "positions": led_control.positions
            }
            
            # ESP32로 HTTP 요청 전송
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/led_control",
                    json=command,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": {
                                "command": command,
                                "esp32_response": result
                            },
                            "message": f"LED 제어 완료: {len(led_indices)}개 LED가 {led_control.color} 색상으로 {led_control.duration}초간 켜집니다."
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"ESP32 응답 오류: {response.status}",
                            "message": f"ESP32에서 오류가 발생했습니다: {error_text}"
                        }
        
        except aiohttp.ClientTimeout:
            return {
                "success": False,
                "error": "Timeout",
                "message": "ESP32 연결 시간 초과"
            }
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "message": f"ESP32 연결 오류: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "message": f"예상치 못한 오류: {str(e)}"
            }
    
    async def turn_off_all_leds(self) -> Dict[str, Any]:
        """모든 LED 끄기"""
        try:
            command = {"action": "turn_off_all"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/led_control",
                    json=command,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return {
                            "success": True,
                            "message": "모든 LED가 꺼졌습니다."
                        }
                    else:
                        return {
                            "success": False,
                            "message": "LED 끄기 실패"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"LED 제어 오류: {str(e)}"
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """ESP32 상태 확인"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/status",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        status = await response.json()
                        return {
                            "success": True,
                            "data": status,
                            "message": "ESP32 연결 정상"
                        }
                    else:
                        return {
                            "success": False,
                            "message": "ESP32 상태 확인 실패"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"ESP32 연결 실패: {str(e)}"
            }

# 시뮬레이션용 가상 ESP32 컨트롤러
class MockESP32Controller(ESP32Controller):
    """개발/테스트용 가상 ESP32 컨트롤러"""
    
    def __init__(self):
        super().__init__("127.0.0.1", 8080)
        self.led_states = {}  # LED 상태 저장
    
    async def control_leds(self, led_control: LEDControl) -> Dict[str, Any]:
        """가상 LED 제어 (시뮬레이션)"""
        try:
            # 위치를 LED 인덱스로 변환
            led_indices = []
            for position in led_control.positions:
                led_index = self.position_to_led_index(position)
                if led_index is not None:
                    led_indices.append(led_index)
                    # 가상 LED 상태 저장
                    self.led_states[led_index] = {
                        "position": position,
                        "color": led_control.color,
                        "duration": led_control.duration
                    }
            
            if not led_indices:
                return {
                    "success": False,
                    "error": "No valid LED positions found",
                    "message": "유효한 LED 위치를 찾을 수 없습니다."
                }
            
            # 시뮬레이션 지연
            await asyncio.sleep(0.5)
            
            return {
                "success": True,
                "data": {
                    "led_indices": led_indices,
                    "positions": led_control.positions,
                    "color": led_control.color,
                    "duration": led_control.duration,
                    "simulation": True
                },
                "message": f"[시뮬레이션] LED 제어 완료: {len(led_indices)}개 LED가 {led_control.color} 색상으로 {led_control.duration}초간 켜집니다."
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"시뮬레이션 오류: {str(e)}"
            }
    
    async def turn_off_all_leds(self) -> Dict[str, Any]:
        """모든 가상 LED 끄기"""
        self.led_states.clear()
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "message": "[시뮬레이션] 모든 LED가 꺼졌습니다."
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """가상 ESP32 상태"""
        return {
            "success": True,
            "data": {
                "device": "Mock ESP32",
                "ip": "127.0.0.1",
                "led_count": self.grid_rows * self.grid_cols,
                "active_leds": len(self.led_states),
                "grid_size": f"{self.grid_rows}x{self.grid_cols}",
                "simulation": True
            },
            "message": "[시뮬레이션] ESP32 연결 정상"
        }

# 컨트롤러 팩토리
def create_esp32_controller(simulation_mode: bool = True) -> ESP32Controller:
    """ESP32 컨트롤러 생성"""
    if simulation_mode:
        return MockESP32Controller()
    else:
        # 실제 ESP32 IP 주소로 변경 필요
        return ESP32Controller("192.168.1.100")

if __name__ == "__main__":
    # 테스트 코드
    async def test_led_control():
        controller = create_esp32_controller(simulation_mode=True)
        
        # 상태 확인
        status = await controller.get_status()
        print("ESP32 상태:", status)
        
        # LED 제어 테스트
        led_control = LEDControl(
            positions=["A1", "A2", "B1"],
            duration=5,
            color="blue"
        )
        
        result = await controller.control_leds(led_control)
        print("LED 제어 결과:", result)
        
        # 모든 LED 끄기
        await asyncio.sleep(2)
        off_result = await controller.turn_off_all_leds()
        print("LED 끄기 결과:", off_result)
    
    # 테스트 실행
    asyncio.run(test_led_control())
