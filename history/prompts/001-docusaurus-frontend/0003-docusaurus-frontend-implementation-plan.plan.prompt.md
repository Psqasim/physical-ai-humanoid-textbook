---
id: 0003
title: Docusaurus frontend implementation plan
stage: plan
date: 2025-12-05
surface: agent
model: claude-sonnet-4-5
feature: 001-docusaurus-frontend
branch: 001-docusaurus-frontend
user: Muhammad Qasim
command: /sp.plan
labels: ["plan", "architecture", "docusaurus", "react-components", "typescript", "frontend-only"]
links:
  spec: specs/001-docusaurus-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-docusaurus-frontend/plan.md
tests:
  - N/A (planning phase, no tests yet)
---

## Prompt

Create a detailed technical implementation plan for the feature "001-docusaurus-frontend" (Docusaurus Frontend Structure).

Instructions:
- Read specs/001-docusaurus-frontend/spec.md completely.
- Create specs/001-docusaurus-frontend/plan.md with HOW to implement (technical design, not code).
- This plan is FRONTEND ONLY - no backend implementation (no FastAPI, Qdrant, Neon, Better-Auth).
- Docusaurus site will be at the REPO ROOT (not in a frontend/ subdirectory).
- Use npm as the package manager.

The plan must include these sections:

1. **Project Layout & Tooling**
   - Confirm Docusaurus v3 at repo root
   - npm scripts for dev, build, serve, deploy
   - TypeScript configuration strategy

2. **Docusaurus Configuration**
   - docusaurus.config.ts structure
   - Theme configuration (title, tagline, favicon, colors)
   - Navbar setup (Course link, RAG Chat placeholder, no Blog)
   - Footer configuration (author attribution, social links)

3. **Docs Structure & MDX Strategy**
   - /docs directory organization (intro + 4 modules)
   - sidebars.ts configuration
   - MDX usage for embedding React components (ChapterActionsBar, etc.)
   - URL slug design

4. **Reusable UI Components**
   - ChapterActionsBar component (Personalize for Me, View in Urdu buttons with inline alert/banner)
   - Component file structure and naming
   - Styling approach (CSS Modules vs global CSS)
   - TypeScript interfaces for component props

5. **Selection-Based Q&A: Frontend Hooks**
   - AskTheTextbookButton component (fixed bottom-right desktop, slide-up mobile)
   - ChatPanelPlaceholder component (shows "backend not connected")
   - TextSelectionTooltip component (10-character minimum trigger)
   - Text selection detection logic (window.getSelection() API)
   - State management for tooltip positioning and chat panel visibility

6. **Homepage Design Implementation**
   - src/pages/index.tsx structure
   - Hero section layout
   - Feature cards section
   - Author section with social links
   - Responsive layout strategy

7. **Responsive Design Strategy**
   - Breakpoints (mobile, tablet, desktop)
   - Sidebar collapse behavior
   - Mobile chat panel slide-up design
   - Touch-friendly button sizing

8. **Build & Deployment Preparation**
   - GitHub Pages configuration
   - Base URL and deployment settings
   - Static asset optimization
   - Build validation checklist

For each section, provide:
- Technical decisions with rationale
- File/directory structure
- Configuration examples (not full code, but clear structure)
- Integration points for future backend
- Risks and mitigation strategies

Keep the plan focused on ARCHITECTURE and DESIGN DECISIONS (HOW), not implementation code. The plan should enable a developer to implement the feature without ambiguity.

## Response snapshot

**Technical Implementation Plan Created Successfully**

Generated comprehensive 856-line plan at `specs/001-docusaurus-frontend/plan.md` covering all 8 required sections plus additional research phase.

**Key Architectural Decisions:**

1. **Project Structure**: Docusaurus v3.x at repo root (not subdirectory), npm for package management, TypeScript 5.x strict mode

2. **Phase 0 - Research**: Identified 5 key areas requiring pre-implementation research:
   - Text selection best practices (examine Docusaurus/React doc sites for patterns)
   - Responsive chat widget patterns (study Intercom, Zendesk implementations)
   - Alert/banner patterns (research GitHub, GitLab inline notification UX)
   - Mobile navigation (analyze Docusaurus mobile docs, Material-UI patterns)
   - GitHub Pages deployment (validate Docusaurus v3 deployment guides)

3. **Component Architecture** (4 main components):
   - **ChapterActionsBar**: Two buttons with inline alert/banner, auto-dismiss after 5s, CSS Modules styling
   - **AskTheTextbookButton**: Fixed positioning (desktop: bottom-right 24px, mobile: slide-up), z-index 1000
   - **ChatPanelPlaceholder**: Desktop width 400px, mobile full-width slide-up, visual mode distinction (whole-book vs selection-based)
   - **TextSelectionTooltip**: React Portal rendering, 10-char minimum trigger, positioned 10px above selection

4. **Text Selection Detection**: Implemented in `src/theme/Root.tsx` global wrapper using `window.getSelection()` API with algorithm:
   ```
   selection = window.getSelection()
   selectedText = selection.toString().trim()
   if length >= 10:
     calculate position from range.getBoundingClientRect()
     show tooltip at (x: center, y: top - 10px)
   ```

5. **Styling Strategy**: CSS Modules for component scoping, global styles in `src/css/custom.css`, responsive breakpoints at 768px (mobile) and 1024px (tablet)

6. **Docusaurus Configuration**:
   - Disabled blog preset (per FR-012)
   - Custom navbar with "Course" and "RAG Chat" placeholder links
   - Footer with author attribution and social links (GitHub, LinkedIn)
   - TypeScript path aliases (`@site/*`)

7. **MDX Strategy**:
   - All chapter pages use `.mdx` extension
   - Import and embed `<ChapterActionsBar />` at top of each chapter
   - Preserve markdown readability while enabling React interactivity

8. **Homepage Layout**:
   - Hero section with CTA button
   - 4 feature cards (Physical AI, Sim-to-Real, AI Tutor, Adaptive Learning)
   - Author section with profile links
   - Footer with copyright and social links

9. **Responsive Design**:
   - Mobile-first approach
   - Sidebar collapses to hamburger menu < 768px
   - Chat button transforms to slide-up panel on mobile
   - Touch targets minimum 44px × 44px

10. **Risk Mitigation**:
    - Text selection conflicts with native browser behavior → Use CSS `user-select` sparingly
    - Mobile chat obscuring content → Implement overlay with close control
    - Alert banner layout shift → Reserve fixed height space
    - TypeScript errors blocking build → Incremental strict mode adoption

**Incremental Implementation Order** (12 phases):
1. Initialize Docusaurus + TypeScript
2. Configure base settings
3. Create docs structure
4. Configure sidebar
5. Build homepage (hero → features → author → footer)
6. Create ChapterActionsBar
7. Create AskTheTextbookButton
8. Create ChatPanelPlaceholder
9. Implement text selection detection
10. Create TextSelectionTooltip
11. Responsive design polish
12. Build validation + deployment config

**Constitution Compliance**: All 7 principles validated (Assignment alignment, Structure-before-content, SDD workflow, Separation of concerns, TypeScript quality, No backend wiring, Clear integration points)

**Next Step**: `/sp.tasks` to break down plan into concrete, testable tasks with acceptance criteria

## Outcome

- ✅ Impact: Comprehensive technical plan created defining complete frontend architecture for Docusaurus textbook site. Plan covers project structure, component design, text selection detection, responsive strategy, and deployment. All 8 requested sections completed plus Phase 0 research recommendations. Ready for task generation phase.
- 🧪 Tests: N/A (planning phase, no tests yet)
- 📁 Files: Created specs/001-docusaurus-frontend/plan.md (856 lines with detailed component interfaces, configuration examples, algorithms, and risk analysis)
- 🔁 Next prompts: `/sp.tasks` to generate concrete task list with acceptance criteria from plan.md; `/sp.adr` if any significant architectural decisions warrant documentation (candidates: text selection detection approach, component styling strategy, mobile chat UX pattern)
- 🧠 Reflection: Plan successfully bridges spec (WHAT/WHY) to implementation (HOW) without becoming implementation code. Phase 0 research section ensures evidence-based decisions before coding. Component interfaces provide clear contracts for future backend integration. Incremental implementation order reduces risk by building foundation before complex interactions. All constitution principles validated. Plan enables unambiguous implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - spec was comprehensive after clarification pass, enabling clean planning without ambiguity
- Graders run and results (PASS/FAIL): Manual validation PASS - all 8 requested sections complete, constitution compliance verified, no implementation code leaked into plan, clear separation of frontend/backend concerns
- Prompt variant (if applicable): N/A (first planning session for this feature)
- Next experiment (smallest change to try): During `/sp.tasks`, validate that text selection detection tasks include acceptance criteria for edge cases (e.g., selection across multiple paragraphs, selection including code blocks, mobile touch selection behavior)
