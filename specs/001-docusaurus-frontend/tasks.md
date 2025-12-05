# Task List: Docusaurus Frontend Structure

**Feature**: 001-docusaurus-frontend | **Branch**: `001-docusaurus-frontend` | **Date**: 2025-12-05
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

## Task Metadata

- **Total Tasks**: 24
- **Estimated Effort**: 8-16 hours
- **Parallelizable Tasks**: 7 (marked with [P])
- **Dependencies**: Most tasks are sequential, but some content creation and component styling can be done in parallel once base structure exists

## Implementation Order

Tasks are ordered to minimize risk and maximize incremental progress:
1. Foundation (setup, config)
2. Structure (docs tree, sidebars)
3. Content (homepage, docs pages)
4. Components (ChapterActionsBar → Chat UI → Text selection)
5. Polish (responsive, testing, deployment)

---

## Phase 1: Foundation Setup (Tasks 1-5)

### Task 1: Initialize Docusaurus project at repo root

**Description**: Create a new Docusaurus v3 project using TypeScript and the classic preset at the repository root (not in a subdirectory).

**Files Created**:
- `package.json`
- `package-lock.json`
- `docusaurus.config.ts`
- `sidebars.ts`
- `tsconfig.json`
- `babel.config.js`
- `.gitignore`
- `README.md`
- `src/` directory structure
- `docs/` directory structure
- `static/` directory structure

**Commands**:
```bash
# Run from repo root
npx create-docusaurus@latest . classic --typescript
```

**Acceptance Criteria**:
- [ ] Docusaurus project initialized successfully
- [ ] `npm start` runs without errors and opens site on http://localhost:3000
- [ ] Default homepage and docs are visible
- [ ] TypeScript configuration is present and valid
- [ ] `.gitignore` includes `node_modules/`, `build/`, `.docusaurus/`

**Dependencies**: None

**Estimated Time**: 10 minutes

**Notes**: If the directory is not empty, the command may fail. Move existing files to a temporary directory if needed, or use `--skip-install` flag and manually install dependencies.

---

### Task 2: Configure TypeScript strict mode and path aliases

**Description**: Update `tsconfig.json` to enable strict mode and configure `@site/*` path alias for cleaner imports.

**Files Modified**:
- `tsconfig.json`

**Changes**:
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

**Acceptance Criteria**:
- [ ] `strict: true` is set
- [ ] `@site/*` path alias is configured
- [ ] `npm start` still runs without TypeScript errors
- [ ] Import statements using `@site/` work correctly

**Dependencies**: Task 1

**Estimated Time**: 5 minutes

---

### Task 3: Configure Docusaurus site metadata and theme

**Description**: Update `docusaurus.config.ts` with site title, tagline, favicon, navbar, footer, and disable blog.

**Files Modified**:
- `docusaurus.config.ts`

**Key Changes**:
- Set `title: 'Physical AI & Humanoid Robotics Textbook'`
- Set `tagline: 'Master embodied intelligence and AI in the physical world'`
- Set `url` and `baseUrl` for GitHub Pages (use placeholders if repo not yet public)
- Configure navbar with "Course" and "Study Assistant" links
- Disable blog preset (`blog: false`)
- Configure footer with author attribution and social links

**Reference**: See plan.md Section 4 for complete configuration example

**Acceptance Criteria**:
- [ ] Site title appears in browser tab and navbar
- [ ] Tagline is visible on homepage
- [ ] Navbar shows "Course" and "Study Assistant" links (no "Blog" link)
- [ ] Footer shows "Copyright © {year} Muhammad Qasim"
- [ ] Footer includes GitHub and LinkedIn links
- [ ] `npm start` runs without errors

**Dependencies**: Task 1

**Estimated Time**: 15 minutes

---

### Task 4: Add favicon and prepare static assets directory

**Description**: Add a favicon to `static/img/` and ensure the static assets directory is properly configured.

**Files Created**:
- `static/img/favicon.ico` (can use a placeholder or default Docusaurus favicon initially)

**Commands**:
```bash
# If using default Docusaurus favicon
cp node_modules/@docusaurus/preset-classic/lib/theme/Icon/favicon.ico static/img/favicon.ico
```

**Acceptance Criteria**:
- [ ] Favicon file exists at `static/img/favicon.ico`
- [ ] Favicon appears in browser tab when site is running
- [ ] No console errors about missing favicon

**Dependencies**: Task 1

**Estimated Time**: 5 minutes

**Notes**: A custom favicon can be added later. For now, use a placeholder or default icon.

---

### Task 5: Create initial custom CSS file with responsive breakpoints

**Description**: Create `src/css/custom.css` and define CSS custom properties for colors, spacing, and responsive breakpoints.

**Files Created/Modified**:
- `src/css/custom.css` (may already exist from Docusaurus init, modify if so)

**Content**:
```css
:root {
  /* Responsive breakpoints */
  --mobile-breakpoint: 768px;
  --tablet-breakpoint: 1024px;

  /* Color palette (customize later) */
  --ifm-color-primary: #2e8555;
  --ifm-color-primary-dark: #29784c;
  --ifm-color-primary-darker: #277148;
  --ifm-color-primary-darkest: #205d3b;
  --ifm-color-primary-light: #33925d;
  --ifm-color-primary-lighter: #359962;
  --ifm-color-primary-lightest: #3cad6e;

  /* Spacing (if needed) */
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 2rem;
}

/* Mobile-first responsive styles */
@media (max-width: 768px) {
  /* Mobile styles will be added here */
}

@media (min-width: 768px) and (max-width: 1024px) {
  /* Tablet styles will be added here */
}

@media (min-width: 1024px) {
  /* Desktop styles will be added here */
}
```

**Acceptance Criteria**:
- [ ] `src/css/custom.css` exists and is imported in `docusaurus.config.ts`
- [ ] CSS custom properties are defined
- [ ] Site still runs without CSS errors
- [ ] No visual regressions (site looks normal)

**Dependencies**: Task 1

**Estimated Time**: 10 minutes

---

## Phase 2: Documentation Structure (Tasks 6-11)

### Task 6: Create docs directory structure for 4 modules

**Description**: Create directories for intro and 4 modules in the `docs/` folder.

**Directories Created**:
- `docs/module-1-ros2/`
- `docs/module-2-digital-twin-gazebo-unity/`
- `docs/module-3-nvidia-isaac/`
- `docs/module-4-vision-language-action/`

**Commands**:
```bash
mkdir -p docs/module-1-ros2
mkdir -p docs/module-2-digital-twin-gazebo-unity
mkdir -p docs/module-3-nvidia-isaac
mkdir -p docs/module-4-vision-language-action
```

**Acceptance Criteria**:
- [ ] All 4 module directories exist under `docs/`
- [ ] Directory names match the planned structure exactly

**Dependencies**: Task 1

**Estimated Time**: 2 minutes

---

### Task 7: Create intro.md with course introduction content

**Description**: Create `docs/intro.md` with a short introduction to the Physical AI & Humanoid Robotics course.

**Files Created**:
- `docs/intro.md`

**Content Template**:
```markdown
---
sidebar_position: 1
title: Introduction to Physical AI & Humanoid Robotics
---

# Introduction to Physical AI & Humanoid Robotics

Welcome to the Physical AI & Humanoid Robotics Textbook. This course provides a comprehensive journey through embodied intelligence, teaching you how to build intelligent robots that understand and interact with the physical world.

## Course Overview

You'll explore four interconnected modules:

1. **ROS 2: Robotic Nervous System** - Learn the middleware that powers modern robotics
2. **Digital Twin (Gazebo & Unity)** - Master simulation for safe, iterative development
3. **NVIDIA Isaac (AI-Robot Brain)** - Integrate AI models for perception and decision-making
4. **Vision-Language-Action (VLA)** - Build robots that understand natural language commands

## Prerequisites

- Basic programming skills (Python or C++)
- Familiarity with Linux command line
- Understanding of basic AI/ML concepts (helpful but not required)

## How to Use This Textbook

- Follow the modules sequentially for a structured learning path
- Each chapter includes explanations, examples, and hands-on exercises
- Use the integrated AI tutor (coming soon) to ask questions as you learn
- Personalize the content to your skill level (beginner/intermediate/advanced)

Let's begin your journey into Physical AI!
```

**Acceptance Criteria**:
- [ ] `docs/intro.md` exists and contains course introduction
- [ ] File is accessible at http://localhost:3000/docs/intro when running `npm start`
- [ ] Sidebar shows "Introduction" link

**Dependencies**: Task 1

**Estimated Time**: 10 minutes

---

### Task 8: [P] Create Module 1 (ROS 2) overview and chapter 1 MDX files

**Description**: Create `overview.mdx` and `chapter-1-basics.mdx` for Module 1 with placeholder content.

**Files Created**:
- `docs/module-1-ros2/overview.mdx`
- `docs/module-1-ros2/chapter-1-basics.mdx`

**Content for overview.mdx**:
```mdx
---
sidebar_position: 1
title: ROS 2 Overview
---

# ROS 2: Robotic Nervous System

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

**Content for chapter-1-basics.mdx**:
```mdx
---
sidebar_position: 2
title: Chapter 1 - ROS 2 Basics
---

# Chapter 1: ROS 2 Basics

Learn the fundamental building blocks of ROS 2, including nodes, topics, publishers, and subscribers.

## Topics Covered

- What is a ROS 2 node?
- Communication patterns (pub/sub, services, actions)
- Creating your first ROS 2 package
- Running nodes and inspecting topics

## Hands-On Exercise

By the end of this chapter, you'll create a simple ROS 2 node that publishes sensor data and subscribes to commands.
```

**Acceptance Criteria**:
- [ ] Both files exist in `docs/module-1-ros2/`
- [ ] Files use `.mdx` extension (not `.md`)
- [ ] Files are accessible via browser (http://localhost:3000/docs/module-1-ros2/overview)
- [ ] Content is professional and free of typos

**Dependencies**: Task 6

**Estimated Time**: 15 minutes

**Notes**: [P] = Can be done in parallel with Tasks 9, 10, 11 (other modules)

---

### Task 9: [P] Create Module 2 (Digital Twin) overview and chapter 1 MDX files

**Description**: Create `overview.mdx` and `chapter-1-simulation-basics.mdx` for Module 2 with placeholder content.

**Files Created**:
- `docs/module-2-digital-twin-gazebo-unity/overview.mdx`
- `docs/module-2-digital-twin-gazebo-unity/chapter-1-simulation-basics.mdx`

**Content Structure**: Similar to Task 8, but focused on Digital Twin, Gazebo, and Unity topics.

**Acceptance Criteria**:
- [ ] Both files exist in `docs/module-2-digital-twin-gazebo-unity/`
- [ ] Files use `.mdx` extension
- [ ] Files are accessible via browser
- [ ] Content is professional and relevant to Digital Twin/simulation

**Dependencies**: Task 6

**Estimated Time**: 15 minutes

**Notes**: [P] = Can be done in parallel with Tasks 8, 10, 11

---

### Task 10: [P] Create Module 3 (NVIDIA Isaac) overview and chapter 1 MDX files

**Description**: Create `overview.mdx` and `chapter-1-getting-started.mdx` for Module 3 with placeholder content.

**Files Created**:
- `docs/module-3-nvidia-isaac/overview.mdx`
- `docs/module-3-nvidia-isaac/chapter-1-getting-started.mdx`

**Content Structure**: Similar to Task 8, but focused on NVIDIA Isaac and AI-Robot Brain topics.

**Acceptance Criteria**:
- [ ] Both files exist in `docs/module-3-nvidia-isaac/`
- [ ] Files use `.mdx` extension
- [ ] Files are accessible via browser
- [ ] Content is professional and relevant to NVIDIA Isaac

**Dependencies**: Task 6

**Estimated Time**: 15 minutes

**Notes**: [P] = Can be done in parallel with Tasks 8, 9, 11

---

### Task 11: [P] Create Module 4 (VLA) overview and chapter 1 MDX files

**Description**: Create `overview.mdx` and `chapter-1-vla-intro.mdx` for Module 4 with placeholder content.

**Files Created**:
- `docs/module-4-vision-language-action/overview.mdx`
- `docs/module-4-vision-language-action/chapter-1-vla-intro.mdx`

**Content Structure**: Similar to Task 8, but focused on Vision-Language-Action (VLA) topics.

**Acceptance Criteria**:
- [ ] Both files exist in `docs/module-4-vision-language-action/`
- [ ] Files use `.mdx` extension
- [ ] Files are accessible via browser
- [ ] Content is professional and relevant to VLA

**Dependencies**: Task 6

**Estimated Time**: 15 minutes

**Notes**: [P] = Can be done in parallel with Tasks 8, 9, 10

---

## Phase 3: Navigation & Sidebar (Task 12)

### Task 12: Configure sidebars.ts with 4 modules

**Description**: Update `sidebars.ts` to include intro and all 4 modules with proper labels and ordering.

**Files Modified**:
- `sidebars.ts`

**Configuration**: See plan.md Section 4 for complete sidebar configuration example.

**Key Requirements**:
- Intro at top
- 4 module categories with full descriptive labels (e.g., "Module 1 – ROS 2: Robotic Nervous System")
- Each module has overview and chapter-1 as items
- `collapsible: false` for all categories

**Acceptance Criteria**:
- [ ] Sidebar shows "Introduction" at top
- [ ] All 4 modules are visible with correct labels
- [ ] Each module shows "Overview" and "Chapter 1" as sub-items
- [ ] Sidebar navigation works correctly (clicking links loads pages)
- [ ] No "Blog" link appears in sidebar or navbar

**Dependencies**: Tasks 7, 8, 9, 10, 11

**Estimated Time**: 10 minutes

---

## Phase 4: Homepage (Task 13)

### Task 13: Create custom homepage with hero, features, and author sections

**Description**: Create `src/pages/index.tsx` with a custom homepage including hero section, feature cards, and author attribution.

**Files Created/Modified**:
- `src/pages/index.tsx` (replace default homepage)

**Structure**:
- Hero section: Title, tagline, "Start the Course" CTA button
- Features section: 4 feature cards (Physical AI, Sim-to-Real, AI Tutor, Adaptive Learning)
- Author section: "Authored by Muhammad Qasim" with social links

**Reference**: See plan.md Section 3 for detailed layout design

**Acceptance Criteria**:
- [ ] Homepage displays hero section with title "Physical AI & Humanoid Robotics"
- [ ] Tagline about embodied intelligence is visible
- [ ] "Start the Course" button links to `/docs/intro`
- [ ] 4 feature cards are visible and styled appropriately
- [ ] Author section shows "Authored by Muhammad Qasim"
- [ ] Social links (GitHub: https://github.com/Psqasim, LinkedIn placeholder) are clickable
- [ ] Homepage is responsive (works on mobile and desktop)
- [ ] No console errors or warnings

**Dependencies**: Task 3

**Estimated Time**: 45 minutes

**Notes**: This is the most complex single task. Break into sub-tasks if needed (hero → features → author).

---

## Phase 5: Reusable Components (Tasks 14-18)

### Task 14: Create ChapterActionsBar component with TypeScript

**Description**: Create the `ChapterActionsBar` component with "Personalize for Me" and "View in Urdu" buttons, plus inline alert/banner logic.

**Files Created**:
- `src/components/learning/ChapterActionsBar.tsx`
- `src/components/learning/ChapterActionsBar.module.css`

**Component Requirements**:
- Two buttons: "Personalize for Me" and "View in Urdu"
- Click handlers that show inline alert below buttons
- Alert message: "Personalization coming soon" or "Urdu translation coming soon"
- Auto-dismiss after 5 seconds
- TypeScript interface for props (see plan.md Section 1)
- CSS Modules for styling

**Acceptance Criteria**:
- [ ] Component file exists at `src/components/learning/ChapterActionsBar.tsx`
- [ ] TypeScript interface `ChapterActionsBarProps` is defined
- [ ] Both buttons render correctly
- [ ] Clicking "Personalize for Me" shows inline alert with message "Personalization coming soon"
- [ ] Clicking "View in Urdu" shows inline alert with message "Urdu translation coming soon"
- [ ] Alert auto-dismisses after 5 seconds
- [ ] Component is responsive (buttons stack on mobile < 768px)
- [ ] No TypeScript errors

**Dependencies**: Task 2 (TypeScript config)

**Estimated Time**: 30 minutes

**Notes**: Test this component standalone before integrating into MDX files.

---

### Task 15: Integrate ChapterActionsBar into all module overview and chapter 1 MDX files

**Description**: Import and embed `<ChapterActionsBar />` at the top of all 8 chapter MDX files (4 modules × 2 pages each).

**Files Modified**:
- `docs/module-1-ros2/overview.mdx`
- `docs/module-1-ros2/chapter-1-basics.mdx`
- `docs/module-2-digital-twin-gazebo-unity/overview.mdx`
- `docs/module-2-digital-twin-gazebo-unity/chapter-1-simulation-basics.mdx`
- `docs/module-3-nvidia-isaac/overview.mdx`
- `docs/module-3-nvidia-isaac/chapter-1-getting-started.mdx`
- `docs/module-4-vision-language-action/overview.mdx`
- `docs/module-4-vision-language-action/chapter-1-vla-intro.mdx`

**Change Pattern**:
```mdx
---
sidebar_position: 1
title: Module X Overview
---

import ChapterActionsBar from '@site/src/components/learning/ChapterActionsBar';

# Module Title

<ChapterActionsBar chapterTitle="Module X Overview" />

[Rest of content...]
```

**Acceptance Criteria**:
- [ ] All 8 MDX files import ChapterActionsBar
- [ ] Component renders at top of each page (below title)
- [ ] Buttons work correctly on all pages
- [ ] No console errors or TypeScript errors
- [ ] Pages still load normally

**Dependencies**: Task 14

**Estimated Time**: 20 minutes

---

### Task 16: Create AskTheTextbookButton component with responsive positioning

**Description**: Create the `AskTheTextbookButton` component that displays a fixed button (desktop) or slide-up button (mobile) to open chat panel.

**Files Created**:
- `src/components/chat/AskTheTextbookButton.tsx`
- `src/components/chat/AskTheTextbookButton.module.css`

**Component Requirements**:
- Stateless component with `onOpen` callback prop
- Desktop: Fixed bottom-right positioning (20px from bottom/right, z-index 1000)
- Mobile: Slide-up pill button from bottom center (responsive behavior)
- TypeScript interface for props (see plan.md Section 1)

**Acceptance Criteria**:
- [ ] Component file exists at `src/components/chat/AskTheTextbookButton.tsx`
- [ ] TypeScript interface `AskTheTextbookButtonProps` is defined
- [ ] Button renders in bottom-right corner on desktop (> 1024px)
- [ ] Button renders as slide-up pill on mobile (< 768px)
- [ ] Clicking button calls `onOpen()` callback
- [ ] No TypeScript errors
- [ ] Button is accessible via keyboard (tab, enter)

**Dependencies**: Task 2

**Estimated Time**: 25 minutes

---

### Task 17: Create ChatPanelPlaceholder component with mode indicators

**Description**: Create the `ChatPanelPlaceholder` component that displays a chat panel with placeholder content and mode distinction (whole-book vs selection-based).

**Files Created**:
- `src/components/chat/ChatPanelPlaceholder.tsx`
- `src/components/chat/ChatPanelPlaceholder.module.css`

**Component Requirements**:
- Controlled component with `isOpen`, `onClose`, `mode`, `selectedText` props
- Desktop: 400px × 600px panel, fixed bottom-right, slide-in animation
- Mobile: Full-width, 60vh height, slide-up from bottom
- Mode indicator badge (blue for whole-book, green for selection)
- Placeholder message: "Chatbot backend not connected yet. This is a frontend-only preview."
- If `mode = 'selection'` and `selectedText` provided, show selected text in quoted block
- Close button (X icon) in top-right corner

**Acceptance Criteria**:
- [ ] Component file exists at `src/components/chat/ChatPanelPlaceholder.tsx`
- [ ] TypeScript interface `ChatPanelPlaceholderProps` is defined
- [ ] Panel renders correctly when `isOpen = true`
- [ ] Mode indicator shows correct badge based on `mode` prop
- [ ] Selected text appears in quoted block when `mode = 'selection'`
- [ ] Close button calls `onClose()` callback
- [ ] Panel is responsive (desktop: 400px wide, mobile: full-width)
- [ ] Slide-in animation works smoothly
- [ ] No TypeScript errors

**Dependencies**: Task 2

**Estimated Time**: 35 minutes

---

### Task 18: Create TextSelectionTooltip component

**Description**: Create the `TextSelectionTooltip` component that appears near selected text with "Ask about this" button.

**Files Created**:
- `src/components/chat/TextSelectionTooltip.tsx`
- `src/components/chat/TextSelectionTooltip.module.css`

**Component Requirements**:
- Controlled component with `position`, `onAsk` props
- Renders at absolute position calculated from selection bounding box
- Small tooltip (120px × 40px) with "Ask about this" text
- Pointer arrow pointing to selected text
- Renders using React Portal to ensure correct z-index layering

**Acceptance Criteria**:
- [ ] Component file exists at `src/components/chat/TextSelectionTooltip.tsx`
- [ ] TypeScript interface `TextSelectionTooltipProps` is defined
- [ ] Tooltip renders at specified `position` (x, y coordinates)
- [ ] Clicking tooltip calls `onAsk()` callback
- [ ] Tooltip renders above all other content (z-index > 1000)
- [ ] Tooltip has pointer arrow pointing down (or up if below selection)
- [ ] No TypeScript errors

**Dependencies**: Task 2

**Estimated Time**: 30 minutes

**Notes**: Test standalone before integrating with Root.tsx wrapper.

---

## Phase 6: Global Text Selection Detection (Task 19)

### Task 19: Create Root.tsx wrapper with text selection detection logic

**Description**: Create `src/theme/Root.tsx` to wrap entire site and implement global text selection detection with 10-character minimum threshold.

**Files Created**:
- `src/theme/Root.tsx`

**Implementation Requirements**:
- Attach `mouseup` and `touchend` event listeners to `document.body`
- Use `window.getSelection()` API to get selected text
- Check if selection length >= 10 characters
- Calculate tooltip position from `range.getBoundingClientRect()`
- Manage state for:
  - `showTooltip: boolean`
  - `tooltipPosition: {x: number, y: number}`
  - `selectedText: string`
  - `chatPanelOpen: boolean`
  - `chatMode: 'whole-book' | 'selection'`
- Render `AskTheTextbookButton`, `ChatPanelPlaceholder`, and `TextSelectionTooltip` components
- Handle tooltip click → open chat panel in selection mode
- Handle button click → open chat panel in whole-book mode

**Reference**: See plan.md Section 2 for complete algorithm

**Acceptance Criteria**:
- [ ] `src/theme/Root.tsx` exists and wraps entire site
- [ ] Text selection >= 10 characters triggers tooltip
- [ ] Tooltip appears near selected text (above if space, below if not)
- [ ] Clicking tooltip opens chat panel in selection mode with selected text displayed
- [ ] `AskTheTextbookButton` is visible on all pages (bottom-right desktop, slide-up mobile)
- [ ] Clicking button opens chat panel in whole-book mode
- [ ] Chat panel close button works correctly
- [ ] Selection < 10 characters does not trigger tooltip
- [ ] Clicking outside tooltip/panel clears selection and hides UI
- [ ] No performance issues (use debounce if needed)
- [ ] No TypeScript errors

**Dependencies**: Tasks 16, 17, 18

**Estimated Time**: 60 minutes

**Notes**: This is the most complex component. Test thoroughly on desktop and mobile. Profile with Chrome DevTools to ensure < 16ms render time.

---

## Phase 7: Responsive Polish & Testing (Tasks 20-22)

### Task 20: Add responsive CSS for all components

**Description**: Add mobile-specific CSS to all component `.module.css` files to ensure proper behavior on screens < 768px.

**Files Modified**:
- `src/components/learning/ChapterActionsBar.module.css`
- `src/components/chat/AskTheTextbookButton.module.css`
- `src/components/chat/ChatPanelPlaceholder.module.css`
- `src/components/chat/TextSelectionTooltip.module.css`
- `src/css/custom.css`

**CSS Requirements**:
- ChapterActionsBar: Buttons stack vertically on mobile
- AskTheTextbookButton: Transform to slide-up pill on mobile
- ChatPanelPlaceholder: Full-width, 60vh height on mobile
- TextSelectionTooltip: Smaller size on mobile if needed
- Use `@media (max-width: 768px)` queries

**Acceptance Criteria**:
- [ ] All components are usable on mobile (375px width, iPhone SE)
- [ ] No horizontal scrolling on mobile
- [ ] Touch targets are at least 44px × 44px
- [ ] Chat panel doesn't obscure navbar on mobile
- [ ] Buttons are clearly visible and tappable
- [ ] Test on Chrome DevTools mobile emulator (iPhone SE, Pixel 5, iPad)

**Dependencies**: Tasks 14-19

**Estimated Time**: 30 minutes

---

### Task 21: [P] Manual testing on all navigation paths and components

**Description**: Manually test all major user flows to ensure everything works correctly.

**Test Cases**:

1. **Navigation Testing**:
   - [ ] Homepage loads correctly
   - [ ] Clicking "Start the Course" navigates to /docs/intro
   - [ ] Sidebar shows all 4 modules with correct labels
   - [ ] Clicking each module overview and chapter 1 loads correct page
   - [ ] Back/forward browser buttons work correctly
   - [ ] URLs are clean (no special characters)

2. **Homepage Testing**:
   - [ ] Hero section displays title and tagline
   - [ ] "Start the Course" button links to /docs/intro
   - [ ] 4 feature cards are visible
   - [ ] Author section shows "Authored by Muhammad Qasim"
   - [ ] Social links (GitHub, LinkedIn) are clickable
   - [ ] Footer shows copyright and links

3. **ChapterActionsBar Testing**:
   - [ ] Buttons appear on all 8 chapter pages
   - [ ] Clicking "Personalize for Me" shows inline alert
   - [ ] Clicking "View in Urdu" shows inline alert
   - [ ] Alerts auto-dismiss after 5 seconds
   - [ ] Buttons work on mobile (stack vertically)

4. **Chat UI Testing**:
   - [ ] "Ask the Textbook" button is visible on all docs pages
   - [ ] Clicking button opens chat panel in whole-book mode
   - [ ] Selecting 10+ characters shows tooltip
   - [ ] Clicking tooltip opens chat panel in selection mode
   - [ ] Selected text appears in chat panel when in selection mode
   - [ ] Close button closes chat panel
   - [ ] Chat panel is usable on mobile

5. **Responsive Testing**:
   - [ ] Site works on desktop (> 1024px)
   - [ ] Site works on tablet (768px - 1024px)
   - [ ] Site works on mobile (< 768px, down to 375px)
   - [ ] Sidebar collapses to hamburger menu on mobile
   - [ ] No horizontal scrolling on any screen size

**Dependencies**: All previous tasks

**Estimated Time**: 45 minutes

**Notes**: [P] = Can be done in parallel with Task 22 (build testing)

---

### Task 22: [P] Build verification and error fixing

**Description**: Run `npm run build` to generate production build and fix any build errors.

**Commands**:
```bash
npm run build
npm run serve
```

**Acceptance Criteria**:
- [ ] `npm run build` completes with zero errors
- [ ] `build/` directory is created (~2-5MB)
- [ ] `npm run serve` serves the production build successfully
- [ ] All pages load correctly in production build
- [ ] No console errors in production build
- [ ] No broken links or 404 errors
- [ ] All routes work correctly (/docs/intro, /docs/module-1-ros2/overview, etc.)

**Dependencies**: All previous tasks

**Estimated Time**: 15 minutes (plus time to fix any errors)

**Notes**: [P] = Can be done in parallel with Task 21 (manual testing)

---

## Phase 8: Deployment Preparation (Tasks 23-24)

### Task 23: Configure GitHub Pages deployment settings

**Description**: Update `docusaurus.config.ts` with correct GitHub Pages URL and configure deployment settings.

**Files Modified**:
- `docusaurus.config.ts`

**Changes Required**:
- Set `url` to `https://[username].github.io` (replace with actual GitHub username)
- Set `baseUrl` to `/[repo-name]/` (replace with actual repo name, or `/` if using custom domain)
- Set `organizationName` to GitHub username
- Set `projectName` to GitHub repo name

**Acceptance Criteria**:
- [ ] All URL fields in `docusaurus.config.ts` are correct
- [ ] `npm run deploy` command is ready (but don't run yet if repo not public)
- [ ] `.github/workflows/` directory can be created for CI/CD (optional for this task)

**Dependencies**: Task 22

**Estimated Time**: 10 minutes

**Notes**: If repo is not yet on GitHub, use placeholder values and document what needs to be changed.

---

### Task 24: Create deployment documentation and README updates

**Description**: Update `README.md` with instructions for running the site locally and deploying to GitHub Pages.

**Files Modified**:
- `README.md`

**Content to Add**:
```markdown
# Physical AI & Humanoid Robotics Textbook

A comprehensive course on embodied intelligence, robotics, and physical AI.

## Getting Started

### Prerequisites

- Node.js 18+ LTS
- npm 10+

### Installation

```bash
npm install
```

### Development

```bash
npm start
```

Opens the site at http://localhost:3000

### Build

```bash
npm run build
```

Generates static files in the `build/` directory.

### Serve Production Build Locally

```bash
npm run serve
```

### Deployment to GitHub Pages

```bash
npm run deploy
```

Pushes the `build/` directory to the `gh-pages` branch.

## Project Structure

- `docs/` - Course content (MDX files)
- `src/components/` - React components
- `src/pages/` - Custom pages (homepage)
- `src/css/` - Global styles
- `static/` - Static assets (images, favicon)
- `docusaurus.config.ts` - Site configuration
- `sidebars.ts` - Sidebar structure

## Features

- 4 comprehensive modules (ROS 2, Digital Twin, NVIDIA Isaac, VLA)
- Responsive design (mobile, tablet, desktop)
- Integrated AI tutor UI (frontend-only, backend coming soon)
- Text selection Q&A (10-character minimum)
- Personalization buttons (placeholder for future backend)

## Author

**Muhammad Qasim**
- GitHub: https://github.com/Psqasim
- LinkedIn: [Add LinkedIn URL]

## License

[Add license information]
```

**Acceptance Criteria**:
- [ ] README.md is comprehensive and up-to-date
- [ ] Installation instructions are clear
- [ ] All npm commands are documented
- [ ] Project structure is explained
- [ ] Author attribution is included

**Dependencies**: All previous tasks

**Estimated Time**: 20 minutes

---

## Success Criteria Validation

After completing all tasks, validate against spec success criteria:

- [ ] **SC-001**: Site builds and runs locally with `npm start` (zero errors)
- [ ] **SC-002**: All primary navigation paths accessible within 3 clicks
- [ ] **SC-003**: Navigate from homepage to any chapter 1 page in under 30 seconds
- [ ] **SC-004**: Homepage loads in under 3 seconds on standard broadband
- [ ] **SC-005**: All UI elements respond within 1 second
- [ ] **SC-006**: Site fully navigable on mobile (down to 375px width)
- [ ] **SC-007**: 100% of 4 modules have overview + chapter 1 pages
- [ ] **SC-008**: Author attribution visible above fold on homepage
- [ ] **SC-009**: "Blog" link NOT visible in navbar
- [ ] **SC-010**: Placeholder UI elements (buttons, chat) respond to clicks
- [ ] **SC-011**: Clean URLs without special characters
- [ ] **SC-012**: Site deployable to GitHub Pages without manual edits

---

## Notes for Implementation

### WSL Environment Considerations

- All commands should work in WSL (Windows Subsystem for Linux)
- Ensure Node.js 18+ is installed in WSL, not Windows
- Use WSL paths (`/mnt/d/...`) for file operations
- Browser auto-open may not work in WSL; manually open http://localhost:3000
- Hot reload should work normally in WSL

### Git Workflow

- Create feature branch `001-docusaurus-frontend` before starting
- Commit after completing each phase (not each task, to reduce commit noise)
- Use descriptive commit messages referencing task numbers
- Example: "feat: complete Phase 1 foundation setup (tasks 1-5)"

### Common Issues & Solutions

1. **"Port 3000 is already in use"**: Kill existing process or use `npm start -- --port 3001`
2. **TypeScript errors blocking build**: Use `// @ts-ignore` temporarily, fix later
3. **MDX import errors**: Ensure `@site/` alias is configured in `tsconfig.json`
4. **Component not rendering in MDX**: Check MDX file extension (should be `.mdx` not `.md`)
5. **CSS not applying**: Ensure CSS Modules file is imported in component, check class name syntax

### Performance Tips

- Use `React.memo()` for TextSelectionTooltip to prevent unnecessary re-renders
- Debounce text selection event handler (100ms delay)
- Use CSS transforms (not top/left) for animations (better performance)
- Profile with Chrome DevTools if any interaction feels sluggish

### Testing Strategy

- Manual testing is sufficient for this phase (no automated tests required)
- Focus on happy path flows first, then edge cases
- Test on multiple screen sizes (375px, 768px, 1024px, 1920px)
- Test in both light and dark modes if Docusaurus theme supports it

---

## Task Summary

| Phase | Tasks | Est. Time | Dependencies |
|-------|-------|-----------|--------------|
| Phase 1: Foundation Setup | 1-5 | 45 min | None |
| Phase 2: Documentation Structure | 6-11 | 1h 15min | Phase 1 |
| Phase 3: Navigation & Sidebar | 12 | 10 min | Phase 2 |
| Phase 4: Homepage | 13 | 45 min | Phase 1 |
| Phase 5: Reusable Components | 14-18 | 2h 30min | Phase 1 |
| Phase 6: Global Selection Detection | 19 | 1h | Phase 5 |
| Phase 7: Responsive Polish & Testing | 20-22 | 1h 30min | Phases 5-6 |
| Phase 8: Deployment Preparation | 23-24 | 30 min | Phase 7 |
| **TOTAL** | **24 tasks** | **~8h 30min** | Sequential with 7 parallelizable |

---

**End of Task List**
