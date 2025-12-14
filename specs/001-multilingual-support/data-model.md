# Data Model: Multilingual Support

**Feature**: 001-multilingual-support
**Date**: 2025-12-11
**Phase**: 1 (Design)

## Overview

This document defines the data entities, state management, and data flows for the multilingual support feature. The data model spans three layers: frontend (localStorage), backend (API requests/responses), and RAG (Qdrant embeddings).

---

## Frontend Entities

### 1. LanguagePreference (localStorage)

**Description**: Stores the user's selected language preference in the browser.

**Storage**: `localStorage.getItem('language-preference')`

**Schema**:
```typescript
interface LanguagePreference {
  preferredLanguage: 'en' | 'ur' | 'ja';
  timestamp: string; // ISO 8601 format
  source: 'manual' | 'browser' | 'default';
}
```

**Example**:
```json
{
  "preferredLanguage": "ur",
  "timestamp": "2025-12-11T10:30:00Z",
  "source": "manual"
}
```

**Fields**:
- `preferredLanguage`: User's selected language code
- `timestamp`: When the preference was last updated
- `source`:
  - `manual`: User explicitly selected from language switcher
  - `browser`: Auto-detected from browser language settings
  - `default`: Fallback to English (no detection or selection)

**Validation Rules**:
- `preferredLanguage` MUST be one of `['en', 'ur', 'ja']`
- `timestamp` MUST be valid ISO 8601 datetime
- `source` MUST be one of `['manual', 'browser', 'default']`

**State Transitions**:
1. **Initial load**: Check localStorage → if empty, detect from browser → set `source: 'browser'`
2. **User selection**: User clicks language switcher → update `preferredLanguage` → set `source: 'manual'`
3. **Persistence**: Read from localStorage on page load → apply to UI immediately

**Access Pattern**:
```typescript
// Read
const preference = JSON.parse(localStorage.getItem('language-preference') || '{}');

// Write
localStorage.setItem('language-preference', JSON.stringify({
  preferredLanguage: 'ur',
  timestamp: new Date().toISOString(),
  source: 'manual'
}));
```

---

### 2. TranslationMetadata (per-document)

**Description**: Tracks translation status for each documentation page.

**Storage**: Embedded in markdown frontmatter or separate `translations.json`

**Schema**:
```typescript
interface TranslationMetadata {
  sourceLanguage: 'en' | 'ur' | 'ja';
  availableLanguages: Array<'en' | 'ur' | 'ja'>;
  completionPercentage: {
    [key in 'en' | 'ur' | 'ja']?: number; // 0-100
  };
  lastUpdated: {
    [key in 'en' | 'ur' | 'ja']?: string; // ISO 8601
  };
}
```

**Example** (markdown frontmatter):
```yaml
---
title: Introduction to Physical AI
translationMetadata:
  sourceLanguage: en
  availableLanguages: [en, ur, ja]
  completionPercentage:
    en: 100
    ur: 85
    ja: 100
  lastUpdated:
    en: "2025-12-10T12:00:00Z"
    ur: "2025-12-11T09:00:00Z"
    ja: "2025-12-11T10:00:00Z"
---
```

**Validation Rules**:
- `sourceLanguage` MUST be one of `['en', 'ur', 'ja']`
- `availableLanguages` MUST include `sourceLanguage`
- `completionPercentage` values MUST be 0-100
- `lastUpdated` MUST be valid ISO 8601 datetime

**Use Cases**:
1. Display translation status indicator (e.g., "85% translated" badge)
2. Prioritize translation work (show incomplete pages to translators)
3. Track translation progress over time

---

## Backend Entities

### 3. LanguageDetectionRequest (API Input)

**Description**: Request payload for `/api/detect-language` endpoint.

**Schema**:
```typescript
interface LanguageDetectionRequest {
  text: string;
}
```

**Example**:
```json
{
  "text": "یہ ایک ٹیسٹ ہے"
}
```

**Validation Rules**:
- `text` MUST be non-empty string
- `text` length MUST be ≤ 5000 characters (to prevent abuse)

---

### 4. LanguageDetectionResult (API Output)

**Description**: Response from `/api/detect-language` endpoint.

**Schema**:
```typescript
interface LanguageDetectionResult {
  detectedLanguage: 'en' | 'ur' | 'ja' | 'unknown';
  confidence: number; // 0.0 to 1.0
  fallbackApplied: boolean;
}
```

**Example**:
```json
{
  "detectedLanguage": "ur",
  "confidence": 0.9,
  "fallbackApplied": false
}
```

**Fields**:
- `detectedLanguage`: Detected language code (or `'unknown'` if unsupported)
- `confidence`: Detection confidence (0.0 = no confidence, 1.0 = certain)
- `fallbackApplied`: `true` if confidence was below threshold and fallback logic was used

**Validation Rules**:
- `detectedLanguage` MUST be one of `['en', 'ur', 'ja', 'unknown']`
- `confidence` MUST be 0.0 ≤ confidence ≤ 1.0
- `fallbackApplied` MUST be boolean

**Business Logic**:
```python
# Pseudo-code
if confidence >= 0.5 and lang in ['en', 'ur', 'ja']:
    return {"detectedLanguage": lang, "confidence": confidence, "fallbackApplied": False}
else:
    return {"detectedLanguage": ui_language or "en", "confidence": 0.0, "fallbackApplied": True}
```

---

### 5. ChatMessage (extended)

**Description**: Chat message with language metadata for RAG system.

**Schema**:
```typescript
interface ChatMessage {
  // Existing fields
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;

  // New language fields
  detectedLanguage?: 'en' | 'ur' | 'ja';
  requestedLanguage?: 'en' | 'ur' | 'ja';
  responseLanguage?: 'en' | 'ur' | 'ja';
}
```

**Example** (user message):
```json
{
  "id": "msg_123",
  "role": "user",
  "content": "ROS 2 کیا ہے؟",
  "timestamp": "2025-12-11T10:30:00Z",
  "detectedLanguage": "ur",
  "requestedLanguage": "ur"
}
```

**Example** (assistant message):
```json
{
  "id": "msg_124",
  "role": "assistant",
  "content": "ROS 2 ایک جدید روبوٹکس فریم ورک ہے...",
  "timestamp": "2025-12-11T10:30:02Z",
  "responseLanguage": "ur"
}
```

**Fields**:
- `detectedLanguage`: Language detected from user input (backend detection)
- `requestedLanguage`: Language user requested via UI setting (frontend preference)
- `responseLanguage`: Language of the assistant's response (may differ if content unavailable)

**Validation Rules**:
- All language fields MUST be one of `['en', 'ur', 'ja']` if present
- `detectedLanguage` and `requestedLanguage` only on user messages
- `responseLanguage` only on assistant messages

**Analytics Use Case**:
- Log language fields to track:
  - Detection accuracy (compare `detectedLanguage` vs `requestedLanguage`)
  - Fallback frequency (when `responseLanguage` ≠ `requestedLanguage`)
  - Language usage distribution

---

### 6. ChatRequest (extended)

**Description**: Extended `/api/chat` request with language parameter.

**Schema**:
```typescript
interface ChatRequest {
  // Existing fields
  message: string;
  sessionId?: string;
  mode?: 'whole-book' | 'selection-based';
  selectedText?: string;

  // New field
  preferredLanguage?: 'en' | 'ur' | 'ja';
}
```

**Example**:
```json
{
  "message": "What is ROS 2?",
  "sessionId": "session_abc123",
  "mode": "whole-book",
  "preferredLanguage": "ja"
}
```

**Validation Rules**:
- `preferredLanguage` is optional; defaults to `'en'` if not provided
- `preferredLanguage` MUST be one of `['en', 'ur', 'ja']` if present

---

### 7. ChatResponse (extended)

**Description**: Extended `/api/chat` response with language metadata.

**Schema**:
```typescript
interface ChatResponse {
  // Existing fields
  response: string;
  sources: Array<{
    docId: string;
    title: string;
    snippet: string;
  }>;

  // New fields
  responseLanguage: 'en' | 'ur' | 'ja';
  detectedInputLanguage: 'en' | 'ur' | 'ja';
  fallbackApplied: boolean;
}
```

**Example**:
```json
{
  "response": "ROS 2 は最新のロボティクスフレームワークです...",
  "sources": [
    {
      "docId": "intro-ros2-ja",
      "title": "ROS 2 入門",
      "snippet": "ROS 2 はリアルタイムシステムに最適化されています..."
    }
  ],
  "responseLanguage": "ja",
  "detectedInputLanguage": "ja",
  "fallbackApplied": false
}
```

**Fields**:
- `responseLanguage`: Language of the response text
- `detectedInputLanguage`: Language detected from user's input
- `fallbackApplied`: `true` if fallback to English content was used

**Validation Rules**:
- All language fields MUST be one of `['en', 'ur', 'ja']`
- `fallbackApplied` MUST be boolean

---

## RAG Entities

### 8. DocumentEmbedding (Qdrant vector)

**Description**: Vector embedding with language metadata in Qdrant payload.

**Schema**:
```typescript
interface DocumentEmbedding {
  id: string;
  vector: number[]; // 1536-dim for OpenAI embeddings
  payload: {
    text: string;
    docId: string;
    language: 'en' | 'ur' | 'ja';
    originalLanguage: 'en' | 'ur' | 'ja';
    translationSource: 'original' | 'human' | 'machine';
    contentType: 'ui' | 'docs' | 'chat_context';
    translationQuality?: number; // 0.0-1.0, only if translationSource !== 'original'
  };
}
```

**Example**:
```json
{
  "id": "embed_001",
  "vector": [0.023, -0.145, ...],
  "payload": {
    "text": "ROS 2 روبوٹکس سسٹم کے لیے ایک فریم ورک ہے",
    "docId": "intro-ros2-ur",
    "language": "ur",
    "originalLanguage": "en",
    "translationSource": "human",
    "contentType": "docs",
    "translationQuality": 0.95
  }
}
```

**Fields**:
- `text`: Chunk of text that was embedded
- `docId`: Source document ID
- `language`: Language of the text chunk
- `originalLanguage`: Language of the source document
- `translationSource`:
  - `original`: Original authored content
  - `human`: Professional human translation
  - `machine`: Machine translation (OpenAI GPT-4)
- `contentType`:
  - `ui`: UI string translation
  - `docs`: Documentation page content
  - `chat_context`: Chat conversation context
- `translationQuality`: Optional quality score (0-1) for machine/human translations

**Validation Rules**:
- `language` and `originalLanguage` MUST be one of `['en', 'ur', 'ja']`
- `translationSource` MUST be one of `['original', 'human', 'machine']`
- `contentType` MUST be one of `['ui', 'docs', 'chat_context']`
- `translationQuality` MUST be 0.0 ≤ quality ≤ 1.0 if present

**Indexing Pattern**:
```python
from qdrant_client.models import PointStruct

point = PointStruct(
    id="embed_001",
    vector=embedding_vector,
    payload={
        "text": chunk_text,
        "docId": doc_id,
        "language": "ur",
        "originalLanguage": "en",
        "translationSource": "human",
        "contentType": "docs"
    }
)
client.upsert(collection_name="textbook_chunks", points=[point])
```

**Query Pattern (with language filter)**:
```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.search(
    collection_name="textbook_chunks",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(key="language", match=MatchValue(value="ur"))
        ]
    ),
    limit=5
)
```

---

## Data Flows

### Flow 1: Language Selection (Frontend)

```
1. User loads page
   ↓
2. Read from localStorage('language-preference')
   ↓
3. If empty:
     → Detect browser language (navigator.language)
     → Map to supported language (en/ur/ja) or default to 'en'
     → Save to localStorage with source='browser'
   Else:
     → Use stored preference
   ↓
4. Apply language to Docusaurus (update URL: /ur/docs/intro)
5. Set document dir attribute: <html dir="rtl"> for Urdu
```

### Flow 2: Language Detection (Backend)

```
1. User sends chat message
   ↓
2. Frontend sends POST /api/chat with:
     - message: "ROS 2 کیا ہے؟"
     - preferredLanguage: "ur" (from localStorage)
   ↓
3. Backend:
     a. Detect language from message text (langdetect)
     b. If confidence >= 0.5 and lang in ['en','ur','ja']:
          → Use detected language
        Else:
          → Use preferredLanguage from request
     c. Query RAG with language filter
     d. Generate response in detected/requested language
   ↓
4. Return ChatResponse with:
     - response: "ROS 2 ایک جدید روبوٹکس فریم ورک ہے..."
     - responseLanguage: "ur"
     - detectedInputLanguage: "ur"
     - fallbackApplied: false
```

### Flow 3: RAG Language Filtering

```
1. User query: "What is ROS 2?" (detectedLanguage: 'en', preferredLanguage: 'ja')
   ↓
2. Backend decides final language:
     - Detection confidence: 0.9 (English detected)
     - Preferred language: Japanese
     - Resolution: Use detectedLanguage ('en') since confidence > 0.5
   ↓
3. Query Qdrant with filter: language='en'
     → Returns 5 English chunks
   ↓
4. If results < 3:
     → Query again with filter: language='en' (fallback)
     → Merge results
   ↓
5. Generate response using retrieved chunks
6. Return response in English with fallbackApplied=false
```

---

## Entity Relationships

```
┌──────────────────────┐
│ LanguagePreference   │
│ (localStorage)       │
└──────────┬───────────┘
           │ persists user choice
           ↓
┌──────────────────────┐
│ ChatRequest          │───────┐
│ (API input)          │       │ includes preferredLanguage
└──────────┬───────────┘       │
           │                   │
           │ sent to           │
           ↓                   ↓
┌──────────────────────┐   ┌──────────────────────┐
│ LanguageDetector     │   │ RAGMultilingual      │
│ (backend service)    │   │ (backend service)    │
└──────────┬───────────┘   └──────────┬───────────┘
           │                          │
           │ returns                  │ queries with filter
           ↓                          ↓
┌──────────────────────┐   ┌──────────────────────┐
│LanguageDetectionResult│   │ DocumentEmbedding    │
│ (API output)         │   │ (Qdrant vectors)     │
└──────────────────────┘   └──────────────────────┘
           │                          │
           │ used in                  │ provides context
           ↓                          ↓
┌──────────────────────────────────────┐
│ ChatResponse (API output)            │
│ - response                           │
│ - responseLanguage                   │
│ - detectedInputLanguage              │
│ - fallbackApplied                    │
└──────────────────────────────────────┘
```

---

## Storage Summary

| Entity | Storage Location | Persistence | Size Estimate |
|--------|------------------|-------------|---------------|
| LanguagePreference | Browser localStorage | Per-device, indefinite | ~100 bytes |
| TranslationMetadata | Markdown frontmatter | Git-tracked | ~200 bytes/doc |
| LanguageDetectionResult | API response (ephemeral) | Not stored | ~100 bytes |
| ChatMessage | Backend logs (optional) | 90 days retention | ~500 bytes/message |
| DocumentEmbedding | Qdrant collection | Permanent | ~6KB/vector (1536-dim) |

**Total Storage (RAG)**:
- 1,000 document chunks × 6KB = ~6MB per language
- 3 languages × 6MB = ~18MB total
- Well within Qdrant Free Tier limits (1GB)

---

## Next Steps

1. ✅ **Data model complete**: All entities documented
2. 📝 **API contracts**: Generate OpenAPI schemas in `/contracts/`
3. 🔧 **Quickstart**: Document setup and usage patterns in `quickstart.md`
4. 🔄 **Agent context**: Update with new API endpoints and entities
