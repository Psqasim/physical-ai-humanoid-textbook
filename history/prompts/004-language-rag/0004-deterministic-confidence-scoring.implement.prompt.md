---
id: 0004
title: Deterministic Confidence Scoring for RAG
stage: implement
date: 2025-12-16
surface: agent
model: claude-opus-4-5
feature: 004-language-rag
branch: 001-multilingual-support
user: ps_qasim
command: /sp.implement
labels: ["rag", "confidence", "deterministic", "retrieval-signals"]
links:
  spec: specs/001-multilingual-support/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/models/schemas.py
  - backend/app/services/rag.py
tests:
  - Confidence is high when ≥5 chunks and no fallback
  - Confidence is medium when 3-4 chunks and no fallback
  - Confidence is low when fallback applied or <3 chunks
  - Same inputs always produce same confidence (deterministic)
---

## Prompt

NEXT TASK: Add deterministic confidence scoring to RAG responses

GOAL:
- Include confidence level in chat response
- Confidence must be deterministic (no LLM involvement)

RULES:
- Use retrieval signals only:
  - number of chunks
  - fallbackApplied flag
- Confidence values: high | medium | low
- Do NOT modify ingestion
- Do NOT modify frontend
- Add confidence field to response payload

LOGIC:
- ≥5 chunks & no fallback → high
- 3–4 chunks & no fallback → medium
- fallbackApplied = true → low
- <3 chunks total → low

OUTPUT:
- Updated rag.py logic
- Example response with confidence
- Confirmation confidence is deterministic

## Response

### Implementation Summary

Added deterministic confidence scoring based purely on retrieval signals (chunk count and fallback status). No LLM involvement ensures reproducible, predictable confidence levels.

### Changes Made

#### 1. `backend/app/models/schemas.py` - Added confidence field

```python
class ChatResponse(BaseModel):
    # ... existing fields ...
    confidence: Literal["high", "medium", "low"] | None = Field(
        None,
        description="Deterministic confidence level based on retrieval quality (high: ≥5 chunks no fallback, medium: 3-4 chunks no fallback, low: <3 chunks or fallback applied)",
    )
```

#### 2. `backend/app/services/rag.py` - Added calculate_confidence()

```python
ConfidenceLevel = Literal["high", "medium", "low"]

def calculate_confidence(
    num_chunks: int,
    fallback_applied: bool,
) -> ConfidenceLevel:
    """
    Calculate deterministic confidence level based on retrieval signals.
    Uses ONLY retrieval metrics (no LLM involvement).

    Logic:
    - high: ≥5 chunks AND no fallback
    - medium: 3-4 chunks AND no fallback
    - low: <3 chunks OR fallback applied
    """
    if fallback_applied:
        return "low"

    if num_chunks >= 5:
        return "high"
    elif num_chunks >= 3:
        return "medium"
    else:
        return "low"
```

#### 3. Updated `answer_chat_request()`

```python
# Calculate deterministic confidence based on retrieval signals only
confidence = calculate_confidence(
    num_chunks=len(chunks),
    fallback_applied=fallback_applied,
)

response = ChatResponse(
    answer=answer_with_sources,
    citations=citations,
    mode=request.mode,
    confidence=confidence,  # NEW
    responseLanguage=response_language,
    fallbackApplied=fallback_applied,
)
```

### Example Response with Confidence

**High Confidence (5+ chunks, no fallback):**
```json
{
  "answer": "ROS 2 is a flexible robotics framework...\n\n📚 Sources:\n1. Introduction...",
  "citations": [...],
  "mode": "whole-book",
  "confidence": "high",
  "responseLanguage": "en",
  "fallbackApplied": false
}
```

**Medium Confidence (3-4 chunks, no fallback):**
```json
{
  "answer": "The communication patterns in ROS 2...\n\n📚 Sources:\n1. ...",
  "citations": [...],
  "mode": "selection",
  "confidence": "medium",
  "responseLanguage": "ja",
  "fallbackApplied": false
}
```

**Low Confidence (fallback applied):**
```json
{
  "answer": "یہ موضوع کتاب میں تفصیل سے نہیں ملا...\n\n📚 ماخذ:\n1. ...",
  "citations": [...],
  "mode": "whole-book",
  "confidence": "low",
  "responseLanguage": "ur",
  "fallbackApplied": true
}
```

### Confidence Logic Table

| Chunks | Fallback | Confidence | Reason |
|--------|----------|------------|--------|
| 5+     | false    | high       | Plenty of relevant content in preferred language |
| 3-4    | false    | medium     | Some relevant content in preferred language |
| 1-2    | false    | low        | Limited relevant content |
| 0      | false    | low        | No relevant content found |
| any    | true     | low        | Content not in preferred language |

### Why Confidence is Deterministic

| Aspect | Implementation |
|--------|---------------|
| **Inputs** | `len(chunks)` and `fallback_applied` only |
| **LLM involvement** | None |
| **Reproducibility** | Same retrieval → same confidence (always) |
| **Algorithm** | Simple threshold-based logic |
| **No randomness** | No temperature, sampling, or probabilistic elements |

### Data Flow

```
RAG Retrieval
    ↓
chunks = [SearchResult, ...]  →  len(chunks) = 5
fallback_applied = False
    ↓
calculate_confidence(5, False)
    ↓
"high"
    ↓
ChatResponse(confidence="high", ...)
```

### Outcome

- Confidence is 100% deterministic and reproducible
- Based purely on retrieval signals (chunk count + fallback)
- No LLM involvement in confidence calculation
- Added to ChatResponse schema for frontend consumption
- No changes to ingestion or frontend required
