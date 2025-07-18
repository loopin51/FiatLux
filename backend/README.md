# 🔧 백엔드 서비스 (Backend)

## 📋 개요

백엔드 서비스는 **Python FastAPI**를 기반으로 한 RESTful API 서버입니다. 
물품 데이터베이스 관리, AI 엔진 통합, 하드웨어 제어 등의 핵심 비즈니스 로직을 담당합니다.

## 🏗️ 아키텍처

```
backend/
├── api/              # REST API 엔드포인트
│   ├── __init__.py
│   ├── items.py      # 물품 관련 API
│   ├── search.py     # 검색 관련 API
│   └── hardware.py   # 하드웨어 제어 API
│
├── controllers/      # 비즈니스 로직
│   ├── __init__.py
│   ├── esp32_controller.py    # ESP32 LED 제어
│   ├── gemini_agent.py        # AI 에이전트
│   └── item_controller.py     # 물품 관리 로직
│
├── database/         # 데이터베이스 관리
│   ├── __init__.py
│   ├── database.py   # 데이터베이스 연결/쿼리
│   └── schema.sql    # 데이터베이스 스키마
│
├── mcp/             # MCP (Model Context Protocol) 서버
│   ├── __init__.py
│   ├── mcp_server.py # MCP 서버 구현
│   └── tools.py      # MCP 도구 정의
│
├── models/          # 데이터 모델
│   ├── __init__.py
│   ├── models.py     # Pydantic 모델
│   └── enums.py      # 열거형 정의
│
└── tests/           # 테스트 코드
    ├── __init__.py
    ├── test_api.py
    ├── test_controllers.py
    └── test_database.py
```

## 🚀 실행 방법

### 개발 환경 실행
```bash
# 백엔드 서비스만 실행
./scripts/start_backend.sh

# 또는 수동 실행
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 접속 정보
- **API 서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/redoc

## 📡 주요 API 엔드포인트

### 물품 관리 API
```
GET    /api/items                 # 모든 물품 조회
GET    /api/items/{id}            # 특정 물품 조회
POST   /api/items                 # 새 물품 추가
PUT    /api/items/{id}            # 물품 정보 수정
DELETE /api/items/{id}            # 물품 삭제
GET    /api/items/search?q={query} # 물품 검색
```

### 하드웨어 제어 API
```
POST   /api/hardware/led/highlight  # LED 위치 표시
POST   /api/hardware/led/off        # 모든 LED 끄기
GET    /api/hardware/status         # 하드웨어 상태 확인
```

### AI 에이전트 API
```
POST   /api/ai/query               # AI 질의 처리
GET    /api/ai/suggestions         # 추천 제안
```

## 🗄️ 데이터베이스 스키마

### items 테이블
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    grid_position TEXT,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 사용 예시
```python
# 물품 검색
items = db.search_items("드라이버")

# 새 물품 추가
new_item = {
    "name": "십자 드라이버",
    "description": "일반용 십자 드라이버",
    "category": "나사_작업",
    "grid_position": "A1",
    "quantity": 5
}
db.add_item(new_item)
```

## 🤖 AI 엔진 통합

### Gemini AI 에이전트
```python
# gemini_agent.py
class GeminiItemAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.db = ItemDatabase()
    
    async def process_query(self, query: str) -> dict:
        """사용자 질의를 AI로 처리"""
        # 1. 데이터베이스에서 관련 아이템 검색
        items = self.db.search_items(query)
        
        # 2. AI 컨텍스트 생성
        context = self.build_context(items)
        
        # 3. AI 응답 생성
        response = await self.model.generate_content(
            f"Context: {context}\nQuery: {query}"
        )
        
        return {
            "message": response.text,
            "items": items,
            "confidence": 0.9
        }
```

## 🔌 하드웨어 제어

### ESP32 LED 제어
```python
# esp32_controller.py
class ESP32Controller:
    def __init__(self, ip_address: str):
        self.ip = ip_address
        self.base_url = f"http://{ip_address}"
    
    def highlight_location(self, positions: List[str], color: dict, duration: int = 5):
        """특정 위치의 LED를 강조 표시"""
        payload = {
            "positions": positions,
            "color": color,
            "duration": duration
        }
        
        response = requests.post(f"{self.base_url}/highlight", json=payload)
        return response.status_code == 200
```

### 그리드 위치 파싱
```python
def parse_grid_position(position: str) -> List[int]:
    """그리드 위치를 LED 인덱스로 변환"""
    # 예: "A1" -> [0], "A1-A3" -> [0, 1, 2]
    if '-' in position:
        start, end = position.split('-')
        return list(range(grid_to_index(start), grid_to_index(end) + 1))
    else:
        return [grid_to_index(position)]
```

## 🔄 MCP 서버

### MCP (Model Context Protocol) 서버
```python
# mcp_server.py
class MCPServer:
    def __init__(self):
        self.db = ItemDatabase()
        self.tools = [
            "search_items",
            "add_item",
            "update_item",
            "delete_item",
            "highlight_location"
        ]
    
    async def handle_request(self, request: dict) -> dict:
        """MCP 요청 처리"""
        tool_name = request.get("tool")
        params = request.get("params", {})
        
        if tool_name == "search_items":
            return self.search_items(params.get("query"))
        elif tool_name == "highlight_location":
            return self.highlight_location(params)
        
        return {"error": "Unknown tool"}
```

## 🧪 테스트

### 단위 테스트 실행
```bash
# 전체 테스트
python -m pytest tests/

# 특정 테스트
python -m pytest tests/test_api.py
python -m pytest tests/test_database.py

# 커버리지 포함
python -m pytest tests/ --cov=backend
```

### API 테스트 예시
```python
# test_api.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_items():
    response = client.get("/api/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_search_items():
    response = client.get("/api/items/search?q=드라이버")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
```

## 🔧 환경 설정

### 필요한 환경 변수
```bash
# .env 파일
DATABASE_URL=sqlite:///items.db
GOOGLE_API_KEY=your_gemini_api_key
ESP32_IP=192.168.1.100
CORS_ORIGINS=http://localhost:3000,http://localhost:8501
DEBUG=true
```

### 의존성 관리
```bash
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.21
pydantic==2.4.2
google-generativeai==0.3.1
requests==2.31.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-cov==4.1.0
```

## 🚨 에러 핸들링

### 공통 에러 응답
```python
# 404 에러
{
    "error": "Item not found",
    "error_code": "ITEM_NOT_FOUND",
    "message": "ID가 123인 물품을 찾을 수 없습니다."
}

# 500 에러
{
    "error": "Internal server error",
    "error_code": "INTERNAL_ERROR",
    "message": "서버 내부 오류가 발생했습니다."
}
```

## 📊 로깅

### 로그 설정
```python
# logging.conf
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)
```

## 🔍 디버깅

### 디버깅 명령어
```bash
# 백엔드 서비스 상태 확인
curl http://localhost:8000/health

# 데이터베이스 직접 확인
sqlite3 items.db "SELECT * FROM items LIMIT 10;"

# 로그 실시간 확인
tail -f logs/backend.log
```

## 🤝 개발 가이드

### 새로운 API 추가
1. `backend/api/` 디렉토리에 새 모듈 생성
2. `backend/controllers/` 에 비즈니스 로직 구현
3. `backend/tests/` 에 테스트 코드 작성
4. API 문서 업데이트

### 데이터베이스 스키마 변경
1. `backend/database/schema.sql` 수정
2. 마이그레이션 스크립트 작성
3. 테스트 데이터 업데이트

---

> 💡 **개발 팁**: API 변경 시 프론트엔드 팀과 사전 협의하고, 테스트 코드를 먼저 작성하는 TDD 방식을 권장합니다!
