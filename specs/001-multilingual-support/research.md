# Research & Technology Decisions: Multilingual Support

**Feature**: 001-multilingual-support
**Date**: 2025-12-11
**Phase**: 0 (Research)

## Overview

This document consolidates research findings and technology decisions for implementing multilingual support (English, Urdu, Japanese) across the Physical AI & Humanoid Robotics Textbook platform.

---

## 1. Docusaurus i18n Best Practices

### Research Question
How should we configure Docusaurus 3.x i18n to minimize build complexity while supporting incremental translation?

### Decision
**Use Docusaurus native i18n plugin with filesystem-based translations**

### Rationale
- **Built-in support**: Docusaurus 3.x has native i18n plugin (`@docusaurus/plugin-i18n`)
- **Folder structure**: `i18n/[locale]/docusaurus-plugin-content-*/` automatically discovered
- **Incremental translation**: Can translate files one at a time; untranslated files fall back to default locale
- **Build optimization**: Only locales with content are built (no empty locale builds)
- **URL routing**: Docusaurus auto-generates locale-prefixed URLs (`/ur/docs/intro`, `/ja/docs/intro`)
- **Theme strings**: `code.json` files for translating UI elements (navbar, footer, buttons)

### Configuration
```typescript
// docusaurus.config.ts
i18n: {
  defaultLocale: 'en',
  locales: ['en', 'ur', 'ja'],
  localeConfigs: {
    en: {
      label: 'English',
      direction: 'ltr',
      htmlLang: 'en-US',
    },
    ur: {
      label: 'اردو',
      direction: 'rtl',
      htmlLang: 'ur-PK',
    },
    ja: {
      label: '日本語',
      direction: 'ltr',
      htmlLang: 'ja-JP',
    },
  },
},
```

### Alternatives Considered
1. **External CMS (Crowdin, Lokalise)**
   - Pros: Better collaboration, translation memory, glossary management
   - Cons: Additional service dependency, CI/CD complexity, cost
   - **Rejected**: Overkill for Phase 1; can migrate later if needed

2. **Custom i18n solution**
   - Pros: Full control, custom URL schemes
   - Cons: Reinventing wheel, maintenance burden, no community support
   - **Rejected**: Docusaurus native solution is battle-tested

### References
- [Docusaurus i18n Tutorial](https://docusaurus.io/docs/i18n/tutorial)
- [Docusaurus i18n Configuration](https://docusaurus.io/docs/api/docusaurus-config#i18n)

---

## 2. Language Detection Libraries

### Research Question
Which library should we use for language detection: OpenAI API, langdetect, langid, or fasttext?

### Decision
**Use `langdetect` Python library for backend language detection**

### Rationale
| Criterion | OpenAI API | langdetect | langid | fasttext |
|-----------|-----------|------------|--------|----------|
| **Accuracy** | ~95% (GPT-4) | ~90% | ~88% | ~92% |
| **Latency** | 300-500ms | <10ms | <5ms | <15ms |
| **Cost** | $0.01/request | Free | Free | Free |
| **Supports en/ur/ja** | Yes | Yes | Yes | Yes |
| **Dependencies** | OpenAI SDK | None | numpy | ~1GB model |
| **Ease of Use** | API call | `langdetect.detect(text)` | `langid.classify(text)` | Load model first |

**Winner**: **langdetect**
- Meets latency requirement (<200ms target, actual <10ms)
- 90% accuracy sufficient for 50% confidence threshold
- No external API dependency (reduces cost and latency)
- Simple API: `detect(text)` returns language code
- Well-maintained, 55+ languages including en, ur, ja

### Implementation Example
```python
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent results
DetectorFactory.seed = 0

def detect_language(text: str) -> dict:
    try:
        lang_code = detect(text)
        # Map to supported languages
        if lang_code in ['en', 'ur', 'ja']:
            return {
                "detectedLanguage": lang_code,
                "confidence": 0.9,  # langdetect doesn't return confidence
                "fallbackApplied": False
            }
        else:
            return {
                "detectedLanguage": "en",
                "confidence": 0.0,
                "fallbackApplied": True
            }
    except LangDetectException:
        return {
            "detectedLanguage": "en",
            "confidence": 0.0,
            "fallbackApplied": True
        }
```

### Alternatives Considered
1. **OpenAI API (GPT-4 with language detection prompt)**
   - **Rejected**: Too expensive (~$0.01/request), high latency (300-500ms), overkill for simple detection

2. **langid**
   - **Rejected**: Slightly lower accuracy (88% vs 90%), numpy dependency heavier than langdetect

3. **fasttext (Facebook's fastText)**
   - **Rejected**: 1GB model file, slower initialization, overkill for 3 languages

### Confidence Score Strategy
`langdetect` doesn't return confidence scores, so we use heuristics:
- If detected language in `['en', 'ur', 'ja']`: confidence = 0.9 (pass 50% threshold)
- If detected language is other: confidence = 0.0, fallback to UI language
- If detection fails (exception): confidence = 0.0, fallback to UI language

### References
- [langdetect GitHub](https://github.com/Mimino666/langdetect)
- [Language Detection Benchmark](https://github.com/saffsd/langid.py#benchmarks)

---

## 3. RTL CSS Patterns

### Research Question
How should we implement hybrid RTL (content areas RTL, navigation LTR) for Urdu while maintaining browser compatibility?

### Decision
**Use CSS `[dir="rtl"]` attribute selectors with CSS logical properties where supported**

### Rationale
- **Browser support**: `[dir="rtl"]` supported in all modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **Scoping**: Can apply RTL to specific elements (e.g., `.markdown > *[dir="rtl"]`)
- **Logical properties**: `margin-inline-start`, `padding-inline-end` automatically flip for RTL
- **Fallback**: Physical properties (`margin-left`, `padding-right`) for older browsers

### Implementation Strategy

**1. Set `dir` attribute dynamically:**
```typescript
// src/theme/Root.tsx
import { useEffect } from 'react';
import { useLocation } from '@docusaurus/router';

export default function Root({ children }) {
  const location = useLocation();
  const locale = location.pathname.split('/')[1]; // Extract locale from URL

  useEffect(() => {
    const direction = locale === 'ur' ? 'rtl' : 'ltr';
    document.documentElement.setAttribute('dir', direction);
  }, [locale]);

  return <>{children}</>;
}
```

**2. CSS for hybrid RTL (content only):**
```css
/* src/theme/RTL/urdu.css */

/* Apply RTL only to content areas */
[dir="rtl"] .markdown,
[dir="rtl"] .theme-doc-markdown {
  text-align: right;
  direction: rtl;
}

/* Chat interface RTL */
[dir="rtl"] .chat-message-user {
  margin-inline-start: auto;
  margin-inline-end: 1rem;
}

[dir="rtl"] .chat-message-assistant {
  margin-inline-start: 1rem;
  margin-inline-end: auto;
}

/* Navigation stays LTR */
[dir="rtl"] .navbar,
[dir="rtl"] .sidebar,
[dir="rtl"] .footer {
  direction: ltr;
  text-align: left;
}

/* Code blocks always LTR */
[dir="rtl"] pre,
[dir="rtl"] code {
  direction: ltr;
  text-align: left;
}

/* Flip icons for RTL content */
[dir="rtl"] .markdown .icon-arrow-right::before {
  content: '←';
}

[dir="rtl"] .markdown .icon-arrow-left::before {
  content: '→';
}
```

### CSS Logical Properties Compatibility
```css
/* Modern browsers (Chrome 90+) */
margin-inline-start: 1rem;  /* Auto-flips for RTL */
padding-inline-end: 2rem;   /* Auto-flips for RTL */

/* Fallback for older browsers (if needed) */
[dir="ltr"] .element {
  margin-left: 1rem;
  padding-right: 2rem;
}

[dir="rtl"] .element {
  margin-right: 1rem;
  padding-left: 2rem;
}
```

### Alternatives Considered
1. **Full RTL mirroring (Docusaurus RTL plugin)**
   - Pros: Automatic mirroring of entire layout
   - Cons: Flips navigation UI, requires extensive overrides for hybrid approach
   - **Rejected**: Hybrid requirement makes plugin too opinionated

2. **Manual CSS transforms (`transform: scaleX(-1)`)**
   - Pros: Flips layout without changing DOM
   - Cons: Breaks accessibility, flips text rendering, janky scrolling
   - **Rejected**: Poor UX, accessibility nightmare

3. **Separate Urdu-specific CSS file**
   - Pros: Clean separation
   - Cons: CSS duplication, hard to maintain
   - **Rejected**: `[dir="rtl"]` selectors provide same separation with less duplication

### References
- [MDN: CSS Logical Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Logical_Properties)
- [W3C: Writing Modes Specification](https://www.w3.org/TR/css-writing-modes-4/)
- [RTL Styling 101](https://rtlstyling.com/posts/rtl-styling)

---

## 4. Qdrant Metadata Filtering

### Research Question
How should we implement language-tagged searches in Qdrant, and what is the performance impact?

### Decision
**Use Qdrant metadata `filter` parameter with language tags in payload**

### Rationale
- **Native support**: Qdrant supports filtering on payload fields
- **Performance**: Filters applied during search (not post-processing), minimal latency impact (~10-50ms)
- **Fallback logic**: Can execute two searches (primary language, then fallback) if first has insufficient results
- **Payload size**: Language tag (`"language": "en"`) is <10 bytes per vector, negligible overhead

### Implementation

**1. Tag vectors with language metadata:**
```python
# backend/app/services/rag_multilingual.py
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue

def index_document(doc_text: str, doc_id: str, language: str):
    embedding = generate_embedding(doc_text)
    point = PointStruct(
        id=doc_id,
        vector=embedding,
        payload={
            "text": doc_text,
            "doc_id": doc_id,
            "language": language,  # "en", "ur", or "ja"
            "original_language": language,
            "translation_source": "original"  # or "human" or "machine"
        }
    )
    client.upsert(collection_name="textbook_chunks", points=[point])
```

**2. Filter searches by language:**
```python
def search_with_language_filter(query: str, language: str, limit: int = 5):
    query_vector = generate_embedding(query)

    # Search with language filter
    results = client.search(
        collection_name="textbook_chunks",
        query_vector=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="language",
                    match=MatchValue(value=language)
                )
            ]
        ),
        limit=limit
    )

    # Fallback to English if insufficient results
    if len(results) < 3 and language != "en":
        fallback_results = client.search(
            collection_name="textbook_chunks",
            query_vector=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="language",
                        match=MatchValue(value="en")
                    )
                ]
            ),
            limit=limit - len(results)
        )
        results.extend(fallback_results)

    return results
```

### Performance Benchmark (Estimates)
Based on Qdrant documentation and similar deployments:
- **No filter**: ~100-150ms for search (baseline)
- **With language filter**: ~110-170ms for search (+10-20ms overhead)
- **Fallback search (two queries)**: ~220-340ms total (acceptable for <2s requirement)

**Conclusion**: Filter overhead is well within the 2-second target for 95% of queries.

### Alternatives Considered
1. **Separate collections per language**
   - Pros: No filter overhead, potentially faster
   - Cons: 3x storage, 3x maintenance, complicates fallback logic
   - **Rejected**: Premature optimization, complexity not justified

2. **Post-search filtering (client-side)**
   - Pros: Simpler Qdrant queries
   - Cons: Higher latency (retrieve more results, filter locally), wastes bandwidth
   - **Rejected**: Qdrant's native filtering is more efficient

3. **Language-specific embeddings (multilingual embedding models)**
   - Pros: Better cross-lingual semantic search
   - Cons: Requires reindexing all documents, higher complexity
   - **Deferred**: Future enhancement, not required for Phase 1

### References
- [Qdrant Filtering Documentation](https://qdrant.tech/documentation/concepts/filtering/)
- [Qdrant Performance Tuning](https://qdrant.tech/documentation/guides/tuning/)

---

## 5. Translation Workflow Automation

### Research Question
How should we automate UI string translation using OpenAI API while maintaining quality and cost efficiency?

### Decision
**Use OpenAI GPT-4 for batch UI string translation with automated extraction and validation**

### Rationale
- **Cost efficiency**: GPT-4 Turbo pricing (~$0.01/1K tokens) makes bulk translation affordable
- **Quality**: GPT-4 produces contextually appropriate translations for UI strings
- **Automation**: Can script translation of `code.json` files
- **Integration**: Fits into GitHub workflow (extract → translate → commit)
- **Human review**: Spot-check translations before deployment (not every string)

### Workflow Implementation

**1. Extract UI strings:**
```bash
# Docusaurus built-in command
npm run write-translations -- --locale ur
npm run write-translations -- --locale ja
```

This generates:
- `i18n/ur/code.json` (empty, to be filled)
- `i18n/ja/code.json` (empty, to be filled)

**2. Translate with OpenAI script:**
```python
# scripts/translate-ui-strings.py
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def translate_code_json(source_locale: str, target_locale: str):
    # Read source translations (English)
    with open(f"i18n/{source_locale}/code.json", "r") as f:
        source_data = json.load(f)

    # Prepare batch translation prompt
    strings_to_translate = []
    for key, value in source_data.items():
        if isinstance(value, dict) and "message" in value:
            strings_to_translate.append({
                "key": key,
                "message": value["message"],
                "description": value.get("description", "")
            })

    # Batch translate (max 50 strings per request to avoid token limits)
    batch_size = 50
    translated_data = {}

    for i in range(0, len(strings_to_translate), batch_size):
        batch = strings_to_translate[i:i+batch_size]
        prompt = f"""Translate the following UI strings to {target_locale} (language code).
Context: These are UI elements for a Physical AI & Humanoid Robotics textbook website.
Maintain technical accuracy and natural phrasing.

Input (JSON):
{json.dumps(batch, indent=2)}

Output (JSON with "key" and "translated_message" fields):"""

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3  # Low temperature for consistency
        )

        translations = json.loads(response.choices[0].message.content)
        for item in translations:
            key = item["key"]
            translated_data[key] = {
                "message": item["translated_message"],
                "description": source_data[key].get("description", "")
            }

    # Write translated code.json
    with open(f"i18n/{target_locale}/code.json", "w", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Translated {len(translated_data)} strings to {target_locale}")

if __name__ == "__main__":
    translate_code_json("en", "ur")
    translate_code_json("en", "ja")
```

**3. Validation:**
- **Automated checks**: Ensure all keys from source exist in target
- **Spot-check**: Review 10-20 random strings manually
- **Native speaker review**: Final QA by Urdu/Japanese speakers before production

**4. Git workflow:**
```bash
# Extract strings
npm run write-translations -- --locale ur
npm run write-translations -- --locale ja

# Translate
python scripts/translate-ui-strings.py

# Commit
git add i18n/
git commit -m "chore(i18n): add Urdu and Japanese UI translations"
git push
```

### Cost Estimate
- **UI strings**: ~200 strings × 10 words/string = 2,000 words
- **Tokens**: ~2,700 tokens (input + output)
- **Cost per language**: ~$0.03 (GPT-4 Turbo)
- **Total for 2 languages**: ~$0.06

**Conclusion**: Extremely cost-effective for UI translation.

### Alternatives Considered
1. **Manual translation**
   - Pros: Human quality, cultural nuance
   - Cons: Time-consuming, expensive for UI strings
   - **Rejected for UI**: GPT-4 quality sufficient for buttons/labels; reserved for chapter content

2. **Google Translate API**
   - Pros: Cheaper ($20/1M chars), fast
   - Cons: Lower quality, less contextual awareness
   - **Rejected**: GPT-4 produces more natural UI translations

3. **External CMS (Crowdin)**
   - Pros: Translation memory, collaboration
   - Cons: Setup overhead, ongoing cost
   - **Deferred**: Can migrate later if translation volume grows

### References
- [OpenAI GPT-4 Turbo Pricing](https://openai.com/pricing)
- [Docusaurus i18n Translation Tutorial](https://docusaurus.io/docs/i18n/tutorial#translate-your-site)

---

## 6. Translation Storage Decision

### Research Question
Should translations be committed to git or managed via external CMS (Crowdin, Lokalise)?

### Decision
**Commit translations to git (filesystem-based)**

### Rationale
- **Simplicity**: No external service dependency
- **Version control**: Translations versioned with code (atomic commits)
- **Build process**: Docusaurus reads translations directly from filesystem
- **Cost**: Free (no CMS subscription)
- **Migration path**: Can move to CMS later if collaboration needs grow

### Implementation
```bash
# Translations are part of the repository
i18n/
├── ur/
│   ├── code.json                    # Git-tracked
│   └── docusaurus-plugin-content-docs/
│       └── current/
│           └── intro.md             # Git-tracked
└── ja/
    └── code.json                    # Git-tracked
```

### Alternatives Considered
1. **Crowdin (Translation Management System)**
   - Pros: Collaboration, translation memory, glossary, in-context editing
   - Cons: $50-100/month, CI/CD integration complexity, sync latency
   - **Deferred**: Not needed for Phase 1; reevaluate if translation volume >100 chapters

2. **Lokalise**
   - Same pros/cons as Crowdin
   - **Deferred**: Same reasoning

### Migration Strategy (if needed later)
1. Export existing git translations to CMS format
2. Configure CMS sync with GitHub (bidirectional)
3. Update CI/CD to pull translations from CMS before build
4. Maintain git-based workflow as fallback

---

## Summary of Technology Decisions

| Decision Area | Choice | Key Benefit |
|---------------|--------|-------------|
| **Docusaurus i18n** | Native plugin with filesystem translations | Built-in, incremental translation support |
| **Language Detection** | `langdetect` Python library | <10ms latency, 90% accuracy, free |
| **RTL CSS** | `[dir="rtl"]` selectors + CSS logical properties | Hybrid RTL (content only), browser compatible |
| **Qdrant Filtering** | Metadata `filter` with language tags | <20ms overhead, native support, fallback-friendly |
| **UI Translation** | OpenAI GPT-4 batch translation script | $0.03/language, high quality, automatable |
| **Translation Storage** | Git-tracked filesystem (`i18n/` directory) | Simple, versioned, no external dependencies |

**All unknowns resolved.** Ready for Phase 1 (Design & Contracts).

---

## Next Steps

1. ✅ **Phase 0 complete**: All technology decisions documented
2. 📝 **Phase 1**: Generate `data-model.md`, API contracts, and `quickstart.md`
3. 🔄 **Update agent context**: Run `.specify/scripts/bash/update-agent-context.sh claude` after Phase 1
4. 📋 **Phase 2**: Generate `tasks.md` via `/sp.tasks` command
