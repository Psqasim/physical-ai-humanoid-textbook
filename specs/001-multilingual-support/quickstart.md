# Quickstart Guide: Multilingual Support

**Feature**: 001-multilingual-support
**Date**: 2025-12-11
**For**: Developers implementing or extending multilingual features

---

## Overview

This guide provides step-by-step instructions for setting up, testing, and extending the multilingual support feature (English, Urdu, Japanese) across the Docusaurus frontend, FastAPI backend, and Qdrant RAG pipeline.

---

## Prerequisites

**Frontend**:
- Node.js 18+ and npm
- Docusaurus 3.x already installed

**Backend**:
- Python 3.11+
- FastAPI, OpenAI SDK, langdetect, Qdrant client

**Services**:
- OpenAI API key
- Qdrant Cloud instance (or local Qdrant server)

---

## Setup

### 1. Frontend Setup (Docusaurus)

**Install dependencies:**
```bash
npm install
```

**Configure i18n in `docusaurus.config.ts`:**
```typescript
module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur', 'ja'],
    localeConfigs: {
      en: { label: 'English', direction: 'ltr', htmlLang: 'en-US' },
      ur: { label: 'اردو', direction: 'rtl', htmlLang: 'ur-PK' },
      ja: { label: '日本語', direction: 'ltr', htmlLang: 'ja-JP' },
    },
  },
  // ...
};
```

**Extract UI strings for translation:**
```bash
# Generate code.json files for Urdu and Japanese
npm run write-translations -- --locale ur
npm run write-translations -- --locale ja
```

This creates:
- `i18n/ur/code.json`
- `i18n/ja/code.json`

**Translate UI strings:**
Option 1: Manual translation
```bash
# Edit i18n/ur/code.json and i18n/ja/code.json manually
```

Option 2: Automated translation (using OpenAI script)
```bash
python scripts/translate-ui-strings.py
```

**Test language switching:**
```bash
# Start dev server in English (default)
npm start

# Start dev server in Urdu
npm run start -- --locale ur

# Start dev server in Japanese
npm run start -- --locale ja
```

**Build all locales:**
```bash
npm run build
```

---

### 2. Backend Setup (FastAPI)

**Install dependencies:**
```bash
cd backend
pip install -r requirements.txt

# Ensure langdetect is included:
pip install langdetect
```

**Configure environment variables:**
Create `.env` file in `backend/` directory:
```env
# OpenAI API
OPENAI_API_KEY=sk-...

# Qdrant
QDRANT_URL=https://your-qdrant-instance.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Language settings (optional)
DEFAULT_LANGUAGE=en
DETECTION_CONFIDENCE_THRESHOLD=0.5
```

**Run backend server:**
```bash
cd backend
uvicorn app.main:app --reload
```

Server starts at `http://localhost:8000`

---

## Testing

### Frontend Tests

**1. Language Switcher**:
- Open `http://localhost:3000`
- Click language switcher in navbar
- Select "اردو" (Urdu) or "日本語" (Japanese)
- Verify UI updates instantly without page reload
- Refresh page → language persists

**2. Browser Language Detection**:
```javascript
// Open browser dev console
localStorage.clear();
// Set browser language to Urdu (ur-PK) in browser settings
// Refresh page → UI should display in Urdu
```

**3. RTL Layout (Urdu)**:
- Switch to Urdu
- Navigate to any doc page
- Verify:
  - Text flows right-to-left
  - Chat messages align right (user) and left (assistant)
  - Navbar/sidebar remain LTR
  - Code blocks remain LTR

---

### Backend Tests

**1. Language Detection Endpoint**:
```bash
# English text
curl -X POST http://localhost:8000/api/detect-language \
  -H "Content-Type: application/json" \
  -d '{"text": "What is ROS 2?"}'

# Expected response:
# {"detectedLanguage": "en", "confidence": 0.9, "fallbackApplied": false}

# Urdu text
curl -X POST http://localhost:8000/api/detect-language \
  -H "Content-Type: application/json" \
  -d '{"text": "ROS 2 کیا ہے؟"}'

# Expected response:
# {"detectedLanguage": "ur", "confidence": 0.9, "fallbackApplied": false}

# Japanese text
curl -X POST http://localhost:8000/api/detect-language \
  -H "Content-Type: application/json" \
  -d '{"text": "ROS 2 とは何ですか？"}'

# Expected response:
# {"detectedLanguage": "ja", "confidence": 0.9, "fallbackApplied": false}
```

**2. Chat Endpoint with Language Preference**:
```bash
# English query with Japanese preference
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is ROS 2?",
    "preferredLanguage": "ja"
  }'

# Expected response includes:
# - "responseLanguage": "en" (if Japanese content unavailable)
# - "detectedInputLanguage": "en"
# - "fallbackApplied": true (if no Japanese docs)

# Urdu query
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ROS 2 کیا ہے؟",
    "preferredLanguage": "ur"
  }'

# Expected response:
# - "detectedInputLanguage": "ur"
# - "responseLanguage": "ur" (if Urdu content available)
# - "fallbackApplied": false
```

---

### RAG Tests

**1. Index Documents with Language Tags**:
```python
# backend/scripts/test_multilingual_indexing.py
from app.services.rag_multilingual import index_document

# Index English document
index_document(
    doc_text="ROS 2 is a modern robotics framework...",
    doc_id="intro-ros2-en",
    language="en"
)

# Index Urdu document
index_document(
    doc_text="ROS 2 ایک جدید روبوٹکس فریم ورک ہے...",
    doc_id="intro-ros2-ur",
    language="ur"
)

# Index Japanese document
index_document(
    doc_text="ROS 2 は最新のロボティクスフレームワークです...",
    doc_id="intro-ros2-ja",
    language="ja"
)
```

**2. Query with Language Filter**:
```python
from app.services.rag_multilingual import search_with_language_filter

# Search for English content
results_en = search_with_language_filter(
    query="What is ROS 2?",
    language="en",
    limit=5
)
print(f"Found {len(results_en)} English results")

# Search for Urdu content
results_ur = search_with_language_filter(
    query="ROS 2 کیا ہے؟",
    language="ur",
    limit=5
)
print(f"Found {len(results_ur)} Urdu results")
```

**3. Fallback Logic Test**:
```python
# Query for Urdu content when only English is available
results = search_with_language_filter(
    query="What is ROS 2?",
    language="ur",  # Request Urdu
    limit=5
)

# Should return English results as fallback
assert all(r.payload["language"] == "en" for r in results)
```

---

## Development Workflow

### Adding a New Language

**1. Update Docusaurus config:**
```typescript
// docusaurus.config.ts
i18n: {
  locales: ['en', 'ur', 'ja', 'fr'], // Add 'fr' for French
  localeConfigs: {
    fr: { label: 'Français', direction: 'ltr', htmlLang: 'fr-FR' },
  },
}
```

**2. Extract translations:**
```bash
npm run write-translations -- --locale fr
```

**3. Translate UI strings:**
```bash
python scripts/translate-ui-strings.py --target fr
```

**4. Update backend validation:**
```python
# backend/app/core/i18n.py
SUPPORTED_LANGUAGES = ['en', 'ur', 'ja', 'fr']
```

**5. Update OpenAPI schemas:**
```yaml
# contracts/detect-language.openapi.yaml
enum: [en, ur, ja, fr]
```

---

### Translating Documentation Pages

**1. Create translated markdown file:**
```bash
# English source: docs/intro.md
# Urdu translation: i18n/ur/docusaurus-plugin-content-docs/current/intro.md
mkdir -p i18n/ur/docusaurus-plugin-content-docs/current
cp docs/intro.md i18n/ur/docusaurus-plugin-content-docs/current/intro.md
```

**2. Translate content:**
Edit `i18n/ur/docusaurus-plugin-content-docs/current/intro.md` and translate all text (keep frontmatter in English).

**3. Add translation metadata:**
```yaml
---
title: Introduction to Physical AI
translationMetadata:
  sourceLanguage: en
  availableLanguages: [en, ur]
  completionPercentage:
    en: 100
    ur: 100
  lastUpdated:
    ur: "2025-12-11T10:00:00Z"
---
```

**4. Build and test:**
```bash
npm run start -- --locale ur
# Navigate to /ur/docs/intro → should show Urdu translation
```

---

## Troubleshooting

### Issue: Language switcher not visible
**Solution**: Verify `LanguageSwitcher` component is imported in navbar config:
```typescript
// docusaurus.config.ts
themeConfig: {
  navbar: {
    items: [
      {
        type: 'localeDropdown',
        position: 'right',
      },
    ],
  },
}
```

### Issue: RTL layout not working for Urdu
**Solution**: Check `[dir="rtl"]` CSS is loaded:
```typescript
// src/theme/Root.tsx
import '@site/src/theme/RTL/urdu.css';
```

### Issue: Language detection returns "unknown"
**Solution**: Verify langdetect is installed and text has sufficient length:
```python
from langdetect import detect
print(detect("Short text may fail"))  # Needs 20+ chars for accuracy
```

### Issue: Qdrant language filter returns no results
**Solution**: Verify documents are tagged with language metadata:
```python
# Check payload in Qdrant
points = client.retrieve(collection_name="textbook_chunks", ids=["doc_id"])
print(points[0].payload.get("language"))  # Should be "en", "ur", or "ja"
```

---

## Performance Optimization

**1. Minimize fallback queries:**
- Ensure sufficient content in each language
- Monitor fallback rates via analytics logs

**2. Cache language detection results:**
```python
# Cache detection for identical messages
from functools import lru_cache

@lru_cache(maxsize=1000)
def detect_language_cached(text: str):
    return detect_language(text)
```

**3. Optimize Qdrant queries:**
- Use `limit` parameter to control result count
- Add `score_threshold` to filter low-relevance results:
```python
results = client.search(
    collection_name="textbook_chunks",
    query_vector=embedding,
    query_filter=language_filter,
    limit=5,
    score_threshold=0.7  # Only return results with score >= 0.7
)
```

---

## Next Steps

1. ✅ **Setup complete**: Frontend and backend configured
2. 🧪 **Tests passing**: Language detection and RAG filtering validated
3. 📝 **Tasks generation**: Run `/sp.tasks` to generate implementation tasks
4. 🚀 **Implementation**: Run `/sp.implement` to execute tasks

---

## Resources

- [Docusaurus i18n Documentation](https://docusaurus.io/docs/i18n/tutorial)
- [langdetect GitHub](https://github.com/Mimino666/langdetect)
- [Qdrant Filtering Guide](https://qdrant.tech/documentation/concepts/filtering/)
- [OpenAPI Specification](./contracts/)
- [Data Model](./data-model.md)
- [Research Findings](./research.md)
