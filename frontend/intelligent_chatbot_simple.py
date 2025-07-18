"""
스마트 물품 관리 시스템 - 지능형 AI 챗봇 (간소화 버전)
초보자를 위한 스마트 검색 및 안내 시스템
"""

import streamlit as st
import asyncio
import json
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import sqlite3
from dataclasses import dataclass

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 간단한 Item 클래스
@dataclass
class Item:
    id: int
    name: str
    description: str
    grid_position: str
    category: str

# 응답 데이터 구조
@dataclass
class ChatResponse:
    action: str
    message: str
    items: List[Item] = None
    suggestions: List[str] = None
    educational_info: Dict[str, Any] = None
    confidence: float = 0.0

# 간단한 데이터베이스 클래스
class SimpleItemDatabase:
    def __init__(self, db_path: str = "items.db"):
        self.db_path = db_path
    
    def search_items(self, query: str) -> List[Item]:
        """키워드로 물품 검색"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, grid_position, category
                FROM items 
                WHERE name LIKE ? OR description LIKE ? OR category LIKE ?
            """, (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            items = []
            for row in cursor.fetchall():
                items.append(Item(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    grid_position=row[3],
                    category=row[4]
                ))
            
            conn.close()
            return items
        except Exception as e:
            print(f"데이터베이스 오류: {e}")
            return []
    
    def get_all_items(self) -> List[Item]:
        """모든 물품 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name, description, grid_position, category FROM items")
            
            items = []
            for row in cursor.fetchall():
                items.append(Item(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    grid_position=row[3],
                    category=row[4]
                ))
            
            conn.close()
            return items
        except Exception as e:
            print(f"데이터베이스 오류: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """카테고리 목록 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT category FROM items")
            categories = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return categories
        except Exception as e:
            print(f"데이터베이스 오류: {e}")
            return []

# 도구 지식 베이스
class ToolKnowledgeBase:
    def __init__(self):
        self.tool_mappings = {
            "전선 자르는 도구": {
                "tools": ["와이어 커터", "니퍼", "스트리핑 툴", "압착 펜치"],
                "description": "전선을 자르고 가공하는 도구들입니다.",
                "keywords": ["전선", "와이어", "케이블", "자르기", "절단"],
                "usage": [
                    "와이어 커터: 전선을 깔끔하게 자를 때 사용",
                    "니퍼: 전선 절단 및 피복 제거 가능",
                    "스트리핑 툴: 전선 피복만 제거할 때 사용",
                    "압착 펜치: 터미널 압착 작업에 사용"
                ]
            },
            "나사 돌리는 도구": {
                "tools": ["십자 드라이버", "일자 드라이버", "육각 드라이버", "토크 드라이버"],
                "description": "나사를 조이고 푸는 도구들입니다.",
                "keywords": ["나사", "스크류", "드라이버", "조이기", "풀기"],
                "usage": [
                    "십자 드라이버: 십자 나사용",
                    "일자 드라이버: 일자 나사용",
                    "육각 드라이버: 육각 나사용",
                    "토크 드라이버: 정밀한 토크 조절 필요시"
                ]
            },
            "측정 도구": {
                "tools": ["멀티미터", "캘리퍼스", "오실로스코프", "전압계"],
                "description": "전기적 특성과 물리적 치수를 측정하는 도구들입니다.",
                "keywords": ["측정", "전압", "전류", "저항", "크기", "길이"],
                "usage": [
                    "멀티미터: 전압, 전류, 저항 측정",
                    "캘리퍼스: 정밀한 길이 측정",
                    "오실로스코프: 전기 신호 파형 관찰",
                    "전압계: 전압 측정 전용"
                ]
            },
            "납땜 도구": {
                "tools": ["납땜기", "솔더링 아이언", "납땜 와이어", "플럭스"],
                "description": "전자 부품을 납땜하는 도구들입니다.",
                "keywords": ["납땜", "솔더링", "연결", "부품", "회로"],
                "usage": [
                    "납땜기: 기본적인 납땜 작업",
                    "솔더링 아이언: 정밀한 납땜 작업",
                    "납땜 와이어: 납땜용 솔더",
                    "플럭스: 더 나은 납땜을 위한 보조제"
                ]
            }
        }
    
    def find_tools_by_description(self, description: str) -> Dict[str, Any]:
        """설명으로 도구 찾기"""
        description_lower = description.lower()
        
        for tool_desc, info in self.tool_mappings.items():
            if any(keyword in description_lower for keyword in info["keywords"]):
                return info
        
        return None
    
    def get_suggestions(self, query: str) -> List[str]:
        """쿼리 기반 제안"""
        suggestions = []
        query_lower = query.lower()
        
        for tool_desc, info in self.tool_mappings.items():
            if any(keyword in query_lower for keyword in info["keywords"]):
                suggestions.extend(info["tools"][:3])  # 최대 3개
        
        return suggestions[:5]  # 최대 5개 제안

# 지능형 챗봇
class IntelligentChatBot:
    def __init__(self):
        self.db = SimpleItemDatabase()
        self.knowledge_base = ToolKnowledgeBase()
        self.conversation_history = []
    
    def analyze_intent(self, query: str) -> str:
        """의도 분석"""
        query_lower = query.lower()
        
        if any(pattern in query_lower for pattern in ["뭔가요", "무엇인가요", "이름이 뭐"]):
            return "definition"
        elif any(pattern in query_lower for pattern in ["있나요", "있는지", "보유"]):
            return "availability"
        elif any(pattern in query_lower for pattern in ["어디에", "위치"]):
            return "location"
        elif any(pattern in query_lower for pattern in ["어떻게", "사용법"]):
            return "usage"
        elif any(pattern in query_lower for pattern in ["모든", "전체", "목록"]):
            return "list_all"
        else:
            return "search"
    
    async def process_query(self, user_input: str) -> ChatResponse:
        """쿼리 처리"""
        intent = self.analyze_intent(user_input)
        
        # 의도별 처리
        if intent == "definition":
            return self.handle_definition(user_input)
        elif intent == "availability":
            return self.handle_availability(user_input)
        elif intent == "list_all":
            return self.handle_list_all()
        else:
            return self.handle_search(user_input)
    
    def handle_definition(self, query: str) -> ChatResponse:
        """정의/설명 처리"""
        tool_info = self.knowledge_base.find_tools_by_description(query)
        
        if tool_info:
            # 실제 보유 도구 확인
            available_items = []
            for tool in tool_info["tools"]:
                items = self.db.search_items(tool)
                available_items.extend(items)
            
            message = f"📚 **{tool_info['description']}**\\n\\n"
            message += f"**일반적인 도구들:**\\n"
            for tool in tool_info["tools"]:
                message += f"• {tool}\\n"
            
            if available_items:
                message += f"\\n**우리가 보유한 도구:**\\n"
                for item in available_items:
                    message += f"• {item.name} - {item.description} (위치: {item.grid_position})\\n"
            else:
                message += f"\\n⚠️ 현재 관련 도구가 재고에 없습니다."
            
            message += f"\\n**사용법:**\\n"
            for usage in tool_info["usage"]:
                message += f"• {usage}\\n"
            
            return ChatResponse(
                action="definition",
                message=message,
                items=available_items,
                suggestions=tool_info["tools"],
                educational_info=tool_info,
                confidence=0.9
            )
        else:
            return self.handle_search(query)
    
    def handle_availability(self, query: str) -> ChatResponse:
        """보유 확인 처리"""
        suggestions = self.knowledge_base.get_suggestions(query)
        available_items = []
        
        # 제안된 도구 검색
        for suggestion in suggestions:
            items = self.db.search_items(suggestion)
            available_items.extend(items)
        
        # 일반 검색도 수행
        words = query.split()
        for word in words:
            if len(word) > 1:
                items = self.db.search_items(word)
                available_items.extend(items)
        
        # 중복 제거
        unique_items = []
        seen_ids = set()
        for item in available_items:
            if item.id not in seen_ids:
                unique_items.append(item)
                seen_ids.add(item.id)
        
        if unique_items:
            message = f"✅ **네, 다음과 같은 도구들이 있습니다:**\\n\\n"
            for item in unique_items:
                message += f"📦 **{item.name}**\\n"
                message += f"   • 설명: {item.description}\\n"
                message += f"   • 위치: {item.grid_position}\\n"
                message += f"   • 카테고리: {item.category}\\n\\n"
            
            return ChatResponse(
                action="availability_found",
                message=message,
                items=unique_items,
                confidence=0.8
            )
        else:
            message = f"❌ **죄송합니다. 관련 도구가 재고에 없습니다.**\\n\\n"
            message += f"**대신 이런 도구들을 찾아보시는 건 어떨까요?**\\n"
            for suggestion in suggestions:
                message += f"• {suggestion}\\n"
            
            return ChatResponse(
                action="availability_not_found",
                message=message,
                suggestions=suggestions,
                confidence=0.6
            )
    
    def handle_list_all(self) -> ChatResponse:
        """전체 목록 처리"""
        items = self.db.get_all_items()
        categories = self.db.get_categories()
        
        if items:
            message = f"📋 **전체 물품 목록** (총 {len(items)}개)\\n\\n"
            
            # 카테고리별 정리
            for category in categories:
                category_items = [item for item in items if item.category == category]
                if category_items:
                    message += f"**{category}** ({len(category_items)}개)\\n"
                    for item in category_items:
                        message += f"• {item.name} - {item.grid_position}\\n"
                    message += "\\n"
            
            return ChatResponse(
                action="list_all",
                message=message,
                items=items,
                confidence=1.0
            )
        else:
            return ChatResponse(
                action="list_all",
                message="📋 현재 등록된 물품이 없습니다.",
                confidence=1.0
            )
    
    def handle_search(self, query: str) -> ChatResponse:
        """일반 검색 처리"""
        # 키워드 추출
        words = query.split()
        keywords = [word for word in words if len(word) > 1 and word not in ["있나요", "어디", "뭔가요"]]
        
        search_results = []
        for keyword in keywords:
            items = self.db.search_items(keyword)
            search_results.extend(items)
        
        # 중복 제거
        unique_items = []
        seen_ids = set()
        for item in search_results:
            if item.id not in seen_ids:
                unique_items.append(item)
                seen_ids.add(item.id)
        
        if unique_items:
            message = f"🔍 **검색 결과** ('{' '.join(keywords)}')\\n\\n"
            for item in unique_items:
                message += f"📦 **{item.name}**\\n"
                message += f"   • 설명: {item.description}\\n"
                message += f"   • 위치: {item.grid_position}\\n"
                message += f"   • 카테고리: {item.category}\\n\\n"
            
            return ChatResponse(
                action="search_results",
                message=message,
                items=unique_items,
                confidence=0.7
            )
        else:
            suggestions = self.knowledge_base.get_suggestions(query)
            message = f"❌ **검색 결과가 없습니다.**\\n\\n"
            if suggestions:
                message += f"**이런 도구들을 찾으시는 건 아닌가요?**\\n"
                for suggestion in suggestions:
                    message += f"• {suggestion}\\n"
            
            return ChatResponse(
                action="no_results",
                message=message,
                suggestions=suggestions,
                confidence=0.3
            )

# Streamlit 앱 설정
st.set_page_config(
    page_title="🤖 지능형 물품 관리 AI 챗봇",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = IntelligentChatBot()

if 'messages' not in st.session_state:
    st.session_state.messages = []

# 메인 헤더
st.markdown("""
# 🤖 지능형 물품 관리 AI 챗봇

초보자를 위한 스마트 도구 안내 시스템입니다.
음성 인식, 교육적 응답, 실시간 제안 기능을 지원합니다.
""")

# 사이드바
with st.sidebar:
    st.header("🛠️ 시스템 설정")
    
    # 빠른 질문 버튼
    st.subheader("💬 빠른 질문")
    quick_questions = [
        "전선 자르는 도구가 뭔가요?",
        "나사 돌리는 도구는 뭐가 있나요?",
        "납땜할 때 뭘 써야 하나요?",
        "전압 측정하는 도구가 있나요?",
        "모든 도구 목록을 보여주세요"
    ]
    
    for question in quick_questions:
        if st.button(question):
            st.session_state.quick_question = question
            st.rerun()
    
    # 사용 팁
    st.subheader("💡 사용 팁")
    st.markdown("""
    **질문 예시:**
    - "전선 자르는 도구가 뭔가요?"
    - "우리 물품 중에 멀티미터 있나요?"
    - "모든 도구 목록을 보여주세요"
    
    **지원 기능:**
    - 도구 정의 및 설명
    - 보유 물품 확인
    - 사용법 안내
    - 관련 도구 제안
    """)
    
    # 대화 기록 초기화
    if st.button("🗑️ 대화 기록 초기화"):
        st.session_state.messages = []
        st.session_state.chatbot.conversation_history = []
        st.rerun()

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # 응답 데이터 표시
        if "response_data" in message and message["response_data"]:
            response_data = message["response_data"]
            
            # 신뢰도 표시
            if response_data.get("confidence", 0) > 0:
                confidence = response_data["confidence"]
                st.progress(confidence, text=f"응답 신뢰도: {confidence:.0%}")
            
            # 아이템 목록 표시
            if response_data.get("items"):
                st.subheader("📦 관련 물품")
                for item in response_data["items"]:
                    with st.expander(f"{item.name} - {item.grid_position}"):
                        st.write(f"**설명:** {item.description}")
                        st.write(f"**카테고리:** {item.category}")
                        st.write(f"**위치:** {item.grid_position}")
            
            # 제안 표시
            if response_data.get("suggestions"):
                st.subheader("💡 관련 제안")
                for suggestion in response_data["suggestions"]:
                    st.write(f"• {suggestion}")

# 채팅 입력 (메인 영역에 배치)
if 'quick_question' in st.session_state:
    user_input = st.session_state.quick_question
    del st.session_state.quick_question
else:
    user_input = st.chat_input("💬 도구나 장비에 대해 무엇이든 물어보세요... (예: '전선 자르는 도구가 뭔가요?')")

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
                    st.progress(response.confidence, text=f"응답 신뢰도: {response.confidence:.0%}")
                
                # 아이템 목록 표시
                if response.items:
                    st.subheader("📦 관련 물품")
                    for item in response.items:
                        with st.expander(f"{item.name} - {item.grid_position}"):
                            st.write(f"**설명:** {item.description}")
                            st.write(f"**카테고리:** {item.category}")
                            st.write(f"**위치:** {item.grid_position}")
                
                # 제안 표시
                if response.suggestions:
                    st.subheader("💡 관련 제안")
                    for suggestion in response.suggestions:
                        st.write(f"• {suggestion}")
                
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

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    🤖 <b>지능형 물품 관리 AI 챗봇</b><br>
    초보자를 위한 스마트 도구 안내 시스템<br>
    <small>AI 기반 의도 분석 • 교육적 응답 • 실시간 제안</small>
</div>
""", unsafe_allow_html=True)
