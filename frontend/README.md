# 🎨 프론트엔드 애플리케이션 (Frontend)

## 📋 개요

프론트엔드는 **두 가지 주요 인터페이스**를 제공합니다:
1. **Next.js 웹 애플리케이션** - 관리자용 물품 관리 인터페이스
2. **Streamlit AI 챗봇** - 사용자용 대화형 검색 인터페이스

## 🏗️ 아키텍처

```
frontend/
├── nextjs-inventory/           # Next.js 웹 애플리케이션
│   ├── src/
│   │   ├── app/               # App Router 페이지
│   │   ├── components/        # React 컴포넌트
│   │   ├── lib/              # 유틸리티 함수
│   │   └── types/            # TypeScript 타입 정의
│   ├── public/               # 정적 파일
│   ├── package.json          # Node.js 의존성
│   └── README.md             # Next.js 앱 문서
│
├── intelligent_chatbot_client.py    # 메인 Streamlit 챗봇
├── intelligent_chatbot_simple.py    # 간단 버전 챗봇
├── streamlit_client.py              # 기본 Streamlit 클라이언트
├── streamlit_optimized_client.py    # 최적화된 클라이언트
└── streamlit_enhanced_chatbot.py    # 향상된 챗봇
```

## 🚀 실행 방법

### Next.js 웹 애플리케이션
```bash
# 프론트엔드 서비스 실행
./scripts/start_frontend.sh

# 또는 수동 실행
cd frontend/nextjs-inventory
npm run dev
```

### Streamlit AI 챗봇
```bash
# 챗봇 서비스 실행
./scripts/start_dev.sh

# 또는 수동 실행
cd frontend
streamlit run intelligent_chatbot_client.py --server.port 8501
```

### 접속 정보
- **Next.js 웹 앱**: http://localhost:3000
- **Streamlit 챗봇**: http://localhost:8501
- **간단 버전 챗봇**: http://localhost:8502

## 🌐 Next.js 웹 애플리케이션

### 주요 기능
1. **대시보드**: 전체 물품 현황 요약
2. **물품 관리**: CRUD 작업 (생성, 조회, 수정, 삭제)
3. **검색 및 필터**: 고급 검색 옵션
4. **그리드 시각화**: 물품 위치 시각적 표시
5. **카테고리 관리**: 물품 분류 시스템

### 페이지 구조
```
src/app/
├── page.tsx              # 홈페이지 (대시보드)
├── items/
│   ├── page.tsx          # 물품 목록 페이지
│   ├── [id]/
│   │   └── page.tsx      # 물품 상세 페이지
│   └── add/
│       └── page.tsx      # 물품 추가 페이지
├── grid/
│   └── page.tsx          # 그리드 시각화 페이지
└── layout.tsx            # 레이아웃 컴포넌트
```

### 주요 컴포넌트
```typescript
// components/ItemCard.tsx
interface ItemCardProps {
  item: Item;
  onEdit: (item: Item) => void;
  onDelete: (id: number) => void;
  onHighlight: (position: string) => void;
}

export const ItemCard: React.FC<ItemCardProps> = ({ item, onEdit, onDelete, onHighlight }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-semibold">{item.name}</h3>
      <p className="text-gray-600">{item.description}</p>
      <div className="mt-4 flex justify-between">
        <span className="text-sm bg-blue-100 px-2 py-1 rounded">
          {item.category}
        </span>
        <span className="text-sm bg-green-100 px-2 py-1 rounded">
          {item.grid_position}
        </span>
      </div>
      <div className="mt-4 flex gap-2">
        <button onClick={() => onEdit(item)} className="btn-primary">
          수정
        </button>
        <button onClick={() => onDelete(item.id)} className="btn-danger">
          삭제
        </button>
        <button onClick={() => onHighlight(item.grid_position)} className="btn-secondary">
          위치 표시
        </button>
      </div>
    </div>
  );
};
```

### API 연동
```typescript
// lib/api.ts
export class ItemsAPI {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  async getAllItems(): Promise<Item[]> {
    const response = await fetch(`${this.baseUrl}/api/items`);
    return response.json();
  }
  
  async searchItems(query: string): Promise<Item[]> {
    const response = await fetch(`${this.baseUrl}/api/items/search?q=${query}`);
    return response.json();
  }
  
  async addItem(item: Omit<Item, 'id'>): Promise<Item> {
    const response = await fetch(`${this.baseUrl}/api/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item)
    });
    return response.json();
  }
  
  async highlightLocation(position: string): Promise<boolean> {
    const response = await fetch(`${this.baseUrl}/api/hardware/led/highlight`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ position })
    });
    return response.ok;
  }
}
```

## 🤖 Streamlit AI 챗봇

### 주요 기능
1. **자연어 처리**: "전선 자르는 도구가 뭔가요?" 같은 질문 이해
2. **교육적 응답**: 초보자를 위한 상세한 설명
3. **음성 인식**: 음성 파일을 텍스트로 변환
4. **실시간 제안**: 관련 도구 추천
5. **LED 제어**: 물품 위치 LED 표시

### 핵심 클래스
```python
# intelligent_chatbot_client.py
class IntelligentChatBot:
    def __init__(self):
        self.db = ItemDatabase()
        self.knowledge_base = ToolKnowledgeBase()
        self.gemini_agent = GeminiItemAgent()
        self.conversation_history = []
    
    def analyze_user_intent(self, query: str) -> Dict[str, Any]:
        """사용자 의도 분석"""
        # 질문 유형 분류: definition, availability, location, usage
        intent = {"type": "unknown", "confidence": 0.0}
        
        if any(pattern in query.lower() for pattern in ["뭔가요", "무엇인가요"]):
            intent["type"] = "definition"
            intent["confidence"] = 0.9
        elif any(pattern in query.lower() for pattern in ["있나요", "보유"]):
            intent["type"] = "availability"
            intent["confidence"] = 0.9
        
        return intent
    
    async def process_query(self, user_input: str) -> ChatResponse:
        """사용자 쿼리 처리"""
        intent = self.analyze_user_intent(user_input)
        
        if intent["type"] == "definition":
            return self.generate_educational_response(intent, user_input)
        elif intent["type"] == "availability":
            return self.check_availability(user_input)
        
        return self.fallback_response(user_input)
```

### 도구 지식 베이스
```python
class ToolKnowledgeBase:
    def __init__(self):
        self.tool_categories = {
            "전선_작업": {
                "tools": ["와이어 커터", "니퍼", "스트리핑 툴"],
                "description": "전선을 자르고, 피복을 벗기고, 연결하는 도구들",
                "keywords": ["전선", "와이어", "케이블", "자르기"],
                "usage": [
                    "전선 자르기: 와이어 커터, 니퍼 사용",
                    "전선 피복 벗기기: 스트리핑 툴 사용"
                ]
            },
            "나사_작업": {
                "tools": ["십자 드라이버", "일자 드라이버", "육각 드라이버"],
                "description": "나사를 조이고 푸는 도구들",
                "keywords": ["나사", "스크류", "볼트", "조이기"],
                "usage": [
                    "십자 나사: 십자 드라이버 사용",
                    "일자 나사: 일자 드라이버 사용"
                ]
            }
        }
```

### 사용자 인터페이스
```python
# Streamlit UI 구성
st.set_page_config(
    page_title="🤖 지능형 물품 관리 AI 챗봇",
    page_icon="🤖",
    layout="wide"
)

# 사이드바 설정
with st.sidebar:
    st.header("🛠️ 시스템 설정")
    
    # 빠른 질문 버튼
    quick_questions = [
        "전선 자르는 도구가 뭔가요?",
        "나사 돌리는 도구는 뭐가 있나요?",
        "납땜할 때 뭘 써야 하나요?"
    ]
    
    for question in quick_questions:
        if st.button(question):
            st.session_state.quick_question = question

# 메인 채팅 영역
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력
user_input = st.chat_input("💬 도구나 장비에 대해 무엇이든 물어보세요...")

if user_input:
    response = asyncio.run(chatbot.process_query(user_input))
    
    # 응답 표시
    with st.chat_message("assistant"):
        st.markdown(response.message)
        
        # 신뢰도 표시
        if response.confidence > 0:
            st.progress(response.confidence)
        
        # 관련 물품 표시
        if response.items:
            for item in response.items:
                with st.expander(f"{item.name} - {item.grid_position}"):
                    st.write(f"**설명:** {item.description}")
                    if st.button(f"위치 표시", key=f"led_{item.id}"):
                        highlight_item_location(item.grid_position)
```

## 🎤 음성 인식 기능

### STT (Speech-to-Text) 구현
```python
class STTManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
    
    def recognize_speech_from_file(self, audio_file) -> str:
        """파일에서 음성을 인식"""
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio, language='ko-KR')
            return text
        except sr.UnknownValueError:
            return "음성을 인식할 수 없습니다."
        except Exception as e:
            return f"오류: {e}"

# Streamlit에서 음성 파일 업로드
uploaded_audio = st.file_uploader("음성 파일 업로드", type=['wav', 'mp3'])
if uploaded_audio:
    recognized_text = stt_manager.recognize_speech_from_file(uploaded_audio)
    st.success(f"인식 결과: {recognized_text}")
```

## 🎨 스타일링 및 테마

### Tailwind CSS 설정
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#667eea',
        secondary: '#764ba2',
        accent: '#f093fb',
      },
    },
  },
  plugins: [],
}
```

### Streamlit 커스텀 CSS
```python
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .educational-box {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4169e1;
    }
    .item-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)
```

## 🔧 환경 설정

### Next.js 환경 변수
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws
```

### Streamlit 설정
```toml
# .streamlit/config.toml
[global]
developmentMode = false

[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## 📱 반응형 디자인

### 모바일 최적화
```typescript
// 반응형 그리드 컴포넌트
const GridView: React.FC = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {items.map(item => (
        <ItemCard key={item.id} item={item} />
      ))}
    </div>
  );
};
```

## 🧪 테스트

### React 컴포넌트 테스트
```typescript
// components/__tests__/ItemCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ItemCard } from '../ItemCard';

describe('ItemCard', () => {
  const mockItem = {
    id: 1,
    name: '십자 드라이버',
    description: '일반용 십자 드라이버',
    category: '나사_작업',
    grid_position: 'A1'
  };

  it('물품 정보를 올바르게 표시한다', () => {
    render(<ItemCard item={mockItem} onEdit={() => {}} onDelete={() => {}} onHighlight={() => {}} />);
    
    expect(screen.getByText('십자 드라이버')).toBeInTheDocument();
    expect(screen.getByText('일반용 십자 드라이버')).toBeInTheDocument();
    expect(screen.getByText('A1')).toBeInTheDocument();
  });
});
```

### Streamlit 테스트
```python
# test_streamlit_app.py
import streamlit as st
from streamlit.testing.v1 import AppTest

def test_chatbot_response():
    """챗봇 응답 테스트"""
    app = AppTest.from_file("intelligent_chatbot_client.py")
    app.run()
    
    # 사용자 입력 시뮬레이션
    app.chat_input("전선 자르는 도구가 뭔가요?").run()
    
    # 응답 확인
    assert len(app.chat_message) > 0
    assert "와이어 커터" in app.chat_message[-1].markdown
```

## 🚀 배포

### Next.js 빌드
```bash
# 프로덕션 빌드
cd frontend/nextjs-inventory
npm run build
npm start
```

### Streamlit 배포
```bash
# Streamlit 클라우드 배포
streamlit run intelligent_chatbot_client.py --server.port 8501 --server.address 0.0.0.0
```

## 🔍 디버깅

### 브라우저 개발자 도구
```javascript
// 디버깅용 콘솔 로그
console.log('API 응답:', response);
console.error('API 오류:', error);

// 성능 모니터링
console.time('API 호출');
await api.getAllItems();
console.timeEnd('API 호출');
```

### Streamlit 디버깅
```python
# 디버깅 정보 표시
if st.checkbox("디버그 모드"):
    st.json({"intent": intent, "confidence": confidence})
    st.write("세션 상태:", st.session_state)
```

## 🤝 개발 가이드

### 새로운 페이지 추가 (Next.js)
1. `src/app/` 하위에 새 디렉토리 생성
2. `page.tsx` 파일 생성
3. 필요한 컴포넌트 개발
4. 라우팅 테스트

### 새로운 챗봇 기능 추가
1. `ToolKnowledgeBase`에 새 카테고리 추가
2. `IntelligentChatBot`에 처리 로직 구현
3. UI 컴포넌트 추가
4. 테스트 케이스 작성

---

> 💡 **개발 팁**: 
> - Next.js는 타입 안전성을 위해 TypeScript를 적극 활용하세요
> - Streamlit은 세션 상태 관리에 주의하세요
> - 두 앱 모두 백엔드 API와의 동기화를 유지하세요
