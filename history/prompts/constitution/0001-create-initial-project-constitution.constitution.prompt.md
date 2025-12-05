---
id: 0001
title: Create initial project constitution
stage: constitution
date: 2025-12-05
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: Muhammad Qasim
command: /sp.constitution
labels: ["constitution", "hackathon", "governance", "initial-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution creation, no tests required)
---

## Prompt

Create a project constitution for the "Physical AI & Humanoid Robotics Textbook" hackathon project.

Context and non‑negotiables:
- This project implements the official "Hackathon I: Physical AI & Humanoid Robotics Textbook" assignment.md.
- Use Spec‑Kit Plus as the primary workflow: /sp.constitution → /sp.specify → /sp.clarify → /sp.plan → /sp.tasks → /sp.implement.
- Tech stack (high‑level):
  - Frontend textbook: Docusaurus (TypeScript) deployed to GitHub Pages (or similar).
  - Backend: FastAPI (Python) using OpenAI Agents / ChatKit SDKs, Qdrant Cloud (Free Tier), and Neon serverless Postgres.
  - Auth & personalization: Better‑Auth for signup/signin and user profile (software + hardware background).
- All requirements and constraints must align with assignment.md; do NOT invent extra robotics/hardware requirements.

Please define principles in the following areas:

1) Hackathon Alignment & Scope
- Always treat assignment.md as the single source of truth.
- Base deliverables:
  - Docusaurus textbook for the "Physical AI & Humanoid Robotics" course (intro + 4 modules).
  - Integrated RAG chatbot that can answer questions about the whole book AND questions based only on user‑selected text.
- Bonus deliverables (if time allows):
  - Claude Code subagents and skills to create reusable intelligence for this project.
  - Better‑Auth signup/signin capturing user software & hardware background.
  - Per‑chapter personalization button that adapts content to the user's level/background.
  - Per‑chapter Urdu translation button.
- No real hardware control is required; the book teaches concepts, simulations, and hardware architecture.

2) Structure‑Before‑Content (Docusaurus)
- Always design and review structure before writing lots of content:
  - Docs tree: intro + 4 modules (ROS 2, Gazebo & Unity, NVIDIA Isaac, VLA) with at least 1 chapter each.
  - Sidebars and routing.
  - Homepage with hero, "Start the Course" CTA to /docs/intro, and key features.
  - Hide/remove blog from navbar unless explicitly requested.
- For each module:
  - First: outline (overview + chapter 1 headings).
  - Then: get human approval.
  - Only then: write content (medium difficulty as baseline, then adapt per user level).

3) Adaptive Learning & Personalization
- During signup with Better‑Auth, collect user background (software experience, robotics/AI exposure, available hardware).
- Based on profile, each chapter can adapt difficulty:
  - Beginner: simpler explanations, more diagrams, fewer assumptions, step‑by‑step.
  - Intermediate (default): medium difficulty.
  - Advanced: deeper technical details, links to specs, performance trade‑offs.
- Constitution should require that:
  - Personalization logic is explicit, auditable, and does NOT silently hide critical safety content.
  - Default content works even without login; personalization is an enhancement, not a dependency.

4) RAG Chatbot & Selection‑Based UX
- RAG backend responsibilities:
  - Answer questions about the entire textbook content.
  - Answer questions restricted to user‑selected text spans (selection‑based Q&A).
- Frontend UI principles:
  - When the user selects text in the docs, a small, unobtrusive "Ask about this" or "Ask the textbook" UI appears.
  - Users can open a chat panel embedded in the book (no janky popups) to interact with the RAG system.
  - Clear indication whether the answer is based on:
    - Whole‑book context, or
    - Only the selected text.
- Data and infra:
  - Use Qdrant Cloud for vector storage of book content.
  - Use Neon Postgres for structured data (users, profiles, personalization config, etc.).
  - Ensure API keys and secrets are never committed to git.

5) Content Quality, Code Examples & UI/UX
- Emphasize:
  - Accurate, modern information about ROS 2, Gazebo, Unity, NVIDIA Isaac, VLA, and related tools.
  - Clear distinctions between "conceptual explanation", "minimal working example", and "production‑ready pattern".
- Code snippets:
  - Prefer TypeScript examples for Docusaurus front‑end integrations.
  - Python examples for FastAPI, ROS 2 (rclpy), NVIDIA Isaac integration stubs, etc.
  - Keep snippets tested or at least syntactically valid; no pseudo‑code unless explicitly labeled as such.
- UI/UX:
  - Clean, modern layout; responsive design.
  - Consistent components for callouts, warnings, hardware requirements, and step‑by‑step labs.
  - Accessibility: readable fonts, good contrast, keyboard navigation basics.
- Branding:
  - Clearly credit the author as "Muhammad Qasim" on the homepage and in the book (e.g., "Authored by Muhammad Qasim").
  - Footer should include GitHub and other relevant links (GitHub: https://github.com/Psqasim, LinkedIn, etc.).

6) Engineering Practices & AI Governance
- Separate concerns:
  - Textbook frontend vs RAG backend vs auth/personalization logic.
  - Each major feature should have its own spec, plan, and tasks where appropriate.
- Git and change management:
  - Small, coherent commits with meaningful messages.
  - Avoid large, unreviewed rewrites without first updating spec/plan/tasks.
- Testing:
  - At minimum:
    - Backend: sanity tests for core FastAPI endpoints (healthcheck, chat, personalization).
    - Frontend: basic checks that main routes build and render, and that RAG UI loads without errors.
- AI usage:
  - Use Spec‑Driven Development: keep spec.md, plan.md, and tasks.md as the single source of truth for implementation decisions.
  - Before generating large amounts of code, ensure the spec and plan are updated to reflect the new scope.
  - Favor clarity and maintainability over overly clever AI‑generated abstractions.

7) Constraints & Out‑of‑Scope
- Do NOT add robotics or hardware requirements beyond what assignment.md clearly describes.
- Real‑world robot control, motor drivers, or safety‑critical closed‑loop systems are out of scope.
- Focus on teaching, simulation, architecture, and developer experience.

Write the constitution as a clear, structured markdown document that future /sp.* steps must respect.

## Response snapshot

Constitution successfully created at `.specify/memory/constitution.md` with version 1.0.0.

**Seven Core Principles Defined**:

I. **Assignment.md as Single Source of Truth (NON-NEGOTIABLE)** - All requirements must align with the official hackathon assignment; no invented robotics/hardware requirements.

II. **Structure-Before-Content (Documentation Philosophy)** - Design and approve structure FIRST (docs tree, sidebars, routing), then write content. Each module requires outline → human approval → content.

III. **Spec-Driven Development (SDD Workflow)** - Mandatory workflow: /sp.constitution → /sp.specify → /sp.clarify → /sp.plan → /sp.tasks → /sp.implement. Keep spec.md (WHAT/WHY) separate from plan.md (HOW).

IV. **Adaptive Learning Without Hiding Safety (Personalization)** - Three difficulty tiers (Beginner/Intermediate/Advanced) based on user profile. Safety content never hidden. Default content works without login.

V. **RAG Chatbot: Whole-Book and Selection-Based Q&A** - Two modes: whole-book context and selection-based queries. Embedded chat panel (no popups). Qdrant Cloud for embeddings, Neon Postgres for structured data.

VI. **Code Quality, Examples, and UI/UX Standards** - Syntactically valid code examples. TypeScript for frontend, Python for backend. Professional branding crediting "Muhammad Qasim". Clean, accessible UI.

VII. **Separation of Concerns and Small, Testable Changes** - Clear architecture boundaries (Docusaurus frontend, FastAPI backend, Better-Auth). Small commits. Sanity tests for core endpoints.

**Technical Stack & Architecture Section** covers:
- Frontend: Docusaurus (TypeScript/React), GitHub Pages deployment
- Backend: FastAPI (Python), OpenAI Agents/ChatKit, Qdrant Cloud, Neon Postgres, Better-Auth
- Secrets management: .env files (never committed)
- Out of scope: Real robotics hardware control, safety-critical systems

**Development Workflow Section** defines:
- Feature development lifecycle (Spec → Clarify → Plan → Tasks → Implement → ADR)
- PHR (Prompt History Record) creation mandatory after all significant interactions
- ADR (Architecture Decision Record) suggestions for significant architectural decisions (three-part test: Impact + Alternatives + Scope)
- Git discipline: small commits, conventional commit format
- Testing expectations: pytest for backend, basic build/render checks for frontend
- Human as Tool strategy: invoke user for ambiguities, dependencies, architectural choices, completion checkpoints

**Governance Section** establishes:
- Amendment procedure with semantic versioning
- Compliance requirements (all PRs must verify constitution compliance)
- Constitution supersedes default practices and AI suggestions

**Templates Reviewed**: spec-template.md, plan-template.md, tasks-template.md all validated for alignment with constitution principles.

**Version**: 1.0.0 | **Ratified**: 2025-12-05 | **Last Amended**: 2025-12-05

## Outcome

- ✅ Impact: Initial constitution created defining 7 core principles, technical stack, development workflow, and governance for the Physical AI & Humanoid Robotics Textbook hackathon project. Provides authoritative guidance for all future /sp.* commands and development work.
- 🧪 Tests: N/A (constitution is governance documentation, not code)
- 📁 Files: Created .specify/memory/constitution.md (v1.0.0, 240 lines)
- 🔁 Next prompts: Suggested commit: `docs: create initial project constitution v1.0.0`. Next steps: `/sp.specify` to create feature specifications for base deliverables (Docusaurus textbook, RAG chatbot).
- 🧠 Reflection: Constitution successfully captures all user requirements including hackathon alignment, structure-before-content philosophy, SDD workflow, personalization without hiding safety, selection-based RAG, code quality standards, and separation of concerns. All placeholders resolved. Templates reviewed for consistency.

## Evaluation notes (flywheel)

- Failure modes observed: None - all user requirements successfully incorporated into constitution structure
- Graders run and results (PASS/FAIL): Manual validation PASS - no unresolved placeholders, all 7 principles clearly defined with rationale, templates reviewed and aligned
- Prompt variant (if applicable): N/A (initial constitution creation)
- Next experiment (smallest change to try): Monitor first `/sp.specify` execution to validate that constitution principles are correctly enforced (especially Structure-Before-Content and Assignment.md alignment)
