# Implementation Plan: Multilingual Support (EN / UR / JA)

**Branch**: `001-multilingual-support` | **Date**: 2025-12-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multilingual-support/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add comprehensive multilingual support (English, Urdu, Japanese) across the Physical AI & Humanoid Robotics Textbook platform. The implementation spans three layers: (1) Docusaurus i18n for frontend UI strings and content, (2) FastAPI backend language detection and language-aware chat endpoints, and (3) Qdrant RAG pipeline with language-tagged embeddings and filtered retrieval. The technical approach uses Docusaurus native i18n features, OpenAI API for language detection, and Qdrant metadata filtering with 50% confidence threshold for balanced detection accuracy.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x / React 18 (Docusaurus)
- Backend: Python 3.11+ (FastAPI)

**Primary Dependencies**:
- Frontend: Docusaurus 3.x, @docusaurus/plugin-content-docs, @docusaurus/plugin-i18n
- Backend: FastAPI, OpenAI Python SDK, langdetect or langid for language detection
- RAG: Qdrant client, existing embedding pipeline

**Storage**:
- Language preference: Browser localStorage (no backend storage)
- Translations: Filesystem (`i18n/[locale]/` directories)
- Document language tags: Qdrant vector payload metadata
- Analytics: Backend logs (language codes, timestamps, session IDs only)

**Testing**:
- Frontend: Manual QA for UI string coverage, RTL rendering validation
- Backend: pytest for `/api/detect-language` and updated `/api/chat` endpoint
- RAG: Integration tests for language-filtered searches with fallback logic
- E2E: Browser language detection, localStorage persistence, language switching

**Target Platform**:
- Frontend: Static site (GitHub Pages), Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Backend: Linux server (existing FastAPI deployment)
- Mobile: Responsive web (320px minimum width)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Language switch UI update: <300ms
- Language detection API: <200ms for messages <500 characters
- RAG with language filter: <2 seconds for 95% of queries
- Chat response latency impact: <100ms additional overhead from language detection

**Constraints**:
- RTL layout: Hybrid approach (content areas + chat RTL, navigation LTR)
- Translation strategy: OpenAI GPT-4 for UI strings, professional translators for chapters
- Detection threshold: 50% confidence (balanced approach)
- No new third-party services beyond OpenAI for language detection
- Qdrant metadata must stay within existing payload limits
- Supported browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

**Scale/Scope**:
- Three languages (en, ur, ja) at launch
- 95%+ UI string translation coverage
- 5-10 chapters translated in Phase 4
- Incremental translation: 5 chapters/language/month post-launch

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Assignment.md as Single Source of Truth
**Status**: PASS
**Justification**: Multilingual support is explicitly required in the assignment ("Urdu translation capability visible in UI"). Implementation aligns with assignment scope: Docusaurus frontend, RAG backend, no invented hardware requirements.

### ✅ II. Structure-Before-Content
**Status**: PASS
**Justification**: This plan focuses on i18n structure setup (folder hierarchy, code.json format, API contracts). Content translation (chapters) deferred to Phase 4 with explicit review workflow. UI structure approved before generating translations.

### ✅ III. Spec-Driven Development
**Status**: PASS
**Justification**: Following SDD workflow: `/sp.specify` completed with clarifications resolved → now `/sp.plan` → next `/sp.tasks` → then `/sp.implement`. Spec separates WHAT/WHY, plan covers HOW.

### ✅ IV. Adaptive Learning Without Hiding Safety
**Status**: N/A
**Justification**: Multilingual feature does not affect personalization logic. Safety content remains visible in all languages (translation requirement, not hiding).

### ✅ V. RAG Chatbot: Whole-Book and Selection-Based Q&A
**Status**: PASS
**Justification**: Language-aware RAG extends existing RAG modes (whole-book, selection-based) with language filtering. No changes to Q&A mode logic. Language tag in Qdrant payload enables filtered retrieval.

### ✅ VI. Code Quality, Examples, and UI/UX Standards
**Status**: PASS
**Justification**:
- TypeScript for Docusaurus components (LanguageSwitcher)
- Python for FastAPI endpoints (language detection, chat)
- Clean UI: language switcher in navbar, unobtrusive translation indicators
- Accessibility: RTL support for Urdu, keyboard navigation for switcher
- No janky popups; embedded language selection

### ✅ VII. Separation of Concerns and Small, Testable Changes
**Status**: PASS
**Justification**:
- Frontend i18n changes isolated to Docusaurus config and components
- Backend endpoints are new/extended (no unrelated changes)
- RAG pipeline changes limited to Qdrant metadata and filtering logic
- Each phase (UI, backend, RAG, content) independently testable
- Small commits per component (config, switcher, detection endpoint, etc.)

**Overall**: **NO VIOLATIONS** - All constitution principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-multilingual-support/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan output)
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - entities and state
├── quickstart.md        # Phase 1 output - developer setup guide
├── contracts/           # Phase 1 output - API schemas
│   ├── detect-language.openapi.yaml
│   └── chat-extended.openapi.yaml
├── checklists/
│   └── requirements.md  # Quality validation (completed)
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Frontend (Docusaurus)
i18n/
├── ur/
│   ├── docusaurus-plugin-content-docs/
│   │   └── current/
│   │       └── [translated .md files - Phase 4]
│   ├── docusaurus-plugin-content-pages/
│   │   └── [translated page files - Phase 4]
│   └── code.json                    # UI string translations - Phase 1
└── ja/
    ├── docusaurus-plugin-content-docs/
    ├── docusaurus-plugin-content-pages/
    └── code.json                    # UI string translations - Phase 1

src/
├── components/
│   └── LanguageSwitcher/            # New component - Phase 1
│       ├── index.tsx
│       ├── styles.module.css
│       └── __tests__/
│           └── LanguageSwitcher.test.tsx
├── theme/
│   └── RTL/                         # RTL stylesheet - Phase 1
│       └── urdu.css
├── css/
│   └── custom.css                   # Extended with RTL support
└── pages/
    └── [existing pages - no changes]

# Backend (FastAPI)
backend/
├── app/
│   ├── api/
│   │   ├── language.py              # New - /api/detect-language endpoint - Phase 2
│   │   └── chat.py                  # Modified - add preferredLanguage param - Phase 2
│   ├── core/
│   │   ├── i18n.py                  # New - language utilities - Phase 2
│   │   └── config.py                # Modified - add language settings - Phase 2
│   ├── services/
│   │   └── rag_multilingual.py      # New - language-aware RAG - Phase 3
│   └── main.py                      # Modified - include language router - Phase 2
└── tests/
    ├── test_language_detection.py   # New - language endpoint tests - Phase 2
    └── test_rag_multilingual.py     # New - RAG filtering tests - Phase 3

# Configuration
docusaurus.config.ts                 # Modified - i18n config - Phase 1
.env.example                         # Updated - document language settings - Phase 1
```

**Structure Decision**: Web application structure selected (frontend + backend). Docusaurus frontend uses native i18n plugin with `i18n/[locale]/` directories. Backend extends existing FastAPI structure with new `app/api/language.py` and `app/core/i18n.py` modules. RAG changes isolated to `rag_multilingual.py` service. Clear separation enables parallel development and independent testing.

## Complexity Tracking

**NO VIOLATIONS** - Constitution check passed. No complexity justification required.

---

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Docusaurus i18n Best Practices**
   - Research: Docusaurus 3.x i18n plugin configuration and folder structure
   - Decision criterion: Minimize build complexity, support incremental translation

2. **Language Detection Libraries**
   - Research: OpenAI API language detection vs langdetect vs langid vs fasttext
   - Decision criterion: Accuracy (>90%), latency (<200ms), supported languages (en/ur/ja)

3. **RTL CSS Patterns**
   - Research: CSS logical properties, `[dir="rtl"]` selectors, Docusaurus RTL plugins
   - Decision criterion: Browser compatibility (Chrome 90+), minimal code duplication

4. **Qdrant Metadata Filtering**
   - Research: Qdrant filter syntax for language tags, performance impact of filters
   - Decision criterion: Query latency (<2s), fallback logic complexity

5. **Translation Workflow Automation**
   - Research: OpenAI API batch translation, i18n extraction tools, translation management
   - Decision criterion: Cost efficiency, quality control, integration with GitHub workflow

### Unknowns to Resolve

- **Docusaurus i18n routing**: Does Docusaurus support URL-based locale switching or only localStorage?
  - **Resolution needed**: Determine if `/ur/docs/intro` URLs are auto-generated or require manual config

- **OpenAI language detection API**: Which OpenAI API endpoint supports language detection?
  - **Resolution needed**: Verify if GPT-4 completion with language detection prompt is reliable, or use dedicated library

- **RTL specifics**: How to handle RTL for content areas while keeping navbar LTR?
  - **Resolution needed**: CSS scoping strategy for hybrid RTL (content-only vs full-page)

- **Qdrant filter performance**: Does adding language filter significantly impact search latency?
  - **Resolution needed**: Benchmark existing Qdrant queries with and without metadata filters

- **Translation storage**: Should translations be in git or external CMS?
  - **Resolution needed**: Decision on whether to commit `i18n/` translations to git or use Crowdin/Lokalise

---

## Phase 1: Design & Contracts

### Data Model (to be generated in data-model.md)

**Frontend Entities**:
- `LanguagePreference` (localStorage)
- `TranslationMetadata` (per-doc translation status)

**Backend Entities**:
- `LanguageDetectionResult` (API response)
- `ChatMessage` (extended with language fields)

**RAG Entities**:
- `DocumentEmbedding` (Qdrant payload with language tag)

### API Contracts (to be generated in /contracts/)

1. **`/api/detect-language` (new endpoint)**
   - Method: POST
   - Request: `{ "text": string }`
   - Response: `{ "detectedLanguage": "en"|"ur"|"ja", "confidence": number, "fallbackApplied": boolean }`

2. **`/api/chat` (modified endpoint)**
   - Method: POST
   - Request: Add `preferredLanguage?: "en"|"ur"|"ja"` field
   - Response: Add `{ "responseLanguage": string, "detectedInputLanguage": string, "fallbackApplied": boolean }`

### Components to Create

1. **LanguageSwitcher** (React component)
   - Location: `src/components/LanguageSwitcher/index.tsx`
   - Props: `{ currentLocale, onLanguageChange }`
   - Features: Dropdown, localStorage persistence, accessibility

2. **RTL Stylesheet** (CSS module)
   - Location: `src/theme/RTL/urdu.css`
   - Scope: `[dir="rtl"]` selectors for content areas and chat
   - Features: Text direction, flex-direction, padding/margin reversals

3. **LanguageDetector** (Backend service)
   - Location: `backend/app/core/i18n.py`
   - Functions: `detect_language(text)`, `get_fallback_language(confidence, ui_lang)`

4. **RAGMultilingual** (Backend service)
   - Location: `backend/app/services/rag_multilingual.py`
   - Functions: `filter_by_language(query, lang)`, `fallback_search(query, primary_lang, fallback_lang)`

### Quickstart (to be generated in quickstart.md)

**Developer Setup**:
1. Install dependencies: `npm install` (frontend), `pip install -r requirements.txt` (backend)
2. Configure `.env`: Add `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`
3. Run Docusaurus dev server: `npm start`
4. Test language switching: Change browser language, select from switcher
5. Test backend: `curl -X POST http://localhost:8000/api/detect-language -d '{"text": "مرحبا"}'`

**Translation Workflow**:
1. Extract UI strings: `npm run write-translations -- --locale ur`
2. Translate `i18n/ur/code.json` (manually or via OpenAI script)
3. Test: `npm run start -- --locale ur`
4. Commit translations: `git add i18n/ && git commit -m "chore: add Urdu UI translations"`

---

## Phase 2: Tasks Generation (deferred to /sp.tasks)

**Note**: Task breakdown is created by `/sp.tasks` command, not by `/sp.plan`. The plan defines architecture and contracts; tasks define implementation order.

Expected task categories:
- **Frontend Setup**: Docusaurus i18n config, language switcher component, RTL CSS
- **Backend Detection**: Language detection endpoint, chat endpoint extension
- **RAG Integration**: Qdrant metadata tagging, language-filtered search
- **Content Translation**: UI strings, high-priority chapters
- **Testing & QA**: Language detection tests, RTL rendering validation, E2E flows

---

## Architectural Decision Records (ADRs)

The following decisions may warrant ADR documentation (to be created via `/sp.adr` if user approves):

1. **ADR-001: Hybrid RTL Layout Strategy**
   - **Decision**: Apply RTL to content areas and chat only, keep navigation LTR
   - **Rationale**: Balances authentic Urdu experience with implementation simplicity
   - **Alternatives**: Full RTL mirroring (complex, high bug risk), text-only RTL (poor UX)

2. **ADR-002: Language Detection with 50% Confidence Threshold**
   - **Decision**: Use 50% confidence threshold with UI language fallback
   - **Rationale**: Balanced approach between detection trust and safety net
   - **Alternatives**: 70% (too conservative, more fallbacks), 90% (over-reliant on UI setting)

3. **ADR-003: Translation Strategy (Hybrid OpenAI + Professional)**
   - **Decision**: OpenAI GPT-4 for UI strings, professional translators for chapters
   - **Rationale**: Speed and cost for UI, quality and cultural appropriateness for content
   - **Alternatives**: Full professional (slow, expensive), full machine (lower quality for content)

**Next Step**: After reviewing this plan, run `/sp.adr <title>` for any of the above decisions to create formal ADR documentation.

---

## Implementation Phases Summary

| Phase | Scope | Duration | Deliverables |
|-------|-------|----------|--------------|
| **Phase 0** | Research & decisions | Complete | research.md with all technology choices |
| **Phase 1** | Design & contracts | Complete | data-model.md, contracts/, quickstart.md |
| **Phase 2** | Task generation | Next | tasks.md (via `/sp.tasks`) |
| **Phase 3** | Implementation | Deferred | Code, tests (via `/sp.implement`) |

**Current Status**: Plan complete. Ready for `/sp.tasks` to generate dependency-ordered implementation tasks.

---

## Notes

- **Translation content**: Phase 4 (chapter translation) is out of scope for this plan. Focus on infrastructure and UI translations first.
- **Performance benchmarking**: Qdrant filter performance testing is a research task; actual benchmarks TBD.
- **Agent context**: Run `.specify/scripts/bash/update-agent-context.sh claude` after Phase 1 artifacts are generated to update agent knowledge of new APIs and components.
- **Testing strategy**: Manual QA for RTL rendering (20-checkpoint checklist from spec), automated tests for backend APIs.
