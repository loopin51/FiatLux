"""
Arduino Uno 시리얼 통신 기반 LED 컨트롤러
Arduino Uno와 USB 시리얼 통신을 통해 NeoPixel LED를 제어합니다.
"""

import serial
import time
import threading
import logging
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LEDPosition(BaseModel):
    """LED 위치 정보"""
    row: str  # A-E
    col: int  # 1-8
    
    def to_string(self) -> str:
        return f"{self.row}{self.col}"
    
    @classmethod
    def from_string(cls, position: str) -> "LEDPosition":
        if len(position) != 2:
            raise ValueError(f"Invalid position format: {position}")
        return cls(row=position[0], col=int(position[1]))

class LEDColor(BaseModel):
    """LED 색상 정보"""
    r: int = 0
    g: int = 0
    b: int = 0
    
    def __post_init__(self):
        # 색상 범위 확인
        for val in [self.r, self.g, self.b]:
            if not 0 <= val <= 255:
                raise ValueError(f"Color values must be between 0-255")
    
    def to_string(self) -> str:
        return f"{self.r},{self.g},{self.b}"
    
    def is_off(self) -> bool:
        return self.r == 0 and self.g == 0 and self.b == 0

class ArduinoLEDController:
    """Arduino Uno 기반 LED 컨트롤러"""
    
    def __init__(self, port: str = "/dev/tty.usbmodem1101", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected = False
        self.simulation_mode = False
        
        # LED 상태 관리 (5x8 그리드)
        self.led_states: Dict[str, LEDColor] = {}
        self.state_lock = threading.Lock()
        
        # 시리얼 통신 스레드
        self.update_thread: Optional[threading.Thread] = None
        self.should_stop = False
        
        # 자동 연결 시도
        self.connect()
    
    def connect(self) -> bool:
        """Arduino에 연결"""
        try:
            # 시리얼 포트 찾기
            available_ports = self._find_arduino_ports()
            
            if not available_ports:
                logger.warning("Arduino를 찾을 수 없습니다. 시뮬레이션 모드로 전환합니다.")
                self.simulation_mode = True
                return True
            
            # 연결 시도
            for port in available_ports:
                try:
                    self.serial_conn = serial.Serial(port, self.baudrate, timeout=1)
                    time.sleep(2)  # Arduino 초기화 대기
                    
                    # 연결 확인
                    if self._test_connection():
                        self.port = port
                        self.is_connected = True
                        self.simulation_mode = False
                        logger.info(f"Arduino 연결 성공: {port}")
                        
                        # 업데이트 스레드 시작
                        self._start_update_thread()
                        return True
                    else:
                        self.serial_conn.close()
                        
                except Exception as e:
                    logger.error(f"포트 {port} 연결 실패: {e}")
                    continue
            
            # 모든 포트에서 연결 실패
            logger.warning("Arduino 연결 실패. 시뮬레이션 모드로 전환합니다.")
            self.simulation_mode = True
            return True
            
        except Exception as e:
            logger.error(f"Arduino 연결 중 오류: {e}")
            self.simulation_mode = True
            return True
    
    def _find_arduino_ports(self) -> List[str]:
        """Arduino 포트 찾기"""
        import serial.tools.list_ports
        
        arduino_ports = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Arduino Uno의 일반적인 VID/PID 또는 설명 확인
            if (port.vid == 0x2341 and port.pid == 0x0043) or \
               "Arduino" in str(port.description) or \
               "USB" in str(port.description):
                arduino_ports.append(port.device)
        
        # macOS에서 일반적인 Arduino 포트 패턴
        import glob
        mac_ports = glob.glob("/dev/tty.usbmodem*") + glob.glob("/dev/tty.usbserial*")
        arduino_ports.extend(mac_ports)
        
        return list(set(arduino_ports))  # 중복 제거
    
    def _test_connection(self) -> bool:
        """연결 테스트"""
        try:
            if not self.serial_conn:
                return False
            
            # STATUS 명령 전송
            self.serial_conn.write(b"STATUS\n")
            time.sleep(0.1)
            
            # 응답 확인
            response = self.serial_conn.read_all().decode('utf-8', errors='ignore')
            return "LED Status" in response or "Ready" in response
            
        except Exception as e:
            logger.error(f"연결 테스트 실패: {e}")
            return False
    
    def _start_update_thread(self):
        """LED 상태 업데이트 스레드 시작"""
        if self.update_thread and self.update_thread.is_alive():
            return
        
        self.should_stop = False
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _update_loop(self):
        """LED 상태 업데이트 루프"""
        while not self.should_stop:
            try:
                if self.is_connected and self.serial_conn:
                    self._send_led_states()
                
                time.sleep(0.1)  # 100ms 간격으로 업데이트
                
            except Exception as e:
                logger.error(f"LED 업데이트 중 오류: {e}")
                time.sleep(1)
    
    def _send_led_states(self):
        """현재 LED 상태를 Arduino로 전송"""
        try:
            with self.state_lock:
                if not self.led_states:
                    return
                
                # 명령 생성
                commands = []
                for position, color in self.led_states.items():
                    commands.append(f"{position}:{color.to_string()}")
                
                if commands:
                    command_str = "|".join(commands) + "\n"
                    self.serial_conn.write(command_str.encode('utf-8'))
                    
        except Exception as e:
            logger.error(f"LED 상태 전송 중 오류: {e}")
    
    def highlight_position(self, position: str, color: LEDColor, duration: int = 5):
        """특정 위치의 LED 하이라이트"""
        try:
            # 위치 검증
            led_pos = LEDPosition.from_string(position)
            
            with self.state_lock:
                self.led_states[position] = color
            
            if self.simulation_mode:
                logger.info(f"[시뮬레이션] {position} 위치 하이라이트: RGB({color.r},{color.g},{color.b})")
                return True
            
            # 즉시 Arduino로 전송
            if self.is_connected and self.serial_conn:
                command = f"{position}:{color.to_string()}\n"
                self.serial_conn.write(command.encode('utf-8'))
                logger.info(f"Arduino로 전송: {command.strip()}")
            
            # 자동 끄기 (duration 후)
            if duration > 0:
                threading.Timer(duration, self._turn_off_position, args=[position]).start()
            
            return True
            
        except Exception as e:
            logger.error(f"LED 하이라이트 중 오류: {e}")
            return False
    
    def highlight_multiple_positions(self, positions: List[str], colors: List[LEDColor], duration: int = 5):
        """여러 위치의 LED 하이라이트"""
        try:
            if len(positions) != len(colors):
                raise ValueError("위치와 색상 배열의 길이가 일치하지 않습니다")
            
            with self.state_lock:
                for position, color in zip(positions, colors):
                    self.led_states[position] = color
            
            if self.simulation_mode:
                for position, color in zip(positions, colors):
                    logger.info(f"[시뮬레이션] {position} 위치 하이라이트: RGB({color.r},{color.g},{color.b})")
                return True
            
            # Arduino로 전송
            if self.is_connected and self.serial_conn:
                commands = []
                for position, color in zip(positions, colors):
                    commands.append(f"{position}:{color.to_string()}")
                
                command_str = "|".join(commands) + "\n"
                self.serial_conn.write(command_str.encode('utf-8'))
                logger.info(f"Arduino로 전송: {command_str.strip()}")
            
            # 자동 끄기
            if duration > 0:
                threading.Timer(duration, self._turn_off_positions, args=[positions]).start()
            
            return True
            
        except Exception as e:
            logger.error(f"다중 LED 하이라이트 중 오류: {e}")
            return False
    
    def _turn_off_position(self, position: str):
        """특정 위치 LED 끄기"""
        with self.state_lock:
            if position in self.led_states:
                del self.led_states[position]
        
        if self.is_connected and self.serial_conn:
            command = f"{position}:0,0,0\n"
            self.serial_conn.write(command.encode('utf-8'))
    
    def _turn_off_positions(self, positions: List[str]):
        """여러 위치 LED 끄기"""
        with self.state_lock:
            for position in positions:
                if position in self.led_states:
                    del self.led_states[position]
        
        if self.is_connected and self.serial_conn:
            commands = [f"{pos}:0,0,0" for pos in positions]
            command_str = "|".join(commands) + "\n"
            self.serial_conn.write(command_str.encode('utf-8'))
    
    def turn_off_all_leds(self):
        """모든 LED 끄기"""
        with self.state_lock:
            self.led_states.clear()
        
        if self.simulation_mode:
            logger.info("[시뮬레이션] 모든 LED 끄기")
            return True
        
        if self.is_connected and self.serial_conn:
            self.serial_conn.write(b"CLEAR\n")
            logger.info("모든 LED 끄기 명령 전송")
        
        return True
    
    def get_led_status(self) -> Dict[str, LEDColor]:
        """현재 LED 상태 반환"""
        with self.state_lock:
            return self.led_states.copy()
    
    def disconnect(self):
        """Arduino 연결 해제"""
        self.should_stop = True
        
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
        
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None
        
        self.is_connected = False
        logger.info("Arduino 연결 해제")
    
    def __del__(self):
        """소멸자"""
        self.disconnect()

# 전역 컨트롤러 인스턴스
arduino_controller = ArduinoLEDController()

# 기존 함수들과의 호환성을 위한 래퍼 함수들
def control_led(led_indices: List[int], color: Dict[str, int], duration: int = 5) -> bool:
    """기존 ESP32 컨트롤러와의 호환성을 위한 함수"""
    try:
        # LED 인덱스를 그리드 위치로 변환
        positions = []
        colors = []
        
        for idx in led_indices:
            # 0-39 인덱스를 A1-E8 위치로 변환
            row = idx // 8
            col = idx % 8
            
            if 0 <= row < 5 and 0 <= col < 8:
                row_char = chr(ord('A') + row)
                position = f"{row_char}{col + 1}"
                positions.append(position)
                colors.append(LEDColor(r=color['r'], g=color['g'], b=color['b']))
        
        if positions:
            return arduino_controller.highlight_multiple_positions(positions, colors, duration)
        
        return False
        
    except Exception as e:
        logger.error(f"LED 제어 중 오류: {e}")
        return False

def turn_off_all_leds() -> bool:
    """모든 LED 끄기"""
    return arduino_controller.turn_off_all_leds()

def get_controller_status() -> Dict:
    """컨트롤러 상태 반환"""
    return {
        "device": "Arduino Uno NeoPixel Controller",
        "connected": arduino_controller.is_connected,
        "simulation_mode": arduino_controller.simulation_mode,
        "port": arduino_controller.port,
        "led_count": len(arduino_controller.get_led_status()),
        "active_leds": list(arduino_controller.get_led_status().keys())
    }

# 테스트 함수
def test_arduino_connection():
    """Arduino 연결 테스트"""
    print("Arduino 연결 테스트 시작...")
    
    status = get_controller_status()
    print(f"상태: {status}")
    
    if status['connected']:
        print("✅ Arduino 연결 성공")
        
        # 테스트 패턴
        test_positions = ["A1", "B2", "C3", "D4", "E5"]
        test_colors = [
            LEDColor(r=255, g=0, b=0),    # 빨강
            LEDColor(r=0, g=255, b=0),    # 초록
            LEDColor(r=0, g=0, b=255),    # 파랑
            LEDColor(r=255, g=255, b=0),  # 노랑
            LEDColor(r=255, g=0, b=255)   # 마젠타
        ]
        
        print("테스트 패턴 전송...")
        arduino_controller.highlight_multiple_positions(test_positions, test_colors, 3)
        
        time.sleep(4)
        print("테스트 완료")
        
    else:
        print("⚠️ Arduino 연결 실패 - 시뮬레이션 모드")

if __name__ == "__main__":
    test_arduino_connection()
