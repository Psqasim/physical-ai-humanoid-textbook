# Implementation Plan: Docusaurus Frontend Structure

**Branch**: `001-docusaurus-frontend` | **Date**: 2025-12-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-docusaurus-frontend/spec.md`

## Summary

Implement a Docusaurus-based frontend for the Physical AI & Humanoid Robotics Textbook. The site will provide a navigable 4-module course structure with homepage, documentation pages, and UI hooks for future personalization and RAG chatbot features. This is a frontend-only feature with no backend integration; all interactive elements display placeholder messages.

**Primary requirement**: Create a TypeScript-based Docusaurus (v3.x) classic site with intro + 4 modules (ROS 2, Digital Twin, NVIDIA Isaac, VLA), custom React components for personalization buttons and chat UI placeholders, text selection detection (10-char minimum), and mobile-responsive design.

**Technical approach**: Use Docusaurus at repo root with TypeScript, MDX for pages needing React components, custom components in `src/components/`, CSS modules for styling, and window.getSelection() API for text selection detection. Frontend-only implementation with clear separation from future backend integration.

## Technical Context

**Language/Version**: TypeScript 5.x (via Docusaurus), Node.js 18+ LTS
**Primary Dependencies**:
- @docusaurus/core v3.x (latest stable)
- @docusaurus/preset-classic v3.x
- React 18.x (bundled with Docusaurus)
- @docusaurus/module-type-aliases (TypeScript support)
- clsx (conditional CSS classes)

**Storage**: N/A (static site, no database)
**Testing**: Manual testing and build verification (`npm run build` success = tests pass for this phase)
**Target Platform**: Static site generation (SSG) for GitHub Pages deployment, supports modern evergreen browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web (Docusaurus static site at repo root, future backend will be in separate `backend/` directory)
**Performance Goals**:
- Homepage load < 3 seconds on standard broadband
- Navigation actions complete < 1 second
- Build time < 2 minutes for current scope (minimal content)

**Constraints**:
- No backend API calls (frontend-only)
- Must work with JavaScript disabled (core content readable via SSG)
- Mobile responsive down to 375px width (iPhone SE)
- Minimal dependencies (avoid heavy UI libraries like Material-UI)
- TypeScript required for all custom components

**Scale/Scope**:
- 1 intro page + 4 modules × 2 pages (overview + chapter 1) = 9 docs pages total
- 3 custom React components (ChapterActionsBar, AskTheTextbookButton, ChatPanelPlaceholder)
- Homepage with hero, features, author section, footer
- Target: ~10-50 concurrent users during development, scalable to 1000+ via GitHub Pages CDN

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle II: Structure-Before-Content ✅
- **Requirement**: Design and review complete structure FIRST; get human approval; then write content
- **Compliance**: This plan defines the complete docs tree (intro + 4 modules with overview + chapter-1), sidebar structure, homepage layout, and component architecture. Content will be minimal placeholders (2-4 sentences per page). Structure is explicitly defined in Project Structure section below.
- **Status**: PASS - Structure fully planned; content intentionally minimal per spec

### Principle III: Spec-Driven Development ✅
- **Requirement**: Follow /sp.constitution → /sp.specify → /sp.clarify → /sp.plan → /sp.tasks → /sp.implement
- **Compliance**: Constitution created (v1.0.0), spec created with 42 FRs and 4 user stories, clarifications resolved (3 questions), now creating plan.md
- **Status**: PASS - Workflow followed correctly

### Principle VI: Code Quality, Examples, and UI/UX Standards ✅
- **Requirement**: TypeScript for frontend, clean/modern/responsive UI, professional branding (Muhammad Qasim attribution)
- **Compliance**: TypeScript enforced (tsconfig.json strict mode), Docusaurus classic theme provides clean base, custom components use TypeScript, responsive design required (FR-040 to FR-042), author attribution on homepage (FR-004, FR-017)
- **Status**: PASS - All requirements met

### Principle VII: Separation of Concerns and Small Changes ✅
- **Requirement**: Clear architecture boundaries, small commits, minimal testing for this phase
- **Compliance**: Frontend-only scope (no backend code), reusable React components (not inline), plan emphasizes incremental implementation, testing is build verification only
- **Status**: PASS - Frontend cleanly separated from future backend

### No Backend Dependencies ✅
- **Constraint**: MUST NOT include FastAPI, Qdrant, Neon, Better-Auth
- **Compliance**: Plan explicitly frontend-only; placeholder components show "backend not connected" messages; no API client code
- **Status**: PASS - No backend dependencies

### Minimal Dependencies ✅
- **Constraint**: Avoid heavy UI libraries without clear justification
- **Compliance**: Using only Docusaurus built-in components, clsx for conditional classes, no Material-UI/Ant Design/etc.
- **Status**: PASS - Minimal dependency set

**Gate Result**: ✅ **PASS** - All constitution checks satisfied, no violations to justify

## Project Structure

### Documentation (this feature)

```text
specs/001-docusaurus-frontend/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Docusaurus v3 best practices, text selection patterns
├── data-model.md        # Phase 1: UI state models for components
├── quickstart.md        # Phase 1: How to run, build, deploy the Docusaurus site
├── contracts/           # Phase 1: Component prop interfaces (TypeScript)
│   ├── ChapterActionsBar.interface.ts
│   ├── AskTheTextbookButton.interface.ts
│   └── ChatPanelPlaceholder.interface.ts
└── tasks.md             # Phase 2: Generated by /sp.tasks (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
/                                   # Repo root = Docusaurus root
├── package.json                    # npm scripts: start, build, serve, deploy
├── tsconfig.json                   # TypeScript configuration (strict mode)
├── docusaurus.config.ts            # Main Docusaurus config (site metadata, navbar, footer, theme)
├── sidebars.ts                     # Sidebar structure (intro + 4 modules grouped)
├── babel.config.js                 # Babel config (Docusaurus default)
├── .gitignore                      # Ignore node_modules, build, .docusaurus
│
├── docs/                           # Documentation content (MDX files)
│   ├── intro.md                    # Course introduction page
│   ├── module-1-ros2/
│   │   ├── overview.mdx            # Module 1 overview (uses ChapterActionsBar)
│   │   └── chapter-1-basics.mdx    # Chapter 1: ROS 2 Basics
│   ├── module-2-digital-twin-gazebo-unity/
│   │   ├── overview.mdx
│   │   └── chapter-1-simulation-basics.mdx
│   ├── module-3-nvidia-isaac/
│   │   ├── overview.mdx
│   │   └── chapter-1-getting-started.mdx
│   └── module-4-vision-language-action/
│       ├── overview.mdx
│       └── chapter-1-vla-intro.mdx
│
├── src/                            # Custom code (React components, CSS, theme overrides)
│   ├── components/                 # Custom React components
│   │   ├── learning/               # Learning-specific components
│   │   │   ├── ChapterActionsBar.tsx        # Personalization + Urdu buttons with inline alerts
│   │   │   └── ChapterActionsBar.module.css # Styles for ChapterActionsBar
│   │   └── chat/                   # Chat-related components
│   │       ├── AskTheTextbookButton.tsx      # Fixed bottom-right button (desktop), slide-up (mobile)
│   │       ├── AskTheTextbookButton.module.css
│   │       ├── ChatPanelPlaceholder.tsx      # Chat panel with mode indicators
│   │       ├── ChatPanelPlaceholder.module.css
│   │       ├── TextSelectionTooltip.tsx      # "Ask about this" tooltip (10-char min)
│   │       └── TextSelectionTooltip.module.css
│   │
│   ├── pages/                      # Custom pages (homepage)
│   │   └── index.tsx               # Homepage with hero, features, author, footer
│   │
│   ├── css/                        # Global styles
│   │   └── custom.css              # Custom CSS variables, overrides
│   │
│   └── theme/                      # Docusaurus theme customizations (if needed)
│       └── Root.tsx                # Global wrapper for text selection detection
│
└── static/                         # Static assets
    ├── img/                        # Images (favicon, logo, feature icons)
    │   └── favicon.ico             # Site favicon
    └── CNAME                       # GitHub Pages custom domain (if applicable)
```

**Structure Decision**: Using Docusaurus at repo root (not in a `frontend/` subdirectory) because this is the primary deliverable for this feature. Future backend will be added in a separate `backend/` directory. This aligns with Docusaurus best practices and simplifies initial development. The `src/components/` structure separates learning components (personalization) from chat components (RAG UI) for clarity and future maintainability.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - Constitution Check passed cleanly. No complexity justifications needed.

---

## Phase 0: Research & Technical Decisions

### Research Areas

1. **Docusaurus v3.x Best Practices**
   - **Question**: What are the current best practices for TypeScript + Docusaurus v3.x project setup?
   - **Decision**: Use Docusaurus v3.5.0+ (latest stable as of Dec 2024), TypeScript strict mode, MDX v3 for pages needing React components
   - **Rationale**: Docusaurus v3 is stable and mature, TypeScript provides type safety for custom components, MDX allows seamless React component integration in markdown
   - **Alternatives considered**: Docusaurus v2 (older, less type-safe), Next.js (more complex, overkill for static docs), VitePress (Vue-based, less React ecosystem)

2. **Text Selection Detection Pattern**
   - **Question**: What's the best way to detect text selection (10-char minimum) and show a tooltip in a React/Docusaurus environment?
   - **Decision**: Use `window.getSelection()` API with `mouseup`/`touchend` event listeners attached to document body in a global `Root.tsx` wrapper; calculate position with `getBoundingClientRect()` and render tooltip using React portal
   - **Rationale**: Built-in browser API (no dependencies), works cross-browser, minimal performance impact, portal ensures tooltip renders above all content
   - **Alternatives considered**:
     - Third-party library (react-selection-popover) - adds unnecessary dependency
     - Per-page listeners - causes code duplication and management complexity
     - CSS-only approach - insufficient control over 10-char minimum logic

3. **Mobile Chat Panel UX Pattern**
   - **Question**: How to implement slide-up chat panel on mobile that doesn't obscure content?
   - **Decision**: Use CSS transforms (`translateY`) with transition for slide-up animation, fixed positioning from bottom with z-index layering, include close/minimize button that slides panel back down, max-height 60vh to leave navbar visible
   - **Rationale**: Native CSS animations perform well on mobile, fixed positioning with controlled height prevents content obscuring, common pattern users recognize from mobile apps
   - **Alternatives considered**:
     - Full-screen modal - too intrusive, hides content completely
     - Overlay with backdrop - adds complexity, not necessary for placeholder
     - Drawer component library - violates minimal dependencies principle

4. **Inline Alert/Banner Implementation**
   - **Question**: How to implement inline alert/banner below personalization buttons?
   - **Decision**: Use conditional rendering (React state) triggered by button click, render alert div below buttons with CSS animation (fade-in), auto-dismiss after 5 seconds or user clicks dismiss button, use Docusaurus Admonition-like styling for consistency
   - **Rationale**: Simple state management, no external libraries, consistent with Docusaurus design language, provides clear feedback without disrupting reading flow
   - **Alternatives considered**:
     - Toast notifications (react-toastify) - adds dependency, less contextual to button location
     - Browser alert() - poor UX, blocks interaction
     - Console log only - not visible to users without dev tools

5. **Sidebar Configuration Strategy**
   - **Question**: How to structure sidebars.ts for 4 modules with clear grouping?
   - **Decision**: Use Docusaurus category objects with custom labels, explicit item ordering, collapsible set to false for flat navigation, clear visual hierarchy with module numbers (Module 1, Module 2, etc.)
   - **Rationale**: Docusaurus sidebar configuration is declarative and type-safe, category objects allow custom labeling while maintaining clean URLs, flat navigation reduces cognitive load for learners
   - **Alternatives considered**:
     - Auto-generated sidebar from file structure - loses control over labels and ordering
     - Single flat list - harder to scan, no visual grouping by module
     - Multiple sidebars - unnecessary complexity for linear course structure

### Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Static Site Generator | Docusaurus | 3.5.0+ | Mature React-based docs framework, excellent DX, TypeScript support, built-in features (sidebar, navbar, search) |
| Language | TypeScript | 5.x | Type safety for custom components, better IDE support, prevents runtime errors |
| React | React | 18.x | Bundled with Docusaurus, industry standard for interactive UIs |
| CSS Strategy | CSS Modules | Built-in | Scoped styles per component, no global namespace pollution, works seamlessly with Docusaurus |
| Package Manager | npm | 10.x | Default Node package manager, widely supported, simple lockfile (package-lock.json) |
| Build Tool | Webpack | 5.x | Bundled with Docusaurus, handles TypeScript transpilation, CSS modules, code splitting |
| Node Runtime | Node.js | 18.x LTS | Stable LTS version, Docusaurus compatibility, long-term support through 2025 |

---

## Phase 1: Design Artifacts

### 1. Component Architecture

#### ChapterActionsBar Component

**Purpose**: Display "Personalize for Me" and "View in Urdu" buttons at the top of chapter pages with inline alert feedback

**Props Interface** (TypeScript):
```typescript
interface ChapterActionsBarProps {
  chapterTitle?: string;  // Optional: for context in future backend integration
  className?: string;      // Allow custom CSS classes
}
```

**State Management**:
- `showPersonalizationAlert: boolean` - Controls visibility of "Personalization coming soon" alert
- `showUrduAlert: boolean` - Controls visibility of "Urdu translation coming soon" alert

**Behavior**:
- On "Personalize for Me" click: Set `showPersonalizationAlert = true`, auto-dismiss after 5 seconds
- On "View in Urdu" click: Set `showUrduAlert = true`, auto-dismiss after 5 seconds
- Alerts appear below buttons with fade-in animation
- Mobile: Buttons stack vertically on screens < 768px width

**Styling** (CSS Modules):
- Buttons: Side-by-side on desktop, stacked on mobile
- Alert: Info-style banner (light blue background, darker blue border, icon optional)
- Spacing: 1rem gap between buttons, 0.5rem gap between buttons and alert
- Typography: 14px font size for buttons, 13px for alert text

---

#### AskTheTextbookButton Component

**Purpose**: Fixed bottom-right button (desktop) or slide-up button (mobile) that opens chat panel

**Props Interface**:
```typescript
interface AskTheTextbookButtonProps {
  onOpen: () => void;  // Callback to open chat panel
  className?: string;
}
```

**State Management**:
- None (stateless component, state managed by parent/Root wrapper)

**Behavior**:
- Desktop: Fixed position bottom-right (20px from bottom, 20px from right), z-index 1000
- Mobile: Slide-up button from bottom center when user scrolls up or taps trigger area
- On click: Call `onOpen()` callback to show chat panel

**Styling**:
- Desktop: Circular button 60px diameter, primary color background, "Ask" text or chat icon
- Mobile: Pill-shaped button 200px width x 50px height, slides up from bottom: 0, visibility controlled by scroll position
- Hover/focus states: Slight scale transform (1.05x), shadow increase for depth

---

#### ChatPanelPlaceholder Component

**Purpose**: Chat panel that displays placeholder content and mode indicators (whole-book vs selection-based)

**Props Interface**:
```typescript
interface ChatPanelPlaceholderProps {
  isOpen: boolean;              // Controls visibility
  onClose: () => void;          // Callback to close panel
  mode: 'whole-book' | 'selection'; // Current mode
  selectedText?: string;        // Text selected by user (if mode = 'selection')
  className?: string;
}
```

**State Management**:
- None (controlled component, state managed by parent/Root wrapper)

**Behavior**:
- Desktop: Overlay panel 400px width, 600px height, fixed position bottom-right, slide-in from right animation
- Mobile: Full-width panel, 60vh height, slide-up from bottom animation, covers bottom 60% of screen
- Close button (X icon) in top-right corner
- Mode indicator: Badge at top showing "Whole-Book Mode" or "Selection-Based Mode"
- Placeholder message: "Chatbot backend not connected yet. This is a frontend-only preview."
- If `mode = 'selection'` and `selectedText` provided, show selected text in a quoted block above placeholder message

**Styling**:
- Background: White (light mode) / Dark gray (dark mode)
- Border: Subtle shadow for depth
- Mode indicator: Badge with distinct color (blue for whole-book, green for selection)
- Typography: 16px base font, 14px for mode indicator

---

#### TextSelectionTooltip Component

**Purpose**: Small tooltip that appears near selected text (10+ chars) with "Ask about this" button

**Props Interface**:
```typescript
interface TextSelectionTooltipProps {
  position: { x: number; y: number }; // Absolute position on screen
  onAsk: () => void;                   // Callback to open chat in selection mode
  className?: string;
}
```

**State Management**:
- None (controlled component, position and visibility managed by Root wrapper)

**Behavior**:
- Appears only when text selection length >= 10 characters
- Position calculated from selection bounding box (above selection if space available, below if not)
- On "Ask about this" click: Call `onAsk()` callback which opens chat panel in selection mode
- Disappears when selection is cleared or user clicks elsewhere

**Styling**:
- Small tooltip: 120px width x 40px height
- Background: Primary theme color with slight transparency
- Text: "Ask about this" in 13px white text, centered
- Pointer arrow pointing to selected text
- Shadow for depth, border radius for modern look

---

### 2. Text Selection Detection Logic

**Implementation Location**: `src/theme/Root.tsx` (global wrapper that wraps entire site)

**Algorithm**:
1. Attach `mouseup` and `touchend` listeners to `document.body` on component mount
2. On trigger:
   ```typescript
   const selection = window.getSelection();
   const selectedText = selection?.toString().trim() || '';

   if (selectedText.length >= 10) {
     const range = selection?.getRangeAt(0);
     const rect = range?.getBoundingClientRect();

     // Calculate tooltip position (10px above selection, centered)
     const position = {
       x: rect.left + (rect.width / 2),
       y: rect.top - 10
     };

     setTooltipPosition(position);
     setSelectedText(selectedText);
     setShowTooltip(true);
   } else {
     setShowTooltip(false);
   }
   ```
3. Listen for `mousedown` or click outside tooltip to clear selection and hide tooltip
4. When tooltip "Ask about this" clicked:
   - Store `selectedText` in state
   - Set chat panel `mode = 'selection'`
   - Set `chatPanelOpen = true`
   - Pass `selectedText` to ChatPanelPlaceholder via props

**Edge Cases**:
- Selection spans multiple paragraphs: Use full selection text, tooltip positioned at start of selection
- Selection in code blocks: Works normally, selection may include line numbers (acceptable for placeholder)
- Mobile touch selection: `touchend` handles this, position calculation may need adjustment for touch vs mouse
- Rapid selection changes: Debounce logic (100ms delay) to avoid excessive re-renders

**Performance Considerations**:
- Listeners attached at Root level (once per page load), not per component
- Tooltip only renders when visible (conditional rendering)
- Position calculation only runs when selection changes and meets length threshold
- Use React.memo() for tooltip component to prevent unnecessary re-renders

---

### 3. Homepage Layout Design

**Component**: `src/pages/index.tsx`

**Structure**:
```typescript
export default function Home(): JSX.Element {
  return (
    <Layout
      title="Physical AI & Humanoid Robotics"
      description="Learn embodied AI, robotics, and physical intelligence"
    >
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <HomepageAuthor />
      </main>
    </Layout>
  );
}
```

**Sections**:

1. **HomepageHeader** (Hero Section)
   - Full-width background (subtle gradient or image)
   - Centered content:
     - H1: "Physical AI & Humanoid Robotics"
     - Subtitle (H2): "Master embodied intelligence and AI in the physical world"
     - Primary CTA button: "Start the Course" → links to `/docs/intro`
   - Responsive: Padding adjusts on mobile, font sizes scale down

2. **HomepageFeatures** (Feature Cards)
   - 2x2 grid on desktop, single column on mobile
   - 4 cards:
     - Card 1: "Physical AI & Embodied Intelligence" (icon + description)
     - Card 2: "Sim-to-Real Robotics & Digital Twins" (icon + description)
     - Card 3: "Integrated AI Tutor (RAG Chatbot)" (icon + description)
     - Card 4: "Adaptive Learning (Beginner/Intermediate/Advanced)" (icon + description)
   - Each card: Icon (emoji or SVG), title (H3), description (paragraph)

3. **HomepageAuthor** (Author Section)
   - Centered content:
     - Text: "Authored by Muhammad Qasim"
     - Links: GitHub (https://github.com/Psqasim), LinkedIn, Twitter/X (placeholder), Email (placeholder)
     - Icons for each link (use react-icons or SVG)
   - Responsive: Links stack vertically on mobile

**Footer** (Configured in `docusaurus.config.ts`, not custom component):
- Left column: Copyright © {year} Muhammad Qasim
- Center column: Quick links (placeholder)
- Right column: Social links (GitHub, LinkedIn, Twitter/X, Email)
- GitHub repo link: (placeholder until repo is public)

---

### 4. Docusaurus Configuration Details

**File**: `docusaurus.config.ts`

**Key Configuration Sections**:

```typescript
import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'Master embodied intelligence and AI in the physical world',
  favicon: 'img/favicon.ico',

  url: 'https://[username].github.io',  // Replace with actual GitHub Pages URL
  baseUrl: '/[repo-name]/',              // Replace with actual repo name

  organizationName: '[username]',        // GitHub username
  projectName: '[repo-name]',            // GitHub repo name

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],  // Urdu can be added later as separate locale
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: 'docs',  // Docs available at /docs/*
        },
        blog: false,  // Disable blog (per FR-012)
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Logo',
        src: 'img/logo.svg',  // Optional: Add logo if available
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Course',  // Links to /docs/intro
        },
        {
          to: '/chat',  // Placeholder page for RAG Chat (create later)
          label: 'Study Assistant',
          position: 'left',
        },
        {
          href: 'https://github.com/Psqasim',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Learn',
          items: [
            {
              label: 'Start Course',
              to: '/docs/intro',
            },
          ],
        },
        {
          title: 'Connect',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/Psqasim',
            },
            {
              label: 'LinkedIn',
              href: 'https://linkedin.com/in/[username]',  // Replace with actual URL
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Muhammad Qasim. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
```

**Key Decisions**:
- `blog: false` disables blog entirely (no navbar link, no blog routes)
- `routeBasePath: 'docs'` keeps docs at `/docs/*` (standard convention)
- Navbar includes "Course" (docs) and "Study Assistant" (placeholder for future RAG chat page)
- Footer includes author attribution, social links, copyright

---

**File**: `sidebars.ts`

**Configuration**:

```typescript
import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'category',
      label: 'Module 1 – ROS 2: Robotic Nervous System',
      collapsible: false,
      items: [
        'module-1-ros2/overview',
        'module-1-ros2/chapter-1-basics',
      ],
    },
    {
      type: 'category',
      label: 'Module 2 – Digital Twin (Gazebo & Unity)',
      collapsible: false,
      items: [
        'module-2-digital-twin-gazebo-unity/overview',
        'module-2-digital-twin-gazebo-unity/chapter-1-simulation-basics',
      ],
    },
    {
      type: 'category',
      label: 'Module 3 – NVIDIA Isaac (AI-Robot Brain)',
      collapsible: false,
      items: [
        'module-3-nvidia-isaac/overview',
        'module-3-nvidia-isaac/chapter-1-getting-started',
      ],
    },
    {
      type: 'category',
      label: 'Module 4 – Vision-Language-Action (VLA)',
      collapsible: false,
      items: [
        'module-4-vision-language-action/overview',
        'module-4-vision-language-action/chapter-1-vla-intro',
      ],
    },
  ],
};

export default sidebars;
```

**Key Decisions**:
- `collapsible: false` keeps all modules expanded for easier scanning
- Category labels use full descriptive names (Module 1 – ROS 2: Robotic Nervous System) per FR-011
- File IDs match directory structure (module-1-ros2/overview)
- Clean, flat hierarchy (no nested categories within modules for now)

---

### 5. MDX Pages Strategy

**Decision**: Use `.mdx` extension for chapter pages (overview and chapter-1 files) that need React components; use `.md` for intro page (plain markdown)

**Example**: `docs/module-1-ros2/overview.mdx`

```mdx
---
sidebar_position: 1
title: ROS 2 Overview
---

import ChapterActionsBar from '@site/src/components/learning/ChapterActionsBar';

# ROS 2: Robotic Nervous System

<ChapterActionsBar chapterTitle="ROS 2 Overview" />

This module introduces ROS 2 (Robot Operating System 2), the next-generation middleware for robotics. You'll learn core concepts like nodes, topics, services, and actions, and how ROS 2 enables distributed robotics systems.

## What You'll Learn

- ROS 2 architecture and design philosophy
- Creating nodes and managing communication
- Using tools like rqt and rviz for debugging
- Integrating ROS 2 with simulators and real hardware

## Prerequisites

- Basic programming skills (Python or C++)
- Familiarity with Linux command line
- Understanding of basic robotics concepts (optional but helpful)
```

**Component Import Pattern**:
- Use `@site/` alias (Docusaurus built-in) to import from `src/`
- Import at top of MDX file (after frontmatter)
- Render component inline with JSX syntax: `<ChapterActionsBar />`

**Frontmatter**:
- `sidebar_position`: Controls ordering within category (1 for overview, 2 for chapter-1)
- `title`: Page title (appears in browser tab, meta tags)
- Additional metadata (description, keywords) can be added for SEO

---

### 6. TypeScript Configuration

**File**: `tsconfig.json`

```json
{
  "extends": "@docusaurus/tsconfig",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@site/*": ["./src/*"]
    },
    "strict": true,
    "jsx": "react",
    "module": "esnext",
    "moduleResolution": "node",
    "target": "es2017",
    "lib": ["es2017", "dom"],
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true
  },
  "include": ["src/**/*", "docs/**/*"],
  "exclude": ["node_modules", "build", ".docusaurus"]
}
```

**Key Settings**:
- `strict: true` - Enables all strict type-checking options (null checks, implicit any, etc.)
- `@site/*` path alias - Allows `import X from '@site/src/...'` instead of relative paths
- `include` covers both `src/` (components) and `docs/` (MDX files)
- `noEmit: true` - TypeScript used for type-checking only, Webpack handles transpilation

---

### 7. Responsive Design Strategy

**Breakpoints** (defined in `src/css/custom.css`):
```css
/* Mobile: < 768px */
/* Tablet: 768px - 1024px */
/* Desktop: > 1024px */

:root {
  --mobile-breakpoint: 768px;
  --tablet-breakpoint: 1024px;
}
```

**Component-Specific Responsive Behaviors**:

1. **ChapterActionsBar**:
   - Desktop: Buttons side-by-side, 200px width each
   - Mobile: Buttons stacked vertically, full-width

2. **AskTheTextbookButton**:
   - Desktop: Fixed bottom-right (60px circular button)
   - Mobile: Slide-up pill button from bottom center (200px x 50px)

3. **ChatPanelPlaceholder**:
   - Desktop: 400px width x 600px height, fixed bottom-right
   - Mobile: Full-width, 60vh height, slide-up from bottom

4. **Homepage**:
   - Hero: Full-width background, centered content, reduced padding on mobile
   - Features: 2x2 grid → single column on mobile
   - Author section: Horizontal links → vertical stack on mobile

**CSS Strategy**:
- Use CSS Modules for component-specific styles (`.module.css` files)
- Use media queries for responsive adjustments
- Use Flexbox and CSS Grid for layouts (better than floats/positioning)
- Use CSS custom properties (--var-name) for consistent spacing, colors, sizes

---

### 8. Build & Deployment Configuration

**npm Scripts** (in `package.json`):

```json
{
  "scripts": {
    "docusaurus": "docusaurus",
    "start": "docusaurus start",
    "build": "docusaurus build",
    "swizzle": "docusaurus swizzle",
    "deploy": "docusaurus deploy",
    "clear": "docusaurus clear",
    "serve": "docusaurus serve",
    "write-translations": "docusaurus write-translations",
    "write-heading-ids": "docusaurus write-heading-ids"
  }
}
```

**GitHub Pages Configuration**:
- Set `url` and `baseUrl` in `docusaurus.config.ts` to match GitHub Pages URL
- Set `organizationName` and `projectName` to GitHub username and repo name
- Optionally create `.github/workflows/deploy.yml` for automated deployment on push to main
- Run `npm run build` to generate `build/` directory (static files)
- Run `npm run deploy` to push `build/` to `gh-pages` branch (requires Git remote configured)

**Build Verification**:
- `npm run build` must complete with zero errors
- Output should be in `build/` directory (~2-5MB for minimal content)
- Test locally with `npm run serve` before deploying
- Check all routes load correctly (/docs/intro, /docs/module-1-ros2/overview, etc.)

---

### 9. Risk & Mitigation Strategy

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Text selection tooltip conflicts with Docusaurus layout** | Medium - Tooltip may not render correctly or may be hidden by Z-index layers | Medium | Use React Portal to render tooltip in a dedicated root-level DOM node, ensure z-index > 1000, test on multiple page types (docs, homepage) |
| **MDX + custom components causing build issues** | High - Build failures block deployment | Low | Test build after adding each component, use TypeScript strict mode to catch errors early, follow Docusaurus MDX guidelines exactly |
| **Mobile slide-up panel obscures content** | Medium - Poor UX on mobile | Medium | Limit panel height to 60vh, include close button, test on iPhone SE (375px) and other small devices, ensure navbar remains visible |
| **Chat button positioning conflicts with Docusaurus theme** | Low - Visual overlap or misalignment | Low | Use fixed positioning with explicit z-index, test with different Docusaurus themes (light/dark), add CSS to override theme defaults if needed |
| **10-character selection threshold too restrictive** | Low - Users frustrated by inability to select short terms | Medium | Document this behavior in quickstart.md, consider making threshold configurable via React context (easy to adjust later) |
| **Performance degradation with text selection listeners** | Low - Page feels sluggish | Low | Debounce selection event handler (100ms), use React.memo() for tooltip component, profile with Chrome DevTools to ensure <16ms render time |
| **TypeScript build errors from Docusaurus upgrades** | Medium - Blocks future updates | Low | Pin Docusaurus version in package.json, test upgrades in separate branch, maintain strict tsconfig to catch breaking changes early |

**Incremental Implementation Order** (to reduce risk):
1. **Phase 1**: Basic Docusaurus setup + homepage (no custom components) → Verify build succeeds
2. **Phase 2**: Add docs structure + sidebars → Verify navigation works
3. **Phase 3**: Add ChapterActionsBar component → Test on one page, then apply to all
4. **Phase 4**: Add AskTheTextbookButton → Test positioning on desktop/mobile
5. **Phase 5**: Add ChatPanelPlaceholder → Test open/close behavior, mode switching
6. **Phase 6**: Add text selection detection + tooltip → Test thoroughly, profile performance
7. **Phase 7**: Final polish (CSS, responsive adjustments, content refinement)

This order ensures core functionality (navigation, homepage) works before adding complex interactive features (text selection, chat panel).

---

## Phase 2: Implementation Readiness

**Status**: Plan complete. Next step is `/sp.tasks` to generate concrete task list.

**Readiness Checklist**:
- ✅ Technical context defined (Docusaurus v3, TypeScript, Node 18+)
- ✅ Constitution check passed (no violations)
- ✅ Project structure documented (repo root layout, component locations)
- ✅ Research completed (Docusaurus best practices, text selection pattern, responsive strategy)
- ✅ Component architecture designed (ChapterActionsBar, AskTheTextbookButton, ChatPanelPlaceholder, TextSelectionTooltip)
- ✅ Configuration files specified (docusaurus.config.ts, sidebars.ts, tsconfig.json)
- ✅ Responsive design strategy defined (breakpoints, mobile behaviors)
- ✅ Build & deployment approach documented (npm scripts, GitHub Pages)
- ✅ Risks identified with mitigations (incremental implementation order)

**Next Command**: `/sp.tasks` to generate detailed task list with file paths, dependencies, and acceptance criteria.

**Estimated Scope**:
- ~15-25 tasks (setup, config, components, docs, testing)
- ~8-16 hours of implementation work (assuming 1 developer)
- ~3-5 days calendar time (accounting for reviews, testing, iterations)

**Success Criteria** (from spec, reconfirmed here):
- ✅ Site builds and runs locally with zero errors (SC-001)
- ✅ All navigation paths accessible within 3 clicks (SC-002)
- ✅ Homepage loads < 3 seconds (SC-004)
- ✅ Mobile responsive down to 375px (SC-006)
- ✅ 100% module coverage (all 4 modules have overview + chapter 1) (SC-007)
- ✅ Author attribution visible above fold (SC-008)
- ✅ Blog link NOT visible in navbar (SC-009)
- ✅ Placeholder UI elements respond to clicks (SC-010)
- ✅ Clean URLs generated (SC-011)
- ✅ Deployable to GitHub Pages without manual edits (SC-012)
