---
id: 0001
title: Docusaurus frontend structure spec
stage: spec
date: 2025-12-05
surface: agent
model: claude-sonnet-4-5
feature: 001-docusaurus-frontend
branch: 001-docusaurus-frontend
user: Muhammad Qasim
command: /sp.specify
labels: ["spec", "docusaurus", "frontend", "textbook-structure", "ui-preparation"]
links:
  spec: specs/001-docusaurus-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-docusaurus-frontend/spec.md
  - specs/001-docusaurus-frontend/checklists/requirements.md
tests:
  - N/A (specification phase, no tests yet)
---

## Prompt

Create a feature specification for the Docusaurus FRONTEND STRUCTURE ONLY for the "Physical AI & Humanoid Robotics Textbook" project.

Scope of this feature:
- Set up a Docusaurus site (TypeScript, classic preset) for the textbook.
- Implement the overall docs structure, routing, nav, and layout, but only light placeholder content.
- No backend wiring yet (no real FastAPI, Qdrant, Neon, or Better-Auth integration in this feature).

High-level goals:
- Provide a clear, navigable textbook structure for the course:
  - Intro to Physical AI & Humanoid Robotics.
  - 4 main modules:
    1) ROS 2 (Robotic Nervous System)
    2) Digital Twin (Gazebo & Unity)
    3) NVIDIA Isaac (AI-Robot Brain)
    4) Vision-Language-Action (VLA)
- Make it easy for students to follow the quarter/weekly breakdown and modules.
- Prepare the UI surfaces where future features (RAG chatbot, personalization, Urdu translation) will plug in.

Functional requirements:

1) Docusaurus Site Setup
- Use the Docusaurus classic template with TypeScript.
- Configure basic theme, favicon, site title, and tagline for: "Physical AI & Humanoid Robotics Textbook".
- Site credits "Authored by Muhammad Qasim" prominently.

2) Docs Tree & Routing
- Create /docs/intro as the main course introduction, reachable via a big CTA.
- Create four module sections, each with at least:
  - An overview page.
  - A "Chapter 1" page as a starting point.
- Proposed structure (can be refined later):
  - docs/
    - intro.md
    - module-1-ros2/
      - overview.md
      - chapter-1-basics.md
    - module-2-digital-twin-gazebo-unity/
      - overview.md
      - chapter-1-simulation-basics.md
    - module-3-nvidia-isaac/
      - overview.md
      - chapter-1-getting-started.md
    - module-4-vision-language-action/
      - overview.md
      - chapter-1-vla-intro.md
- Ensure clean, readable slugs (e.g. /docs/module-1-ros2/overview).

3) Sidebar & Navigation
- Group docs in the sidebar by module with clear labels:
  - "Intro"
  - "Module 1 – ROS 2: Robotic Nervous System"
  - "Module 2 – Digital Twin (Gazebo & Unity)"
  - "Module 3 – NVIDIA Isaac (AI-Robot Brain)"
  - "Module 4 – Vision-Language-Action (VLA)"
- Hide or remove the blog from the navbar by default (unless explicitly enabled later).
- Navbar includes:
  - "Course" (docs)
  - Maybe a placeholder "RAG Chat" or "Study Assistant" link that will later open the chatbot page.

4) Homepage Design
- Hero section with:
  - Title: "Physical AI & Humanoid Robotics"
  - Subtitle about embodied intelligence and AI in the physical world.
  - Primary button: "Start the Course" linking to /docs/intro.
- Feature cards highlighting:
  - Physical AI & embodied intelligence.
  - Sim-to-real robotics and digital twins.
  - Integrated AI tutor (RAG chatbot).
  - Adaptive learning (beginner / intermediate / advanced).
- Author section:
  - "Authored by Muhammad Qasim"
  - Links to GitHub (https://github.com/Psqasim), LinkedIn, and other key profiles.
- Footer:
  - Copyright with your name.
  - GitHub repo link (to be filled once repo is on GitHub).
  - Social links (GitHub, LinkedIn, Twitter/X, email).

5) Per-Chapter UI Hooks for Personalization & Urdu
- At the top of each chapter page, include a dedicated UI area with two buttons:
  - "Personalize for Me" (to adapt difficulty/content later).
  - "View in Urdu" (to switch to Urdu translation later).
- For THIS feature, these buttons can:
  - Either be static/stubbed, or
  - Show a simple placeholder message like "Personalization coming soon".
- Ensure the UI is implemented via reusable React components so we can later connect them to the backend and Better-Auth.

6) RAG Chat UI & Selection-Based Q&A Hooks
- Provide frontend-only UI components for:
  - A floating or docked "Ask the Textbook" button that opens a chat panel.
  - A selection-based Q&A trigger:
    - When the user selects text in a doc, show a small "Ask about this" tooltip/button.
- For this feature, they do NOT call any backend:
  - They can log to console or show placeholder text ("Chatbot backend not connected yet").
- Ensure:
  - Clear visual distinction between "Ask about whole chapter/book" vs "Ask about selected text".
  - Good UX on desktop and mobile.

7) Content Level & Placeholders
- Only add light, representative content for each page:
  - Short paragraph explaining the purpose of the module or chapter.
  - Do NOT attempt to fully write the textbook here; that will be a separate feature/spec per module later.
- Assume "Intermediate" difficulty as the baseline content level for now.

8) Non-Functional Requirements
- Clean, readable code using TypeScript where applicable.
- Keep dependencies minimal; avoid adding heavy UI libraries without a clear reason.
- Ensure the site builds with `npm/yarn/pnpm` and can be deployed to GitHub Pages later.
- Follow the project constitution:
  - Structure-before-content,
  - Clear separation of concerns,
  - No backend details in this feature.

Success criteria:
- Docusaurus site builds and runs locally.
- /docs/intro and each module overview + chapter 1 are accessible from the sidebar.
- Homepage shows hero, features, author section, and "Start the Course" CTA.
- Blog link is hidden from navbar.
- Each chapter has visible "Personalize for Me" and "View in Urdu" buttons (stubbed).
- An "Ask the Textbook" entry point exists, plus visible UI reaction to text selection, even if the backend calls are mocked.

Keep this spec focused on WHAT and WHY for the frontend structure. We will define the technical implementation details (HOW) later in a separate /sp.plan step.

## Response snapshot

Successfully created comprehensive feature specification for Docusaurus Frontend Structure (branch: 001-docusaurus-frontend).

**Four User Stories Defined (P1-P4)**:

1. **Navigate Course Structure (P1)** - Core textbook navigation with sidebar, 4 modules, clean URLs. MVP foundation.
2. **Discover Course Value (P2)** - Homepage with hero, feature cards, author attribution, social links. Entry point for new users.
3. **Access Future Personalization Features (P3)** - Per-chapter "Personalize for Me" and "View in Urdu" buttons (stubbed, reusable components).
4. **Interact with AI Tutor (Preparation) (P4)** - "Ask the Textbook" button, text selection detection, chat panel placeholder (no backend).

**42 Functional Requirements (FR-001 to FR-042)** organized into 8 categories:
- Site Setup & Configuration (FR-001 to FR-005)
- Documentation Structure & Routing (FR-006 to FR-010)
- Navigation & Sidebar (FR-011 to FR-014)
- Homepage Design (FR-015 to FR-018)
- Per-Chapter UI Hooks (FR-019 to FR-023)
- RAG Chat UI Frontend-Only (FR-024 to FR-032)
- Content & Placeholders (FR-033 to FR-035)
- Build & Deployment Readiness (FR-036 to FR-039)
- Responsive Design (FR-040 to FR-042)

**12 Success Criteria (SC-001 to SC-012)** - All measurable and technology-agnostic:
- Build success, navigation efficiency (3 clicks, 30 seconds)
- Load time (under 3 seconds), responsiveness (down to 375px)
- 100% module coverage, author attribution visibility
- Clean URLs, deployment readiness, no Blog link

**Key Entities**: Module, Chapter, Page, Navigation Item, Author Profile, Feature Card

**10 Assumptions** documented: Node.js v18+, Docusaurus v3.x, modern browsers, GitHub Pages deployment, placeholder content acceptable

**8 Constraints** defined: No backend dependencies, TypeScript required, Docusaurus classic template, structure-before-content, separation of concerns, no blog, minimal dependencies, clean URLs

**6 Edge Cases** identified: 404 handling, mobile/small screens, JS disabled, placeholder clicks, refresh behavior, incomplete social links

**Validation**: Specification quality checklist created at `specs/001-docusaurus-frontend/checklists/requirements.md`
- ✅ ALL checklist items passed
- Zero [NEEDS CLARIFICATION] markers (all decisions made based on detailed user input)
- All requirements testable and unambiguous
- Success criteria measurable and technology-agnostic
- No implementation details in spec (maintains WHAT/WHY vs HOW separation)

**Spec File**: `specs/001-docusaurus-frontend/spec.md` (247 lines)

## Outcome

- ✅ Impact: Comprehensive feature specification created defining the entire Docusaurus frontend structure for the Physical AI & Humanoid Robotics Textbook. Spec covers navigation, homepage, personalization/translation UI hooks, RAG chatbot UI preparation, and responsive design. Ready for `/sp.plan` phase.
- 🧪 Tests: N/A (specification phase, no code tests yet)
- 📁 Files: Created specs/001-docusaurus-frontend/spec.md (247 lines), specs/001-docusaurus-frontend/checklists/requirements.md (validation checklist)
- 🔁 Next prompts: `/sp.plan` to define technical implementation approach (Docusaurus configuration, React component architecture, sidebar config, text selection detection, mobile responsiveness strategy)
- 🧠 Reflection: Specification is comprehensive, well-structured, and constitution-compliant. All functional requirements are testable. Success criteria are measurable and technology-agnostic. Zero clarification markers needed due to detailed user input. User stories are independently testable with clear priorities (P1-P4). Edge cases, assumptions, and constraints thoroughly documented. Validation checklist confirms spec readiness for planning phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - detailed user input eliminated ambiguity; no clarifications needed
- Graders run and results (PASS/FAIL): Specification Quality Checklist PASS (all items complete, zero unresolved markers)
- Prompt variant (if applicable): N/A (first spec for this feature)
- Next experiment (smallest change to try): During `/sp.plan`, validate that reusable React component architecture for personalization buttons and chat UI aligns with Docusaurus plugin/theme customization best practices
