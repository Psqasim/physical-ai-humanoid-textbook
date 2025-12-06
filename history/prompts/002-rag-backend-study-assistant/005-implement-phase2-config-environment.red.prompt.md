---
id: 005
title: Implement Phase 2 Config and Environment
stage: red
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-rag-backend-study-assistant
branch: 001-docusaurus-frontend
user: developer
command: /sp.implement
labels: ["implementation", "configuration", "backend", "phase2", "pydantic", "logging"]
links:
  spec: specs/002-rag-backend-study-assistant/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/core/config.py
  - backend/app/core/logging.py
  - backend/app/core/deps.py
  - backend/README.md
  - backend/verify_config.py
tests:
  - backend/verify_config.py (passed)
---

## Prompt

/sp.implement

Implement ONLY the Phase 2 configuration & environment handling tasks
for the feature "002-rag-backend-study-assistant" as defined in
specs/002-rag-backend-study-assistant/tasks.md.

Constraints:
- Do NOT create any API routes or RAG logic yet.
- Do NOT make external network calls.
- Focus on core config, logging, and dependency helpers.

Goals:
- Create backend/app/core/config.py using Pydantic BaseSettings:
  - Load env vars defined in backend/.env.example:
    OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_CHAT_MODEL,
    QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME,
    DATABASE_URL, CORS_ORIGINS, MAX_QUESTION_TOKENS,
    MAX_SELECTION_TOKENS, CHUNK_RETRIEVAL_LIMIT, LOG_LEVEL.
  - Provide a Settings class and a get_settings() helper.
- Create backend/app/core/logging.py:
  - Configure a basic logger using LOG_LEVEL from settings.
- Create backend/app/core/deps.py:
  - Expose dependency functions like get_settings() for FastAPI (using
    functools.lru_cache where appropriate).
- Update backend/README.md briefly to explain how to:
  - Copy .env.example to .env
  - Set required values (with a note that real keys will be added later).

Stop after these config-related tasks are complete. Do NOT implement DB,
Qdrant, or /api/chat in this step.

At the end, summarize:
- Files created/modified.
- Any instructions to reload uv/venv if needed.

## Response snapshot

Successfully implemented all 4 tasks from Phase 2 (Configuration & Environment Handling):

**T008**: Created backend/app/core/config.py with comprehensive Settings class:
- Uses Pydantic BaseSettings for environment variable loading
- Includes all 14 environment variables from .env.example
- Required fields: OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, DATABASE_URL, CORS_ORIGINS
- Optional fields with defaults: embedding model, chat model, collection name, limits, log level
- Implements cors_origins_list property to parse comma-separated CORS origins
- Provides get_settings() function with @lru_cache for singleton pattern
- Exports pre-instantiated settings for convenience

**T009**: cors_origins_list property implemented in Settings class:
- Parses CORS_ORIGINS string into list of strings
- Strips whitespace from each origin
- Example: "http://localhost:3000,https://example.com" → ["http://localhost:3000", "https://example.com"]

**T010**: Created backend/app/core/logging.py for structured logging:
- setup_logging() function configures logger with LOG_LEVEL from settings
- Log format: timestamp, level, logger name, message
- Output to stdout (captured by hosting platforms)
- get_logger(name) helper for module-specific loggers
- log_config_on_startup() utility to log non-sensitive config on startup
- Pre-configured logger exported for convenience

**T011**: Created backend/app/core/deps.py with dependency injection helpers:
- get_settings() dependency returns cached Settings instance
- SettingsDep type alias for cleaner FastAPI dependency injection
- Placeholder dependencies for future phases:
  - get_db() - will be implemented in Phase 4 (Neon Postgres)
  - get_qdrant_client() - will be implemented in Phase 5 (Qdrant)
  - get_openai_client() - will be implemented in Phase 6 (Indexing)
- Each placeholder raises NotImplementedError with helpful message

**README.md Update**: Enhanced environment variable setup section:
- Added detailed instructions for copying .env.example to .env
- Listed all required variables with descriptions and where to get them
- Listed all optional variables with default values
- Added note about using placeholder values for initial testing

**Verification Script**: Created backend/verify_config.py:
- Tests Settings class loads correctly
- Verifies all required fields present
- Validates default values
- Tests cors_origins_list property
- Tests logger configuration
- Tests dependency injection helpers
- All tests passed ✅

## Outcome

- ✅ Impact: Complete configuration layer implemented. Settings can load from environment, logging is configured, dependency injection is ready for future phases.
- 🧪 Tests: Created and ran verify_config.py - all tests passed (exit code 0)
- 📁 Files: Created 4 files (config.py, logging.py, deps.py, verify_config.py), modified 1 file (README.md)
- 🔁 Next prompts: Run `/sp.implement` for Phase 3 (Foundational Infrastructure - US5 Health Endpoint) to create FastAPI app with CORS and health check endpoint
- 🧠 Reflection: Configuration layer is robust and well-documented. The Settings class follows Pydantic best practices with proper typing and validation. Logging provides good observability. Dependency injection stubs with NotImplementedError are clear about what's not yet implemented. The verification script gives immediate feedback that everything works. Ready for Phase 3.

## Evaluation notes (flywheel)

- Failure modes observed: Initial uv warning about deprecated tool.uv.dev-dependencies field (not critical, just a deprecation warning)
- Graders run and results (PASS/FAIL): verify_config.py - PASS (all tests passed, exit code 0)
- Prompt variant (if applicable): Standard /sp.implement workflow for Phase 2
- Next experiment (smallest change to try): Consider migrating from tool.uv.dev-dependencies to dependency-groups.dev in pyproject.toml to resolve deprecation warning
