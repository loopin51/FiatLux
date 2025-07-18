import streamlit as st
import asyncio
import io
import base64
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import speech_recognition as sr
import tempfile
import os
import time

# 직접 import
from backend.database.database import ItemDatabase
from esp32_controller import create_esp32_controller
from backend.models.models import LEDControl, Item
from mcp_server import parse_grid_position

# Gemini 에이전트 import (기본 에이전트의 백업)
try:
    from gemini_agent import GeminiItemAgent as ItemAgent
    GEMINI_AVAILABLE = True
except ImportError:
    print("⚠️ Gemini 라이브러리가 없습니다. 기본 에이전트를 사용합니다.")
    GEMINI_AVAILABLE = False
    
    # 기본 에이전트 정의 (백업용)
    class ItemAgent:
        def __init__(self):
            self.db = ItemDatabase()
            self.esp32_controller = create_esp32_controller(simulation_mode=True)
        
        async def process_query(self, user_input: str) -> Dict[str, Any]:
            """사용자 입력을 처리하고 적절한 동작을 수행합니다."""
            user_input_lower = user_input.lower()
            
            # 간단한 의도 분류
            if any(keyword in user_input_lower for keyword in ["찾아", "검색", "어디", "위치"]):
                return self._handle_search_query(user_input)
            elif any(keyword in user_input_lower for keyword in ["모든", "전체", "목록", "리스트"]):
                return self._handle_get_all_items()
            elif any(keyword in user_input_lower for keyword in ["카테고리", "분류", "종류"]):
                return self._handle_get_categories()
            elif "켜" in user_input_lower or "led" in user_input_lower or "표시" in user_input_lower:
                return await self._handle_led_query(user_input)
            else:
                return self._handle_search_query(user_input)
        
        def _handle_search_query(self, user_input: str) -> Dict[str, Any]:
            """검색 쿼리를 처리합니다."""
            keywords = []
            for word in user_input.split():
                if len(word) > 1 and word not in ["어디", "있나", "찾아", "검색", "해줘"]:
                    keywords.append(word)
            
            if keywords:
                query = " ".join(keywords)
                items = self.db.search_items(query)
                return {
                    "action": "search",
                    "query": query,
                    "items": items,
                    "message": f"'{query}' 검색 결과입니다."
                }
            else:
                return {
                    "action": "error",
                    "message": "검색할 내용을 구체적으로 말씀해주세요."
                }
        
        def _handle_get_all_items(self) -> Dict[str, Any]:
            """모든 아이템을 가져옵니다."""
            items = self.db.get_all_items()
            return {
                "action": "get_all",
                "items": items,
                "message": f"총 {len(items)}개의 물품이 등록되어 있습니다."
            }
        
        def _handle_get_categories(self) -> Dict[str, Any]:
            """모든 카테고리를 가져옵니다."""
            categories = self.db.get_categories()
            return {
                "action": "get_categories",
                "categories": categories,
                "message": f"등록된 카테고리: {', '.join(categories)}"
            }
        
        async def _handle_led_query(self, user_input: str) -> Dict[str, Any]:
            """LED 관련 쿼리를 처리합니다."""
            # 간단한 키워드 추출
            keywords = []
            for word in user_input.split():
                if len(word) > 1 and word not in ["켜", "led", "표시", "해줘"]:
                    keywords.append(word)
            
            if keywords:
                query = " ".join(keywords)
                items = self.db.search_items(query)
                
                if items:
                    item = items[0]  # 첫 번째 결과 사용
                    positions = parse_grid_position(item.grid_position)
                    
                    # LED 제어
                    led_control = LEDControl(
                        action="highlight",
                        positions=positions,
                        color=[255, 0, 0],  # 빨간색
                        duration=5000  # 5초
                    )
                    
                    await self.esp32_controller.send_command(led_control)
                    
                    return {
                        "action": "led_highlight",
                        "item": item,
                        "positions": positions,
                        "message": f"'{item.name}' 위치를 LED로 표시했습니다."
                    }
                else:
                    return {
                        "action": "error",
                        "message": f"'{query}'에 해당하는 물품을 찾을 수 없습니다."
                    }
            else:
                return {
                    "action": "error",
                    "message": "LED로 표시할 물품을 말씀해주세요."
                }

# STT 관련 함수들
class STTManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # 마이크 설정
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def recognize_speech_from_audio(self, audio_data) -> str:
        """오디오 데이터에서 음성을 인식합니다."""
        try:
            # Google Web Speech API 사용
            text = self.recognizer.recognize_google(audio_data, language='ko-KR')
            return text
        except sr.UnknownValueError:
            return "음성을 인식할 수 없습니다."
        except sr.RequestError as e:
            return f"음성 인식 서비스 오류: {e}"
    
    def recognize_speech_from_file(self, audio_file) -> str:
        """파일에서 음성을 인식합니다."""
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            return self.recognize_speech_from_audio(audio)
        except Exception as e:
            return f"파일 처리 오류: {e}"

# TTS 관련 함수들 (틀만 구현)
class TTSManager:
    def __init__(self):
        self.enabled = False  # 추후 구현을 위한 플래그
    
    def text_to_speech(self, text: str) -> Optional[bytes]:
        """텍스트를 음성으로 변환합니다. (추후 구현)"""
        # TODO: TTS 라이브러리 구현
        # 예: gTTS, pyttsx3, Azure Speech Services 등
        if not self.enabled:
            return None
        
        # 구현 예시 (실제로는 TTS 라이브러리 사용)
        # from gtts import gTTS
        # tts = gTTS(text=text, lang='ko')
        # audio_buffer = io.BytesIO()
        # tts.write_to_fp(audio_buffer)
        # return audio_buffer.getvalue()
        
        return None
    
    def play_audio(self, audio_data: bytes):
        """오디오 데이터를 재생합니다. (추후 구현)"""
        # TODO: 오디오 재생 구현
        pass

# 챗봇 관련 함수들
class ChatBot:
    def __init__(self):
        self.agent = ItemAgent()
        self.conversation_history = []
        self.max_history = 50
    
    def add_to_history(self, role: str, content: str):
        """대화 히스토리에 추가"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 히스토리 크기 제한
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    async def process_message(self, user_input: str) -> Dict[str, Any]:
        """사용자 메시지를 처리합니다."""
        # 히스토리에 사용자 메시지 추가
        self.add_to_history("user", user_input)
        
        # 에이전트로 처리
        response = await self.agent.process_query(user_input)
        
        # 히스토리에 봇 응답 추가
        self.add_to_history("assistant", response.get("message", ""))
        
        return response
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """대화 히스토리를 반환합니다."""
        return self.conversation_history
    
    def clear_history(self):
        """대화 히스토리를 초기화합니다."""
        self.conversation_history = []

# Streamlit 앱 설정
st.set_page_config(
    page_title="🤖 스마트 물품 관리 AI 챗봇",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 설정
st.sidebar.title("🤖 AI 챗봇 설정")

# 세션 상태 초기화
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = ChatBot()

if 'stt_manager' not in st.session_state:
    st.session_state.stt_manager = STTManager()

if 'tts_manager' not in st.session_state:
    st.session_state.tts_manager = TTSManager()

if 'messages' not in st.session_state:
    st.session_state.messages = []

# 사이드바 기능들
st.sidebar.subheader("🎤 음성 기능")

# STT 기능
st.sidebar.markdown("### 음성 인식 (STT)")
stt_enabled = st.sidebar.checkbox("음성 인식 활성화", value=True)

if stt_enabled:
    # 파일 업로드 방식
    uploaded_audio = st.sidebar.file_uploader(
        "음성 파일 업로드",
        type=['wav', 'mp3', 'flac', 'aiff'],
        help="음성 파일을 업로드하면 자동으로 텍스트로 변환됩니다."
    )
    
    if uploaded_audio is not None:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(uploaded_audio.read())
            tmp_file_path = tmp_file.name
        
        try:
            # 음성 인식 수행
            with st.spinner("음성을 인식하고 있습니다..."):
                recognized_text = st.session_state.stt_manager.recognize_speech_from_file(tmp_file_path)
            
            st.sidebar.success(f"인식된 텍스트: {recognized_text}")
            
            # 인식된 텍스트를 채팅 입력으로 설정
            if recognized_text and "오류" not in recognized_text and "인식할 수 없습니다" not in recognized_text:
                st.session_state.recognized_text = recognized_text
        
        finally:
            # 임시 파일 삭제
            os.unlink(tmp_file_path)

# TTS 기능 (틀만 구현)
st.sidebar.markdown("### 음성 합성 (TTS)")
tts_enabled = st.sidebar.checkbox("음성 합성 활성화 (추후 구현)", value=False, disabled=True)

if tts_enabled:
    st.sidebar.info("TTS 기능은 추후 구현 예정입니다.")

# 채팅 설정
st.sidebar.subheader("💬 채팅 설정")

# 대화 히스토리 초기화
if st.sidebar.button("대화 히스토리 초기화"):
    st.session_state.chatbot.clear_history()
    st.session_state.messages = []
    st.rerun()

# 자동 스크롤 설정
auto_scroll = st.sidebar.checkbox("자동 스크롤", value=True)

# 메인 콘텐츠
st.title("🤖 스마트 물품 관리 AI 챗봇")
st.markdown("---")

# 상태 표시
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🎤 음성 인식", "활성화" if stt_enabled else "비활성화")

with col2:
    st.metric("🔊 음성 합성", "개발 중" if tts_enabled else "비활성화")

with col3:
    st.metric("💬 대화 수", len(st.session_state.messages))

st.markdown("---")

# 채팅 인터페이스
st.subheader("💬 채팅")

# 채팅 메시지 표시
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # 타임스탬프 표시
            if "timestamp" in message:
                st.caption(message["timestamp"])

# 채팅 입력
chat_input_container = st.container()

with chat_input_container:
    # 텍스트 입력
    user_input = st.chat_input("물품에 대해 무엇이든 물어보세요...")
    
    # 음성 인식 결과가 있으면 자동으로 처리
    if 'recognized_text' in st.session_state:
        user_input = st.session_state.recognized_text
        del st.session_state.recognized_text

    # 사용자 입력 처리
    if user_input:
        # 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # 봇 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("답변을 생성하고 있습니다..."):
                try:
                    response = asyncio.run(st.session_state.chatbot.process_message(user_input))
                    
                    # 응답 처리
                    if response["action"] == "search":
                        st.markdown(response["message"])
                        
                        if response["items"]:
                            st.markdown("### 검색 결과:")
                            for item in response["items"]:
                                with st.expander(f"📦 {item.name}"):
                                    st.write(f"**카테고리:** {item.category}")
                                    st.write(f"**위치:** {item.grid_position}")
                                    if item.description:
                                        st.write(f"**설명:** {item.description}")
                                    st.write(f"**등록일:** {item.created_at}")
                        else:
                            st.warning("검색 결과가 없습니다.")
                    
                    elif response["action"] == "get_all":
                        st.markdown(response["message"])
                        
                        if response["items"]:
                            st.markdown("### 전체 물품 목록:")
                            for item in response["items"]:
                                with st.expander(f"📦 {item.name}"):
                                    st.write(f"**카테고리:** {item.category}")
                                    st.write(f"**위치:** {item.grid_position}")
                                    if item.description:
                                        st.write(f"**설명:** {item.description}")
                    
                    elif response["action"] == "get_categories":
                        st.markdown(response["message"])
                        
                        if response["categories"]:
                            st.markdown("### 카테고리별 통계:")
                            for category in response["categories"]:
                                items_count = len([item for item in st.session_state.chatbot.agent.db.get_all_items() 
                                                 if item.category == category])
                                st.write(f"• **{category}**: {items_count}개")
                    
                    elif response["action"] == "led_highlight":
                        st.markdown(response["message"])
                        st.success(f"'{response['item'].name}'의 위치를 LED로 표시했습니다!")
                        
                        # 위치 정보 표시
                        st.info(f"위치: {response['item'].grid_position}")
                    
                    elif response["action"] == "error":
                        st.error(response["message"])
                        st.markdown("💡 **사용 가능한 명령어:**")
                        st.markdown("- `[물품명] 찾아줘` - 물품 검색")
                        st.markdown("- `모든 물품 보여줘` - 전체 목록")
                        st.markdown("- `카테고리 보여줘` - 카테고리 목록")
                        st.markdown("- `[물품명] LED 켜줘` - LED 표시")
                    
                    else:
                        st.markdown(response.get("message", "알 수 없는 응답입니다."))
                    
                    # 봇 메시지 히스토리에 추가
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.get("message", ""),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "response_data": response
                    })
                    
                    # TTS 기능 (추후 구현)
                    if tts_enabled and st.session_state.tts_manager.enabled:
                        audio_data = st.session_state.tts_manager.text_to_speech(response.get("message", ""))
                        if audio_data:
                            st.audio(audio_data, format='audio/wav')
                
                except Exception as e:
                    error_message = f"오류가 발생했습니다: {str(e)}"
                    st.error(error_message)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        # 자동 스크롤
        if auto_scroll:
            st.rerun()

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        🤖 스마트 물품 관리 AI 챗봇<br>
        음성 인식, 자연어 처리, LED 제어 기능 제공<br>
        <small>Made with ❤️ using Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True
)

# 개발자 정보 (사이드바 하단)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 시스템 정보")
st.sidebar.info(f"Gemini AI: {'✅ 사용 가능' if GEMINI_AVAILABLE else '❌ 사용 불가'}")
st.sidebar.info(f"음성 인식: {'✅ 활성화' if stt_enabled else '❌ 비활성화'}")
st.sidebar.info(f"대화 히스토리: {len(st.session_state.chatbot.conversation_history)}개")

# 사용법 안내
with st.sidebar.expander("📖 사용법"):
    st.markdown("""
    **텍스트 입력:**
    - 채팅창에 직접 입력
    
    **음성 입력:**
    - 음성 파일 업로드
    - 자동으로 텍스트 변환
    
    **명령어 예시:**
    - "드라이버 찾아줘"
    - "모든 물품 보여줘"  
    - "카테고리 보여줘"
    - "드라이버 LED 켜줘"
    """)
