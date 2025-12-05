---
id: 002
title: Clarify RAG Backend Specification
stage: clarify
date: 2025-12-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-rag-backend-study-assistant
branch: 001-docusaurus-frontend
user: user
command: /sp.clarify
labels: ["rag", "backend", "clarification", "requirements", "retrieval", "citations", "data-storage"]
links:
  spec: /specs/002-rag-backend-study-assistant/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-rag-backend-study-assistant/spec.md
tests:
  - None (clarification phase)
---

## Prompt

/sp.clarify

Run a structured clarification pass for the feature
"002-rag-backend-study-assistant" (RAG backend + chat API).

Instructions:
- Read specs/002-rag-backend-study-assistant/spec.md completely.
- Identify ambiguities or options around:
  - Whole-book vs selection-based retrieval behavior
  - How many citations to return and in what format
  - Chunking strategy (by heading vs fixed size)
  - Expected OpenAI model family (e.g. GPT-4.1 vs smaller)
  - How strictly answers must stick to retrieved docs (hallucination control)
  - Minimum data stored in Neon and retention policy
  - CORS / security expectations for public demo
- Ask me up to 5 focused clarification questions.
- After I answer, update the "Clarifications" (or similar) section in the spec
  and ensure all functional requirements remain testable.

Keep the focus on WHAT & WHY, not implementation details (HOW will be done in /sp.plan).

## Response snapshot

Ran structured clarification pass with 4 targeted questions covering:

**Questions Asked**:
1. **Retrieval Count**: How many chunks to retrieve in whole-book mode? → Decision: Top 5-10 chunks (balanced approach)
2. **Answer Quality**: How to handle low relevance scores? → Decision: Always answer, no threshold (better UX)
3. **Selection Scope**: What retrieval scope for selection-based Q&A? → Decision: Selected chunk + 2-3 neighbors (balanced context)
4. **Data & Citations**: Citation count and anonymous user storage? → Decision: 3-5 citations, no storage for anonymous users (privacy-focused)

**Clarifications Documented**:
1. **Retrieval Count**: Top 5-10 chunks for whole-book mode (balanced coverage, reasonable cost/latency)
2. **Answer Quality**: Always answer using top chunks regardless of similarity score (OpenAI model handles irrelevant context gracefully)
3. **Selection-Based Scope**: Selected chunk + 2-3 neighboring chunks (before/after) in same document
4. **Citation Count**: Return 3-5 citations matching most relevant chunks (compact, readable format)
5. **Data Storage Policy**: Do NOT store sessions/messages for anonymous users (userId null/missing); 90-day retention for authenticated users

**Requirements Updated**:
- FR-004: Clarified to retrieve "top 5-10 most relevant chunks using cosine similarity"
- FR-005: Specified "selected chunk + 2-3 neighboring chunks (before/after)"
- FR-008: Updated to "3-5 citations corresponding to most relevant chunks"
- FR-009: Added "ONLY when userId is provided (non-null and non-empty)"
- FR-010: Added "ONLY for sessions with a userId"
- FR-021: NEW requirement - "MUST NOT persist for anonymous users"
- NFR-015: Clarified "5-10 chunks (as specified in FR-004)"

**User Story Updates**:
- User Story 2, Scenario 1: Clarified retrieval behavior to "selected text plus 2-3 neighboring chunks"

**API Examples Updated**:
- Example 1 (Whole-Book): Now shows 3 citations instead of 1
- Response schema reflects 3-5 citation objects

**Open Questions Resolved**: 5 product/behavioral questions resolved; 5 technical HOW questions deferred to /sp.plan phase

**Validation**: All updated requirements remain independently testable and measurable.

## Outcome

- ✅ Impact: Spec clarified with 5 concrete product decisions documented in new "Clarifications" section. All ambiguities around retrieval behavior, citation count, and data storage resolved. 7 functional requirements updated or added (FR-004, FR-005, FR-008, FR-009, FR-010, FR-021, NFR-015). Spec ready for /sp.plan phase.
- 🧪 Tests: None (clarification phase)
- 📁 Files: Updated specs/002-rag-backend-study-assistant/spec.md (added Clarifications section, updated 7 requirements, updated user story scenarios, updated API examples)
- 🔁 Next prompts: /sp.plan to make technical architecture decisions (chunking strategy, OpenAI models, Qdrant config, deployment target, indexing workflow)
- 🧠 Reflection: Clarification focused on WHAT/WHY decisions (product behavior, user experience, data policy) and deferred HOW decisions (implementation details) to planning phase. All requirements validated to remain testable. Privacy-focused approach chosen for anonymous users.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation - PASS (all updated requirements are testable, clarifications add specificity without ambiguity, WHAT/WHY separation maintained)
- Prompt variant (if applicable): Standard /sp.clarify workflow with targeted question grouping
- Next experiment (smallest change to try): Proceed with /sp.plan to resolve remaining technical decisions
