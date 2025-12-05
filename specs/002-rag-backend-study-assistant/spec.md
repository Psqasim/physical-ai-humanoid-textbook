# Feature Specification: RAG Backend & Study Assistant Chat API

**Feature Branch**: `002-rag-backend-study-assistant`
**Created**: 2025-12-05
**Status**: Draft
**Input**: User description: "Create a feature specification for the RAG backend + chat API for the Physical AI & Humanoid Robotics Textbook project."

## User Scenarios & Testing

### User Story 1 - Whole-Book Q&A (Priority: P1)

As a student reading the Physical AI textbook, I want to ask general questions about any topic in the book (e.g., "How do I set up a ROS 2 workspace?", "What's the difference between Gazebo and Unity for robotics?") and receive accurate, context-aware answers so that I can learn without leaving the textbook interface.

**Why this priority**: This is the foundational RAG capability. Without whole-book Q&A, the Study Assistant has no value. This delivers immediate value by enabling students to query the entire textbook corpus.

**Independent Test**: Can be fully tested by deploying the backend with indexed textbook content, calling POST /api/chat with mode="whole-book" and a sample question, and verifying that the response includes a relevant answer and citations from the textbook.

**Acceptance Scenarios**:

1. **Given** the textbook has been indexed and the backend is running, **When** a user sends a POST request to /api/chat with `{"mode": "whole-book", "question": "What is ROS 2?"}`, **Then** the system returns a JSON response with `{"answer": "...", "citations": [...], "mode": "whole-book"}` within 7 seconds
2. **Given** the user asks a question about content across multiple modules, **When** the question is "Compare Gazebo and Unity for robot simulation", **Then** the system retrieves chunks from both Module 2 (Gazebo) and Module 2 (Unity) sections and synthesizes an answer
3. **Given** the user asks a question about content not in the textbook, **When** the question is "How do I program an Arduino?", **Then** the system responds with a message indicating the topic is not covered in the textbook

---

### User Story 2 - Selection-Based Q&A (Priority: P2)

As a student reading a specific section or paragraph, I want to select text (e.g., a code snippet or technical definition) and ask clarifying questions specifically about that selection (e.g., "Explain this line", "What does this parameter do?") so that I can understand dense or complex content in context without the answer being polluted by irrelevant textbook sections.

**Why this priority**: This is the key differentiator for the Study Assistant. Selection-based Q&A provides focused, context-aware help for specific paragraphs, code snippets, or technical definitions. It's P2 because whole-book Q&A must work first, but selection-based Q&A significantly enhances the learning experience.

**Independent Test**: Can be fully tested by sending a POST request to /api/chat with `{"mode": "selection", "question": "Explain this code", "selectedText": "rclpy.init()", "docPath": "/docs/module-1-ros2/chapter-1-basics"}` and verifying that the response is scoped to the selected text and nearby content, not the entire textbook.

**Acceptance Scenarios**:

1. **Given** the user has selected a code snippet on the page, **When** the user sends a request with `{"mode": "selection", "selectedText": "rclpy.spin(node)", "docPath": "/docs/module-1-ros2/chapter-1-basics", "question": "What does this do?"}`, **Then** the system retrieves the chunk containing the selected text plus 2-3 neighboring chunks (before/after) and returns a focused answer about `rclpy.spin()`
2. **Given** the user selects a paragraph of text, **When** the selection includes a technical term like "DDS", **Then** the system retrieves context from the selected text, the containing section, and related chunks, and answers specifically about DDS in the context of the selection
3. **Given** the user selects text but does not provide a question, **When** the request includes `{"mode": "selection", "selectedText": "...", "question": ""}`, **Then** the system generates a default question like "Explain this selection" and returns a summary or explanation of the selected content

---

### User Story 3 - Textbook Content Indexing & Embedding Pipeline (Priority: P1)

As a developer maintaining the textbook, I want to run a script that processes all Markdown/MDX content under /docs, chunks it intelligently (by section/heading or token length), generates embeddings using OpenAI, and stores them in Qdrant Cloud with metadata (doc path, module ID, heading, chunk index) so that the RAG system can retrieve relevant content for user queries.

**Why this priority**: Without indexed content, the RAG system cannot function. This is a prerequisite for both whole-book and selection-based Q&A. It's P1 because it's the foundation of the entire feature.

**Independent Test**: Can be fully tested by running `python backend/scripts/index_docs.py` (or similar CLI), verifying that embeddings are created in Qdrant Cloud, and querying Qdrant to confirm metadata (doc_path, module_id, heading, chunk_index) is correctly stored for a sample document.

**Acceptance Scenarios**:

1. **Given** the textbook has 4 modules with at least 1 chapter each, **When** the indexing script runs, **Then** all Markdown/MDX files under /docs are processed, chunked, embedded, and stored in Qdrant Cloud with correct metadata
2. **Given** a doc file contains frontmatter (e.g., YAML metadata), **When** the indexing script processes it, **Then** the frontmatter is stripped and not included in the embedding, but the module_id and doc_path are extracted and stored as metadata
3. **Given** a doc file has multiple headings (##, ###), **When** the indexing script chunks the content, **Then** each chunk includes the heading hierarchy (e.g., "Chapter 1: Basics > Section 1.1: Installation") so that citations can show the heading structure
4. **Given** the textbook content changes (a new chapter is added or an existing one is updated), **When** the indexing script is re-run, **Then** the script updates or replaces the affected embeddings in Qdrant Cloud without duplicating unchanged content

---

### User Story 4 - Chat Session Persistence (Priority: P3)

As a student using the Study Assistant, I want my chat sessions and messages to be persisted in a database so that I can return later and review my previous questions and answers, and (in the future) have continuity across sessions.

**Why this priority**: This is P3 because it's not required for the MVP (users can still ask questions and get answers without persistence). However, it's valuable for future features like chat history, personalization, and analytics.

**Independent Test**: Can be fully tested by sending multiple chat requests with a userId parameter, then querying the Neon Postgres database to confirm that chat_sessions and chat_messages tables contain the expected records.

**Acceptance Scenarios**:

1. **Given** a user (identified by userId) asks a question, **When** the backend processes the request, **Then** a new chat_session record is created in Neon Postgres with (user_id, started_at, mode)
2. **Given** a chat_session exists, **When** the user sends a follow-up question in the same session, **Then** a new chat_messages record is created with (session_id, role="user", content="...", created_at)
3. **Given** the backend responds to a user question, **When** the response is generated, **Then** a new chat_messages record is created with (session_id, role="assistant", content="...", created_at)
4. **Given** the user sends a selection-based question, **When** the message is persisted, **Then** the chat_messages record includes selected_text and doc_path fields

---

### User Story 5 - API Health & Status Monitoring (Priority: P2)

As a frontend developer or DevOps engineer, I want to call a simple health check endpoint (GET /api/health) that returns the status of the backend, Qdrant Cloud, and Neon Postgres so that I can monitor the system and detect failures before users encounter errors.

**Why this priority**: This is P2 because it's essential for production deployment and monitoring, but not required for the core RAG functionality to work. It enables reliable operations and debugging.

**Independent Test**: Can be fully tested by calling GET /api/health and verifying that the response includes status indicators for the backend, Qdrant Cloud, and Neon Postgres.

**Acceptance Scenarios**:

1. **Given** the backend is running and all dependencies are healthy, **When** a request is sent to GET /api/health, **Then** the response is `{"status": "ok", "services": {"qdrant": "ok", "postgres": "ok"}}`
2. **Given** the backend cannot connect to Qdrant Cloud, **When** a request is sent to GET /api/health, **Then** the response is `{"status": "degraded", "services": {"qdrant": "error", "postgres": "ok"}}` with a 503 status code
3. **Given** the backend cannot connect to Neon Postgres, **When** a request is sent to GET /api/health, **Then** the response is `{"status": "degraded", "services": {"qdrant": "ok", "postgres": "error"}}` with a 503 status code

---

### Edge Cases

- **What happens when Qdrant Cloud returns no relevant chunks for a query?** The system should respond with a polite message like "I couldn't find relevant content in the textbook for your question. Can you rephrase or ask about a specific module?"
- **What happens when OpenAI API rate limits are hit?** The backend should return a 429 status code with a clear error message: "The chatbot is temporarily overloaded. Please try again in a moment."
- **What happens when a user sends an extremely long question (> 1000 tokens)?** The backend should truncate or reject the question with a 400 error: "Your question is too long. Please keep it under 500 words."
- **What happens when selectedText is very long (e.g., user selects an entire page)?** The backend should either truncate the selection or return an error: "Your selection is too large. Please select a smaller section (max 500 words)."
- **What happens when docPath is invalid or doesn't exist in the embeddings?** The backend should fall back to whole-book mode with a warning: "The specified document was not found. Searching the entire textbook instead."
- **What happens when the frontend sends a request with mode="selection" but no selectedText?** The backend should return a 400 error: "mode='selection' requires selectedText to be provided."
- **What happens when the indexing script is run while the backend is serving requests?** The system should gracefully handle Qdrant updates (no crashes or partial results). Ideally, indexing should be atomic or use versioned collections.

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept POST requests to /api/chat with a JSON body containing `{"mode": "whole-book" | "selection", "question": string, "selectedText"?: string, "docPath"?: string, "userId"?: string | null}`
- **FR-002**: System MUST validate that `mode` is either "whole-book" or "selection", and return a 400 error if invalid
- **FR-003**: System MUST validate that when `mode="selection"`, `selectedText` is provided and non-empty, and return a 400 error otherwise
- **FR-004**: System MUST retrieve the top 5-10 most relevant textbook chunks from Qdrant Cloud based on the user's question and mode, using cosine similarity ranking
- **FR-005**: System MUST restrict retrieval to the chunk(s) containing the selected text plus 2-3 neighboring chunks (before/after) in the same document when `mode="selection"`
- **FR-006**: System MUST call OpenAI (via Agents/ChatKit SDK) with the user's question and retrieved chunks to generate an answer
- **FR-007**: System MUST return a JSON response with `{"answer": string, "citations": [{docPath: string, heading: string, snippet: string}], "mode": string}` within 7 seconds (P95 latency target)
- **FR-008**: System MUST include 3-5 citations (doc path + heading + snippet) in the response when relevant content is found, corresponding to the most relevant chunks used for context
- **FR-009**: System MUST persist chat sessions in Neon Postgres with (id, user_id, started_at, mode) ONLY when userId is provided (non-null and non-empty)
- **FR-010**: System MUST persist chat messages in Neon Postgres with (id, session_id, role, content, created_at, selected_text, doc_path) ONLY for sessions with a userId
- **FR-011**: System MUST provide a GET /api/health endpoint that returns `{"status": string, "services": {}}` with status codes (200 for healthy, 503 for degraded)
- **FR-012**: System MUST load API keys (OpenAI, Qdrant Cloud, Neon Postgres) from environment variables and NEVER commit them to git
- **FR-013**: System MUST implement CORS headers that allow only the Docusaurus origin (e.g., GitHub Pages URL or localhost for dev)
- **FR-014**: System MUST handle OpenAI API errors gracefully and return clear error messages to the frontend (e.g., rate limits, invalid API key)
- **FR-015**: System MUST provide a CLI script (e.g., `python backend/scripts/index_docs.py`) to index textbook content
- **FR-016**: Indexing script MUST process all Markdown/MDX files under /docs, strip frontmatter, and chunk content by heading or token length (target: 200-500 tokens per chunk)
- **FR-017**: Indexing script MUST generate embeddings using OpenAI (e.g., text-embedding-3-small or text-embedding-ada-002) and store them in Qdrant Cloud
- **FR-018**: Indexing script MUST store metadata for each chunk: `{"doc_path": string, "module_id": int, "heading": string, "chunk_index": int}`
- **FR-019**: System MUST handle missing or empty docPath gracefully by falling back to whole-book mode
- **FR-020**: System MUST truncate or reject questions and selectedText that exceed reasonable length limits (e.g., 500 words)
- **FR-021**: System MUST NOT persist chat sessions or messages when userId is null, missing, or an empty string (anonymous users are not tracked)

### Key Entities

- **ChatSession**: Represents a conversation between a user and the Study Assistant. Attributes: id (UUID), user_id (string, nullable for now), started_at (timestamp), mode ("whole-book" | "selection"), ended_at (timestamp, nullable).
- **ChatMessage**: Represents a single message in a chat session. Attributes: id (UUID), session_id (UUID, foreign key to ChatSession), role ("user" | "assistant"), content (text), created_at (timestamp), selected_text (text, nullable), doc_path (string, nullable).
- **EmbeddingChunk**: Represents a chunk of textbook content stored in Qdrant Cloud. Metadata: doc_path (string, e.g., "/docs/module-1-ros2/chapter-1-basics"), module_id (int, 1-4), heading (string, e.g., "Chapter 1: Basics"), chunk_index (int), embedding (vector, generated by OpenAI).
- **User**: Placeholder entity for future auth integration. Attributes: id (UUID), external_id (string, from Better-Auth), created_at (timestamp). Not fully implemented in this feature; userId in chat sessions is just a string for now.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A developer can run the indexing script and successfully index the entire textbook (all modules) in Qdrant Cloud within 5 minutes
- **SC-002**: Users can ask whole-book questions (mode="whole-book") and receive accurate, relevant answers with at least 1 citation within 7 seconds (P95 latency)
- **SC-003**: Users can ask selection-based questions (mode="selection") and receive answers that are scoped to the selected text and nearby content, not the entire textbook
- **SC-004**: The backend handles 10 concurrent chat requests without errors or response time degradation (basic concurrency test)
- **SC-005**: The GET /api/health endpoint correctly detects and reports the status of Qdrant Cloud and Neon Postgres
- **SC-006**: Chat sessions and messages are persisted in Neon Postgres for all requests that include a userId parameter
- **SC-007**: The frontend can call POST /api/chat with both whole-book and selection-based queries and receive valid JSON responses that match the documented schema
- **SC-008**: The backend returns clear, user-friendly error messages for common failure cases (invalid mode, missing selectedText, OpenAI rate limit, no relevant content found)

## Non-Functional Requirements (NFRs)

### Performance

- **NFR-001**: P95 latency for POST /api/chat must be < 7 seconds (including OpenAI API call and Qdrant retrieval)
- **NFR-002**: Indexing script must process and embed the entire textbook (4 modules, ~10-20 Markdown files) in < 5 minutes
- **NFR-003**: Backend must handle at least 10 concurrent chat requests without errors or response time degradation

### Reliability

- **NFR-004**: Backend must return a valid HTTP status code and error message for all failure cases (no unhandled exceptions or crashes)
- **NFR-005**: Backend must gracefully handle Qdrant Cloud or Neon Postgres downtime (return 503 with clear error message, not crash)
- **NFR-006**: Indexing script must be idempotent (running it multiple times should not create duplicate embeddings or corrupt the Qdrant collection)

### Security

- **NFR-007**: API keys (OpenAI, Qdrant Cloud, Neon Postgres) MUST be loaded from environment variables and NEVER committed to git
- **NFR-008**: Backend MUST implement CORS headers that allow only the Docusaurus origin (e.g., GitHub Pages URL or localhost for dev)
- **NFR-009**: Backend MUST validate all user inputs (mode, question, selectedText, docPath) and reject invalid requests with 400 errors
- **NFR-010**: Backend MUST sanitize user inputs before passing them to OpenAI (prevent prompt injection or abuse)

### Deployment

- **NFR-011**: Backend must be deployable to a simple hosting service (Railway, Fly.io, Render, or similar) with a single FastAPI entrypoint (backend/main.py)
- **NFR-012**: Backend must include a README or docs/setup.md that documents required environment variables and deployment steps
- **NFR-013**: Indexing script must be runnable from the command line with clear instructions and error messages

### Cost

- **NFR-014**: RAG system should use free tiers where possible (Qdrant Cloud Free Tier, Neon Postgres Free Tier) to minimize costs
- **NFR-015**: OpenAI API usage should be minimized by caching embeddings and limiting the number of chunks retrieved per query to 5-10 chunks (as specified in FR-004)

## API Design

### Core Endpoints

#### GET /api/health

**Description**: Health check endpoint for monitoring backend status and dependencies.

**Request**: None (GET request)

**Response**:

```json
{
  "status": "ok" | "degraded",
  "services": {
    "qdrant": "ok" | "error",
    "postgres": "ok" | "error"
  }
}
```

**Status Codes**:
- 200: All services healthy
- 503: One or more services degraded or unavailable

---

#### POST /api/chat

**Description**: Main chat endpoint for whole-book and selection-based Q&A.

**Request Body**:

```json
{
  "mode": "whole-book" | "selection",
  "question": "string (required, max 500 words)",
  "selectedText": "string (optional, required if mode='selection', max 500 words)",
  "docPath": "string (optional, e.g., '/docs/module-1-ros2/chapter-1-basics')",
  "userId": "string | null (optional, for future auth integration)"
}
```

**Response**:

```json
{
  "answer": "string (the AI-generated answer)",
  "citations": [
    {
      "docPath": "string (e.g., '/docs/module-1-ros2/chapter-1-basics')",
      "heading": "string (e.g., 'Chapter 1: Basics > Section 1.1: Installation')",
      "snippet": "string (short excerpt from the chunk, ~50-100 words)"
    }
  ],
  "mode": "whole-book" | "selection"
}
```

**Error Responses**:

- **400 Bad Request**:
  ```json
  {"error": "Invalid mode. Must be 'whole-book' or 'selection'."}
  ```
  or
  ```json
  {"error": "mode='selection' requires selectedText to be provided."}
  ```
  or
  ```json
  {"error": "Question is too long. Please keep it under 500 words."}
  ```

- **429 Too Many Requests**:
  ```json
  {"error": "The chatbot is temporarily overloaded. Please try again in a moment."}
  ```

- **500 Internal Server Error**:
  ```json
  {"error": "An unexpected error occurred. Please try again later."}
  ```

- **503 Service Unavailable**:
  ```json
  {"error": "The chatbot service is temporarily unavailable. Please try again later."}
  ```

**Status Codes**:
- 200: Success
- 400: Invalid request (bad parameters)
- 429: Rate limit exceeded
- 500: Internal server error
- 503: Service unavailable (Qdrant or OpenAI error)

---

### Future Enhancement: Streaming Responses (Out of Scope for MVP)

The spec allows for future enhancement to support streaming responses (e.g., Server-Sent Events or WebSocket) for a more interactive chat experience. This is NOT required for the MVP but should be considered in the /sp.plan phase.

---

## Data Storage (Neon Postgres)

### Purpose

Neon Postgres is used for:
1. Persisting chat sessions and messages for each user
2. Linking sessions to a userId (string) even if real auth is not yet implemented
3. (Optional) Storing basic analytics (e.g., which docs are asked about most, common queries)

### High-Level Schema

#### Table: `users`

**Purpose**: Store user records for future auth integration. For now, this table is mostly a placeholder.

**Columns**:
- `id` (UUID, primary key): Unique user identifier
- `external_id` (string, unique): External auth ID (from Better-Auth or similar, nullable for now)
- `created_at` (timestamp): When the user record was created

---

#### Table: `chat_sessions`

**Purpose**: Store metadata about each chat session.

**Columns**:
- `id` (UUID, primary key): Unique session identifier
- `user_id` (string, nullable): User identifier (string for now, foreign key to users.id in the future)
- `started_at` (timestamp): When the session started
- `ended_at` (timestamp, nullable): When the session ended (if applicable)
- `mode` (enum: "whole-book" | "selection"): The mode used for this session
- `created_at` (timestamp): Record creation timestamp

---

#### Table: `chat_messages`

**Purpose**: Store individual messages in each chat session.

**Columns**:
- `id` (UUID, primary key): Unique message identifier
- `session_id` (UUID, foreign key to chat_sessions.id): The session this message belongs to
- `role` (enum: "user" | "assistant"): Who sent the message
- `content` (text): The message content (user question or assistant answer)
- `selected_text` (text, nullable): The selected text (if mode="selection")
- `doc_path` (string, nullable): The doc path (if provided)
- `created_at` (timestamp): When the message was created

---

### Why This Schema?

- **users**: Placeholder for future auth. For now, userId in chat_sessions is just a string, but this table allows easy migration to real auth later.
- **chat_sessions**: Groups messages together and tracks the mode (whole-book vs selection). This enables chat history and analytics (e.g., "how many users use selection-based Q&A?").
- **chat_messages**: Stores the conversation history. The selected_text and doc_path fields are nullable because they're only used for selection-based Q&A.

---

## Embedding & Indexing Pipeline

### Goal

Process all textbook content (Markdown/MDX files under /docs), chunk it intelligently, generate embeddings, and store them in Qdrant Cloud with metadata so that the RAG system can retrieve relevant content for user queries.

### Process

1. **Content Collection**:
   - Recursively scan /docs for all .md and .mdx files
   - Read each file and extract raw Markdown content

2. **Preprocessing**:
   - Strip YAML frontmatter (e.g., `---\ntitle: ...\n---`)
   - Preserve headings (##, ###) and their hierarchy
   - Extract metadata from frontmatter or file path: module_id (1-4), doc_path (e.g., "/docs/module-1-ros2/chapter-1-basics")

3. **Chunking Strategy**:
   - **Option 1 (Preferred)**: Chunk by heading (each section under a ## or ### becomes one chunk)
     - Pros: Semantic coherence, citations can reference specific sections
     - Cons: Some chunks may be too long or too short
   - **Option 2**: Fixed token length (e.g., 200-500 tokens per chunk) with overlap
     - Pros: Consistent chunk sizes, better for embeddings
     - Cons: May split sentences or paragraphs awkwardly
   - **Recommendation**: Use Option 1 (heading-based) with a fallback: if a heading-based chunk exceeds 500 tokens, split it further with Option 2.

4. **Embedding Generation**:
   - Use OpenAI's text-embedding-3-small or text-embedding-ada-002 model
   - Generate one embedding vector per chunk
   - Each vector should be 1536 dimensions (for ada-002) or 1536/768/256 (for text-embedding-3-small, depending on configuration)

5. **Metadata Storage**:
   - For each chunk, store in Qdrant Cloud:
     - `doc_path` (string): e.g., "/docs/module-1-ros2/chapter-1-basics"
     - `module_id` (int): 1-4 (extracted from doc_path or frontmatter)
     - `heading` (string): e.g., "Chapter 1: Basics > Section 1.1: Installation"
     - `chunk_index` (int): Position of this chunk in the document (0, 1, 2, ...)
     - `text` (string): The raw text of the chunk (for citations)

6. **Qdrant Collection Setup**:
   - Create a Qdrant collection named "textbook_embeddings" (or similar)
   - Use cosine similarity for vector search
   - Configure payload schema to include doc_path, module_id, heading, chunk_index, text

7. **CLI Script**:
   - Provide a Python script `backend/scripts/index_docs.py` that:
     - Accepts command-line arguments (e.g., `--docs-dir /path/to/docs`, `--collection-name textbook_embeddings`)
     - Processes all docs, generates embeddings, and uploads to Qdrant
     - Prints progress and summary (e.g., "Indexed 45 chunks from 12 documents")
     - Handles errors gracefully (e.g., OpenAI rate limits, Qdrant connection issues)

8. **Idempotency**:
   - Script should be idempotent: running it multiple times should update existing embeddings, not duplicate them
   - Recommendation: Use doc_path + chunk_index as a unique ID in Qdrant

---

## Integration with Existing Frontend

### Current Frontend Components

The Docusaurus frontend has three key components for the Study Assistant:

1. **AskTheTextbookButton** (src/components/chat/AskTheTextbookButton.tsx):
   - Floating button that opens the chat panel
   - Triggers whole-book Q&A mode by default

2. **ChatPanelPlaceholder** (src/components/chat/ChatPanelPlaceholder.tsx):
   - Modal/panel that displays the chat UI
   - Supports mode switching between whole-book and selection-based Q&A
   - Shows selected text context when mode="selection"
   - Currently shows a "Backend Not Connected" placeholder

3. **TextSelectionTooltip** (src/components/chat/TextSelectionTooltip.tsx):
   - Small tooltip that appears when user selects text
   - Has a button "Ask about this" that opens the chat panel in selection mode

### Expected Integration (No Frontend Changes in This Spec)

The frontend components are already designed to:
- Call POST /api/chat with the correct request body (mode, question, selectedText, docPath)
- Display the answer text in the ChatPanelPlaceholder
- Show citations as a list of doc titles and headings (future enhancement)

**What the backend must provide**:
- A clear API contract (documented above) that matches the frontend's expectations
- JSON responses with `{"answer": string, "citations": [...], "mode": string}`
- CORS headers that allow the Docusaurus origin

**What the backend does NOT need to worry about**:
- How the frontend renders the chat UI (that's already implemented)
- How the frontend detects text selection (that's already implemented)
- How the frontend switches modes (that's already implemented)

---

## Out of Scope for This Feature

The following are explicitly OUT OF SCOPE for this feature and will be handled in separate specs:

- **User authentication and authorization**: No Better-Auth integration in this feature. userId is just a string for now.
- **Personalization logic**: No adaptive learning or difficulty tiers in this feature. The RAG system answers questions based on the textbook content only, without personalization.
- **Urdu translation**: No language translation in this feature. All questions and answers are in English.
- **Chat history UI**: The backend persists chat sessions and messages, but the frontend does NOT display chat history yet. That's a future enhancement.
- **Streaming responses**: The backend returns a single JSON response, not a stream. Streaming is a future enhancement.
- **Advanced analytics**: The backend stores basic data (sessions, messages), but does NOT implement analytics dashboards or reports. That's a future enhancement.
- **Rate limiting and abuse prevention**: Basic error handling is required, but advanced rate limiting (e.g., per-user limits, IP-based throttling) is out of scope.
- **Multi-turn conversations**: The backend handles single-shot Q&A only. Context from previous messages in the same session is NOT used in this feature. That's a future enhancement.

---

## Clarifications (Resolved 2025-12-05)

### 1. Retrieval Count (Whole-Book Mode)
**Decision**: Retrieve **top 5-10 chunks** from Qdrant for whole-book Q&A.

**Rationale**: Balanced approach that provides good coverage for most questions while keeping costs and latency reasonable. This is sufficient context for the OpenAI chat model to generate accurate answers without overwhelming it with too much information.

**Impact on Requirements**:
- NFR-015 updated to specify: "limit the number of chunks retrieved per query to 5-10"
- FR-004 clarified: "retrieve top 5-10 most relevant chunks based on cosine similarity"

---

### 2. Answer Quality and Relevance Threshold
**Decision**: **Always answer using top chunks, regardless of similarity score**. No minimum similarity threshold.

**Rationale**: Users always get a response, even for off-topic questions. This provides a better user experience than rejecting queries. The system should trust the OpenAI model to handle marginally relevant context gracefully and say "I don't have information about that in the textbook" if the chunks are truly irrelevant.

**Impact on Requirements**:
- Edge case updated: When Qdrant returns no relevant chunks OR chunks have very low similarity, the system still attempts to answer but the OpenAI model may respond with "This topic is not covered in the textbook."
- No FR changes needed; existing FR-004 and edge cases already cover this behavior.

---

### 3. Selection-Based Retrieval Scope
**Decision**: Retrieve **selected chunk + 2-3 neighboring chunks** (before and after in the same document).

**Rationale**: Balanced context that includes surrounding paragraphs for better understanding without including too much irrelevant information. This is ideal for questions like "Explain this code" or "What does this parameter do?" where immediate context is critical.

**Impact on Requirements**:
- FR-005 updated to specify: "restrict retrieval to the chunk(s) containing the selected text plus 2-3 neighboring chunks (before/after) in the same document"
- User Story 2 acceptance scenario clarified: system retrieves selected chunk + 2-3 neighbors

---

### 4. Citation Count
**Decision**: Return **3-5 citations** in the API response, matching the most relevant chunks used for context.

**Rationale**: Shows primary sources without overwhelming the user. This is a good balance for the frontend to display citations in a compact, readable format. Citations should be the top 3-5 chunks by relevance score, not necessarily all chunks retrieved.

**Impact on Requirements**:
- FR-008 updated to specify: "include 3-5 citations (doc path + heading + snippet) in the response when relevant content is found, corresponding to the most relevant chunks"
- API response schema clarified to show 3-5 citation objects in examples

---

### 5. Data Storage Policy for Anonymous Users
**Decision**: **Do NOT store chat sessions or messages for anonymous users** (userId is null or missing). Only store data when userId is provided.

**Rationale**: Privacy-focused approach. Anonymous users can still use the chatbot, but their queries are not tracked. This reduces privacy concerns and database storage costs. Authenticated users (when auth is implemented later) will have 90-day retention for chat history and personalization features.

**Impact on Requirements**:
- FR-009 updated to specify: "persist chat sessions in Neon Postgres ONLY when userId is provided (non-null and non-empty)"
- FR-010 updated to specify: "persist chat messages in Neon Postgres ONLY for sessions with a userId"
- New FR-021 added: "System MUST NOT persist chat sessions or messages when userId is null, missing, or an empty string (anonymous users)"
- Data retention policy: 90 days for authenticated users (to be enforced later when auth is implemented)

---

## Open Questions (Remaining for /sp.plan)

The following technical decisions are deferred to the /sp.plan phase:

1. **Chunking strategy**: Should we use heading-based chunking, fixed token length, or a hybrid approach? (Architectural decision for implementation)
2. **OpenAI model selection**: Which OpenAI model should we use for embeddings (text-embedding-3-small vs text-embedding-ada-002)? Which model for chat (gpt-4o-mini vs gpt-3.5-turbo)? (Technical implementation detail)
3. **Qdrant collection configuration**: What vector size should we use? What similarity metric (cosine vs dot product)? (Technical implementation detail)
4. **Deployment target**: Where should the backend be deployed (Railway, Fly.io, Render, AWS Lambda, other)? (Infrastructure decision for /sp.plan)
5. **Indexing workflow**: Should the indexing script be run manually by a developer, or should it be automated (e.g., via GitHub Actions when docs are updated)? (DevOps workflow decision)

---

## Appendix: Example API Calls

### Example 1: Whole-Book Q&A

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "whole-book",
    "question": "What is ROS 2?"
  }'
```

**Response**:
```json
{
  "answer": "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robotic platforms.",
  "citations": [
    {
      "docPath": "/docs/module-1-ros2/chapter-1-basics",
      "heading": "Chapter 1: Basics > What is ROS 2?",
      "snippet": "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software..."
    },
    {
      "docPath": "/docs/module-1-ros2/chapter-1-basics",
      "heading": "Chapter 1: Basics > ROS 2 Architecture",
      "snippet": "ROS 2 uses a Data Distribution Service (DDS) for communication between nodes..."
    },
    {
      "docPath": "/docs/module-1-ros2/chapter-2-getting-started",
      "heading": "Chapter 2: Getting Started > Installation",
      "snippet": "ROS 2 supports multiple platforms including Ubuntu, Windows, and macOS..."
    }
  ],
  "mode": "whole-book"
}
```

---

### Example 2: Selection-Based Q&A

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "selection",
    "question": "What does this line do?",
    "selectedText": "rclpy.spin(node)",
    "docPath": "/docs/module-1-ros2/chapter-1-basics"
  }'
```

**Response**:
```json
{
  "answer": "rclpy.spin(node) is a blocking call that keeps your ROS 2 node alive and processing callbacks. It continuously checks for incoming messages, timer callbacks, and service requests until the node is shut down.",
  "citations": [
    {
      "docPath": "/docs/module-1-ros2/chapter-1-basics",
      "heading": "Chapter 1: Basics > Running a Node",
      "snippet": "The spin function keeps the node running and processes callbacks..."
    }
  ],
  "mode": "selection"
}
```

---

### Example 3: Error Handling (Invalid Mode)

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "invalid-mode",
    "question": "What is ROS 2?"
  }'
```

**Response**:
```json
{
  "error": "Invalid mode. Must be 'whole-book' or 'selection'."
}
```

**Status Code**: 400 Bad Request

---

## Summary

This specification defines the WHAT and WHY for the RAG backend and Study Assistant chat API. It includes:

1. **5 prioritized, independently testable user stories** covering whole-book Q&A, selection-based Q&A, indexing pipeline, chat persistence, and health monitoring
2. **20 functional requirements** and **15 non-functional requirements** (security, performance, reliability, deployment, cost)
3. **Detailed API design** for POST /api/chat and GET /api/health, including request/response schemas and error handling
4. **High-level data schema** for Neon Postgres (users, chat_sessions, chat_messages)
5. **Embedding & indexing pipeline** description (content collection, chunking, embedding generation, metadata storage)
6. **Integration points** with existing Docusaurus frontend components (no frontend changes required in this spec)
7. **Clear scope boundaries** (what's in scope, what's out of scope)
8. **Open questions** to be resolved in /sp.clarify before moving to /sp.plan

This spec is ready for the /sp.clarify step to resolve ambiguities and open questions, followed by /sp.plan to design the technical architecture and make implementation decisions.
