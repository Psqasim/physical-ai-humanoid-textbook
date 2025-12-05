---
id: 001
title: Create RAG Backend Specification
stage: spec
date: 2025-12-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-rag-backend-study-assistant
branch: 001-docusaurus-frontend
user: user
command: /sp.specify
labels: ["rag", "backend", "fastapi", "qdrant", "openai", "specification"]
links:
  spec: /specs/002-rag-backend-study-assistant/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-rag-backend-study-assistant/spec.md
tests:
  - None (specification phase)
---

## Prompt

/sp.specify

Create a feature specification for the RAG backend + chat API for the
"Physical AI & Humanoid Robotics Textbook" project.

Feature name suggestion: "002-rag-backend-study-assistant".

Scope:
- Backend and API *only* for the Study Assistant (RAG chatbot).
- Implemented with FastAPI (Python) in a separate backend/ directory.
- Uses OpenAI Agents / ChatKit SDKs, Qdrant Cloud (Free Tier), and Neon
  serverless Postgres.
- Integrates with the existing Docusaurus frontend components:
  - AskTheTextbookButton
  - ChatPanelPlaceholder
  - TextSelectionTooltip
- Auth, personalization logic, and Urdu translation are OUT OF SCOPE for
  this feature; they will be handled in separate specs.

High-level goals (WHAT/WHY):
1) Whole-book Q&A mode
- When a user asks a question from the homepage, /chat page, or floating
  chat button without selection, the backend should:
  - Use embeddings of the entire textbook content (Docusaurus docs) stored in
    Qdrant Cloud.
  - Retrieve relevant chunks and call OpenAI (via Agents/ChatKit) to answer.
- API should clearly expose a "mode": "whole-book".

2) Selection-based Q&A mode
- When the user selects text and clicks "Ask about this", the frontend sends:
  - The selectedText,
  - The current doc path and (optionally) heading/section info,
  - The user's question (if any).
- Backend should:
  - Restrict retrieval to the region(s) around the selection (e.g. same doc
    + neighboring chunks), instead of the whole corpus.
  - Clearly tag responses as "selection-based" so UI can show the mode.
- API should expose a "mode": "selection" and accept selectedText as a field.

3) Embedding & indexing pipeline
- Define how textbook content (Markdown/MDX under /docs) is:
  - Collected and preprocessed (strip frontmatter, preserve headings, module
    IDs, etc.).
  - Chunked (e.g. by section/heading or fixed token length).
  - Embedded using OpenAI models and stored in Qdrant Cloud with metadata:
    - doc_path (e.g. /docs/module-1-ros2/chapter-1-basics)
    - module_id (1–4)
    - heading/section
    - chunk index
- Provide a CLI or script (e.g. backend/scripts/index_docs.py) that can be
  run manually to (re)index the book.

4) Chat API design
- Core endpoints (examples):
  - GET /api/health → returns simple status for frontend.
  - POST /api/chat → body includes:
    - mode: "whole-book" | "selection"
    - question: string
    - selectedText?: string
    - docPath?: string
    - userId?: string | null (to be used later once auth exists)
  - Optional: GET /api/docs/preview or similar if helpful.
- Responses should include:
  - answer: string
  - citations: list of docPath + heading + short snippet (for frontend to show
    "sources" later)
  - mode: "whole-book" | "selection"
- For now, a simple "single-shot" response is enough (no streaming), but
  spec should allow streaming as a future enhancement.

5) Data storage (Neon Postgres)
- Use Neon Postgres for:
  - Persisting chat sessions and messages
  - Linking sessions to a userId (string) even if real auth is not yet wired
  - Optional: storing basic analytics (which docs are asked about most, etc.)
- Define high-level tables, e.g.:
  - users (id, external_id string from future auth)
  - chat_sessions (id, user_id, started_at, mode, etc.)
  - chat_messages (id, session_id, role, content, created_at, selected_text, doc_path)
- The spec should describe WHAT data is stored and WHY, not exact SQL.

6) Integration with existing frontend
- Assume frontend will call:
  - POST /api/chat with mode + question + optional selectedText + docPath.
- ChatPanelPlaceholder will:
  - Show loading states and current mode.
  - Display the answer text and, optionally, a list of citations (doc titles,
    headings).
- No actual frontend code changes are in this spec, but the API contract
  must be clear enough for the frontend to consume later.

7) Non-functional requirements
- Security:
  - API keys (OpenAI, Qdrant, Neon) must be loaded from environment variables
    and never committed.
  - CORS should allow only the Docusaurus origin (e.g. GitHub Pages URL).
- Reliability:
  - Basic error handling and clear error responses to the frontend.
- Performance:
  - Reasonable response times for a small textbook (e.g. < 5–7s including
    LLM call).
- Deployment:
  - Backend should be deployable to a simple service (railway/fly.io/render
    or similar; exact provider can be decided later in /sp.plan).
  - Single FastAPI app entrypoint (e.g. backend/main.py).

Success criteria:
- Clear, testable functional requirements for:
  - Whole-book Q&A,
  - Selection-based Q&A,
  - Indexing pipeline,
  - Chat API endpoints,
  - Minimal data persistence in Neon.
- No tech-stack HOW details beyond what's requested here (that will come
  in /sp.plan).
- Spec is compatible with the existing Docusaurus frontend structure and
  chat UI.

Keep this spec focused on WHAT and WHY for the RAG backend. We will create a
separate /sp.plan and /sp.tasks for this feature afterwards.

## Response snapshot

Created comprehensive feature specification for 002-rag-backend-study-assistant with:

**5 Prioritized User Stories**:
1. P1: Whole-Book Q&A - Foundation RAG capability for querying entire textbook
2. P2: Selection-Based Q&A - Key differentiator for context-focused help
3. P1: Textbook Content Indexing Pipeline - Prerequisites for RAG functionality
4. P3: Chat Session Persistence - Future-proofing for chat history features
5. P2: API Health & Status Monitoring - Essential for production operations

**20 Functional Requirements (FR-001 to FR-020)**:
- API endpoint definitions (POST /api/chat, GET /api/health)
- Request/response validation and error handling
- Qdrant retrieval and OpenAI integration requirements
- Indexing pipeline requirements
- Data persistence requirements for Neon Postgres

**15 Non-Functional Requirements**:
- Performance: < 7s P95 latency, 10 concurrent requests, < 5min indexing
- Reliability: Error handling, graceful degradation, idempotent operations
- Security: Environment variables, CORS, input validation, sanitization
- Deployment: Simple hosting service, single entrypoint, documented setup
- Cost: Free tier usage, embedding caching, limited chunk retrieval

**Detailed API Design**:
- GET /api/health with service status monitoring
- POST /api/chat with comprehensive request/response schemas
- Error responses for 400/429/500/503 status codes
- Example API calls for whole-book and selection-based queries

**Data Schema (Neon Postgres)**:
- users table (placeholder for future auth)
- chat_sessions table (session metadata, mode tracking)
- chat_messages table (conversation history with selection context)

**Embedding & Indexing Pipeline**:
- Content collection and preprocessing steps
- Chunking strategy options (heading-based vs fixed token length)
- Embedding generation with OpenAI models
- Metadata storage in Qdrant Cloud
- CLI script design for manual indexing

**Clear Scope Boundaries**:
- Out of scope: auth, personalization, Urdu translation, chat history UI, streaming, analytics, rate limiting, multi-turn conversations

**7 Open Questions** identified for /sp.clarify phase:
- Chunking strategy selection
- OpenAI model selection (embeddings and chat)
- Qdrant collection configuration
- Deployment target selection
- Indexing workflow automation
- Citation relevance threshold
- Selection-based retrieval strategy

Specification document created at: specs/002-rag-backend-study-assistant/spec.md

## Outcome

- ✅ Impact: Comprehensive RAG backend specification created with 5 prioritized user stories, 20 functional requirements, 15 NFRs, detailed API design, data schema, and indexing pipeline definition. Ready for /sp.clarify and /sp.plan phases.
- 🧪 Tests: None (specification phase)
- 📁 Files: Created specs/002-rag-backend-study-assistant/spec.md (comprehensive 600+ line specification)
- 🔁 Next prompts: /sp.clarify to resolve 7 open questions, then /sp.plan for technical architecture, then /sp.tasks for implementation breakdown
- 🧠 Reflection: Spec successfully maintains separation between WHAT/WHY (requirements) and HOW (implementation). Tech stack choices were specified in user prompt, not added autonomously. Integration points with existing frontend components clearly defined with API contract. All user stories are independently testable with clear acceptance criteria.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation - PASS (spec includes clear user stories, testable requirements, success criteria, NFRs, API design, data schema, and scope boundaries)
- Prompt variant (if applicable): Standard /sp.specify workflow
- Next experiment (smallest change to try): Proceed with /sp.clarify to resolve open questions before planning phase
