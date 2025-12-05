# Tasks: RAG Backend & Study Assistant Chat API

**Feature**: `002-rag-backend-study-assistant`
**Input**: Design documents from `/specs/002-rag-backend-study-assistant/`
**Prerequisites**: plan.md (complete), spec.md (complete)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Backend Project Scaffold

**Purpose**: Initialize the Python backend project structure with uv and FastAPI

- [ ] T001 Create backend directory structure (backend/app/, backend/scripts/, backend/tests/)
- [ ] T002 Initialize uv project with pyproject.toml in backend/
- [ ] T003 Set .python-version to Python 3.11+ in backend/
- [ ] T004 Add FastAPI, uvicorn, pydantic, pydantic-settings to pyproject.toml dependencies
- [ ] T005 Create backend/.env.example with all required environment variables (OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, DATABASE_URL, CORS_ORIGINS, etc.)
- [ ] T006 Update .gitignore to exclude backend/.env, backend/.venv, backend/__pycache__/, etc.
- [ ] T007 [P] Create backend/README.md with setup instructions

**Checkpoint**: Basic project structure is in place, uv can install dependencies

---

## Phase 2: Configuration & Environment Handling

**Purpose**: Set up configuration management using Pydantic BaseSettings

- [ ] T008 Create backend/app/core/config.py with Settings class (all env vars from plan.md)
- [ ] T009 Implement cors_origins_list property in Settings to parse comma-separated CORS_ORIGINS
- [ ] T010 [P] Create backend/app/core/logging.py for structured logging setup
- [ ] T011 [P] Create backend/app/core/deps.py stub for dependency injection (get_db, get_qdrant_client, get_openai_client placeholders)

**Checkpoint**: Configuration module loads environment variables successfully

---

## Phase 3: Foundational Infrastructure (US5 - Health Endpoint)

**Purpose**: Core infrastructure that MUST be complete before RAG functionality

**⚠️ CRITICAL**: This phase must complete before User Stories 1, 2, 3, and 4 can begin

### User Story 5: API Health & Status Monitoring (Priority: P2)

**Goal**: Provide health check endpoint for monitoring backend and dependencies

**Independent Test**: Call GET /api/health and verify status of Qdrant and Postgres

- [ ] T012 Create backend/app/main.py with FastAPI app instance and CORS middleware
- [ ] T013 Create backend/app/api/health.py with health check router
- [ ] T014 Implement GET /api/health endpoint skeleton (returns hardcoded "ok" for now)
- [ ] T015 Add health router to main.py with /api prefix
- [ ] T016 Test that uvicorn can start the app and /api/health returns 200

**Checkpoint**: Foundation ready - FastAPI app runs, health endpoint responds

---

## Phase 4: Neon Postgres Models & Session Management (US4 Dependencies)

**Purpose**: Database layer for chat session persistence

**Note**: Required for US4, but US1 and US2 can work without this

- [ ] T017 Add sqlalchemy[asyncio], asyncpg, alembic to pyproject.toml dependencies
- [ ] T018 Create backend/app/db/session.py with async SQLAlchemy engine and session factory
- [ ] T019 Create backend/app/models/db.py with Base declarative_base
- [ ] T020 [P] Implement ChatSession model in backend/app/models/db.py (id, user_id, mode, started_at, ended_at, created_at, updated_at)
- [ ] T021 [P] Implement ChatMessage model in backend/app/models/db.py (id, session_id, role, content, selected_text, doc_path, created_at)
- [ ] T022 Implement get_db dependency in backend/app/core/deps.py (yields AsyncSession)
- [ ] T023 Add database health check to backend/app/api/health.py (test SELECT 1)
- [ ] T024 Add startup event to main.py to initialize database engine
- [ ] T025 (OPTIONAL) Setup Alembic migrations in backend/app/db/migrations/ or use Base.metadata.create_all on startup

**Checkpoint**: Database models defined, session factory works, health endpoint checks Postgres

---

## Phase 5: Qdrant Client Configuration

**Purpose**: Set up Qdrant Cloud client and collection schema

**Note**: Required for US1, US2, and US3

- [ ] T026 Add qdrant-client to pyproject.toml dependencies
- [ ] T027 Create backend/app/services/qdrant.py with QdrantClient wrapper
- [ ] T028 Implement get_qdrant_client dependency in backend/app/core/deps.py
- [ ] T029 Add Qdrant health check to backend/app/api/health.py (test get_collections)
- [ ] T030 Create backend/scripts/create_qdrant_collection.py to create "textbook_embeddings" collection (VectorParams: size=1536, distance=COSINE)
- [ ] T031 Document Qdrant collection setup in backend/README.md

**Checkpoint**: Qdrant client connects successfully, health endpoint checks Qdrant, collection can be created

---

## Phase 6: User Story 3 - Textbook Content Indexing Pipeline (Priority: P1) 🎯 MVP Prerequisite

**Goal**: Process all /docs content, chunk it, generate embeddings, and store in Qdrant Cloud

**Independent Test**: Run indexing script, verify embeddings exist in Qdrant with correct metadata

### Implementation for User Story 3

- [ ] T032 Add openai, tiktoken, python-frontmatter, click to pyproject.toml dependencies
- [ ] T033 Create backend/app/services/embeddings.py with OpenAI embeddings service (embed_text, batch_embed)
- [ ] T034 Implement get_openai_client dependency in backend/app/core/deps.py
- [ ] T035 Create backend/scripts/index_docs.py CLI script skeleton with click arguments (--docs-dir, --collection-name, --batch-size, --dry-run)
- [ ] T036 Implement file discovery logic in index_docs.py (recursively scan for .md and .mdx files)
- [ ] T037 Implement frontmatter stripping and metadata extraction (module_id from path, doc_path)
- [ ] T038 Implement hybrid chunking strategy: heading-based chunking with token-length fallback for chunks > 500 tokens
- [ ] T039 Implement heading hierarchy extraction for chunk metadata (e.g., "Chapter 1 > Section 1.1")
- [ ] T040 Implement batch embedding generation using embeddings service (up to 100 chunks per API call)
- [ ] T041 Implement Qdrant upsert logic with ID = doc_path:chunk_index, payload = {doc_path, module_id, heading, chunk_index, text}
- [ ] T042 Add error handling and retry logic for OpenAI rate limits (exponential backoff)
- [ ] T043 Add progress logging and summary output (e.g., "Indexed 45 chunks from 12 documents")
- [ ] T044 Test indexing script locally with ../docs directory

**Checkpoint**: Indexing script successfully processes docs and uploads embeddings to Qdrant Cloud

---

## Phase 7: User Story 1 - Whole-Book Q&A (Priority: P1) 🎯 MVP

**Goal**: Enable students to ask general questions and get answers from the entire textbook

**Independent Test**: POST /api/chat with mode="whole-book", verify relevant answer and citations

### Implementation for User Story 1

- [ ] T045 Create backend/app/models/schemas.py with ChatRequest, Citation, ChatResponse Pydantic models
- [ ] T046 Add request validation in ChatRequest (mode, question length, selectedText requirement)
- [ ] T047 Create backend/app/api/chat.py with chat router
- [ ] T048 Implement POST /api/chat endpoint skeleton (validates request, returns dummy response)
- [ ] T049 Add chat router to main.py with /api prefix
- [ ] T050 Create backend/app/services/rag.py with RAG pipeline functions
- [ ] T051 Implement whole-book retrieval logic in rag.py: generate question embedding, search Qdrant (top 5-10 chunks, cosine similarity)
- [ ] T052 Implement OpenAI chat completion logic with system prompt (rules to reduce hallucinations) and retrieved chunks as context
- [ ] T053 Implement citation extraction from top 3-5 chunks (docPath, heading, snippet ~50-100 words)
- [ ] T054 Integrate RAG pipeline into POST /api/chat for mode="whole-book"
- [ ] T055 Add error handling for OpenAI rate limits (429), OpenAI errors (503), Qdrant errors (503)
- [ ] T056 Add input validation for question length (max 500 words, FR-020)
- [ ] T057 Test whole-book Q&A locally with sample questions

**Checkpoint**: Whole-book Q&A works end-to-end, returns accurate answers with citations

---

## Phase 8: User Story 2 - Selection-Based Q&A (Priority: P2)

**Goal**: Enable students to select text and ask questions scoped to that selection

**Independent Test**: POST /api/chat with mode="selection", verify answer is scoped to selected text and neighbors

### Implementation for User Story 2

- [ ] T058 Implement selection-based retrieval logic in backend/app/services/qdrant.py: find_chunk_by_text (filter by doc_path, search by selectedText embedding)
- [ ] T059 Implement get_chunks_by_index_range in qdrant.py (retrieve 2-3 chunks before/after selected chunk)
- [ ] T060 Update RAG pipeline in backend/app/services/rag.py to handle mode="selection": retrieve selected chunk + neighbors
- [ ] T061 Implement fallback to whole-book mode when docPath is invalid or no chunks found (FR-019)
- [ ] T062 Add logging/warning when falling back to whole-book mode
- [ ] T063 Add input validation for selectedText length (max 500 words, FR-020)
- [ ] T064 Integrate selection-based logic into POST /api/chat
- [ ] T065 Test selection-based Q&A locally with sample selectedText and docPath

**Checkpoint**: Selection-based Q&A works, answers are focused on selected text + context

---

## Phase 9: User Story 4 - Chat Session Persistence (Priority: P3)

**Goal**: Persist chat sessions and messages in Neon Postgres for authenticated users

**Independent Test**: Send chat requests with userId, query database to verify sessions and messages

### Implementation for User Story 4

- [ ] T066 Create backend/app/services/chat_storage.py with save_chat function
- [ ] T067 Implement session creation logic: create ChatSession record with (user_id, mode, started_at, ended_at)
- [ ] T068 Implement message creation logic: create ChatMessage records for user question and assistant answer
- [ ] T069 Add check to only persist when userId is provided and non-empty (FR-021)
- [ ] T070 Integrate chat_storage.save_chat into POST /api/chat after RAG pipeline
- [ ] T071 Handle database errors gracefully (log but don't fail chat request)
- [ ] T072 Test session persistence locally with and without userId

**Checkpoint**: Chat sessions and messages are correctly persisted for authenticated users, skipped for anonymous users

---

## Phase 10: Testing & Validation

**Purpose**: Ensure all user stories work independently and together

- [ ] T073 [P] Create backend/tests/conftest.py with pytest fixtures (mocked OpenAI, Qdrant, DB)
- [ ] T074 [P] Create backend/tests/test_health.py with tests for healthy and degraded states
- [ ] T075 [P] Create backend/tests/test_chat.py with tests for whole-book and selection modes
- [ ] T076 [P] Add tests for error cases: invalid mode, missing selectedText, question too long, rate limits
- [ ] T077 [P] Create backend/tests/test_chat_storage.py with tests for session persistence (with/without userId)
- [ ] T078 Run all tests with pytest and verify 100% pass rate
- [ ] T079 Test full stack integration locally (backend on :8000, frontend on :3000)

**Checkpoint**: All tests pass, full stack integration works locally

---

## Phase 11: Deployment Preparation & Documentation

**Purpose**: Prepare backend for production deployment

- [ ] T080 Document all environment variables in backend/README.md
- [ ] T081 Add deployment instructions for Render/Fly.io/Railway in backend/README.md
- [ ] T082 Document indexing workflow (run locally, not in production) in backend/README.md
- [ ] T083 Add CORS configuration notes for production (GitHub Pages URL)
- [ ] T084 (OPTIONAL) Create Dockerfile for backend if using Fly.io or containerized deployment
- [ ] T085 Verify all secrets are loaded from environment variables, none committed to git
- [ ] T086 Test backend startup with minimal .env file to ensure all required vars are documented

**Checkpoint**: Backend is documented and ready for deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Scaffold)**: No dependencies - start immediately
- **Phase 2 (Config)**: Depends on Phase 1 completion
- **Phase 3 (Health Endpoint - US5)**: Depends on Phase 2 - BLOCKS all other user stories
- **Phase 4 (Postgres Models)**: Depends on Phase 3 - Required for US4 only
- **Phase 5 (Qdrant Client)**: Depends on Phase 3 - Required for US1, US2, US3
- **Phase 6 (Indexing - US3)**: Depends on Phase 5 - MVP PREREQUISITE (must run before testing US1/US2)
- **Phase 7 (Whole-Book - US1)**: Depends on Phase 5, Phase 6 (needs indexed content) - MVP
- **Phase 8 (Selection - US2)**: Depends on Phase 7 (builds on whole-book logic)
- **Phase 9 (Persistence - US4)**: Depends on Phase 4, can be done in parallel with Phase 7/8
- **Phase 10 (Testing)**: Depends on all implementation phases
- **Phase 11 (Deployment)**: Depends on all phases, ideally after testing

### Parallel Opportunities

**Within Phase 1**:
- T007 (README) can run in parallel with T001-T006

**Within Phase 2**:
- T010 (logging.py) can run in parallel with T008-T009
- T011 (deps.py stub) can run in parallel with T008-T010

**Within Phase 4**:
- T020 (ChatSession model) and T021 (ChatMessage model) can run in parallel

**Within Phase 10 (Testing)**:
- T073-T077 (all test file creation) can run in parallel

**Across Phases**:
- Once Phase 5 completes, Phase 6 (US3) and Phase 7 (US1) can start in parallel if indexing is done first
- Phase 9 (US4) can run in parallel with Phase 8 (US2) since they touch different files

---

## Implementation Strategy

### MVP First (US1 + US3 Only)

1. Complete Phase 1: Scaffold
2. Complete Phase 2: Config
3. Complete Phase 3: Health Endpoint (US5)
4. Complete Phase 5: Qdrant Client
5. Complete Phase 6: Indexing Pipeline (US3)
6. Complete Phase 7: Whole-Book Q&A (US1)
7. **STOP and VALIDATE**: Test US1 independently
8. Deploy/demo if ready

### Incremental Delivery

1. Scaffold + Config + Health → Foundation ready
2. Add Qdrant + Indexing (US3) → Can index content
3. Add Whole-Book Q&A (US1) → Test independently → Deploy/Demo (MVP!)
4. Add Selection Q&A (US2) → Test independently → Deploy/Demo
5. Add Persistence (US4) + Postgres Models → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Phase 1-3 together (Foundation)
2. Phase 4 and Phase 5 can be done by different developers in parallel
3. Once Phase 5 and 6 done:
   - Developer A: Phase 7 (US1 - Whole-Book)
   - Developer B: Phase 9 (US4 - Persistence)
4. Once Phase 7 done:
   - Developer A: Phase 8 (US2 - Selection)
5. All developers: Phase 10 (Testing)

---

## Critical Path to MVP

**MVP = Whole-Book Q&A Working**

Critical path (must be done sequentially):
1. T001-T007: Scaffold
2. T008-T011: Config
3. T012-T016: Health Endpoint
4. T026-T031: Qdrant Client
5. T032-T044: Indexing Pipeline (US3)
6. T045-T057: Whole-Book Q&A (US1)

**Estimated MVP tasks**: ~57 tasks on critical path

**Parallelizable after foundation**: Postgres models (Phase 4) can be skipped for MVP if US4 is deferred

---

## Notes

- [P] tasks can run in parallel (different files, no dependencies)
- [US#] label maps task to specific user story for traceability
- US3 (Indexing) is a prerequisite for US1 and US2 - must complete before testing RAG
- US4 (Persistence) can be deferred if MVP only needs whole-book Q&A
- US5 (Health) is foundational but low complexity
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Run indexing script before testing US1/US2 locally
