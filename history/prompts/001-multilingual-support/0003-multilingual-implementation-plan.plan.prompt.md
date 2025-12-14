---
id: 0003
title: Multilingual Implementation Plan
stage: plan
date: 2025-12-11
surface: agent
model: claude-sonnet-4-5
feature: 001-multilingual-support
branch: 001-multilingual-support
user: ps_qasim
command: /sp.plan
labels: ["architecture", "design", "api-contracts", "multilingual", "i18n"]
links:
  spec: specs/001-multilingual-support/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-multilingual-support/plan.md
  - specs/001-multilingual-support/research.md
  - specs/001-multilingual-support/data-model.md
  - specs/001-multilingual-support/quickstart.md
  - specs/001-multilingual-support/contracts/detect-language.openapi.yaml
  - specs/001-multilingual-support/contracts/chat-extended.openapi.yaml
tests:
  - Constitution check validation (all 7 principles passed)
  - Technology decision validation (6 research areas resolved)
  - Data model validation (8 entities defined with schemas)
  - API contract validation (2 OpenAPI specs generated)
---

## Prompt

001-multilingual-support

## Response snapshot

**Planning Phase Complete**: Generated comprehensive implementation plan for multilingual support (English, Urdu, Japanese) across Docusaurus frontend, FastAPI backend, and Qdrant RAG pipeline.

**Artifacts Created**:

1. **plan.md** (348 lines)
   - Summary and technical context
   - Constitution check (all 7 principles passed, no violations)
   - Project structure (frontend i18n, backend APIs, RAG services)
   - Complexity tracking (no violations)
   - Phase 0/1 outlines, ADR suggestions

2. **research.md** (6 technology decisions resolved)
   - Docusaurus i18n: Native plugin with filesystem translations
   - Language detection: `langdetect` library (<10ms latency, 90% accuracy)
   - RTL CSS: `[dir="rtl"]` selectors + CSS logical properties (hybrid approach)
   - Qdrant filtering: Metadata filters with language tags (~20ms overhead)
   - Translation automation: OpenAI GPT-4 batch translation ($0.03/language)
   - Translation storage: Git-tracked filesystem (simple, versioned)

3. **data-model.md** (8 entities defined)
   - Frontend: LanguagePreference (localStorage), TranslationMetadata
   - Backend: LanguageDetectionRequest/Result, ChatMessage (extended), ChatRequest/Response (extended)
   - RAG: DocumentEmbedding (Qdrant with language tags)
   - Data flows and entity relationships documented

4. **contracts/** (2 OpenAPI 3.0 specs)
   - detect-language.openapi.yaml: New language detection endpoint
   - chat-extended.openapi.yaml: Extended chat endpoint with preferredLanguage parameter

5. **quickstart.md** (Developer guide)
   - Setup instructions (frontend + backend)
   - Testing procedures (language switcher, RTL, detection, RAG filtering)
   - Development workflow (adding languages, translating docs)
   - Troubleshooting common issues
   - Performance optimization tips

**Key Technical Decisions**:
- Docusaurus native i18n (no external CMS for Phase 1)
- langdetect for backend detection (free, fast, accurate)
- Hybrid RTL (content areas + chat, navigation stays LTR)
- 50% confidence threshold (balanced detection approach)
- OpenAI GPT-4 for UI strings, professional translators for chapters

**Architecture Highlights**:
- 3-layer design: Frontend (Docusaurus i18n), Backend (FastAPI language detection), RAG (Qdrant language filtering)
- localStorage for language preference (no backend storage)
- Qdrant metadata payload for language tags (no separate collections)
- Fallback logic: Detected language → UI language → English

**ADR Suggestions** (3 significant decisions):
1. Hybrid RTL Layout Strategy
2. Language Detection with 50% Confidence Threshold
3. Translation Strategy (Hybrid OpenAI + Professional)

**Performance Targets**:
- Language switch: <300ms
- Detection API: <200ms
- RAG with filter: <2s for 95% of queries
- Chat latency impact: <100ms

## Outcome

- ✅ Impact: Complete implementation plan with architecture, contracts, and developer guide. Constitution-compliant, all research resolved.
- 🧪 Tests: Constitution check (7/7 pass), technology validation (6/6 resolved), data model validation (8 entities), API contracts (2 OpenAPI specs)
- 📁 Files: 6 artifacts created (plan.md, research.md, data-model.md, quickstart.md, 2 OpenAPI specs)
- 🔁 Next prompts: Run `/sp.tasks` to generate dependency-ordered implementation tasks, then `/sp.implement` to execute
- 🧠 Reflection: Planning phase successful with clear separation between Phase 0 (research) and Phase 1 (design). All unknowns resolved, contracts defined, developer workflow documented. Ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed without blockers
- Graders run and results (PASS/FAIL):
  - Constitution Check: PASS (all 7 principles satisfied, no violations)
  - Research Completeness: PASS (all unknowns resolved with decisions + rationale)
  - Data Model Completeness: PASS (8 entities with schemas, validation rules, examples)
  - API Contract Completeness: PASS (2 OpenAPI 3.0 specs with examples, error handling)
  - Developer Experience: PASS (quickstart guide with setup, testing, troubleshooting)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run `/sp.tasks` with plan.md context to validate task generation correctly maps to architecture phases
