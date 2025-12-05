# Implementation Plan: RAG Backend & Study Assistant Chat API

**Feature**: `002-rag-backend-study-assistant`
**Created**: 2025-12-05
**Status**: Draft
**Spec**: [spec.md](./spec.md)

---

## 1. Project & Directory Structure

### Overview

The backend will be a standalone Python FastAPI application living under `backend/` at the project root. It will be completely independent of the Docusaurus frontend, communicating only via HTTP/JSON APIs.

### Directory Layout

```
backend/
├── pyproject.toml          # uv project config (dependencies, metadata)
├── .python-version         # Python 3.11+
├── README.md               # Backend setup and deployment instructions
├── .env.example            # Example environment variables
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app entrypoint (app instance, lifespan, CORS)
│   ├── api/                # API routes/routers
│   │   ├── __init__.py
│   │   ├── health.py       # GET /api/health
│   │   └── chat.py         # POST /api/chat
│   ├── core/               # Core configuration, logging, dependencies
│   │   ├── __init__.py
│   │   ├── config.py       # Pydantic BaseSettings for env vars
│   │   ├── logging.py      # Structured logging setup
│   │   └── deps.py         # Dependency injection (get_db, get_qdrant_client, etc.)
│   ├── models/             # Data models
│   │   ├── __init__.py
│   │   ├── db.py           # SQLAlchemy models (ChatSession, ChatMessage)
│   │   └── schemas.py      # Pydantic schemas (request/response models)
│   ├── services/           # Business logic and external integrations
│   │   ├── __init__.py
│   │   ├── rag.py          # RAG pipeline logic (retrieval + answer generation)
│   │   ├── embeddings.py   # OpenAI embeddings service
│   │   ├── qdrant.py       # Qdrant client wrapper and search logic
│   │   └── chat_storage.py # Neon Postgres persistence logic
│   └── db/                 # Database session management
│       ├── __init__.py
│       ├── session.py      # Async SQLAlchemy engine and session factory
│       └── migrations/     # Alembic migrations (optional for MVP)
├── scripts/
│   ├── __init__.py
│   └── index_docs.py       # CLI script to index ../docs into Qdrant
└── tests/
    ├── __init__.py
    ├── conftest.py         # Pytest fixtures (mocked OpenAI, Qdrant, DB)
    ├── test_health.py      # Health endpoint tests
    └── test_chat.py        # Chat endpoint tests (whole-book, selection)
```

### Key Architectural Decisions

**Separation of Concerns**:
- **API Layer** (`app/api/`): FastAPI routers handle HTTP request/response, validation, and error formatting. No business logic here.
- **Service Layer** (`app/services/`): All business logic lives here. Services orchestrate calls to OpenAI, Qdrant, Neon Postgres, and encapsulate the RAG pipeline.
- **Data Access Layer** (`app/db/`, `app/models/db.py`): SQLAlchemy models and database session management. Services depend on this layer for persistence.

**Dependency Injection**:
- Use FastAPI's `Depends()` for injecting:
  - Database sessions (`get_db`)
  - Qdrant client (`get_qdrant_client`)
  - OpenAI client (`get_openai_client`)
  - Config (`get_config`)
- This makes testing easy (inject mocks) and keeps routers clean.

**FastAPI App Wiring** (`app/main.py`):
```python
# Pseudocode structure
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, chat
from app.core.config import settings

app = FastAPI(title="Study Assistant RAG API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # from env vars
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Lifespan event for DB/Qdrant initialization (optional)
@app.on_event("startup")
async def startup():
    # Initialize DB engine, test Qdrant connection, etc.
    pass

@app.on_event("shutdown")
async def shutdown():
    # Close DB connections, etc.
    pass
```

---

## 2. Configuration & Environment

### Environment Variables

All secrets and configuration will be managed via environment variables, loaded using **Pydantic BaseSettings**.

**Required Environment Variables**:
- `OPENAI_API_KEY`: OpenAI API key for embeddings and chat
- `QDRANT_URL`: Qdrant Cloud HTTPS URL (e.g., `https://xyz.qdrant.io`)
- `QDRANT_API_KEY`: Qdrant Cloud API key
- `DATABASE_URL`: Neon Postgres connection string (asyncpg format: `postgresql+asyncpg://user:password@host/db`)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (e.g., `http://localhost:3000,https://yourusername.github.io`)
- `OPENAI_EMBEDDING_MODEL`: Model name for embeddings (e.g., `text-embedding-3-small`)
- `OPENAI_CHAT_MODEL`: Model name for chat (e.g., `gpt-4o-mini`)
- `QDRANT_COLLECTION_NAME`: Qdrant collection name (e.g., `textbook_embeddings`)

**Optional Environment Variables**:
- `LOG_LEVEL`: Logging level (`INFO`, `DEBUG`, `WARNING`), default `INFO`
- `MAX_QUESTION_TOKENS`: Max question length in tokens (default 500)
- `MAX_SELECTION_TOKENS`: Max selectedText length in tokens (default 500)
- `CHUNK_RETRIEVAL_LIMIT`: Number of chunks to retrieve (default 10)

### Configuration Module (`app/core/config.py`)

```python
# Pseudocode structure
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "textbook_embeddings"

    # Neon Postgres
    DATABASE_URL: str

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Limits
    MAX_QUESTION_TOKENS: int = 500
    MAX_SELECTION_TOKENS: int = 500
    CHUNK_RETRIEVAL_LIMIT: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

settings = Settings()
```

### Dev vs Prod Configuration

**Development** (`.env` file in `backend/`):
- `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`
- Database and API keys for dev/staging resources
- `.env` is in `.gitignore` (NEVER committed)

**Production**:
- Environment variables set via hosting platform (Render, Fly.io, Railway)
- `CORS_ORIGINS=https://yourusername.github.io` (Docusaurus GitHub Pages URL)
- Production API keys and database URLs

### .gitignore Rules

```gitignore
# Backend
backend/.env
backend/.python-version
backend/__pycache__/
backend/**/__pycache__/
backend/.pytest_cache/
backend/**/.pytest_cache/
backend/dist/
backend/.venv/
```

---

## 3. Data Modeling (Neon Postgres)

### SQLAlchemy Models (`app/models/db.py`)

**Technology Choice**:
- **SQLAlchemy 2.x** with async support
- **asyncpg** driver for Neon Postgres
- **UUID** for primary keys (future-proof for distributed systems)
- **Timestamps** for all records (created_at, updated_at)

**ChatSession Model**:
```python
# Pseudocode structure
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=True, index=True)  # String for now, nullable
    mode = Column(Enum("whole-book", "selection", name="chat_mode"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to messages (one-to-many)
    # messages = relationship("ChatMessage", back_populates="session")
```

**ChatMessage Model**:
```python
# Pseudocode structure
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(Enum("user", "assistant", name="message_role"), nullable=False)
    content = Column(Text, nullable=False)
    selected_text = Column(Text, nullable=True)  # Only for selection-based messages
    doc_path = Column(String, nullable=True)  # Only for selection-based messages
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to session (many-to-one)
    # session = relationship("ChatSession", back_populates="messages")
```

**Future-Proofing for Better-Auth**:
- `user_id` is a `String` (not a foreign key to a users table yet)
- When Better-Auth is integrated later, we can:
  - Create a `users` table with `id (UUID)` and `external_id (String)`
  - Migrate existing `user_id` strings to foreign key references
  - Add a migration to backfill `users` table from existing `chat_sessions.user_id`

**Database Initialization**:
- Use Alembic for migrations (optional for MVP; can also just create tables on startup)
- For MVP, can use `Base.metadata.create_all(engine)` on app startup if tables don't exist
- For production, recommend Alembic migrations for schema evolution

---

## 4. Qdrant Schema & Indexing Strategy

### Qdrant Collection Configuration

**Collection Name**: `textbook_embeddings`

**Vector Configuration**:
- **Model**: `text-embedding-3-small` (OpenAI)
- **Dimensions**: 1536 (default for text-embedding-3-small)
- **Distance Metric**: Cosine similarity (standard for semantic search)

**Payload Schema** (metadata stored with each vector):
```json
{
  "doc_path": "/docs/module-1-ros2/chapter-1-basics",
  "module_id": 1,
  "heading": "Chapter 1: Basics > Section 1.1: Installation",
  "chunk_index": 0,
  "text": "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software..."
}
```

**Index Configuration**:
- Use HNSW (Hierarchical Navigable Small World) index for fast approximate nearest neighbor search
- Default parameters should work for small corpus (< 10k chunks)

**Collection Creation** (done once, manually or via script):
```python
# Pseudocode
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

client.create_collection(
    collection_name="textbook_embeddings",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)
```

### Indexing Script: `backend/scripts/index_docs.py`

**Purpose**: Process all Markdown/MDX files under `../docs`, chunk them, generate embeddings, and upsert to Qdrant.

**Workflow**:

1. **Discover Files**:
   - Recursively scan `../docs` for all `.md` and `.mdx` files
   - Skip non-content files (e.g., `_category_.json`, hidden files)

2. **Parse and Preprocess**:
   - Read file content
   - Strip YAML frontmatter (using regex or `python-frontmatter` library)
   - Extract metadata from frontmatter or file path:
     - `module_id`: Infer from path (e.g., `/docs/module-1-ros2/...` → `1`)
     - `doc_path`: Relative path from project root (e.g., `/docs/module-1-ros2/chapter-1-basics`)

3. **Chunking Strategy** (Hybrid Approach):
   - **Primary**: Chunk by heading (##, ###)
     - Split on Markdown headings
     - Preserve heading hierarchy (e.g., "Chapter 1 > Section 1.1")
     - Each chunk = content under one heading
   - **Secondary**: If heading-based chunk > 500 tokens, split further using fixed token length (200-500 tokens) with 50-token overlap
   - Use `tiktoken` library to count tokens (for `text-embedding-3-small` tokenizer)

4. **Generate Embeddings**:
   - For each chunk, call OpenAI embeddings API:
     ```python
     response = openai.Embedding.create(
         model="text-embedding-3-small",
         input=chunk_text
     )
     embedding = response['data'][0]['embedding']
     ```
   - Batch requests (up to 100 chunks per API call) for efficiency

5. **Upsert to Qdrant**:
   - Use `doc_path + chunk_index` as unique ID (e.g., `"/docs/module-1-ros2/chapter-1-basics:0"`)
   - Upsert points to Qdrant collection:
     ```python
     client.upsert(
         collection_name="textbook_embeddings",
         points=[
             {
                 "id": f"{doc_path}:{chunk_index}",
                 "vector": embedding,
                 "payload": {
                     "doc_path": doc_path,
                     "module_id": module_id,
                     "heading": heading,
                     "chunk_index": chunk_index,
                     "text": chunk_text
                 }
             }
         ]
     )
     ```

6. **Idempotence**:
   - Using `doc_path:chunk_index` as ID ensures upsert behavior: existing chunks are updated, new chunks are inserted
   - Re-running the script will not duplicate chunks
   - If a document is deleted, its chunks remain in Qdrant (manual cleanup required, or implement a "delete missing docs" step)

7. **Error Handling**:
   - Retry logic for OpenAI API rate limits (exponential backoff)
   - Log errors for individual files but continue processing other files
   - Print summary at end: "Indexed 45 chunks from 12 documents (3 errors)"

8. **CLI Interface**:
   ```bash
   # Run from project root
   uv run python backend/scripts/index_docs.py --docs-dir ./docs

   # Optional flags
   --collection-name textbook_embeddings  # Override collection name
   --batch-size 50                        # Batch size for embeddings API
   --dry-run                              # Preview chunks without uploading
   ```

**Dependencies**:
- `qdrant-client`: Qdrant Python client
- `openai`: OpenAI Python SDK
- `tiktoken`: Token counting for OpenAI models
- `python-frontmatter`: Parse YAML frontmatter
- `click`: CLI framework (optional, for better UX)

---

## 5. Chat Pipeline (Whole-Book & Selection-Based)

### Request/Response Schemas (`app/models/schemas.py`)

**ChatRequest**:
```python
# Pseudocode
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    mode: Literal["whole-book", "selection"]
    question: str = Field(..., min_length=1, max_length=2000)
    selectedText: str | None = None
    docPath: str | None = None
    userId: str | None = None

    @validator("selectedText")
    def validate_selection_mode(cls, v, values):
        if values.get("mode") == "selection" and not v:
            raise ValueError("selectedText is required when mode='selection'")
        return v
```

**Citation**:
```python
class Citation(BaseModel):
    docPath: str
    heading: str
    snippet: str  # ~50-100 words
```

**ChatResponse**:
```python
class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list, min_items=0, max_items=5)
    mode: Literal["whole-book", "selection"]
```

### RAG Pipeline (`app/services/rag.py`)

**High-Level Flow**:
```
1. Validate request (question length, selectedText if needed)
2. Retrieve relevant chunks from Qdrant
3. Construct context from retrieved chunks
4. Call OpenAI chat completion with context + question
5. Extract citations from retrieved chunks
6. Return ChatResponse
```

**Whole-Book Mode**:
1. **Generate Question Embedding**:
   ```python
   question_embedding = await embeddings_service.embed_text(request.question)
   ```

2. **Search Qdrant** (top 5-10 chunks):
   ```python
   search_results = qdrant_client.search(
       collection_name="textbook_embeddings",
       query_vector=question_embedding,
       limit=10,  # FR-004: retrieve top 5-10 chunks
       score_threshold=None  # No threshold (Clarification #2)
   )
   ```

3. **Extract Chunks**:
   ```python
   chunks = [result.payload for result in search_results]
   ```

**Selection Mode**:
1. **Find Chunks Containing Selected Text**:
   - Approach 1 (Exact Match): Query Qdrant payload for chunks where `text` contains `selectedText`
   - Approach 2 (Embedding Search): Embed `selectedText`, search within `docPath` filtered results

   **Recommended: Hybrid Approach**:
   - Filter by `doc_path == request.docPath`
   - Search within filtered results using selectedText embedding
   - Retrieve top 1 matching chunk + 2-3 neighbors by `chunk_index`

   ```python
   # Step 1: Find the chunk containing selectedText
   selected_chunk = await qdrant_service.find_chunk_by_text(
       doc_path=request.docPath,
       text=request.selectedText
   )

   # Step 2: Get neighboring chunks
   chunk_index = selected_chunk.payload["chunk_index"]
   neighbor_chunks = await qdrant_service.get_chunks_by_index_range(
       doc_path=request.docPath,
       start_index=max(0, chunk_index - 2),
       end_index=chunk_index + 3
   )

   chunks = neighbor_chunks  # 5-6 chunks total (2 before, 1 selected, 2-3 after)
   ```

2. **Fallback**:
   - If `docPath` is invalid or no chunks found, fall back to whole-book mode with warning (FR-019)

**OpenAI Chat Completion**:

**System Prompt** (designed to reduce hallucinations):
```
You are a helpful study assistant for the Physical AI & Humanoid Robotics Textbook.
Your role is to answer questions based ONLY on the provided textbook excerpts.

IMPORTANT RULES:
1. Only use information from the provided textbook excerpts.
2. If the excerpts don't contain the answer, say: "I don't have information about that in the textbook."
3. Do not make up information or use external knowledge.
4. Cite specific sections when answering (e.g., "According to Chapter 1...").
5. Be concise but thorough.

TEXTBOOK EXCERPTS:
{context}

Answer the user's question based on the excerpts above.
```

**User Prompt**:
```
{question}
```

**API Call**:
```python
response = await openai_client.chat.completions.create(
    model=settings.OPENAI_CHAT_MODEL,  # gpt-4o-mini
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.question}
    ],
    temperature=0.3,  # Low temperature for factual responses
    max_tokens=500
)

answer = response.choices[0].message.content
```

**Construct Citations** (top 3-5 chunks):
```python
citations = []
for chunk in chunks[:5]:  # FR-008: 3-5 citations
    citations.append(Citation(
        docPath=chunk["doc_path"],
        heading=chunk["heading"],
        snippet=chunk["text"][:200] + "..."  # ~50-100 words
    ))
```

**Error Handling**:
- OpenAI rate limits (429): Return 429 with message "The chatbot is temporarily overloaded. Please try again in a moment."
- OpenAI errors (500): Return 503 with message "The chatbot service is temporarily unavailable."
- Qdrant errors: Return 503 with message "The search service is temporarily unavailable."

---

## 6. API Design & Routing

### Health Endpoint (`app/api/health.py`)

**Route**: `GET /api/health`

**Purpose**: Check status of backend, Qdrant Cloud, and Neon Postgres

**Response Schema**:
```python
class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    services: dict[str, Literal["ok", "error"]]
```

**Implementation**:
```python
@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db),
    qdrant_client: QdrantClient = Depends(get_qdrant_client)
):
    services = {}

    # Check Qdrant
    try:
        qdrant_client.get_collections()  # Simple health check
        services["qdrant"] = "ok"
    except Exception:
        services["qdrant"] = "error"

    # Check Postgres
    try:
        await db.execute(text("SELECT 1"))
        services["postgres"] = "ok"
    except Exception:
        services["postgres"] = "error"

    # Overall status
    status = "ok" if all(v == "ok" for v in services.values()) else "degraded"

    # Return 503 if degraded
    if status == "degraded":
        raise HTTPException(status_code=503, detail={"status": status, "services": services})

    return HealthResponse(status=status, services=services)
```

### Chat Endpoint (`app/api/chat.py`)

**Route**: `POST /api/chat`

**Request**: `ChatRequest` (see schemas above)

**Response**: `ChatResponse`

**Implementation Flow**:
```python
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    qdrant_client: QdrantClient = Depends(get_qdrant_client)
):
    # 1. Validate request (Pydantic handles most of this)
    validate_input_lengths(request)  # FR-020

    # 2. RAG pipeline
    answer, chunks = await rag_service.generate_answer(request, qdrant_client)

    # 3. Create citations
    citations = create_citations(chunks[:5])  # FR-008

    # 4. Persist session and messages (if userId provided)
    if request.userId:
        await chat_storage_service.save_chat(db, request, answer)

    # 5. Return response
    return ChatResponse(
        answer=answer,
        citations=citations,
        mode=request.mode
    )
```

**Error Responses** (standardized format):
```python
class ErrorResponse(BaseModel):
    error: str
    code: str | None = None

# Examples:
# 400: {"error": "Invalid mode. Must be 'whole-book' or 'selection'."}
# 400: {"error": "mode='selection' requires selectedText to be provided."}
# 429: {"error": "The chatbot is temporarily overloaded. Please try again in a moment."}
# 503: {"error": "The chatbot service is temporarily unavailable."}
```

### CORS Configuration

**Allowed Origins** (from `settings.CORS_ORIGINS`):
- **Development**: `http://localhost:3000`, `http://127.0.0.1:3000`
- **Production**: `https://yourusername.github.io` (GitHub Pages URL for Docusaurus)

**Allowed Methods**: `GET`, `POST`

**Allowed Headers**: `*` (all headers, including `Content-Type`)

**Configuration in `app/main.py`**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 7. Session Persistence Logic

### When to Create a Session

**Decision Point**: Create a new `ChatSession` for EACH chat request when `userId` is provided (FR-009).

**Rationale**:
- No multi-turn conversation support in MVP (out of scope)
- Each question is stateless
- Session groups a single user question + assistant response pair
- `started_at` and `ended_at` are the same (or `ended_at` is set immediately after response)

**Future Enhancement**: When multi-turn conversations are added, we can:
- Keep sessions open (don't set `ended_at` immediately)
- Reuse session for follow-up questions from same user in short time window
- Add `last_activity_at` field to track session timeout

### Session Creation Flow (`app/services/chat_storage.py`)

```python
async def save_chat(
    db: AsyncSession,
    request: ChatRequest,
    answer: str
):
    if not request.userId or request.userId.strip() == "":
        # FR-021: Do not persist for anonymous users
        return

    # Create session
    session = ChatSession(
        user_id=request.userId,
        mode=request.mode,
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow()  # Immediately closed for single-shot Q&A
    )
    db.add(session)
    await db.flush()  # Get session.id before creating messages

    # Create user message
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.question,
        selected_text=request.selectedText if request.mode == "selection" else None,
        doc_path=request.docPath if request.mode == "selection" else None
    )
    db.add(user_message)

    # Create assistant message
    assistant_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer
    )
    db.add(assistant_message)

    await db.commit()
```

### Anonymous User Behavior

- If `userId` is `null`, missing, or empty string: **Do NOT persist session or messages** (FR-021)
- RAG pipeline still runs normally (retrieve chunks, generate answer, return response)
- No database writes
- No analytics tracking
- Privacy-focused: anonymous users leave no trace

---

## 8. Testing & Local Development

### Local Development Commands

**Setup**:
```bash
cd backend

# Install dependencies with uv
uv sync

# Copy example env file
cp .env.example .env
# Edit .env with your API keys and database URL

# Create Qdrant collection (one-time setup)
uv run python scripts/create_qdrant_collection.py

# Index textbook content
uv run python scripts/index_docs.py --docs-dir ../docs

# Run database migrations (if using Alembic)
uv run alembic upgrade head
```

**Run Development Server**:
```bash
# Run FastAPI app with hot reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at http://localhost:8000
# API docs at http://localhost:8000/docs (Swagger UI)
```

**Re-index After Docs Changes**:
```bash
uv run python scripts/index_docs.py --docs-dir ../docs
```

### Testing Strategy

**Test Framework**: `pytest` with `pytest-asyncio` for async tests

**Test Coverage**:
1. **Health Endpoint** (`tests/test_health.py`):
   - Test healthy state (all services ok)
   - Test degraded state (Qdrant error)
   - Test degraded state (Postgres error)

2. **Chat Endpoint** (`tests/test_chat.py`):
   - Whole-book mode happy path
   - Selection mode happy path
   - Invalid mode (400 error)
   - Missing selectedText for selection mode (400 error)
   - Question too long (400 error)
   - OpenAI rate limit (429 error, mocked)
   - Qdrant error (503 error, mocked)

3. **Session Persistence** (`tests/test_chat_storage.py`):
   - Session created when userId provided
   - No session created when userId is null
   - User and assistant messages persisted correctly

**Mocking Strategy**:
- **OpenAI API**: Mock with `pytest-mock` or `unittest.mock`
- **Qdrant Client**: Mock search results
- **Database**: Use in-memory SQLite or test Postgres database

**Example Test** (`tests/test_chat.py`):
```python
@pytest.mark.asyncio
async def test_whole_book_chat(client, mock_openai, mock_qdrant):
    # Mock Qdrant search results
    mock_qdrant.search.return_value = [
        # Mock search result with payload
    ]

    # Mock OpenAI chat completion
    mock_openai.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="ROS 2 is a framework..."))]
    )

    # Send request
    response = await client.post("/api/chat", json={
        "mode": "whole-book",
        "question": "What is ROS 2?"
    })

    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "whole-book"
    assert len(data["citations"]) >= 1
    assert "ROS 2" in data["answer"]
```

### Frontend Integration (Dev Mode)

**Frontend Configuration**:
- Docusaurus frontend (running on `http://localhost:3000`) will call backend at `http://localhost:8000/api/chat`
- Backend CORS allows `http://localhost:3000`
- Frontend adds backend URL to environment variables or config:
  ```javascript
  // In Docusaurus config or component
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

  // API call
  const response = await fetch(`${BACKEND_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: "whole-book", question: "..." })
  });
  ```

**Testing Full Stack Locally**:
1. Start backend: `uv run uvicorn app.main:app --reload` (port 8000)
2. Start frontend: `npm start` (port 3000)
3. Open `http://localhost:3000` in browser
4. Click "Ask the Textbook" button
5. Type a question and verify response from backend

---

## 9. Deployment Considerations

### Deployment Target Options

We will defer the final deployment target decision until implementation, but here are the recommended options:

**Option 1: Render (Recommended for MVP)**:
- **Pros**: Free tier available, easy setup, PostgreSQL included, good for Python apps
- **Cons**: Cold starts on free tier, limited compute
- **Setup**: Connect GitHub repo, set env vars via dashboard, deploy

**Option 2: Fly.io**:
- **Pros**: Fast deployments, good free tier, global edge deployment
- **Cons**: Requires Dockerfile, slightly more complex setup
- **Setup**: Create `fly.toml`, deploy with `flyctl deploy`

**Option 3: Railway**:
- **Pros**: Simple setup, good DX, PostgreSQL included
- **Cons**: Free tier limits, pricing can scale quickly
- **Setup**: Connect GitHub repo, set env vars, deploy

**Option 4: AWS Lambda (Advanced)**:
- **Pros**: Serverless, scales automatically, pay-per-request
- **Cons**: Cold starts, complexity (API Gateway, Lambda layers), not ideal for FastAPI
- **Not Recommended** for this project (FastAPI works better on long-running servers)

### Environment Variables in Production

**Setup Process** (example for Render):
1. Add all required env vars via hosting platform dashboard:
   - `OPENAI_API_KEY`
   - `QDRANT_URL`, `QDRANT_API_KEY`
   - `DATABASE_URL` (auto-provided by Render PostgreSQL)
   - `CORS_ORIGINS=https://yourusername.github.io`
   - `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`
   - `OPENAI_CHAT_MODEL=gpt-4o-mini`
   - `QDRANT_COLLECTION_NAME=textbook_embeddings`

2. Set build and start commands:
   - **Build**: `uv sync --frozen`
   - **Start**: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Indexing in Production

**Decision**: Indexing should be run **locally by the developer**, not in production.

**Rationale**:
- Indexing is a one-time or infrequent operation (only when textbook content changes)
- Running indexing in production adds complexity (need to trigger script, handle long-running tasks)
- Local indexing is simpler and more controllable

**Workflow**:
1. Developer edits textbook content (Markdown files in `docs/`)
2. Developer runs `uv run python backend/scripts/index_docs.py --docs-dir ./docs` locally
3. Script uploads embeddings to Qdrant Cloud (same instance used by production backend)
4. Changes are immediately available to production backend (no redeployment needed)

**Future Enhancement** (Out of Scope for MVP):
- Automate indexing via GitHub Actions:
  - Trigger on push to `docs/` directory
  - Run indexing script in CI
  - Upload to Qdrant Cloud

### Database Migrations

**For MVP**:
- Use `Base.metadata.create_all(engine)` on app startup to create tables if they don't exist
- Simple and sufficient for MVP with 2 tables

**For Production** (Recommended):
- Set up Alembic migrations:
  ```bash
  uv add alembic
  uv run alembic init migrations
  uv run alembic revision --autogenerate -m "Initial schema"
  uv run alembic upgrade head
  ```
- Run migrations as part of deployment process (before starting the app)

### Monitoring and Logging

**Logging**:
- Use structured logging with `structlog` or Python's `logging` module
- Log to stdout (hosting platforms capture logs automatically)
- Log levels: `INFO` for normal operations, `WARNING` for recoverable errors, `ERROR` for failures

**Metrics** (Future Enhancement):
- Track request latency, error rates, Qdrant search times, OpenAI API latency
- Use hosting platform's built-in metrics or integrate with tools like Sentry, DataDog

**Health Checks**:
- Hosting platforms will ping `GET /api/health` to check if app is alive
- Return 200 for healthy, 503 for degraded (causes platform to restart service)

---

## 10. Architecture Decision Records (ADR)

### ADR Candidates

The following architectural decisions should be documented as ADRs (to be created during implementation):

1. **ADR-001: Hybrid Chunking Strategy** (heading-based + token-length fallback)
   - **Decision**: Use heading-based chunking with token-length fallback for chunks > 500 tokens
   - **Rationale**: Balances semantic coherence (headings) with embedding model constraints (token limits)
   - **Alternatives**: Pure heading-based (chunks too variable), pure token-based (splits sentences awkwardly)

2. **ADR-002: OpenAI Model Selection**
   - **Decision**: Use `text-embedding-3-small` for embeddings, `gpt-4o-mini` for chat
   - **Rationale**: Cost-effective, sufficient performance for textbook Q&A, fast inference
   - **Alternatives**: `text-embedding-ada-002` (older, similar performance), `gpt-3.5-turbo` (cheaper but lower quality)

3. **ADR-003: Single-Shot Q&A vs Multi-Turn Conversations**
   - **Decision**: MVP implements single-shot Q&A only (no conversation context)
   - **Rationale**: Simplifies implementation, meets MVP requirements, can add multi-turn later
   - **Alternatives**: Multi-turn (more complex, requires session state management, out of scope for MVP)

4. **ADR-004: Stateless Backend vs Session State**
   - **Decision**: Backend is stateless; sessions are persisted to DB but not held in memory
   - **Rationale**: Simplifies deployment, scales horizontally, no need for Redis/session store
   - **Alternatives**: In-memory sessions (doesn't scale), Redis-backed sessions (adds complexity)

5. **ADR-005: Local Indexing vs Production Indexing**
   - **Decision**: Indexing runs locally by developer, not in production
   - **Rationale**: Simpler workflow, avoids long-running tasks in production, Qdrant is shared between local and prod
   - **Alternatives**: Production indexing via cron job or GitHub Actions (future enhancement)

**Suggestion**: Run `/sp.adr` after `/sp.plan` approval to document these decisions formally.

---

## 11. Complexity Tracking

### Complexity Budget

**Target Complexity**: Medium (appropriate for a hackathon project with clear requirements)

**Complexity Sources**:
1. **Hybrid Chunking Strategy**: Medium complexity (heading parsing + token counting + splitting logic)
2. **Selection-Based Retrieval**: Medium complexity (finding chunks by text + neighbors by index)
3. **Async SQLAlchemy**: Low-Medium complexity (async/await, session management)
4. **OpenAI + Qdrant Integration**: Low complexity (well-documented SDKs, straightforward API calls)
5. **CORS and Error Handling**: Low complexity (FastAPI built-ins)

**Complexity Mitigation**:
- Use well-tested libraries (`qdrant-client`, `openai`, `sqlalchemy`)
- Keep service layer functions focused and single-purpose
- Write tests for complex logic (chunking, retrieval, citations)
- Defer advanced features to future enhancements (multi-turn, streaming, analytics)

**Total Estimated Complexity**: **Medium** (acceptable for MVP scope)

---

## 12. Constitution Compliance Check

### Alignment with Constitution Principles

✅ **I. Assignment.md as Single Source of Truth**:
- Plan aligns with hackathon assignment requirements for RAG backend
- No invented robotics/hardware features

✅ **III. Spec-Driven Development**:
- Plan follows /sp.specify → /sp.clarify → /sp.plan workflow
- Spec (WHAT/WHY) is separate from plan (HOW)
- All requirements from spec.md are addressed in plan

✅ **V. RAG Chatbot: Whole-Book and Selection-Based Q&A**:
- Plan implements both modes as specified
- Qdrant Cloud and OpenAI Agents/ChatKit are used
- API keys are never committed (env vars only)

✅ **VI. Code Quality Standards**:
- Python for backend (as per constitution)
- Clear separation of concerns (API, services, data layers)
- Testable architecture with dependency injection

✅ **VII. Separation of Concerns**:
- Backend is completely independent of frontend
- Small, testable components (services, routers, models)
- Clear boundaries between layers

### No Constitution Violations

No aspects of this plan violate the project constitution.

---

## 13. Risks and Mitigations

### Risk 1: OpenAI Rate Limits

**Risk**: OpenAI API may rate-limit requests during indexing or high traffic.

**Mitigation**:
- Implement exponential backoff retry logic in indexing script
- Return 429 error to frontend when rate-limited during chat (frontend can show "Try again" message)
- Use batch embedding API for indexing (up to 100 chunks per request)

### Risk 2: Qdrant Free Tier Limits

**Risk**: Qdrant Cloud Free Tier may have storage or request limits.

**Mitigation**:
- Monitor Qdrant usage via dashboard
- Textbook is small (< 10k chunks expected), well within free tier
- If limits are hit, upgrade to paid tier (low cost for this scale)

### Risk 3: Neon Postgres Free Tier Limits

**Risk**: Neon Free Tier may have storage or connection limits.

**Mitigation**:
- Only persist sessions for authenticated users (FR-021 reduces DB usage)
- Anonymous users don't create DB records (privacy-focused approach)
- Implement 90-day retention policy to clean up old sessions (future task)

### Risk 4: Selection-Based Retrieval Accuracy

**Risk**: Finding chunks containing `selectedText` may fail if text doesn't match exactly (e.g., user selects formatted code, but chunk has raw Markdown).

**Mitigation**:
- Normalize text before comparison (strip whitespace, lowercase)
- Fall back to whole-book mode if selection retrieval fails (FR-019)
- Log failures for debugging and improvement

### Risk 5: Cold Starts on Free Tier Hosting

**Risk**: Render/Fly.io free tier may have cold start delays (5-10 seconds).

**Mitigation**:
- Accept cold starts for MVP (hackathon demo, not production)
- If unacceptable, upgrade to paid tier or use "keep-alive" pings

---

## 14. Next Steps

After plan approval:

1. **Run `/sp.tasks`** to generate dependency-ordered tasks from this plan
2. **Run `/sp.adr`** to create ADRs for key architectural decisions
3. **Run `/sp.implement`** to execute tasks and build the backend
4. **Test locally** with Docusaurus frontend
5. **Deploy to production** (Render/Fly.io/Railway)
6. **Index textbook content** to Qdrant Cloud
7. **Verify frontend integration** with deployed backend

---

## Summary

This plan provides a complete technical architecture for the RAG backend and Study Assistant chat API:

- ✅ **Clear project structure** with separation of concerns (API, services, data layers)
- ✅ **Environment-based configuration** using Pydantic BaseSettings
- ✅ **SQLAlchemy models** for Neon Postgres (ChatSession, ChatMessage)
- ✅ **Qdrant schema and indexing strategy** (hybrid chunking, embeddings, metadata)
- ✅ **RAG pipeline** for whole-book and selection-based Q&A
- ✅ **FastAPI routers** for `/api/health` and `/api/chat`
- ✅ **Session persistence logic** (only for authenticated users)
- ✅ **Testing strategy** and local development workflow
- ✅ **Deployment considerations** (Render/Fly.io/Railway, env vars, indexing workflow)

The plan is **constitution-compliant**, **testable**, and **ready for task generation**.
