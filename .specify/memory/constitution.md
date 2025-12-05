# Physical AI & Humanoid Robotics Textbook Constitution

<!--
Sync Impact Report:
- Version change: Initial creation → v1.0.0
- New constitution created for hackathon project
- Principles added: 7 core principles defined
- Sections added: Core Principles, Technical Stack & Architecture, Development Workflow, Governance
- Templates requiring updates:
  ✅ spec-template.md - reviewed, aligned with principles
  ✅ plan-template.md - reviewed, aligned with constitution check
  ✅ tasks-template.md - reviewed, aligned with task categorization
- Follow-up TODOs: None - all placeholders resolved
-->

## Core Principles

### I. Assignment.md as Single Source of Truth (NON-NEGOTIABLE)

The official hackathon assignment.md file defines ALL project requirements and deliverables. Every feature, user story, and technical decision MUST align with assignment.md. Do NOT invent robotics/hardware requirements, control systems, or safety-critical features beyond what is explicitly stated in the assignment.

**Rationale**: This is a hackathon project with a defined scope. Scope creep and invented requirements waste time and risk failing to deliver the actual assignment.

### II. Structure-Before-Content (Documentation Philosophy)

For Docusaurus and all documentation work:
- Design and review the complete structure FIRST (docs tree, sidebars, routing, navigation)
- Get explicit human approval of the structure
- ONLY THEN write content for each section

For each module or major section:
- Start with an outline (overview + chapter headings)
- Present to user for approval
- Write content after approval

**Rationale**: Writing lots of content without an approved structure leads to massive rewrites, wasted effort, and poor information architecture. Structure decisions are architectural; content is implementation.

### III. Spec-Driven Development (SDD Workflow)

All features MUST follow the Spec-Kit Plus workflow:
1. `/sp.constitution` → Define project principles (this document)
2. `/sp.specify` → Create feature specification with user stories, requirements, success criteria
3. `/sp.clarify` → Identify and resolve ambiguities before planning
4. `/sp.plan` → Design architecture, make technical decisions, document in plan.md
5. `/sp.tasks` → Generate dependency-ordered, independently testable tasks
6. `/sp.implement` → Execute tasks with continuous validation

**Key disciplines**:
- Keep spec.md (WHAT/WHY) separate from plan.md (HOW)
- Never generate large amounts of code without an approved spec and plan
- Update spec/plan/tasks before changing scope
- All major architectural decisions require explicit documentation and user approval

**Rationale**: Spec-Driven Development prevents drift, ensures alignment with requirements, enables clear checkpoints, and makes AI-assisted development predictable and auditable.

### IV. Adaptive Learning Without Hiding Safety (Personalization)

The textbook provides personalized content based on user profiles (software experience, hardware background, available equipment). Personalization MUST follow these rules:
- **Default content works for everyone**: Personalization is an enhancement, not a dependency
- **Safety content is never hidden**: Critical warnings, safety guidelines, and prerequisite knowledge are always shown regardless of user level
- **Explicit difficulty tiers**: Beginner, Intermediate (default), Advanced
  - Beginner: simpler language, more diagrams, step-by-step, fewer assumptions
  - Intermediate: medium difficulty, balanced explanations
  - Advanced: deeper technical details, performance trade-offs, links to specs
- **Auditable logic**: Personalization decisions are logged and inspectable
- **No login walls**: Unauthenticated users see the default (intermediate) content

**Rationale**: Personalization should enhance learning, not create barriers or hide important information. Users must understand what's being adapted and why.

### V. RAG Chatbot: Whole-Book and Selection-Based Q&A

The RAG (Retrieval-Augmented Generation) chatbot has two distinct modes:
1. **Whole-book Q&A**: Answer questions using the entire textbook as context
2. **Selection-based Q&A**: Answer questions restricted to user-selected text spans

**Requirements**:
- When users select text in the docs, show a small, unobtrusive "Ask about this" UI
- Open an embedded chat panel (no popups or new windows)
- Clearly indicate which mode is active (whole-book vs selection-based)
- Store embeddings in Qdrant Cloud (Free Tier)
- Use OpenAI Agents / ChatKit SDKs for chat orchestration
- Keep API keys and secrets out of git (use .env files)

**Rationale**: Selection-based Q&A is a key differentiator. Users should be able to ask detailed questions about specific paragraphs or code snippets without irrelevant context pollution.

### VI. Code Quality, Examples, and UI/UX Standards

**Code quality**:
- Prioritize clarity and maintainability over cleverness
- Use TypeScript for Docusaurus frontend integrations
- Use Python for FastAPI backend, ROS 2 (rclpy) examples, NVIDIA Isaac stubs
- All code snippets MUST be syntactically valid or explicitly labeled as pseudo-code
- Distinguish clearly between "conceptual example", "minimal working snippet", and "production pattern"

**UI/UX standards**:
- Clean, modern, responsive design
- Consistent components for callouts, warnings, hardware requirements, step-by-step labs
- Accessibility basics: readable fonts, good contrast, keyboard navigation
- No janky popups or modals; prefer embedded, contextual UI elements

**Branding and attribution**:
- Homepage and book MUST credit author "Muhammad Qasim"
- Footer includes GitHub (https://github.com/Psqasim), LinkedIn, and other relevant links

**Rationale**: This is a technical textbook and a portfolio piece. Quality, accuracy, and professionalism are critical. Poor code examples undermine trust and learning outcomes.

### VII. Separation of Concerns and Small, Testable Changes

**Architecture**:
- Textbook frontend (Docusaurus)
- RAG backend (FastAPI + Qdrant + Neon Postgres)
- Auth/personalization service (Better-Auth)
- Each major feature has its own spec, plan, and tasks

**Change management**:
- Small, coherent commits with meaningful messages
- No large, unreviewed rewrites without updating spec/plan/tasks
- Avoid unrelated edits when fixing bugs or adding features

**Testing**:
- Backend: sanity tests for core FastAPI endpoints (healthcheck, chat, personalization)
- Frontend: basic checks that main routes build and render, RAG UI loads without errors
- No real-world hardware testing required (this is a teaching project, not a robot control system)

**Rationale**: Clear separation of concerns enables parallel work, independent testing, and easier debugging. Small changes reduce risk and improve reviewability.

## Technical Stack & Architecture

### Frontend (Docusaurus Textbook)
- **Framework**: Docusaurus (TypeScript/React)
- **Deployment**: GitHub Pages or similar static hosting
- **Structure**: Intro + 4 modules (ROS 2, Gazebo & Unity, NVIDIA Isaac, VLA) with at least 1 chapter each
- **UI Components**: Custom React components for RAG chat panel, personalization controls, Urdu translation button
- **Routing**: Clean URLs matching course structure (/docs/intro, /docs/module-1/chapter-1, etc.)

### Backend (RAG & Personalization)
- **Framework**: FastAPI (Python)
- **AI/Chat**: OpenAI Agents / ChatKit SDKs
- **Vector DB**: Qdrant Cloud (Free Tier) for embeddings and semantic search
- **Relational DB**: Neon serverless Postgres for users, profiles, personalization config
- **Auth**: Better-Auth for signup/signin, capturing user software & hardware background

### Content & Data
- **Textbook content**: Markdown files in Docusaurus docs/ directory
- **Embeddings**: Generated from textbook content, stored in Qdrant
- **User profiles**: Stored in Neon Postgres (software experience, hardware background, preferred difficulty)
- **Personalization logic**: Explicit rules or lightweight models, NOT opaque AI black boxes

### Secrets Management
- Use `.env` files for API keys (OpenAI, Qdrant, Neon, Better-Auth)
- `.env` MUST be in `.gitignore`
- Document required environment variables in README or docs/setup.md

### Out of Scope
- Real robotics hardware control, motor drivers, safety-critical closed-loop systems
- Complex multi-agent orchestration beyond basic RAG chatbot
- Video hosting or streaming (images and diagrams are fine; embedded YouTube links are acceptable)

## Development Workflow

### 1. Feature Development Lifecycle
Every feature follows:
1. **Spec** (`/sp.specify`): Define user stories, requirements, success criteria in `specs/<feature>/spec.md`
2. **Clarify** (`/sp.clarify`): Identify and resolve ambiguities with targeted questions
3. **Plan** (`/sp.plan`): Architectural decisions, technical context, constitution check in `specs/<feature>/plan.md`
4. **Tasks** (`/sp.tasks`): Dependency-ordered, testable tasks in `specs/<feature>/tasks.md`
5. **Implement** (`/sp.implement`): Execute tasks, validate, commit
6. **ADR** (`/sp.adr` if applicable): Document architecturally significant decisions in `history/adr/`

### 2. Prompt History Records (PHRs)
After every significant user interaction, create a PHR:
- **Routing** (all under `history/prompts/`):
  - `constitution` → `history/prompts/constitution/`
  - Feature-specific (spec, plan, tasks, etc.) → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- **Content**: Full user input (verbatim), key assistant output, stage, feature, files changed, tests run
- **Format**: Use `.specify/templates/phr-template.prompt.md`
- **Mandatory**: Do NOT skip PHR creation unless the command is `/sp.phr` itself

### 3. Architecture Decision Records (ADRs)
When a significant architectural decision is made (framework choice, data model, API design, security approach), suggest:
> "📋 Architectural decision detected: <brief description> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"

Wait for user consent; NEVER auto-create ADRs. Group related decisions into one ADR when appropriate.

**Three-part test for ADR significance**:
- **Impact**: Long-term consequences? (e.g., framework, data model, API, platform)
- **Alternatives**: Multiple viable options considered with trade-offs?
- **Scope**: Cross-cutting and influences system design?

If ALL true, suggest ADR.

### 4. Git and Commit Discipline
- Small, focused commits with clear messages (e.g., "feat: add RAG selection-based Q&A UI", "docs: create ROS 2 module structure")
- Commit after each task or logical group of changes
- No force pushes to main/master without explicit user approval
- Follow conventional commit format where applicable (feat, fix, docs, refactor, test, chore)

### 5. Testing and Validation
- Backend: pytest for FastAPI endpoints
- Frontend: Basic build and render checks, manual testing of RAG UI
- No hardware-in-the-loop testing required
- Validate each user story independently before moving to next priority

### 6. Human as Tool Strategy
Invoke the user for input when:
- **Ambiguous requirements**: Ask 2-3 targeted clarifying questions
- **Unforeseen dependencies**: Surface and ask for prioritization
- **Architectural uncertainty**: Present options with trade-offs, get user preference
- **Completion checkpoint**: Summarize what was done, confirm next steps

Do NOT attempt to solve every problem autonomously. Human judgment is a specialized tool.

## Governance

### Amendment Procedure
1. Propose change with rationale and impact analysis
2. Update constitution.md with new version number (semantic versioning)
3. Propagate changes to dependent templates (spec, plan, tasks)
4. Create ADR if the amendment itself is architecturally significant
5. Commit with message: `docs: amend constitution to vX.Y.Z (<brief description>)`

### Versioning Policy
- **MAJOR**: Backward-incompatible principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance and Review
- All PRs and reviews MUST verify compliance with constitution principles
- Constitution supersedes default practices, AI suggestions, and "common" patterns
- Complexity and deviations MUST be justified in plan.md "Complexity Tracking" section
- Use `.specify/memory/constitution.md` as the authoritative governance document

### Runtime Guidance
- See `CLAUDE.md` for agent-specific development guidance
- See `.specify/templates/` for spec, plan, tasks, PHR, ADR templates
- See `.specify/scripts/bash/` for automation scripts (PHR creation, etc.)

**Version**: 1.0.0 | **Ratified**: 2025-12-05 | **Last Amended**: 2025-12-05
