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
nano .env  # or use your preferred editor
```

**Required environment variables** (set these in `.env`):

- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- `QDRANT_URL` - Your Qdrant Cloud cluster URL (e.g., `https://xyz.qdrant.io`)
- `QDRANT_API_KEY` - Get from Qdrant Cloud dashboard
- `DATABASE_URL` - Neon Postgres connection string (format: `postgresql+asyncpg://user:password@host/database`)
- `CORS_ORIGINS` - Comma-separated allowed origins (e.g., `http://localhost:3000,https://yourusername.github.io`)

**Optional variables** (have defaults):
- `OPENAI_EMBEDDING_MODEL` - Default: `text-embedding-3-small`
- `OPENAI_CHAT_MODEL` - Default: `gpt-4o-mini`
- `QDRANT_COLLECTION_NAME` - Default: `textbook_embeddings`
- `MAX_QUESTION_TOKENS` - Default: `500`
- `MAX_SELECTION_TOKENS` - Default: `500`
- `CHUNK_RETRIEVAL_LIMIT` - Default: `10`
- `LOG_LEVEL` - Default: `INFO` (options: DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Note**: Real API keys and credentials will be added when you're ready to test the RAG functionality. For now, you can use placeholder values to verify the configuration loads correctly.

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

Before the RAG system can answer questions, you must index the textbook content using the `index_docs.py` script.

### Prerequisites

Ensure you have configured the following environment variables in `.env`:
- `OPENAI_API_KEY` - Required for generating embeddings
- `QDRANT_URL` - Required for storing embeddings
- `QDRANT_API_KEY` - Required for Qdrant authentication

### Usage

**Important**: The indexing script is safe to import (no network calls on import). All OpenAI and Qdrant API calls only happen when the script is executed.

#### Dry Run (Recommended First)

Preview how the content will be chunked without making any API calls:

```bash
cd backend
uv run python -m scripts.index_docs --dry-run
```

This will:
- Scan all Markdown/MDX files in `../docs` (relative to backend/)
- Parse frontmatter and extract metadata
- Chunk content by headings
- Print a summary (number of files, chunks generated)
- **NOT** call OpenAI or Qdrant APIs

#### Test with Limited Files

Index only the first N documents (useful for testing):

```bash
uv run python -m scripts.index_docs --dry-run --limit 5
```

#### Full Indexing

Once you've verified the dry run output and configured your API keys:

```bash
# Index the entire docs corpus
uv run python -m scripts.index_docs
```

This will:
1. Scan all Markdown/MDX files in `../docs`
2. Strip YAML frontmatter and extract metadata:
   - `doc_path` (e.g., `/docs/module-1-ros2/chapter-1-basics`)
   - `module_id` (1-4, extracted from folder names)
3. Chunk content using a hybrid strategy:
   - Primary: Split by headings (## and ###)
   - Fallback: Split large chunks (>500 tokens) by paragraphs
4. Extract heading hierarchy for each chunk (e.g., "Chapter 1 > Section 1.1")
5. Generate embeddings using OpenAI's `text-embedding-3-small`
6. Store in Qdrant Cloud with metadata:
   - `id`: `doc_path:chunk_index` (e.g., `/docs/intro:0`)
   - `vector`: 1536-dimension embedding
   - `payload`: `{doc_path, module_id, heading, chunk_index, text}`

### Script Options

```bash
# Get help
uv run python -m scripts.index_docs --help

# Custom docs directory
uv run python -m scripts.index_docs --docs-dir /path/to/docs

# Adjust batch size for OpenAI API calls
uv run python -m scripts.index_docs --batch-size 50

# Limit number of files (for testing)
uv run python -m scripts.index_docs --limit 10

# Dry run (no API calls)
uv run python -m scripts.index_docs --dry-run
```

### Expected Output

```
============================================================
Textbook Content Indexing Script
============================================================
Docs directory: /path/to/docs
Found 15 Markdown files
LIVE MODE: Will call OpenAI and Qdrant APIs
Ensuring Qdrant collection exists...
✓ Qdrant collection already exists
[1/15] Processing: intro.md
  → Generated 4 chunks with embeddings
[2/15] Processing: module-1-ros2/chapter-1.md
  → Generated 12 chunks with embeddings
...
============================================================
Uploading 156 chunks to Qdrant...
✓ Successfully uploaded all chunks
============================================================
Indexing Summary
============================================================
Files processed: 15
Total chunks: 156
Average chunks per file: 10.4
✓ Indexing complete!
============================================================
```

### Troubleshooting

**Error: "OPENAI_API_KEY is not configured"**
- Ensure you have set `OPENAI_API_KEY` in your `.env` file
- Verify the `.env` file is in the `backend/` directory

**Error: "QDRANT_URL is not configured"**
- Set `QDRANT_URL` and `QDRANT_API_KEY` in your `.env` file
- Ensure the URL includes `https://` (e.g., `https://xyz.qdrant.io`)

**Error: "Docs directory not found"**
- The script expects `../docs` relative to `backend/`
- Use `--docs-dir` to specify a custom path

**Rate Limit Errors**
- The script uses batch embedding (100 texts per API call)
- OpenAI has rate limits; if you hit them, wait a few minutes and retry
- Consider using `--limit` to index a subset first

### Re-indexing

The script is **idempotent** - running it multiple times is safe:
- Chunks use `doc_path:chunk_index` as unique IDs
- Qdrant will update existing chunks instead of duplicating
- Use this to refresh content after updating docs

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
