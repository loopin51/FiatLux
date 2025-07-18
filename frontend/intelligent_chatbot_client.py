"""
스마트 물품 관리 시스템 - 지능형 AI 챗봇
초보자를 위한 스마트 검색 및 안내 시스템
"""

import streamlit as st
import asyncio
import json
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tempfile
import time
import re
from dataclasses import dataclass

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 기존 시스템 컴포넌트 import
try:
    from backend.database.database import ItemDatabase
    from backend.models.models import Item, LEDControl
    from backend.controllers.esp32_controller import highlight_item_location, control_leds, turn_off_all_leds
    from backend.mcp.mcp_server import parse_grid_position
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 데이터베이스 모듈 import 실패: {e}")
    DATABASE_AVAILABLE = False
    
    # 기본 Item 클래스 정의
    class Item:
        def __init__(self, id, name, description, grid_position, category):
            self.id = id
            self.name = name
            self.description = description
            self.grid_position = grid_position
            self.category = category
    
    # 기본 데이터베이스 클래스
    class ItemDatabase:
        def __init__(self):
            self.items = []
        
        def search_items(self, query):
            return []
        
        def get_all_items(self):
            return []
        
        def get_categories(self):
            return []

# Gemini 에이전트 import
try:
    from backend.controllers.gemini_agent import GeminiItemAgent
    GEMINI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Gemini 에이전트 import 실패: {e}")
    GEMINI_AVAILABLE = False

# STT 라이브러리 import
try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    print("⚠️ SpeechRecognition 라이브러리가 없습니다. STT 기능이 비활성화됩니다.")
    STT_AVAILABLE = False

# 응답 데이터 구조
@dataclass
class ChatResponse:
    action: str
    message: str
    items: List[Item] = None
    categories: List[str] = None
    suggestions: List[str] = None
    educational_info: Dict[str, Any] = None
    confidence: float = 0.0

# 도구 및 장비 데이터베이스
class ToolKnowledgeBase:
    """도구 및 장비에 대한 지식 베이스"""
    
    def __init__(self):
        # 도구 카테고리별 상세 정보
        self.tool_categories = {
            "전선_작업": {
                "tools": ["와이어 커터", "니퍼", "스트리핑 툴", "압착 펜치", "와이어 스트리퍼"],
                "description": "전선을 자르고, 피복을 벗기고, 연결하는 도구들",
                "keywords": ["전선", "와이어", "케이블", "자르기", "벗기기", "압착"],
                "usage": [
                    "전선 자르기: 와이어 커터, 니퍼 사용",
                    "전선 피복 벗기기: 와이어 스트리퍼, 스트리핑 툴 사용",
                    "터미널 압착: 압착 펜치 사용"
                ]
            },
            "나사_작업": {
                "tools": ["십자 드라이버", "일자 드라이버", "육각 드라이버", "토크 드라이버", "전동 드라이버"],
                "description": "나사를 조이고 푸는 도구들",
                "keywords": ["나사", "스크류", "볼트", "조이기", "풀기", "고정"],
                "usage": [
                    "십자 나사: 십자 드라이버 사용",
                    "일자 나사: 일자 드라이버 사용",
                    "육각 나사: 육각 드라이버 사용",
                    "정밀 작업: 토크 드라이버 사용"
                ]
            },
            "측정_도구": {
                "tools": ["멀티미터", "오실로스코프", "전압계", "전류계", "저항계", "캘리퍼스", "버니어"],
                "description": "전기적 특성과 물리적 치수를 측정하는 도구들",
                "keywords": ["측정", "전압", "전류", "저항", "크기", "길이", "두께"],
                "usage": [
                    "전압 측정: 멀티미터의 전압 모드 사용",
                    "전류 측정: 멀티미터의 전류 모드 사용",
                    "저항 측정: 멀티미터의 저항 모드 사용",
                    "치수 측정: 캘리퍼스, 버니어 사용"
                ]
            },
            "납땜_도구": {
                "tools": ["납땜기", "솔더링 아이언", "납땜 와이어", "플럭스", "납땜 팁", "디솔더링 펌프"],
                "description": "전자 부품을 납땜하고 분리하는 도구들",
                "keywords": ["납땜", "솔더링", "연결", "부품", "PCB", "회로"],
                "usage": [
                    "부품 납땜: 납땜기와 납땜 와이어 사용",
                    "플럭스 적용: 더 나은 납땜을 위해 플럭스 사용",
                    "납땜 제거: 디솔더링 펌프 사용"
                ]
            },
            "절단_도구": {
                "tools": ["커터", "가위", "절단기", "톱", "드릴", "리머"],
                "description": "다양한 재료를 자르고 구멍을 뚫는 도구들",
                "keywords": ["자르기", "절단", "구멍", "뚫기", "가공"],
                "usage": [
                    "플라스틱 절단: 커터, 가위 사용",
                    "금속 절단: 톱, 절단기 사용",
                    "구멍 뚫기: 드릴 사용"
                ]
            },
            "조립_도구": {
                "tools": ["핀셋", "집게", "홀더", "바이스", "클램프", "고정 클립"],
                "description": "부품을 잡고 고정하는 도구들",
                "keywords": ["잡기", "고정", "조립", "홀딩", "클램핑"],
                "usage": [
                    "작은 부품 조작: 핀셋 사용",
                    "작업물 고정: 바이스, 클램프 사용",
                    "임시 고정: 클립 사용"
                ]
            }
        }
        
        # 일반적인 질문 패턴
        self.question_patterns = {
            "what_is": ["뭔가요", "무엇인가요", "이름이 뭐", "어떤 도구"],
            "how_to_use": ["어떻게 사용", "사용법", "쓰는 법", "사용 방법"],
            "do_we_have": ["있나요", "있는지", "보유", "가지고 있"],
            "where_is": ["어디에", "위치", "어디 있"],
            "recommendation": ["추천", "좋은 것", "어떤 게 좋", "뭘 써야"]
        }
    
    def find_tool_by_purpose(self, purpose: str) -> List[Dict[str, Any]]:
        """목적에 맞는 도구 찾기"""
        results = []
        purpose_lower = purpose.lower()
        
        for category, info in self.tool_categories.items():
            # 키워드 매칭
            for keyword in info["keywords"]:
                if keyword in purpose_lower:
                    results.append({
                        "category": category,
                        "tools": info["tools"],
                        "description": info["description"],
                        "usage": info["usage"],
                        "confidence": 0.8
                    })
                    break
        
        return results
    
    def get_tool_suggestions(self, query: str) -> List[str]:
        """쿼리에 기반한 도구 제안"""
        suggestions = []
        query_lower = query.lower()
        
        # 일반적인 작업별 제안
        if any(word in query_lower for word in ["자르", "절단", "cut"]):
            suggestions.extend(["와이어 커터", "니퍼", "커터", "가위"])
        if any(word in query_lower for word in ["나사", "드라이버", "screw"]):
            suggestions.extend(["십자 드라이버", "일자 드라이버", "전동 드라이버"])
        if any(word in query_lower for word in ["측정", "재", "measure"]):
            suggestions.extend(["멀티미터", "캘리퍼스", "버니어"])
        if any(word in query_lower for word in ["납땜", "solder"]):
            suggestions.extend(["납땜기", "솔더링 아이언", "플럭스"])
        
        return suggestions[:5]  # 최대 5개 제안

# 지능형 AI 챗봇 클래스
class IntelligentChatBot:
    def __init__(self):
        self.db = ItemDatabase() if DATABASE_AVAILABLE else None
        self.knowledge_base = ToolKnowledgeBase()
        
        # Gemini 에이전트 초기화
        if GEMINI_AVAILABLE:
            try:
                self.gemini_agent = GeminiItemAgent()
                self.use_gemini = True
            except Exception as e:
                print(f"⚠️ Gemini 초기화 실패: {e}")
                self.use_gemini = False
        else:
            self.use_gemini = False
        
        self.conversation_history = []
        self.user_context = {
            "skill_level": "beginner",  # beginner, intermediate, advanced
            "recent_searches": [],
            "preferences": {}
        }
    
    def analyze_user_intent(self, query: str) -> Dict[str, Any]:
        """사용자 의도 분석"""
        query_lower = query.lower()
        
        # 질문 유형 분류
        intent = {
            "type": "unknown",
            "confidence": 0.0,
            "entities": [],
            "purpose": None
        }
        
        # 패턴 매칭
        if any(pattern in query_lower for pattern in ["뭔가요", "무엇인가요", "이름이 뭐"]):
            intent["type"] = "definition"
            intent["confidence"] = 0.9
        elif any(pattern in query_lower for pattern in ["있나요", "있는지", "보유"]):
            intent["type"] = "availability"
            intent["confidence"] = 0.9
        elif any(pattern in query_lower for pattern in ["어디에", "위치", "어디 있"]):
            intent["type"] = "location"
            intent["confidence"] = 0.8
        elif any(pattern in query_lower for pattern in ["어떻게", "사용법", "방법"]):
            intent["type"] = "usage"
            intent["confidence"] = 0.8
        elif any(pattern in query_lower for pattern in ["추천", "좋은", "뭘 써야"]):
            intent["type"] = "recommendation"
            intent["confidence"] = 0.8
        
        # 엔티티 추출 (간단한 키워드 기반)
        tools_mentioned = []
        for category, info in self.knowledge_base.tool_categories.items():
            for tool in info["tools"]:
                if tool.lower() in query_lower:
                    tools_mentioned.append(tool)
            for keyword in info["keywords"]:
                if keyword in query_lower:
                    intent["entities"].append(keyword)
        
        intent["tools_mentioned"] = tools_mentioned
        
        return intent
    
    def generate_educational_response(self, intent: Dict[str, Any], query: str) -> ChatResponse:
        """교육적 응답 생성"""
        
        if intent["type"] == "definition":
            # "전선 자르는 도구가 뭔가요?" 같은 질문
            purpose_matches = self.knowledge_base.find_tool_by_purpose(query)
            
            if purpose_matches:
                category_info = purpose_matches[0]
                tools = category_info["tools"]
                
                # 데이터베이스에서 실제 보유 도구 확인
                available_tools = []
                if self.db:
                    for tool in tools:
                        items = self.db.search_items(tool)
                        if items:
                            available_tools.extend(items)
                
                message = f"📚 **{category_info['description']}**\\n\\n"
                message += f"**일반적인 도구들:**\\n"
                for tool in tools:
                    message += f"• {tool}\\n"
                
                if available_tools:
                    message += f"\\n**우리가 보유한 도구:**\\n"
                    for item in available_tools:
                        message += f"• {item.name} - {item.description} ({item.grid_position})\\n"
                else:
                    message += f"\\n⚠️ 현재 이러한 도구들이 재고에 없습니다."
                
                message += f"\\n**사용법:**\\n"
                for usage in category_info["usage"]:
                    message += f"• {usage}\\n"
                
                return ChatResponse(
                    action="educational",
                    message=message,
                    items=available_tools,
                    suggestions=self.knowledge_base.get_tool_suggestions(query),
                    educational_info=category_info,
                    confidence=0.9
                )
        
        elif intent["type"] == "availability":
            # "우리 물품중에 있나요?" 같은 질문
            suggestions = self.knowledge_base.get_tool_suggestions(query)
            available_items = []
            
            if self.db:
                # 제안된 도구들 중 실제 보유 확인
                for suggestion in suggestions:
                    items = self.db.search_items(suggestion)
                    available_items.extend(items)
                
                # 일반적인 키워드로도 검색
                for entity in intent["entities"]:
                    items = self.db.search_items(entity)
                    available_items.extend(items)
            
            if available_items:
                message = f"✅ **네, 다음과 같은 도구들이 있습니다:**\\n\\n"
                for item in available_items:
                    message += f"📦 **{item.name}**\\n"
                    message += f"   • 설명: {item.description}\\n"
                    message += f"   • 위치: {item.grid_position}\\n"
                    message += f"   • 카테고리: {item.category}\\n\\n"
                
                return ChatResponse(
                    action="availability_found",
                    message=message,
                    items=available_items,
                    confidence=0.9
                )
            else:
                message = f"❌ **죄송합니다. 현재 관련 도구가 재고에 없습니다.**\\n\\n"
                message += f"**대신 이런 도구들을 찾아보시는 건 어떨까요?**\\n"
                for suggestion in suggestions:
                    message += f"• {suggestion}\\n"
                
                return ChatResponse(
                    action="availability_not_found",
                    message=message,
                    suggestions=suggestions,
                    confidence=0.8
                )
        
        elif intent["type"] == "recommendation":
            # "뭘 써야 하나요?" 같은 질문
            purpose_matches = self.knowledge_base.find_tool_by_purpose(query)
            
            if purpose_matches:
                category_info = purpose_matches[0]
                message = f"💡 **추천 도구:**\\n\\n"
                message += f"{category_info['description']}를 위해서는 다음 도구들을 추천합니다:\\n\\n"
                
                for i, tool in enumerate(category_info["tools"][:3], 1):
                    message += f"{i}. **{tool}**\\n"
                    
                    # 실제 보유 여부 확인
                    if self.db:
                        items = self.db.search_items(tool)
                        if items:
                            message += f"   ✅ 보유 중 - 위치: {items[0].grid_position}\\n"
                        else:
                            message += f"   ❌ 현재 없음\\n"
                    message += "\\n"
                
                message += f"**사용 팁:**\\n"
                for usage in category_info["usage"]:
                    message += f"• {usage}\\n"
                
                return ChatResponse(
                    action="recommendation",
                    message=message,
                    suggestions=category_info["tools"],
                    educational_info=category_info,
                    confidence=0.9
                )
        
        # 기본 응답
        return ChatResponse(
            action="general_search",
            message="더 구체적인 정보를 위해 일반 검색을 수행하겠습니다.",
            confidence=0.5
        )
    
    async def process_query(self, user_input: str) -> ChatResponse:
        """사용자 쿼리 처리"""
        
        # 사용자 의도 분석
        intent = self.analyze_user_intent(user_input)
        
        # 교육적 응답 생성
        educational_response = self.generate_educational_response(intent, user_input)
        
        # 교육적 응답이 충분하지 않은 경우 Gemini 사용
        if educational_response.confidence < 0.7 and self.use_gemini:
            try:
                gemini_response = await self.gemini_agent.process_query(user_input)
                
                # Gemini 응답을 ChatResponse 형태로 변환
                return ChatResponse(
                    action=gemini_response.get("action", "gemini_response"),
                    message=gemini_response.get("message", ""),
                    items=gemini_response.get("items", []),
                    confidence=0.9
                )
            except Exception as e:
                print(f"Gemini 처리 실패: {e}")
        
        # 기본 검색 수행
        if educational_response.action == "general_search" and self.db:
            # 키워드 추출 및 검색
            keywords = intent["entities"] + intent.get("tools_mentioned", [])
            if not keywords:
                # 간단한 키워드 추출
                words = user_input.split()
                keywords = [word for word in words if len(word) > 1]
            
            search_results = []
            for keyword in keywords:
                items = self.db.search_items(keyword)
                search_results.extend(items)
            
            if search_results:
                message = f"🔍 **검색 결과:**\\n\\n"
                for item in search_results:
                    message += f"📦 **{item.name}**\\n"
                    message += f"   • 설명: {item.description}\\n"
                    message += f"   • 위치: {item.grid_position}\\n"
                    message += f"   • 카테고리: {item.category}\\n\\n"
                
                return ChatResponse(
                    action="search_results",
                    message=message,
                    items=search_results,
                    confidence=0.7
                )
        
        return educational_response
    
    def add_to_history(self, role: str, content: str, response_data: Dict[str, Any] = None):
        """대화 히스토리에 추가"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })
        
        # 히스토리 크기 제한
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

# STT 관리 클래스
class STTManager:
    def __init__(self):
        if not STT_AVAILABLE:
            self.available = False
            return
        
        self.available = True
        self.recognizer = sr.Recognizer()
        
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
        except:
            self.microphone = None
    
    def recognize_speech_from_file(self, audio_file) -> str:
        """파일에서 음성을 인식합니다."""
        if not self.available:
            return "STT 기능이 사용 불가능합니다."
        
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio, language='ko-KR')
            return text
        except sr.UnknownValueError:
            return "음성을 인식할 수 없습니다."
        except sr.RequestError as e:
            return f"음성 인식 서비스 오류: {e}"
        except Exception as e:
            return f"파일 처리 오류: {e}"

# Streamlit 앱 설정
st.set_page_config(
    page_title="🤖 지능형 물품 관리 AI 챗봇",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        text-align: center;
    }
    .educational-box {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4169e1;
        margin: 1rem 0;
    }
    .suggestion-box {
        background: #f5f5dc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #daa520;
        margin: 1rem 0;
    }
    .item-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .confidence-bar {
        background: #e0e0e0;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcf7f);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = IntelligentChatBot()

if 'stt_manager' not in st.session_state:
    st.session_state.stt_manager = STTManager()

if 'messages' not in st.session_state:
    st.session_state.messages = []

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🤖 지능형 물품 관리 AI 챗봇</h1>
    <p style="text-align: center; color: #f0f0f0; margin: 0;">
        초보자를 위한 스마트 도구 안내 | 음성 인식 | 교육적 응답 | 실시간 LED 제어
    </p>
</div>
""", unsafe_allow_html=True)

# 사이드바
st.sidebar.title("🛠️ 시스템 설정")

# 시스템 상태 표시
st.sidebar.subheader("📊 시스템 상태")
st.sidebar.info(f"💾 데이터베이스: {'✅ 연결됨' if DATABASE_AVAILABLE else '❌ 연결 안됨'}")
st.sidebar.info(f"🧠 AI 엔진: {'✅ Gemini' if GEMINI_AVAILABLE else '⚠️ 기본 모드'}")
st.sidebar.info(f"🎤 음성 인식: {'✅ 사용 가능' if STT_AVAILABLE else '❌ 사용 불가'}")

# 사용자 레벨 설정
st.sidebar.subheader("👤 사용자 설정")
user_level = st.sidebar.selectbox(
    "경험 수준",
    ["초보자", "중급자", "고급자"],
    index=0
)

if user_level == "초보자":
    st.sidebar.info("💡 더 자세한 설명과 사용법을 제공합니다.")
elif user_level == "중급자":
    st.sidebar.info("⚡ 적절한 수준의 기술적 정보를 제공합니다.")
else:
    st.sidebar.info("🔧 고급 기능과 상세한 기술 정보를 제공합니다.")

# STT 설정
st.sidebar.subheader("🎤 음성 인식")
if STT_AVAILABLE:
    uploaded_audio = st.sidebar.file_uploader(
        "음성 파일 업로드",
        type=['wav', 'mp3', 'flac', 'aiff'],
        help="음성 파일을 업로드하면 자동으로 텍스트로 변환됩니다."
    )
    
    if uploaded_audio is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(uploaded_audio.read())
            tmp_file_path = tmp_file.name
        
        try:
            with st.spinner("🎤 음성을 인식하고 있습니다..."):
                recognized_text = st.session_state.stt_manager.recognize_speech_from_file(tmp_file_path)
            
            if recognized_text and "오류" not in recognized_text:
                st.sidebar.success(f"✅ 인식 결과: {recognized_text}")
                st.session_state.recognized_text = recognized_text
            else:
                st.sidebar.error(f"❌ {recognized_text}")
        finally:
            os.unlink(tmp_file_path)

# 빠른 질문 템플릿
st.sidebar.subheader("💬 빠른 질문")
quick_questions = [
    "전선 자르는 도구가 뭔가요?",
    "나사 돌리는 도구는 뭐가 있나요?",
    "납땜할 때 뭘 써야 하나요?",
    "전압 측정하는 도구가 있나요?",
    "모든 도구 목록을 보여주세요",
    "카테고리별로 정리해주세요"
]

for question in quick_questions:
    if st.sidebar.button(f"❓ {question}"):
        st.session_state.quick_question = question

# 메인 채팅 영역
col1, col2 = st.columns([3, 1])

with col1:
    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # 응답 데이터 처리
            if "response_data" in message and message["response_data"]:
                response_data = message["response_data"]
                
                # 신뢰도 표시
                if response_data.get("confidence", 0) > 0:
                    confidence = response_data["confidence"]
                    st.markdown(f"""
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {confidence*100}%"></div>
                    </div>
                    <small>응답 신뢰도: {confidence:.0%}</small>
                    """, unsafe_allow_html=True)
                
                # 교육적 정보 표시
                if response_data.get("educational_info"):
                    edu_info = response_data["educational_info"]
                    st.markdown(f"""
                    <div class="educational-box">
                        <h4>📚 추가 학습 정보</h4>
                        <p><strong>카테고리:</strong> {edu_info.get('description', '')}</p>
                        <p><strong>관련 도구들:</strong> {', '.join(edu_info.get('tools', []))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 제안 사항 표시
                if response_data.get("suggestions"):
                    suggestions = response_data["suggestions"]
                    st.markdown(f"""
                    <div class="suggestion-box">
                        <h4>💡 관련 제안</h4>
                        <p>{' • '.join(suggestions)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 아이템 목록 표시
                if response_data.get("items"):
                    items = response_data["items"]
                    st.markdown("### 📦 관련 물품")
                    for item in items:
                        st.markdown(f"""
                        <div class="item-card">
                            <h5>📦 {item.name}</h5>
                            <p><strong>설명:</strong> {item.description}</p>
                            <p><strong>위치:</strong> {item.grid_position}</p>
                            <p><strong>카테고리:</strong> {item.category}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # LED 제어 버튼
                        if st.button(f"💡 {item.name} 위치 표시", key=f"led_{item.id}"):
                            try:
                                positions = parse_grid_position(item.grid_position)
                                success = highlight_item_location(positions, {"r": 255, "g": 0, "b": 0}, 5)
                                if success:
                                    st.success(f"💡 {item.name} 위치를 LED로 표시했습니다!")
                                else:
                                    st.error("LED 제어에 실패했습니다.")
                            except Exception as e:
                                st.error(f"오류: {e}")

    # 채팅 입력
    user_input = st.chat_input("💬 도구나 장비에 대해 무엇이든 물어보세요... (예: '전선 자르는 도구가 뭔가요?')")
    
    # 음성 인식 결과 처리
    if 'recognized_text' in st.session_state:
        user_input = st.session_state.recognized_text
        del st.session_state.recognized_text
    
    # 빠른 질문 처리
    if 'quick_question' in st.session_state:
        user_input = st.session_state.quick_question
        del st.session_state.quick_question
    if 'recognized_text' in st.session_state:
        user_input = st.session_state.recognized_text
        del st.session_state.recognized_text
    
    # 빠른 질문 처리
    if 'quick_question' in st.session_state:
        user_input = st.session_state.quick_question
        del st.session_state.quick_question
    
    # 사용자 입력 처리
    if user_input:
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(user_input)
        
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # 봇 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("🤖 분석하고 답변을 생성하고 있습니다..."):
                try:
                    response = asyncio.run(st.session_state.chatbot.process_query(user_input))
                    
                    # 응답 표시
                    st.markdown(response.message)
                    
                    # 신뢰도 표시
                    if response.confidence > 0:
                        st.markdown(f"""
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {response.confidence*100}%"></div>
                        </div>
                        <small>응답 신뢰도: {response.confidence:.0%}</small>
                        """, unsafe_allow_html=True)
                    
                    # 교육적 정보 표시
                    if response.educational_info:
                        edu_info = response.educational_info
                        st.markdown(f"""
                        <div class="educational-box">
                            <h4>📚 추가 학습 정보</h4>
                            <p><strong>카테고리:</strong> {edu_info.get('description', '')}</p>
                            <p><strong>관련 도구들:</strong> {', '.join(edu_info.get('tools', []))}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 제안 사항 표시
                    if response.suggestions:
                        st.markdown(f"""
                        <div class="suggestion-box">
                            <h4>💡 관련 제안</h4>
                            <p>{' • '.join(response.suggestions)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 아이템 목록 표시
                    if response.items:
                        st.markdown("### 📦 관련 물품")
                        for item in response.items:
                            st.markdown(f"""
                            <div class="item-card">
                                <h5>📦 {item.name}</h5>
                                <p><strong>설명:</strong> {item.description}</p>
                                <p><strong>위치:</strong> {item.grid_position}</p>
                                <p><strong>카테고리:</strong> {item.category}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 히스토리에 추가
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.message,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "response_data": {
                            "action": response.action,
                            "confidence": response.confidence,
                            "suggestions": response.suggestions,
                            "educational_info": response.educational_info,
                            "items": response.items
                        }
                    })
                    
                except Exception as e:
                    error_message = f"❌ 오류가 발생했습니다: {str(e)}"
                    st.error(error_message)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        st.rerun()

# 사이드바 우측 패널
with col2:
    st.subheader("🎯 사용 팁")
    
    with st.expander("💡 질문 예시"):
        st.markdown("""
        **도구 찾기:**
        - "전선 자르는 도구가 뭔가요?"
        - "나사 돌리는 도구는?"
        - "납땜할 때 뭘 써야 하나요?"
        
        **보유 확인:**
        - "우리 물품 중에 있나요?"
        - "멀티미터 있나요?"
        - "드라이버 어디 있나요?"
        
        **사용법:**
        - "어떻게 사용하나요?"
        - "사용 방법을 알려주세요"
        - "주의사항이 있나요?"
        """)
    
    with st.expander("🔧 도구 카테고리"):
        st.markdown("""
        - **전선 작업**: 와이어 커터, 니퍼, 스트리퍼
        - **나사 작업**: 드라이버, 렌치, 토크 도구
        - **측정 도구**: 멀티미터, 캘리퍼스, 게이지
        - **납땜 도구**: 솔더링 아이언, 플럭스
        - **절단 도구**: 커터, 가위, 톱
        - **조립 도구**: 핀셋, 클램프, 바이스
        """)
    
    with st.expander("⚙️ 고급 기능"):
        st.markdown("""
        - **음성 인식**: 음성 파일 업로드
        - **LED 제어**: 물품 위치 표시
        - **스마트 검색**: AI 기반 의도 분석
        - **교육적 응답**: 초보자 친화적 설명
        - **실시간 제안**: 관련 도구 추천
        """)

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        🤖 <b>지능형 물품 관리 AI 챗봇</b><br>
        초보자를 위한 스마트 도구 안내 시스템<br>
        <small>AI 기반 의도 분석 • 교육적 응답 • 실시간 LED 제어</small>
    </div>
    """,
    unsafe_allow_html=True
)
