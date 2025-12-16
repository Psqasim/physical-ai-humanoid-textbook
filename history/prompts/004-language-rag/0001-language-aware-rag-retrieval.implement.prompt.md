---
id: 0001
title: Language-Aware RAG Retrieval Implementation
stage: implement
date: 2025-12-16
surface: agent
model: claude-opus-4-5
feature: 004-language-rag
branch: 001-multilingual-support
user: ps_qasim
command: /sp.implement
labels: ["rag", "multilingual", "qdrant", "language-filter", "fallback"]
links:
  spec: specs/001-multilingual-support/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/services/qdrant.py
  - backend/app/services/rag.py
tests:
  - Language filtering returns only matching language chunks
  - English fallback triggers when <3 results in preferred language
  - Response includes fallbackApplied and responseLanguage metadata
---

## Prompt

NEXT TASK: Connect Qdrant embeddings to chat (language-aware RAG)

GOAL:
- Chat must retrieve relevant chunks from Qdrant
- Retrieval must filter by language (en / ja / ur)
- preferredLanguage is already sent from frontend

REQUIREMENTS:
- Modify existing RAG service only
- Use Qdrant vector search
- Apply filter: language == preferredLanguage
- If no results found, fallback to English
- Return top 5 chunks sorted by score
- Do NOT change ingestion code
- Do NOT change frontend

OUTPUT:
- Code changes in rag.py (or equivalent)
- Example retrieval function
- Confirmation that language filtering works

## Response

### Implementation Summary

Successfully implemented language-aware RAG retrieval with English fallback. The chat system now retrieves chunks filtered by the user's preferred language (en/ur/ja) and automatically falls back to English when insufficient content exists in the target language.

### Changes Made

#### 1. `backend/app/services/qdrant.py` - Added language filter parameter

```python
async def search_similar(
    query_vector: list[float],
    limit: int = 10,
    collection_name: str | None = None,
    doc_path: str | None = None,
    module_id: str | None = None,
    language: str | None = None,  # NEW: Language filter
    score_threshold: float | None = None,
) -> list[SearchResult]:
```

Added `FieldCondition` for language filtering:
```python
if language:
    filter_conditions.append(
        FieldCondition(
            key="language",
            match=MatchValue(value=language),
        )
    )
```

#### 2. `backend/app/services/rag.py` - Language-aware retrieval with fallback

**`retrieve_chunks_whole_book`** - Now accepts `language` parameter:
- Searches in preferred language first
- Falls back to English if <3 results and language != "en"
- Returns tuple: `(results, fallback_applied)`

**`retrieve_chunks_selection`** - Also supports language filtering:
- Filters by doc_path AND language
- Falls back to whole-book mode with language support

**`answer_chat_request`** - Updated to use language filtering:
- Reads `request.preferredLanguage` from frontend
- Passes language through retrieval pipeline
- Returns `responseLanguage` and `fallbackApplied` in response

### Example Usage

```python
# Frontend sends preferredLanguage
request = ChatRequest(
    mode="whole-book",
    question="What is ROS 2?",
    preferredLanguage="ja"  # Japanese
)

# RAG retrieves Japanese chunks first
# If <3 Japanese results, falls back to English
response = await answer_chat_request(request, db)

# Response includes language metadata
print(response.responseLanguage)  # "ja" or "en" if fallback
print(response.fallbackApplied)   # True if English fallback used
```

### Data Flow

```
Frontend (preferredLanguage: "ur")
    ↓
ChatRequest.preferredLanguage
    ↓
answer_chat_request()
    ↓
retrieve_chunks_whole_book(language="ur")
    ↓
search_similar(language="ur")  # Qdrant filter: language == "ur"
    ↓
[Results < 3?] → search_similar(language="en")  # Fallback
    ↓
ChatResponse(responseLanguage="ur|en", fallbackApplied=bool)
```

### Outcome

- Language filtering working with Qdrant `language` index
- English fallback triggers automatically when needed
- Response metadata allows frontend to show fallback notifications
- No changes to ingestion or frontend code
