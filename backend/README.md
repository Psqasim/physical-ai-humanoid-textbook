# Physical AI RAG Backend

FastAPI-based backend for the Study Assistant RAG (Retrieval-Augmented Generation) system, providing intelligent Q&A capabilities for the Physical AI & Humanoid Robotics Textbook.

## Features

- **Whole-Book Q&A**: Ask questions about any topic in the textbook
- **Selection-Based Q&A**: Get focused answers for specific text selections
- **Vector Search**: Powered by Qdrant Cloud for semantic textbook search
- **Chat Persistence**: Store chat sessions and messages in Neon Postgres
- **OpenAI Integration**: GPT-4o-mini for answers, text-embedding-3-small for embeddings

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key
- Qdrant Cloud account and API key
- Neon Postgres database

## Installation

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Navigate to backend directory

```bash
cd backend
```

### 3. Install dependencies

```bash
# Install all dependencies (including dev dependencies)
uv sync

# Or install only production dependencies
uv sync --no-dev
```

This will:
- Create a virtual environment in `.venv`
- Install FastAPI, uvicorn, pydantic, and other dependencies
- Set up pytest for testing

### 4. Configure environment variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
# Required variables:
# - OPENAI_API_KEY
# - QDRANT_URL
# - QDRANT_API_KEY
# - DATABASE_URL
# - CORS_ORIGINS
```

## Development

### Run the development server

Once the API endpoints are implemented (Phase 3+), you can start the server:

```bash
# From the backend/ directory
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs (Swagger UI)
- Alternative docs: http://localhost:8000/redoc (ReDoc)

### Run tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entrypoint
│   ├── api/                 # API routes/routers
│   │   ├── __init__.py
│   │   ├── health.py        # GET /api/health
│   │   └── chat.py          # POST /api/chat
│   ├── core/                # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py        # Pydantic settings
│   │   ├── logging.py       # Logging setup
│   │   └── deps.py          # Dependency injection
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   ├── db.py            # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── rag.py           # RAG pipeline
│   │   ├── embeddings.py    # OpenAI embeddings
│   │   ├── qdrant.py        # Qdrant client wrapper
│   │   └── chat_storage.py  # Postgres persistence
│   └── db/                  # Database
│       ├── __init__.py
│       ├── session.py       # Async SQLAlchemy session
│       └── migrations/      # Alembic migrations (optional)
├── scripts/
│   ├── __init__.py
│   └── index_docs.py        # Index textbook content to Qdrant
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_health.py       # Health endpoint tests
│   └── test_chat.py         # Chat endpoint tests
├── .env.example             # Example environment variables
├── .python-version          # Python version (3.11)
├── pyproject.toml           # uv project configuration
└── README.md                # This file
```

## API Endpoints

### Health Check

```http
GET /api/health
```

Returns the status of the backend and its dependencies (Qdrant, Postgres).

### Chat

```http
POST /api/chat
Content-Type: application/json

{
  "mode": "whole-book" | "selection",
  "question": "What is ROS 2?",
  "selectedText": "optional, required if mode='selection'",
  "docPath": "optional, e.g., '/docs/module-1-ros2/chapter-1-basics'",
  "userId": "optional, for session persistence"
}
```

Returns an AI-generated answer with citations from the textbook.

## Indexing Textbook Content

Before the RAG system can answer questions, you must index the textbook content:

```bash
# Run from the project root
cd backend
uv run python scripts/index_docs.py --docs-dir ../docs

# Optional flags
uv run python scripts/index_docs.py \
  --docs-dir ../docs \
  --collection-name textbook_embeddings \
  --batch-size 50 \
  --dry-run  # Preview chunks without uploading
```

This script will:
1. Scan all Markdown/MDX files in `../docs`
2. Chunk content by headings (with fallback to token-based chunking)
3. Generate embeddings using OpenAI
4. Upload to Qdrant Cloud with metadata (doc_path, module_id, heading, chunk_index)

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model name | `text-embedding-3-small` |
| `OPENAI_CHAT_MODEL` | Chat model name | `gpt-4o-mini` |
| `QDRANT_URL` | Qdrant Cloud HTTPS URL | `https://xyz.qdrant.io` |
| `QDRANT_API_KEY` | Qdrant Cloud API key | `...` |
| `QDRANT_COLLECTION_NAME` | Collection name | `textbook_embeddings` |
| `DATABASE_URL` | Neon Postgres connection string | `postgresql+asyncpg://user:pass@host/db` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000,https://yourusername.github.io` |
| `MAX_QUESTION_TOKENS` | Max question length in tokens | `500` |
| `MAX_SELECTION_TOKENS` | Max selectedText length in tokens | `500` |
| `CHUNK_RETRIEVAL_LIMIT` | Number of chunks to retrieve | `10` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Deployment

The backend can be deployed to various platforms:

### Render (Recommended)

1. Connect your GitHub repository
2. Set environment variables in the Render dashboard
3. Set build command: `uv sync --frozen`
4. Set start command: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Fly.io

1. Create `fly.toml` configuration
2. Set secrets: `fly secrets set OPENAI_API_KEY=...`
3. Deploy: `flyctl deploy`

### Railway

1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Railway auto-detects Python and runs the app

## Development Workflow

1. **Setup** (Phase 1): Project scaffold ✅
2. **Config** (Phase 2): Environment and dependency injection
3. **Health** (Phase 3): Basic health check endpoint
4. **Database** (Phase 4): Postgres models and session management
5. **Qdrant** (Phase 5): Vector database client
6. **Indexing** (Phase 6): Index textbook content
7. **Whole-Book Q&A** (Phase 7): MVP - General questions
8. **Selection Q&A** (Phase 8): Context-aware questions
9. **Persistence** (Phase 9): Session storage
10. **Testing** (Phase 10): Pytest suite
11. **Deployment** (Phase 11): Production deployment

## Next Steps

After Phase 1 (current):
1. Implement configuration management (Phase 2)
2. Create health check endpoint (Phase 3)
3. Set up database models (Phase 4)
4. Configure Qdrant client (Phase 5)
5. Build indexing script (Phase 6)
6. Implement RAG pipeline (Phases 7-8)

## License

Part of the Physical AI & Humanoid Robotics Textbook project.

## Support

For issues or questions, refer to the main project documentation or create an issue in the repository.
