# Implementation Tasks: Multilingual Support (EN / UR / JA)

**Feature**: 001-multilingual-support
**Branch**: `001-multilingual-support`
**Date**: 2025-12-11
**Status**: Ready for Implementation

---

## Overview

This document defines the implementation tasks for multilingual support (English, Urdu, Japanese) across the Docusaurus frontend, FastAPI backend, and Qdrant RAG pipeline. Tasks are organized by user story to enable independent implementation and testing.

**Total Tasks**: 45
**Parallelizable Tasks**: 23 (marked with [P])
**User Stories**: 8 (P1: 3 stories, P2: 3 stories, P3: 2 stories)

---

## Implementation Strategy

### MVP Scope (User Story 1 Only)
For fastest time-to-value, implement only **User Story 1** (Language Selection and Persistence) as MVP:
- Docusaurus i18n configuration
- Language switcher component
- Browser language detection
- localStorage persistence
- RTL CSS foundation

This delivers the core multilingual infrastructure and can be deployed independently.

### Incremental Delivery
After MVP, implement user stories in priority order:
1. **P1 stories (US1-US3)**: Foundation + core chat functionality
2. **P2 stories (US4-US6)**: Enhanced UX + backend intelligence
3. **P3 stories (US7-US8)**: Advanced features + edge cases

Each story is independently testable and deliverable.

---

## Phase 1: Setup & Prerequisites

**Goal**: Prepare development environment and install dependencies.

**Independent Test**: All commands run without errors, dependencies installed successfully.

### Tasks

- [X] T001 Install frontend dependencies: `npm install` in project root
- [X] T002 Install backend dependencies: `pip install -r backend/requirements.txt` and `pip install langdetect`
- [X] T003 [P] Create `.env.example` file documenting required environment variables (OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, DEFAULT_LANGUAGE)
- [X] T004 [P] Update `backend/requirements.txt` to include `langdetect==1.0.9`
- [X] T005 Verify Docusaurus dev server runs: `npm start` (should compile without errors)
- [X] T006 Verify backend dev server runs: `cd backend && uvicorn app.main:app --reload` (should start on port 8000)

---

## Phase 2: Foundational Tasks (Blocking Prerequisites)

**Goal**: Set up shared infrastructure required by all user stories.

**Independent Test**: i18n directories exist, base configuration is valid, scripts are executable.

### Tasks

- [X] T007 Create i18n directory structure: `mkdir -p i18n/ur i18n/ja`
- [X] T008 [P] Create empty `i18n/ur/code.json` and `i18n/ja/code.json` placeholder files
- [X] T009 [P] Create translation automation script `scripts/translate-ui-strings.py` (skeleton only, no OpenAI calls yet)
- [X] T010 [P] Create RTL stylesheet directory: `mkdir -p src/theme/RTL`
- [X] T011 [P] Create backend i18n module directory: `mkdir -p backend/app/core` (if not exists)
- [X] T012 [P] Create backend language API directory: `mkdir -p backend/app/api` (if not exists)

---

## Phase 3: User Story 1 - Language Selection and Persistence (P1)

**Story Goal**: Enable users to select their preferred language, detect browser language, and persist choice across sessions.

**Independent Test**:
1. Visit site with browser set to Urdu → UI displays in Urdu
2. Select Japanese from switcher → UI updates without reload
3. Refresh page → language persists (Japanese still selected)
4. Check localStorage → `language-preference` entry exists with correct data

### Tasks

- [X] T013 [US1] Configure Docusaurus i18n in `docusaurus.config.ts`: set `i18n.locales` to `['en', 'ur', 'ja']` and define `localeConfigs` with labels, directions, htmlLang
- [X] T014 [US1] Add `localeDropdown` to navbar items in `docusaurus.config.ts` (position: 'right')
- [X] T015 [P] [US1] Create `src/components/LanguageSwitcher/index.tsx` React component with dropdown UI
- [X] T016 [P] [US1] Implement localStorage read/write logic in LanguageSwitcher: `getItem('language-preference')` and `setItem('language-preference')`
- [X] T017 [P] [US1] Create `src/components/LanguageSwitcher/styles.module.css` with dropdown styling
- [X] T018 [US1] Create `src/theme/Root.tsx` to detect browser language on first visit using `navigator.language`
- [X] T019 [US1] Implement language persistence logic in Root.tsx: check localStorage → detect browser → default to English
- [X] T020 [US1] Set `document.documentElement.setAttribute('dir', direction)` in Root.tsx based on selected language (rtl for Urdu, ltr for others)
- [ ] T021 [US1] Test browser language detection: Set browser to `ur-PK` → visit site → verify Urdu UI
- [ ] T022 [US1] Test language switcher: Select Japanese → verify instant UI update without page reload
- [ ] T023 [US1] Test persistence: Select Urdu → refresh → verify Urdu persists
- [ ] T024 [US1] Test unsupported language fallback: Set browser to French → verify English default

---

## Phase 4: User Story 2 - UI String Translation (P1)

**Story Goal**: Translate all UI strings (navbar, footer, buttons, modals, errors) into Urdu and Japanese.

**Independent Test**:
1. Switch to Japanese → verify navbar shows "コース", "学習アシスタント"
2. Switch to Urdu → verify footer copyright in Urdu
3. Trigger error → verify error message in selected language
4. Check translation coverage → 95%+ strings translated

### Tasks

- [X] T025 [US2] Extract UI strings for Urdu: run `npm run write-translations -- --locale ur`
- [X] T026 [US2] Extract UI strings for Japanese: run `npm run write-translations -- --locale ja`
- [X] T027 [P] [US2] Implement `scripts/translate-ui-strings.py` to translate `code.json` files using OpenAI GPT-4 API (batch translation with temperature=0.3)
- [X] T028 [US2] Run translation script for Urdu: `python scripts/translate-ui-strings.py --target ur`
- [X] T029 [US2] Run translation script for Japanese: `python scripts/translate-ui-strings.py --target ja`
- [X] T030 [P] [US2] Manually review 10-20 random translations in `i18n/ur/code.json` for quality
- [X] T031 [P] [US2] Manually review 10-20 random translations in `i18n/ja/code.json` for quality
- [ ] T032 [US2] Test Japanese navbar: Switch to Japanese → verify "コース" (Course), "学習アシスタント" (Study Assistant) displayed
- [ ] T033 [US2] Test Urdu footer: Switch to Urdu → verify copyright text translated
- [ ] T034 [US2] Test error messages: Trigger network error in each language → verify localized error text
- [ ] T035 [US2] Calculate translation coverage: Count translated vs total strings → verify ≥95%

---

## Phase 5: User Story 3 - Study Assistant Language-Aware Chat (P1)

**Story Goal**: Backend detects language from chat messages and responds in user's language, querying language-specific content.

**Independent Test**:
1. Send Urdu message → verify response in Urdu with RTL
2. Send Japanese message → verify response in Japanese
3. Send English with low confidence → verify fallback to UI language
4. Check response metadata → `detectedInputLanguage` and `responseLanguage` present

### Tasks

- [X] T036 [P] [US3] Create `backend/app/core/i18n.py` with `detect_language(text)` function using langdetect library
- [X] T037 [P] [US3] Implement confidence threshold logic in i18n.py: return detected language if confidence ≥0.5, else fallback
- [X] T038 [P] [US3] Create `backend/app/api/language.py` with `/api/detect-language` POST endpoint
- [X] T039 [P] [US3] Implement LanguageDetectionRequest/Result Pydantic models in backend/app/api/language.py
- [ ] T040 [US3] Update `backend/app/api/chat.py` to accept `preferredLanguage` parameter in ChatRequest model
- [ ] T041 [US3] Integrate language detection in chat endpoint: call `detect_language()` on incoming message
- [ ] T042 [US3] Add language metadata to chat response: `responseLanguage`, `detectedInputLanguage`, `fallbackApplied` fields
- [ ] T043 [US3] Update OpenAI system prompt template to include "Reply in {detected_language}" instruction
- [X] T044 [US3] Update `backend/app/main.py` to include language router: `app.include_router(language.router, prefix="/api", tags=["language"])`
- [ ] T045 [US3] Test detection endpoint with Urdu text: `curl -X POST /api/detect-language -d '{"text": "ROS 2 کیا ہے؟"}'` → verify `detectedLanguage: "ur"`
- [ ] T046 [US3] Test detection endpoint with Japanese text: verify `detectedLanguage: "ja"`
- [ ] T047 [US3] Test chat with Urdu message: Send "ROS 2 کیا ہے؟" → verify response in Urdu
- [ ] T048 [US3] Test language fallback: Send ambiguous text → verify fallback to `preferredLanguage`

---

## Phase 6: User Story 4 - Urdu RTL Support (P2)

**Story Goal**: Implement hybrid RTL layout for Urdu (content areas + chat RTL, navigation LTR).

**Independent Test**:
1. Switch to Urdu → verify content text flows right-to-left
2. Verify chat messages: user messages align right, assistant left
3. Verify navbar/sidebar remain LTR
4. Verify code blocks remain LTR

### Tasks

- [X] T049 [P] [US4] Create `src/theme/RTL/urdu.css` with `[dir="rtl"]` selectors for content areas (`.markdown`, `.theme-doc-markdown`)
- [X] T050 [P] [US4] Add RTL chat message alignment in urdu.css: `.chat-message-user` (margin-inline-start: auto), `.chat-message-assistant` (margin-inline-end: auto)
- [X] T051 [P] [US4] Add navigation LTR override in urdu.css: `.navbar`, `.sidebar`, `.footer` (direction: ltr, text-align: left)
- [X] T052 [P] [US4] Add code block LTR override in urdu.css: `pre`, `code` (direction: ltr, text-align: left)
- [X] T053 [P] [US4] Add icon flipping for RTL: `.icon-arrow-right::before` → content: '←', `.icon-arrow-left::before` → content: '→'
- [X] T054 [US4] Import urdu.css in Root.tsx: `import '@site/src/theme/RTL/urdu.css'`
- [ ] T055 [US4] Test Urdu RTL content: Switch to Urdu → navigate to doc page → verify text flows right-to-left
- [ ] T056 [US4] Test chat RTL: Send Urdu message in chat → verify user message aligns right, assistant left
- [ ] T057 [US4] Test navbar LTR: Switch to Urdu → verify navbar items remain left-aligned
- [ ] T058 [US4] Test code blocks: View code example in Urdu doc → verify code remains LTR

---

## Phase 7: User Story 5 - Backend Language Detection (P2)

**Story Goal**: Backend accurately detects language from chat messages and logs analytics.

**Independent Test**:
1. Send English, Urdu, Japanese messages → verify correct detection (90%+ accuracy)
2. Send mixed-language text → verify dominant language detected
3. Check logs → language metadata present (no PII)
4. Test confidence threshold → low confidence triggers fallback

### Tasks

- [X] T059 [P] [US5] Add language detection logging in `backend/app/api/language.py`: log detected language, confidence, timestamp (no message content)
- [X] T060 [P] [US5] Implement get_fallback_language function in i18n.py: return `ui_lang` if confidence < 0.5 or detected language not in ['en', 'ur', 'ja']
- [X] T061 [P] [US5] Add analytics logging in chat endpoint: log `detectedInputLanguage`, `requestedLanguage`, `responseLanguage` per message
- [X] T062 [US5] Create pytest test file `backend/tests/test_language_detection.py`
- [X] T063 [P] [US5] Write test cases for language detection: test English, Urdu, Japanese texts → assert correct language codes
- [X] T064 [P] [US5] Write test case for mixed language: send "ROS 2 is روبوٹکس" → assert dominant language detected
- [X] T065 [P] [US5] Write test case for unsupported language: send Arabic text → assert fallback to "en"
- [X] T066 [P] [US5] Write test case for low confidence: send ambiguous text → assert fallback applied
- [X] T067 [US5] Run pytest: `pytest backend/tests/test_language_detection.py -v` → verify all tests pass

---

## Phase 8: User Story 6 - Language-Tagged Content Retrieval (P2)

**Story Goal**: RAG pipeline filters searches by language and falls back to English if needed.

**Independent Test**:
1. Index test docs in English, Urdu, Japanese with language tags
2. Query in Japanese → verify Japanese docs returned first
3. Query in Urdu with no Urdu docs → verify English fallback
4. Measure search latency → verify <2s for 95% of queries

### Tasks

- [X] T068 [P] [US6] Create `backend/app/services/rag_multilingual.py` with `index_document(doc_text, doc_id, language)` function
- [X] T069 [P] [US6] Implement Qdrant PointStruct creation with language metadata in payload: `{"language": "en", "originalLanguage": "en", "translationSource": "original"}`
- [X] T070 [P] [US6] Implement `search_with_language_filter(query, language, limit)` function with Qdrant Filter for language field
- [X] T071 [P] [US6] Implement fallback search logic: if results < 3, query again with `language="en"` and merge results
- [X] T072 [US6] Update existing embedding pipeline to add language tag when indexing: modify `backend/scripts/index_docs.py` to include `language="en"` in payload
- [ ] T073 [US6] Re-index existing English documents with language tag: run `python backend/scripts/index_docs.py --add-language-tags`
- [X] T074 [P] [US6] Create pytest test file `backend/tests/test_rag_multilingual.py`
- [X] T075 [P] [US6] Write test: index 3 English docs → query "ROS 2" with language="en" → assert returns English docs
- [X] T076 [P] [US6] Write test: index 2 Japanese docs → query in Japanese with language="ja" → assert Japanese docs prioritized
- [X] T077 [P] [US6] Write test: query in Urdu with no Urdu docs → assert fallback to English docs and `fallbackApplied=true`
- [ ] T078 [US6] Run pytest: `pytest backend/tests/test_rag_multilingual.py -v` → verify all tests pass
- [ ] T079 [US6] Benchmark search performance: measure 100 queries with language filter → verify p95 latency <2s

---

## Phase 9: User Story 7 - Translation Toggle for Documentation (P3)

**Story Goal**: Display translation toggle on doc pages showing available languages.

**Independent Test**:
1. Create test doc with Urdu translation
2. View doc → verify toggle appears showing "EN | UR"
3. Click Urdu toggle → verify content switches to Urdu
4. Check incomplete translation → verify badge shows completion %

### Tasks

- [X] T080 [P] [US7] Create TranslationToggle React component in `src/components/TranslationToggle/index.tsx`
- [X] T081 [P] [US7] Implement TranslationToggle to read `translationMetadata` from document frontmatter
- [X] T082 [P] [US7] Display language toggle buttons (EN | UR | JA) based on `availableLanguages` array
- [X] T083 [P] [US7] Display completion badge if `completionPercentage` < 100: `<Badge>{percentage}% complete</Badge>`
- [X] T084 [US7] Add TranslationToggle to doc page layout: modify `src/theme/DocItem/index.tsx` to include toggle above content
- [X] T085 [P] [US7] Create test doc with translation metadata: `docs/test-translation.md` with frontmatter including `translationMetadata`
- [X] T086 [P] [US7] Create Urdu translation file: `i18n/ur/docusaurus-plugin-content-docs/current/test-translation.md`
- [X] T087 [US7] Test translation toggle: View test doc → verify toggle shows "EN | UR"
- [X] T088 [US7] Test language switch: Click UR toggle → verify content updates to Urdu
- [X] T089 [US7] Test incomplete translation badge: Set `completionPercentage.ur: 85` → verify "85% complete" badge displays

---

## Phase 10: User Story 8 - Voice Input Edge Cases (P3)

**Story Goal**: Handle voice input transcription and language detection for multilingual speech.

**Independent Test**:
1. Enable voice input → speak Japanese → verify transcription in Japanese
2. Speak with background noise → verify noise filtering works
3. Code-switch mid-speech → verify dominant language detected
4. Speech recognition fails → verify error message in UI language

### Tasks

- [X] T090 [P] [US8] Research browser Speech Recognition API compatibility (Chrome, Safari, Firefox)
- [X] T091 [P] [US8] Create VoiceInput React component in `src/components/VoiceInput/index.tsx`
- [X] T092 [P] [US8] Implement Speech Recognition initialization with language-specific models (en-US, ur-PK, ja-JP)
- [X] T093 [P] [US8] Add noise filtering: set `recognition.maxAlternatives = 3` and choose highest confidence result
- [X] T094 [P] [US8] Implement code-switching detection: analyze transcription, detect dominant language, update UI accordingly
- [X] T095 [P] [US8] Add error handling: catch SpeechRecognitionError → display localized error message from `code.json`
- [X] T096 [US8] Integrate VoiceInput into chat interface: add microphone button next to text input (integration example provided in README)
- [ ] T097 [US8] Test voice input in Japanese: Speak "ROS 2 とは何ですか？" → verify transcription in Japanese characters
- [ ] T098 [US8] Test noise filtering: Speak with background music → verify transcription still accurate
- [ ] T099 [US8] Test code-switching: Speak "ROS 2 is روبوٹکس" → verify dominant language (Urdu or English) detected
- [ ] T100 [US8] Test error handling: Block microphone permission → verify localized error "Microphone access denied"

---

## Phase 11: Polish & Cross-Cutting Concerns

**Goal**: Final QA, documentation, and deployment preparation.

**Independent Test**: All acceptance scenarios pass, documentation complete, performance targets met.

### Tasks

- [ ] T101 [P] Run full QA checklist from spec.md: 20-point RTL checklist, translation coverage check, performance benchmarks
- [X] T102 [P] Create developer documentation: update README.md with multilingual setup instructions
- [X] T103 [P] Document translation workflow: add MULTILINGUAL-WORKFLOW.md with backend and voice input sections
- [X] T104 [P] Update API documentation: document language endpoints in MULTILINGUAL-WORKFLOW.md
- [ ] T105 [P] Create language analytics dashboard query: write SQL to aggregate language usage from logs
- [X] T106 Build all locales: `npm run build` → verify builds for en, ur, ja complete without errors
- [ ] T107 Test mobile responsiveness: Open on 320px width → verify no layout breaks in all 3 languages
- [ ] T108 Test performance: Measure language switch time → verify <300ms (SC-001)
- [ ] T109 Test performance: Measure detection API latency → verify <200ms (SC-005)
- [ ] T110 Test performance: Measure RAG search with filter → verify <2s (SC-006)
- [ ] T111 Final smoke test: Complete one full user journey in each language (English, Urdu, Japanese)

---

## Dependencies & Execution Order

### Story Dependency Graph

```
Setup (Phase 1)
  ↓
Foundational (Phase 2)
  ↓
┌─────────────────────┬─────────────────────┬─────────────────────┐
│ US1: Lang Selection │ US2: UI Translation │ US3: Chat Detection │
│ (Phase 3)           │ (Phase 4)           │ (Phase 5)           │
│ INDEPENDENT         │ Depends on US1      │ Depends on US1      │
└─────────────────────┴─────────────────────┴─────────────────────┘
  ↓                     ↓                     ↓
┌─────────────────────┬─────────────────────┬─────────────────────┐
│ US4: RTL Support    │ US5: Detection Logs │ US6: Content Filter │
│ (Phase 6)           │ (Phase 7)           │ (Phase 8)           │
│ Depends on US1      │ Depends on US3      │ Depends on US3      │
└─────────────────────┴─────────────────────┴─────────────────────┘
  ↓                                           ↓
┌─────────────────────┬─────────────────────────────────────────┐
│ US7: Doc Toggle     │ US8: Voice Input                        │
│ (Phase 9)           │ (Phase 10)                              │
│ Depends on US1,US2  │ Depends on US1,US3                      │
└─────────────────────┴─────────────────────────────────────────┘
  ↓
Polish (Phase 11)
```

### Parallel Execution Opportunities

**US1 (Phase 3)**: Tasks T015-T017 (LanguageSwitcher files) can run in parallel
**US2 (Phase 4)**: Tasks T027, T030-T031 (translation + review) can run in parallel
**US3 (Phase 5)**: Tasks T036-T039 (backend modules) can run in parallel
**US4 (Phase 6)**: Tasks T049-T053 (CSS rules) can run in parallel
**US5 (Phase 7)**: Tasks T059-T061, T063-T066 (logging + tests) can run in parallel
**US6 (Phase 8)**: Tasks T068-T071, T074-T077 (RAG implementation + tests) can run in parallel
**US7 (Phase 9)**: Tasks T080-T083, T085-T086 (component + test docs) can run in parallel
**US8 (Phase 10)**: Tasks T090-T095 (VoiceInput component logic) can run in parallel
**Polish (Phase 11)**: Tasks T101-T105 (documentation + QA) can run in parallel

---

## Task Summary

| Phase | User Story | Task Count | Parallelizable | Blocking? |
|-------|-----------|------------|----------------|-----------|
| 1 | Setup | 6 | 2 | Yes (all stories) |
| 2 | Foundational | 6 | 5 | Yes (all stories) |
| 3 | US1 (P1) | 12 | 3 | No (independent) |
| 4 | US2 (P1) | 11 | 4 | Depends on US1 |
| 5 | US3 (P1) | 13 | 5 | Depends on US1 |
| 6 | US4 (P2) | 10 | 5 | Depends on US1 |
| 7 | US5 (P2) | 9 | 6 | Depends on US3 |
| 8 | US6 (P2) | 12 | 8 | Depends on US3 |
| 9 | US7 (P3) | 10 | 6 | Depends on US1, US2 |
| 10 | US8 (P3) | 11 | 6 | Depends on US1, US3 |
| 11 | Polish | 11 | 5 | Final phase |
| **Total** | - | **111** | **55** | - |

---

## Notes

**Tests**: Backend tests included for US5 (language detection) and US6 (RAG filtering) per spec testing requirements. Frontend tests are manual QA per spec guidance.

**MVP**: For fastest delivery, implement only Phase 1-3 (Setup + US1) = 24 tasks. This provides basic multilingual UI.

**Performance**: Performance validation tasks (T108-T110) in Polish phase verify all success criteria.

**Translation Content**: Chapter translation (spec Phase 4) is out of scope for this task list. Focus on infrastructure first.

---

## Next Steps

1. ✅ **Tasks generated**: 111 tasks across 11 phases
2. 🚀 **Ready for implementation**: Run `/sp.implement 001-multilingual-support`
3. 📊 **Progress tracking**: Use TodoWrite tool to track task completion
4. ✅ **Independent testing**: Each user story can be tested independently per acceptance scenarios
