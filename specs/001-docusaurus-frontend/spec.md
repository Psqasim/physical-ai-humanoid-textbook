# Feature Specification: Docusaurus Frontend Structure

**Feature Branch**: `001-docusaurus-frontend`
**Created**: 2025-12-05
**Status**: Draft
**Input**: User description: "Create a feature specification for the Docusaurus FRONTEND STRUCTURE ONLY for the Physical AI & Humanoid Robotics Textbook project. Scope of this feature: Set up a Docusaurus site (TypeScript, classic preset) for the textbook. Implement the overall docs structure, routing, nav, and layout, but only light placeholder content. No backend wiring yet (no real FastAPI, Qdrant, Neon, or Better-Auth integration in this feature)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate Course Structure (Priority: P1)

As a student learning Physical AI and Humanoid Robotics, I want to access a well-organized textbook with clear navigation so I can find and study course materials in a logical sequence.

**Why this priority**: Without a navigable structure, the textbook is unusable. This is the foundation that all other features depend on.

**Independent Test**: Can be fully tested by visiting the site homepage, clicking "Start the Course", and navigating through all four modules via the sidebar. Success is achieved when all module overviews and chapter 1 pages load correctly.

**Acceptance Scenarios**:

1. **Given** I am on the homepage, **When** I click "Start the Course", **Then** I am taken to /docs/intro
2. **Given** I am on /docs/intro, **When** I open the sidebar, **Then** I see four clearly labeled modules: ROS 2, Digital Twin, NVIDIA Isaac, and Vision-Language-Action
3. **Given** I am in the sidebar, **When** I click on any module, **Then** I see the module overview and chapter 1 as navigation options
4. **Given** I am on any documentation page, **When** I navigate using the sidebar, **Then** the URL updates to reflect the current page location
5. **Given** I am on any docs page, **When** I look at the navbar, **Then** I see "Course" link but NOT a "Blog" link

---

### User Story 2 - Discover Course Value (Priority: P2)

As a prospective student, I want to learn what the course offers and who created it so I can decide if it's right for me.

**Why this priority**: The homepage is the entry point for new users. It must communicate value and credibility before users commit to studying.

**Independent Test**: Can be tested by visiting the homepage and verifying that the hero section, feature cards, and author information are clearly visible and compelling.

**Acceptance Scenarios**:

1. **Given** I visit the homepage, **When** the page loads, **Then** I see a hero section with "Physical AI & Humanoid Robotics" title and subtitle about embodied intelligence
2. **Given** I am on the homepage, **When** I scroll to the features section, **Then** I see cards highlighting: Physical AI concepts, sim-to-real robotics, integrated AI tutor, and adaptive learning
3. **Given** I am on the homepage, **When** I scroll to the author section, **Then** I see "Authored by Muhammad Qasim" with links to GitHub (https://github.com/Psqasim), LinkedIn, and other profiles
4. **Given** I am on the homepage, **When** I scroll to the footer, **Then** I see copyright with author name, GitHub repo link, and social media links

---

### User Story 3 - Access Future Personalization Features (Priority: P3)

As a student, I want to see where personalization and translation features will be available so I know these options exist and can use them when they're ready.

**Why this priority**: This is preparatory UI work for future features. It doesn't block learning but ensures the UI surface is ready for backend integration.

**Independent Test**: Can be tested by visiting any chapter page (e.g., /docs/module-1-ros2/chapter-1-basics) and verifying that "Personalize for Me" and "View in Urdu" buttons are visible at the top of the chapter.

**Acceptance Scenarios**:

1. **Given** I am on any chapter page, **When** the page loads, **Then** I see two buttons at the top: "Personalize for Me" and "View in Urdu"
2. **Given** I am on a chapter page, **When** I click "Personalize for Me", **Then** I see an inline alert/banner below the buttons with message "Personalization coming soon"
3. **Given** I am on a chapter page, **When** I click "View in Urdu", **Then** I see an inline alert/banner below the buttons with message "Urdu translation coming soon"
4. **Given** I am viewing these buttons on mobile, **When** the screen size is small, **Then** the buttons remain visible and usable

---

### User Story 4 - Interact with AI Tutor (Preparation) (Priority: P4)

As a student, I want to access the AI tutor chatbot interface and understand how selection-based Q&A will work so I can get help with course content when the backend is ready.

**Why this priority**: This prepares the UI for the RAG chatbot feature but doesn't block core learning functionality. Students can still study without the chatbot.

**Independent Test**: Can be tested by visiting any docs page and verifying that: (1) an "Ask the Textbook" button is visible, (2) when text is selected, a "Ask about this" tooltip appears, (3) clicking either shows a placeholder response.

**Acceptance Scenarios**:

1. **Given** I am on any docs page, **When** the page loads, **Then** I see a floating or docked "Ask the Textbook" button
2. **Given** I am on a docs page, **When** I click "Ask the Textbook", **Then** a chat panel opens with a placeholder message like "Chatbot backend not connected yet"
3. **Given** I am reading a docs page, **When** I select text, **Then** a small "Ask about this" tooltip or button appears near the selection
4. **Given** the "Ask about this" button is visible, **When** I click it, **Then** the chat panel opens with an indication that this is "selection-based Q&A" and shows a placeholder message
5. **Given** the chat panel is open, **When** I look at the UI, **Then** I can clearly distinguish between "whole-book" mode and "selection-based" mode
6. **Given** I am using the chat UI on mobile, **When** the screen is small, **Then** the chat panel is usable and doesn't obscure content

---

## Clarifications

### Session 2025-12-05

- Q: When users click the "Personalize for Me" or "View in Urdu" buttons (FR-021, FR-022), should the placeholder feedback be console log only, inline alert/banner, modal/popup, or toast notification? → A: Display inline alert/banner below the buttons with message "Feature coming soon"
- Q: For the "Ask the Textbook" button (FR-024), what positioning strategy should be used? → A: Fixed bottom-right corner (desktop), slide-up from bottom (mobile)
- Q: For text selection detection (FR-027, FR-028), what minimum selection length should trigger the "Ask about this" tooltip? → A: 10 characters minimum

### Edge Cases

- What happens when a user tries to navigate to a non-existent route (e.g., /docs/module-5)? → Should show Docusaurus's default 404 page
- What happens when the user is on mobile with a very small screen? → Sidebar should collapse into a hamburger menu, all buttons should remain usable
- What happens when the user has JavaScript disabled? → Core content should still be readable (static site generation ensures this)
- What happens when a user tries to click the placeholder chatbot buttons? → Should show a clear message that the feature is coming soon (logged to console or displayed in UI)
- What happens when the user refreshes a docs page? → Should remain on the same page (clean URLs and proper routing)
- What happens when the user clicks social links in the footer before the repo is on GitHub? → Links should either point to correct profiles or be clearly marked as "Coming Soon"

## Requirements *(mandatory)*

### Functional Requirements

**Site Setup & Configuration**

- **FR-001**: System MUST initialize a Docusaurus site using the classic template with TypeScript support
- **FR-002**: System MUST display site title as "Physical AI & Humanoid Robotics Textbook"
- **FR-003**: System MUST display site tagline related to embodied intelligence and AI in the physical world
- **FR-004**: System MUST prominently credit "Muhammad Qasim" as the author on the homepage
- **FR-005**: System MUST configure a favicon for the site

**Documentation Structure & Routing**

- **FR-006**: System MUST create /docs/intro as the main course introduction page
- **FR-007**: System MUST create four module directories under /docs:
  - module-1-ros2
  - module-2-digital-twin-gazebo-unity
  - module-3-nvidia-isaac
  - module-4-vision-language-action
- **FR-008**: Each module directory MUST contain at least two pages: overview.md and chapter-1-[topic].md
- **FR-009**: System MUST generate clean, readable URL slugs for all pages (e.g., /docs/module-1-ros2/overview, not /docs/module_1/page1)
- **FR-010**: All module pages MUST be reachable from the sidebar navigation

**Navigation & Sidebar**

- **FR-011**: System MUST display sidebar grouped by module with clear labels:
  - "Intro"
  - "Module 1 – ROS 2: Robotic Nervous System"
  - "Module 2 – Digital Twin (Gazebo & Unity)"
  - "Module 3 – NVIDIA Isaac (AI-Robot Brain)"
  - "Module 4 – Vision-Language-Action (VLA)"
- **FR-012**: System MUST hide or remove the "Blog" link from the navbar
- **FR-013**: System MUST display "Course" link in the navbar that leads to /docs/intro
- **FR-014**: System MUST display a placeholder link for "RAG Chat" or "Study Assistant" in the navbar (can be non-functional or point to a coming-soon page)

**Homepage Design**

- **FR-015**: Homepage MUST include a hero section with:
  - Title: "Physical AI & Humanoid Robotics"
  - Subtitle explaining embodied intelligence and AI in the physical world
  - Primary call-to-action button labeled "Start the Course" linking to /docs/intro
- **FR-016**: Homepage MUST include feature cards section highlighting:
  - Physical AI & embodied intelligence
  - Sim-to-real robotics and digital twins
  - Integrated AI tutor (RAG chatbot)
  - Adaptive learning (beginner/intermediate/advanced)
- **FR-017**: Homepage MUST include author section with:
  - "Authored by Muhammad Qasim"
  - Clickable links to GitHub (https://github.com/Psqasim), LinkedIn, and other key profiles
- **FR-018**: Homepage MUST include footer with:
  - Copyright notice with author name
  - GitHub repository link (placeholder acceptable if repo not yet public)
  - Social media links (GitHub, LinkedIn, Twitter/X, email)

**Per-Chapter UI Hooks (Personalization & Translation)**

- **FR-019**: Each chapter page MUST display two buttons at the top:
  - "Personalize for Me"
  - "View in Urdu"
- **FR-020**: These buttons MUST be implemented as reusable React components (not hardcoded in each page)
- **FR-021**: Clicking "Personalize for Me" button MUST display an inline alert/banner below the buttons with the message "Personalization coming soon"
- **FR-022**: Clicking "View in Urdu" button MUST display an inline alert/banner below the buttons with the message "Urdu translation coming soon"
- **FR-023**: Both buttons MUST be visible and usable on mobile devices

**RAG Chat UI (Frontend-Only, No Backend)**

- **FR-024**: System MUST display "Ask the Textbook" button visible on all docs pages, positioned in fixed bottom-right corner on desktop and as a slide-up element from bottom on mobile
- **FR-025**: Clicking "Ask the Textbook" button MUST open a chat panel (embedded, not a popup or new window)
- **FR-026**: Chat panel MUST display a placeholder message indicating the backend is not yet connected (e.g., "Chatbot backend not connected yet")
- **FR-027**: System MUST detect when user selects text on a docs page (minimum 10 characters)
- **FR-028**: When text is selected (minimum 10 characters), system MUST display a small "Ask about this" tooltip or button near the selection
- **FR-029**: Clicking "Ask about this" MUST open the chat panel with a clear indication that this is "selection-based Q&A" mode
- **FR-030**: Chat panel UI MUST visually distinguish between:
  - "Whole-book" context mode (questions about the entire textbook)
  - "Selection-based" context mode (questions about selected text only)
- **FR-031**: Chat panel MUST be usable on both desktop and mobile devices, with mobile implementation using slide-up panel from bottom of screen
- **FR-032**: Chat panel on mobile MUST include close/minimize control and not permanently obscure page content

**Content & Placeholders**

- **FR-033**: Each page (intro, module overviews, chapter 1s) MUST contain light placeholder content:
  - A short paragraph (2-4 sentences) explaining the purpose of the module or chapter
  - No attempt to fully write textbook content (that is a separate feature)
- **FR-034**: Placeholder content MUST assume "Intermediate" difficulty level as the baseline
- **FR-035**: Placeholder content MUST be professional, accurate, and free of typos or grammatical errors

**Build & Deployment Readiness**

- **FR-036**: System MUST successfully build using a standard Node.js package manager (npm, yarn, or pnpm)
- **FR-037**: System MUST be deployable to GitHub Pages or similar static hosting without additional configuration
- **FR-038**: System MUST minimize dependencies and avoid adding heavy UI libraries without clear justification
- **FR-039**: All custom React components MUST use TypeScript where applicable

**Responsive Design**

- **FR-040**: Site MUST be fully responsive and usable on desktop, tablet, and mobile devices
- **FR-041**: Sidebar MUST collapse into a hamburger menu on mobile devices
- **FR-042**: All interactive elements (buttons, links, chat panel) MUST be accessible via keyboard navigation

### Key Entities *(include if feature involves data)*

- **Module**: Represents a major section of the course (e.g., ROS 2, Digital Twin, NVIDIA Isaac, VLA). Attributes: title, short description, order/sequence, directory path.
- **Chapter**: Represents a lesson within a module. Attributes: title, module reference, order/sequence, content (markdown), difficulty level (placeholder: "intermediate").
- **Page**: Generic documentation page. Attributes: title, route/slug, content (markdown), parent (module or intro).
- **Navigation Item**: Represents a link in the sidebar or navbar. Attributes: label, route, icon (optional), group/category (module).
- **Author Profile**: Information about the course author. Attributes: name ("Muhammad Qasim"), GitHub URL, LinkedIn URL, other social links, bio/description.
- **Feature Card**: Highlighting key course features on the homepage. Attributes: title, description, icon (optional), order.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Site successfully builds and runs locally using `npm start` or equivalent command with zero build errors
- **SC-002**: All primary navigation paths (Homepage → Intro → All four module overviews → All four chapter 1 pages) are accessible within 3 clicks
- **SC-003**: Students can navigate from the homepage to any chapter 1 page in under 30 seconds
- **SC-004**: Homepage loads in under 3 seconds on a standard broadband connection
- **SC-005**: All interactive UI elements (buttons, links, sidebar, chat panel placeholder) are visible and respond to user actions within 1 second
- **SC-006**: Site is fully navigable on mobile devices with screen widths down to 375px (iPhone SE size)
- **SC-007**: 100% of the 4 modules have an overview page and a chapter 1 page accessible via the sidebar
- **SC-008**: Author attribution ("Muhammad Qasim") is visible on the homepage within the first screen (above the fold)
- **SC-009**: "Blog" link is NOT visible in the navbar (confirms successful removal)
- **SC-010**: Placeholder UI elements for chatbot and personalization are visible on appropriate pages and respond to clicks (even if with placeholder messages)
- **SC-011**: Site generates clean URLs without special characters or unclear abbreviations (human-readable slugs)
- **SC-012**: Site is deployable to a static hosting service (GitHub Pages) without manual file edits or additional build steps

## Assumptions

1. **Node.js and Package Manager**: Assumes Node.js (v18 or later) and npm/yarn/pnpm are available in the development environment
2. **Docusaurus Version**: Assumes use of Docusaurus v3.x (latest stable) unless otherwise specified
3. **Placeholder Content Quality**: Light placeholder content is acceptable; full textbook content will be written in separate features per module
4. **No Backend Integration**: This feature explicitly excludes any backend API calls, database connections, or authentication flows
5. **Social Links**: Assumes GitHub URL (https://github.com/Psqasim) and LinkedIn are already active; if not, placeholders are acceptable
6. **Repository Hosting**: Assumes the project will eventually be hosted on GitHub, so GitHub Pages is the target deployment platform
7. **Browser Support**: Assumes modern evergreen browsers (Chrome, Firefox, Safari, Edge) with JavaScript enabled
8. **Favicon**: Assumes a simple favicon (can be a placeholder or default Docusaurus icon) is sufficient for this phase
9. **Chat Panel Styling**: Assumes a simple, clean design for the chat panel placeholder; detailed design specifications will come from a future design/plan phase
10. **Text Selection Detection**: Assumes standard browser APIs for text selection (window.getSelection()) are sufficient; no special libraries required unless justified

## Constraints

1. **No Backend Dependencies**: This feature MUST NOT include FastAPI, Qdrant, Neon, Better-Auth, or any backend service calls
2. **TypeScript Requirement**: All custom React components MUST be written in TypeScript, not plain JavaScript
3. **Docusaurus Classic Template**: MUST use the Docusaurus classic template as the base (no custom templates or alternative frameworks)
4. **Structure-Before-Content**: Per constitution, structure MUST be approved by user before writing full content (this spec defines structure; content is minimal placeholders)
5. **Separation of Concerns**: Personalization buttons, chat UI, and other reusable elements MUST be separate React components, not inline code
6. **No Blog**: Blog feature MUST be hidden or removed from the navbar unless explicitly requested by the user in a future feature
7. **Minimal Dependencies**: MUST avoid adding heavy UI libraries (e.g., Material-UI, Ant Design) without clear justification; prefer Docusaurus built-in components and simple custom CSS
8. **Clean URLs**: All routes MUST use clean, human-readable slugs (no underscores, no query parameters, no file extensions in URLs)

## Open Questions

All critical ambiguities resolved via `/sp.clarify` session on 2025-12-05. See Clarifications section for details. Remaining implementation details (e.g., exact CSS styling, animation timings) can be determined during `/sp.plan` phase.
