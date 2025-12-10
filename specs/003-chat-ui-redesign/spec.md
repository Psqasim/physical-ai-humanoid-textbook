# Feature Specification: Study Assistant UI Redesign

**Feature Branch**: `003-chat-ui-redesign`
**Created**: 2025-12-08
**Status**: Draft
**Input**: User description: "Redesign Study Assistant chat UI to be modern, responsive, and professional while keeping all backend functionality unchanged"

## Executive Summary

The Study Assistant chat feature currently works well functionally (RAG backend, whole-book Q&A, selection-based Q&A) but has significant UI/UX issues that make it unprofessional and unusable on mobile devices. This specification defines a complete visual redesign that transforms the chat interface into a modern, responsive, theme-aware component that matches Docusaurus design standards while maintaining 100% functional compatibility with existing backend systems.

**Core Principle**: Structure-Before-Content - we're changing the presentation layer only, not the logic.

## User Scenarios & Testing

### User Story 1 - Mobile Student Accesses Study Assistant (Priority: P1)

A student studying on their phone (iPhone SE, 375px width) navigates to any chapter, taps the floating chat button, and uses the Study Assistant to ask questions about the content.

**Why this priority**: Mobile is critical - most students study on phones during commutes or breaks. Current UI is completely broken on mobile (panel overflows, button overlaps content, input hidden by keyboard).

**Independent Test**: Load textbook on mobile device (375px), open chat, send message, receive response with citations, close chat. All UI elements must be accessible and functional.

**Acceptance Scenarios**:

1. **Given** student is on any textbook page on mobile (375px), **When** they tap the floating chat button, **Then** the chat panel slides in smoothly from the right, occupies 100% width with proper padding, and the floating button hides or repositions to avoid overlap.

2. **Given** chat panel is open on mobile, **When** student types in the input field, **Then** the keyboard appears without hiding the input area, messages scroll properly, and the send button remains accessible.

3. **Given** student receives a response with citations on mobile, **When** they scroll the message, **Then** citation cards are readable (not cut off), tappable, and navigate correctly when clicked.

4. **Given** student wants to close the chat on mobile, **When** they tap the X button or swipe the panel, **Then** panel slides out smoothly and page content is fully accessible again.

---

### User Story 2 - Desktop Student Uses Selection-Based Q&A (Priority: P1)

A student reading a complex section on desktop highlights a paragraph, clicks the "Ask about this" tooltip, and gets an AI explanation specific to that selected text.

**Why this priority**: Selection-based Q&A is a key differentiator and power feature. Current tooltip is awkward and unclear, leading to low adoption.

**Independent Test**: On desktop, select text on any page, verify tooltip appears correctly positioned, click "Ask about this", verify chat panel opens in selection mode with the selected text visible, send question, receive contextual response.

**Acceptance Scenarios**:

1. **Given** student is reading on desktop, **When** they select text (10+ characters), **Then** a modern tooltip appears above/below selection with smooth fade-in, showing first 50 chars of selection and a clear "Ask about this" button.

2. **Given** tooltip is visible, **When** student clicks "Ask about this" button, **Then** chat panel opens in selection mode, the selected text is displayed as context in the chat, and the input is focused for immediate typing.

3. **Given** tooltip is visible, **When** student clicks outside or presses Escape, **Then** tooltip dismisses smoothly with fade-out animation.

4. **Given** student asks a question in selection mode, **When** AI responds, **Then** the response clearly indicates it's based on the selected text, and citations reference the specific section.

---

### User Story 3 - Student Asks Question in Whole-Book Mode (Priority: P2)

A student opens the Study Assistant without selecting text and asks a general question like "How does ROS 2 handle sensor fusion?" expecting an answer that draws from multiple chapters.

**Why this priority**: Whole-book mode is the default use case for general questions. Current UI works but lacks visual polish and clear loading states.

**Independent Test**: Open chat without text selection, verify default mode is "Whole-book Q&A", send question, observe loading indicator, receive response with citations from multiple chapters, verify citations are visually distinct and clickable.

**Acceptance Scenarios**:

1. **Given** chat panel is opened without text selection, **When** panel loads, **Then** mode selector shows "Whole-book Q&A" active, input placeholder says "Ask anything about the textbook...", and empty state shows helpful prompt.

2. **Given** student types a question and clicks send, **When** request is processing, **Then** input is disabled, send button shows loading spinner, and animated typing dots appear in chat area indicating AI is thinking.

3. **Given** AI finishes processing, **When** response arrives, **Then** message fades in smoothly, citations appear as distinct cards (not plain text), and each citation shows doc title, section heading, and snippet preview.

4. **Given** student clicks a citation card, **When** navigation occurs, **Then** page navigates to the cited section, citation is highlighted (if possible), and chat panel remains accessible.

---

### User Story 4 - Student Switches Between Light and Dark Mode (Priority: P2)

A student who prefers dark mode at night and light mode during the day switches themes using Docusaurus theme toggle and expects chat UI to adapt seamlessly.

**Why this priority**: Theme consistency is critical for professional appearance and accessibility. Current chat UI doesn't properly adapt to both modes.

**Independent Test**: With chat panel open and messages visible, toggle Docusaurus theme from light to dark and back. Verify all chat UI elements (panel background, message bubbles, borders, text, buttons) use correct theme colors without page reload.

**Acceptance Scenarios**:

1. **Given** chat panel is open in light mode, **When** student toggles to dark mode, **Then** chat background becomes dark, message bubbles adapt (user messages darker, AI messages lighter), text remains readable (proper contrast), and all interactive elements show correct theme colors.

2. **Given** citations are visible, **When** theme is toggled, **Then** citation cards adapt their background, border, and text colors to match the new theme while maintaining readability.

3. **Given** chat panel is open, **When** theme is toggled, **Then** transition is smooth (no flash of wrong colors), and theme preference persists across page navigation.

---

### User Story 5 - Student on Tablet Uses Chat in Landscape Mode (Priority: P3)

A student using an iPad in landscape mode (1024px width) opens the Study Assistant and expects an optimal layout that doesn't waste space or feel cramped.

**Why this priority**: Tablet is an edge case but important for accessibility. Current UI either wastes space or feels cramped depending on orientation.

**Independent Test**: Load textbook on tablet (768-1024px), open chat in both portrait and landscape, verify panel width is optimal (not too wide/narrow), messages are readable, and input area is properly sized.

**Acceptance Scenarios**:

1. **Given** student is on tablet in landscape (1024px), **When** they open chat panel, **Then** panel occupies ~40-50% of screen width (not full width), positioned on the right, with proper padding and readable message width.

2. **Given** tablet is in portrait (768px), **When** chat panel opens, **Then** panel occupies ~80-90% of screen width, leaving a small margin to show underlying page, and content remains accessible.

---

### Edge Cases

**Display & Rendering:**
- What happens when a message contains very long words (e.g., URLs, code snippets) that could break layout?
  - **Solution**: Apply `word-break: break-word` and `overflow-wrap: anywhere` to message content.

- What happens when AI response is extremely long (e.g., 5000+ characters)?
  - **Solution**: Message area scrolls independently, with smooth scroll-to-bottom on new messages.

- What happens when a citation has a very long heading or snippet?
  - **Solution**: Citation cards have max-height with ellipsis for heading, snippet truncated to 150 chars with "..." indicator.

**Interaction:**
- What happens when student rapidly clicks send button multiple times?
  - **Solution**: Button is disabled during loading, subsequent clicks are ignored until response arrives.

- What happens when student closes chat panel while AI is responding?
  - **Solution**: Request continues in background, response is stored, chat reopens to show completed conversation.

- What happens when student selects text while chat panel is already open?
  - **Solution**: Tooltip does not appear if chat is open (to avoid confusion), or tooltip shows "Switch to selection mode" option.

**Network & Errors:**
- What happens when backend API is unreachable?
  - **Solution**: Error message appears in chat: "Unable to connect. Please check your connection and try again." with a "Retry" button.

- What happens when API returns 500 error?
  - **Solution**: Error message: "Something went wrong. Please try again." Message is styled distinctly (red border, alert icon).

- What happens when request times out after 30 seconds?
  - **Solution**: Loading indicator stops, error message: "Request timed out. Please try again with a shorter question."

**Accessibility:**
- What happens when student navigates chat using only keyboard (Tab, Enter, Escape)?
  - **Solution**: All interactive elements (buttons, citations, mode toggle) are focusable with clear focus indicators. Enter sends message, Escape closes panel.

- What happens when screen reader user opens chat?
  - **Solution**: Panel announces "Study Assistant opened", messages have ARIA labels, loading states are announced ("AI is typing...").

**Theme & Appearance:**
- What happens when custom Docusaurus theme uses non-standard colors?
  - **Solution**: Chat uses CSS variables from Docusaurus (`--ifm-color-*`), inheriting custom theme colors automatically.

## Requirements

### Functional Requirements

**Core Chat Functionality (Unchanged):**
- **FR-001**: System MUST maintain 100% functional compatibility with existing RAG backend API at `/chat` endpoint
- **FR-002**: System MUST support both "whole-book" and "selection" modes as currently implemented
- **FR-003**: System MUST send and receive messages using existing `ChatRequest` and `ChatResponse` interfaces
- **FR-004**: System MUST display citations received from backend without modifying citation data structure
- **FR-005**: System MUST preserve all existing props and state management (`isOpen`, `onClose`, `selectedText`, `initialMode`)

**Responsive Design:**
- **FR-006**: Chat panel MUST be fully functional on mobile devices (320px+ width)
- **FR-007**: Chat panel MUST adapt layout for tablet devices (768px-1024px width)
- **FR-008**: Chat panel MUST optimize layout for desktop devices (1024px+ width)
- **FR-009**: Floating chat button MUST scale and reposition appropriately across all screen sizes
- **FR-010**: Input area MUST remain accessible when virtual keyboard appears on mobile devices

**Visual Design:**
- **FR-011**: User messages MUST be visually distinct from AI messages (different alignment, background color, or styling)
- **FR-012**: Messages MUST display in chronological order with clear visual separation
- **FR-013**: System MUST show loading indicator (animated typing dots) when waiting for AI response
- **FR-014**: Messages MUST fade in smoothly when sent or received (300ms animation)
- **FR-015**: Chat panel MUST slide in from right side of screen when opened (300ms animation)

**Citations Display:**
- **FR-016**: Citations MUST be displayed as visually distinct cards (not plain text links)
- **FR-017**: Each citation card MUST show: document title, section heading, and snippet preview
- **FR-018**: Citation cards MUST be clickable and navigate to the referenced document section
- **FR-019**: Citation cards MUST have hover effect on desktop and tap highlight on mobile
- **FR-020**: Citations MUST display a clear icon indicating they are source references

**Text Selection Tooltip:**
- **FR-021**: Tooltip MUST appear when user selects text (10+ characters) on any textbook page
- **FR-022**: Tooltip MUST show first 50 characters of selected text as preview
- **FR-023**: Tooltip MUST display clear "Ask about this" call-to-action button
- **FR-024**: Tooltip MUST position itself above or below selection without overlapping
- **FR-025**: Tooltip MUST be dismissible by clicking outside, pressing Escape, or clicking X button
- **FR-026**: Tooltip MUST fade in smoothly on appearance (200ms) and fade out on dismiss (150ms)

**Theme Integration:**
- **FR-027**: Chat UI MUST use Docusaurus CSS variables for all colors (`--ifm-color-*`, `--ifm-background-*`)
- **FR-028**: Chat UI MUST adapt to both light and dark themes without requiring page reload
- **FR-029**: Chat UI MUST match Docusaurus design language (borders, shadows, border-radius)
- **FR-030**: All text in chat UI MUST meet WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text)

**Accessibility:**
- **FR-031**: All interactive elements MUST be keyboard navigable (Tab, Enter, Escape)
- **FR-032**: All interactive elements MUST show clear focus indicators when focused
- **FR-033**: Chat panel MUST announce state changes to screen readers (opened, closed, loading, error)
- **FR-034**: Messages MUST have appropriate ARIA labels ("User message", "AI response")
- **FR-035**: Loading state MUST announce "AI is typing" to screen readers

**Performance:**
- **FR-036**: Chat panel animation MUST run at 60fps (use GPU-accelerated properties: transform, opacity)
- **FR-037**: Message rendering MUST not cause layout reflow (use fixed dimensions where possible)
- **FR-038**: Chat panel MUST load without blocking page render (lazy load if possible)

### Key Entities

**Message:**
- Represents a single message in the chat conversation
- Attributes:
  - `role`: 'user' or 'assistant' (indicates sender)
  - `text`: Message content (string, can be long)
  - `citations`: Optional array of citation objects
- Relationships: Messages are displayed in chronological order in the conversation

**Citation:**
- Represents a source reference from AI response
- Attributes:
  - `docPath`: Path to the referenced document (e.g., "/docs/chapter1/sensors")
  - `heading`: Section heading within the document (e.g., "Lidar Sensors")
  - `snippet`: Text preview from the referenced section (150 chars max display)
- Relationships: Multiple citations can be attached to a single assistant message

**ChatMode:**
- Represents the current operating mode of the chat
- Values:
  - `'whole-book'`: AI can answer from entire textbook corpus
  - `'selection'`: AI answers based on user-selected text as context
- Behavior: Mode affects API request and UI display (shows selected text in selection mode)

**Theme State:**
- Represents current Docusaurus theme (inherited from global context)
- Values: `'light'` or `'dark'`
- Behavior: All chat UI colors and styles adapt based on this state

## Success Criteria

### Measurable Outcomes

**Functionality:**
- **SC-001**: All existing chat functionality works identically to current implementation (100% feature parity)
- **SC-002**: Chat panel is fully functional on iPhone SE (375px width) - verified by manual testing
- **SC-003**: Chat panel is fully functional on iPad (768px width) - verified by manual testing
- **SC-004**: Chat panel is fully functional on desktop (1440px+ width) - verified by manual testing
- **SC-005**: Zero console errors or warnings related to chat component rendering

**Visual Quality:**
- **SC-006**: All color contrast ratios meet WCAG AA standards - verified with contrast checker tool
- **SC-007**: Chat panel matches Docusaurus theme in both light and dark modes - verified by visual inspection
- **SC-008**: All animations run at 60fps - verified with Chrome DevTools Performance tab
- **SC-009**: User and AI messages are clearly visually distinct - confirmed by peer review

**User Experience:**
- **SC-010**: Students can complete a full chat interaction (open, ask, receive, close) on mobile in under 30 seconds
- **SC-011**: Citation cards are immediately recognizable as clickable sources - confirmed by user testing
- **SC-012**: Loading states are clear and don't cause confusion - no "is it working?" questions from testers
- **SC-013**: Text selection tooltip appears within 100ms of text selection on desktop

**Accessibility:**
- **SC-014**: All interactive elements are reachable via keyboard navigation (Tab)
- **SC-015**: Screen reader announces all critical state changes (opened, loading, error, message received)
- **SC-016**: Focus indicators are visible on all interactive elements

**Performance:**
- **SC-017**: Chat panel opens in under 300ms (animation time)
- **SC-018**: No layout shift when messages are added (CLS score remains low)
- **SC-019**: Chat component bundle size increase is under 5KB (CSS + minimal markup changes only)

## Technical Approach

### Architecture Overview

**Unchanged Components:**
- Backend RAG API (`/chat` endpoint)
- API request/response interfaces (`ChatRequest`, `ChatResponse`)
- State management logic (React hooks for `messages`, `loading`, `error`, `mode`)
- Props interface (`ChatPanelPlaceholderProps`)

**Changed Components:**
- `ChatPanelPlaceholder.tsx`: JSX structure redesigned for better layout and visual hierarchy
- `ChatPanelPlaceholder.module.css`: Complete rewrite with mobile-first responsive design
- `TextSelectionTooltip.tsx`: JSX updated for modern tooltip design
- `TextSelectionTooltip.module.css`: Complete rewrite for positioning and animations
- `FloatingChatButton.tsx` (if exists): Minor style updates for consistency

**New Components** (extracted for modularity):
- `CitationCard.tsx` + `CitationCard.module.css`: Displays individual citation with doc title, section, snippet
- `LoadingIndicator.tsx` + `LoadingIndicator.module.css`: Animated typing dots ("AI is typing...")
- `ErrorMessage.tsx` + `ErrorMessage.module.css`: Inline error display with retry button
- Location: Same directory as `ChatPanelPlaceholder.tsx` (no subdirectory)

### Design Specifications

**Chat Panel Layout:**

```
┌─────────────────────────────────────┐
│  Study Assistant            [Mode]  │  ← Header (fixed)
│                                 [X] │
├─────────────────────────────────────┤
│                                     │
│  [Empty State / Messages Area]      │  ← Scrollable content
│                                     │
│  User: "How does ROS 2 work?"       │
│  AI: "ROS 2 is..."                  │
│    📄 Citation 1                    │
│    📄 Citation 2                    │
│                                     │
│  [Loading: ● ● ● ]                  │  ← Only when loading
│                                     │
├─────────────────────────────────────┤
│  [Input field]           [Send]     │  ← Input area (fixed)
└─────────────────────────────────────┘

Desktop: 450px width, slide from right
Tablet:  80% width, slide from right
Mobile:  100% width, slide from right
```

**Message Bubble Design:**

```
User message:                AI message:
┌────────────────────┐       ┌────────────────────┐
│ How does ROS 2     │       │ ROS 2 is a robot   │
│ handle navigation? │       │ framework that...  │
└────────────────────┘       │                    │
     (Align right)           │ 📄 Citation 1      │
     (Blue/Primary color)    │ 📄 Citation 2      │
                             └────────────────────┘
                                  (Align left)
                                  (Gray/Surface color)
```

**Citation Card Design:**

```
┌──────────────────────────────────────────┐
│ 📄  Introduction to ROS 2                │  ← Doc title (bold)
│     Navigation Stack                     │  ← Section heading
│     "The navigation stack provides..."   │  ← Snippet (gray, italic)
│                                      → │  ← Hover: underline, pointer
└──────────────────────────────────────────┘
```

**Text Selection Tooltip:**

```
       Selected text: "ROS 2 provides..."
                  ↓
      ┌──────────────────────────┐
      │  "ROS 2 provides..."  [X]│  ← Preview (truncated)
      │  [💬 Ask about this]     │  ← CTA button
      └──────────────────────────┘
              ▼ (arrow)
```

**Loading Indicator:**

```
AI is typing...
  ● ● ●  (animated bounce/fade)
```

### Responsive Breakpoints

```css
/* Mobile-first approach */
.chatPanel {
  width: 100%; /* Mobile: 320-575px */
}

@media (min-width: 576px) {
  .chatPanel {
    width: 90%; /* Small tablets: 576-767px */
  }
}

@media (min-width: 768px) {
  .chatPanel {
    width: 80%; /* Tablets: 768-991px */
    max-width: 500px;
  }
}

@media (min-width: 992px) {
  .chatPanel {
    width: 450px; /* Desktop: 992px+ */
  }
}
```

### Color System

**Implementation Approach**: Use Docusaurus CSS variables directly with fallback values for graceful degradation. All chat UI colors reference `--ifm-*` variables to ensure automatic theme adaptation.

**Required Variables** (from Docusaurus theme):
- `--ifm-background-surface-color`: Panel background
- `--ifm-color-primary-lightest` / `--ifm-color-primary-darkest`: User message bubbles
- `--ifm-color-emphasis-100` / `--ifm-color-emphasis-200`: AI message bubbles
- `--ifm-color-emphasis-300`: Borders and dividers
- `--ifm-color-content`: Text color
- `--ifm-color-primary`: Interactive elements (buttons, links)

**Implementation Pattern**:
```css
/* Use Docusaurus variables with fallbacks */
.chatPanel {
  background: var(--ifm-background-surface-color, #ffffff);
  border: 1px solid var(--ifm-color-emphasis-300, #e0e0e0);
  color: var(--ifm-color-content, #1c1e21);
}

.userMessage {
  background: var(--ifm-color-primary-lightest, #e7f2ff);
}

.aiMessage {
  background: var(--ifm-color-emphasis-100, #f5f5f5);
}
```

**Note**: Hex values shown are fallbacks only. Actual colors are determined by the active Docusaurus theme configuration.

### Animation Specifications

```css
/* Panel slide-in */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.chatPanel {
  animation: slideInRight 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Message fade-in */
.message {
  animation: fadeIn 300ms ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Typing indicator */
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

.typingDot {
  animation: bounce 1.4s infinite;
  animation-delay: calc(var(--i) * 0.2s);
}
```

## Visual Mockups

### Mockup 1: Empty State (First Open)

**Context**: Student opens Study Assistant for the first time, no messages yet.

```
┌─────────────────────────────────────────┐
│  Study Assistant      [Whole-book ▼] [X]│
├─────────────────────────────────────────┤
│                                         │
│          💬                             │
│                                         │
│    Welcome to Study Assistant!          │
│                                         │
│    Ask me anything about:               │
│    • ROS 2 fundamentals                 │
│    • Sensor integration                 │
│    • Navigation algorithms              │
│    • Computer vision                    │
│    • And more...                        │
│                                         │
│    Or select text on any page to ask    │
│    specific questions.                  │
│                                         │
├─────────────────────────────────────────┤
│  Ask anything about the textbook... [→]│
└─────────────────────────────────────────┘
```

**Key Elements:**
- Centered welcome icon and text
- Helpful example topics (educational context)
- Clear prompt to start asking
- Mode selector shows "Whole-book" by default
- Input is ready and focused

---

### Mockup 2: Loading State (AI Thinking)

**Context**: Student sent a question, waiting for AI response.

```
┌─────────────────────────────────────────┐
│  Study Assistant      [Whole-book ▼] [X]│
├─────────────────────────────────────────┤
│                                         │
│                  ┌──────────────────┐   │
│                  │ How does ROS 2   │   │
│                  │ handle messages? │   │
│                  └──────────────────┘   │
│                                         │
│  ● ● ●  AI is typing...                 │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│  [Input disabled]                   [⊙]│
└─────────────────────────────────────────┘
```

**Key Elements:**
- User message aligned right, styled with primary color
- Animated typing indicator (3 dots bouncing)
- "AI is typing..." text for clarity
- Input field disabled (grayed out)
- Send button shows loading spinner

---

### Mockup 3: Response with Citations

**Context**: AI provided answer with 2 citations from different chapters.

```
┌─────────────────────────────────────────┐
│  Study Assistant      [Whole-book ▼] [X]│
├─────────────────────────────────────────┤
│                                         │
│                  ┌──────────────────┐   │
│                  │ How does ROS 2   │   │
│                  │ handle messages? │   │
│                  └──────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ ROS 2 uses a publish-subscribe   │   │
│  │ messaging model with DDS. Nodes   │   │
│  │ communicate by publishing to      │   │
│  │ topics and subscribing to them.   │   │
│  │                                   │   │
│  │ ┌─────────────────────────────┐  │   │
│  │ │ 📄 ROS 2 Basics             │  │   │
│  │ │    Communication Patterns    │  │   │
│  │ │    "Topics are named buses..."│  │   │
│  │ └─────────────────────────────┘  │   │
│  │                                   │   │
│  │ ┌─────────────────────────────┐  │   │
│  │ │ 📄 Advanced ROS 2           │  │   │
│  │ │    DDS Configuration         │  │   │
│  │ │    "DDS provides Quality of..."│  │   │
│  │ └─────────────────────────────┘  │   │
│  └─────────────────────────────────┘   │
│                                         │
├─────────────────────────────────────────┤
│  Ask a follow-up question...        [→]│
└─────────────────────────────────────────┘
```

**Key Elements:**
- AI message aligned left, distinct background color
- Citations displayed as cards within message
- Each citation shows: icon, doc title, section, snippet
- Citations have subtle border and hover effect
- Input re-enabled for follow-up questions

---

### Mockup 4: Selection Mode with Context

**Context**: Student selected text and asked a question about it.

```
┌─────────────────────────────────────────┐
│  Study Assistant      [Selection ▼]  [X]│
├─────────────────────────────────────────┤
│  📌 Selected text:                      │
│  "ROS 2 provides real-time capabilities │
│   through DDS middleware..."            │
│                                         │
│                  ┌──────────────────┐   │
│                  │ What are the     │   │
│                  │ benefits of DDS? │   │
│                  └──────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Based on the selected text, DDS  │   │
│  │ provides several key benefits... │   │
│  │                                   │   │
│  │ ┌─────────────────────────────┐  │   │
│  │ │ 📄 Middleware Overview      │  │   │
│  │ │    DDS Architecture          │  │   │
│  │ │    "DDS enables real-time..." │  │   │
│  │ └─────────────────────────────┘  │   │
│  └─────────────────────────────────┘   │
│                                         │
├─────────────────────────────────────────┤
│  Ask about this selection...        [→]│
└─────────────────────────────────────────┘
```

**Key Elements:**
- Mode badge shows "Selection" (different color, e.g., green)
- Selected text displayed at top with pin icon
- AI response explicitly references selected context
- Input placeholder says "Ask about this selection..."
- User can switch back to whole-book mode via dropdown

---

### Mockup 5: Mobile Layout (375px)

**Context**: Same conversation on iPhone SE.

```
┌─────────────────────────┐
│ Study Assistant    [☰][X]│
│ [Whole-book ▼]          │
├─────────────────────────┤
│                         │
│            ┌─────────┐  │
│            │ How does│  │
│            │ ROS 2   │  │
│            │ work?   │  │
│            └─────────┘  │
│                         │
│ ┌─────────────────────┐ │
│ │ ROS 2 is a robot    │ │
│ │ framework that...   │ │
│ │                     │ │
│ │ ┌─────────────────┐ │ │
│ │ │ 📄 ROS 2 Basics │ │ │
│ │ │    Getting      │ │ │
│ │ │    Started      │ │ │
│ │ │    "ROS 2..."   │ │ │
│ │ └─────────────────┘ │ │
│ └─────────────────────┘ │
│                         │
├─────────────────────────┤
│ Ask...          [→]     │
└─────────────────────────┘
```

**Key Elements:**
- Full-width panel (no side margin)
- Mode selector compressed (hamburger menu icon)
- Larger touch targets (48px minimum)
- Citation cards stack vertically
- Input and button sized for thumb reach
- Shorter text in UI (truncated headings)

---

### Mockup 6: Text Selection Tooltip (Desktop)

**Context**: Student hovers over selected text on chapter page.

```
Page content with selected text:
"ROS 2 provides real-time [SELECTED: capabilities through DDS middleware] which enables..."

         ┌─────────────────────────────────┐
         │ "capabilities through DDS..."[X]│
         │                                 │
         │  [💬 Ask about this selection]  │
         └─────────────────────────────────┘
                        ▼
```

**Key Elements:**
- Tooltip appears above selection (or below if no space above)
- Shows truncated preview of selected text (first 50 chars)
- Clear CTA button with chat icon
- Close button (X) in top-right
- Subtle shadow for depth
- Rounded corners matching Docusaurus style
- Fade-in animation (200ms)

## Out of Scope

The following features are explicitly **not included** in this redesign and will be addressed in future features:

1. **Chat History Sidebar**: Saving conversation history, showing previous chats, resuming old conversations (requires authentication system)

2. **Message Editing/Deletion**: Ability to edit sent messages or delete messages from conversation

3. **File Uploads**: Uploading PDFs, images, or other documents to ask questions about them

4. **Voice Input/Output**: Speech-to-text for asking questions, text-to-speech for reading answers

5. **Multi-language UI**: Translating the chat interface itself to other languages (AI can already respond in different languages)

6. **Emoji Reactions**: Adding reactions (👍, ❤️, etc.) to AI responses

7. **Message Sharing**: Copying, exporting, or sharing chat conversations

8. **Advanced Formatting**: Markdown rendering, code syntax highlighting, LaTeX math in messages (future enhancement)

9. **Conversation Branching**: Creating multiple conversation threads or branching from specific messages

10. **Backend Changes**: Any modifications to RAG logic, embedding models, vector database, or API structure

## Clarifications

### Session 2025-12-08

- Q: Exact Color Values for Theme Variables - Should we use hardcoded hex values from spec examples, CSS variables with fallbacks, or custom chat-specific CSS variables? → A: Use CSS variables with fallbacks and document the actual Docusaurus variables used in our theme. This ensures automatic theme adaptation and consistency with future theme updates.

- Q: New Component Files Creation - Should we keep all UI within ChatPanelPlaceholder.tsx, extract new components in same directory, or create a new subdirectory? → A: Extract new components for CitationCard, LoadingIndicator, ErrorMessage in same directory. This provides modularity for testing and reuse while keeping related files together.

- Q: Testing Approach - Manual vs Automated Priority - Should v1 be purely manual, include automated tests for critical logic only, or require full automated test suite? → A: Write automated tests only for critical business logic (API calls, state management), defer UI component tests. This balances speed with quality and allows catching regressions without slowing down the visual redesign focus.

- Q: Rollback Plan if New UI Has Issues - Should rollback be via git revert, feature flag toggle, or gradual A/B rollout? → A: Feature flag to toggle between old and new UI, keep old code for 1 sprint. This provides instant rollback without redeployment if critical issues emerge, with cleanup after validation.

## Testing Strategy

### Manual Testing Checklist

**Responsive Design Testing:**
- [ ] Test on iPhone SE (375px width): Chat panel opens, messages display, input accessible with keyboard
- [ ] Test on iPhone 12 Pro (390px width): Same as above
- [ ] Test on iPad Mini (768px portrait): Panel width appropriate, layout not cramped
- [ ] Test on iPad Pro (1024px landscape): Panel width ~40%, messages readable
- [ ] Test on MacBook (1440px): Panel width 450px, optimal reading experience
- [ ] Test on 4K display (2560px): Chat panel maintains max-width, doesn't stretch excessively

**Theme Testing:**
- [ ] Load page in light mode, open chat: All colors readable, proper contrast
- [ ] Toggle to dark mode with chat open: Colors transition smoothly, no flash
- [ ] Send message in dark mode: User and AI bubbles have correct dark mode colors
- [ ] Click citation in dark mode: Citation card uses dark mode colors
- [ ] Reload page in dark mode: Chat opens with dark mode colors immediately

**Functionality Testing (Whole-book Mode):**
- [ ] Open chat without text selection: Default mode is "Whole-book Q&A"
- [ ] Type question and press Enter: Message sends, loading indicator appears
- [ ] Wait for response: Loading stops, AI message fades in
- [ ] Response includes citations: Citations display as cards with doc title, section, snippet
- [ ] Click citation card: Navigates to correct section in textbook
- [ ] Send follow-up question: Conversation continues, new messages append

**Functionality Testing (Selection Mode):**
- [ ] Select text (20 characters) on any page: Tooltip appears above/below selection
- [ ] Click "Ask about this" in tooltip: Chat opens in selection mode, selected text shown
- [ ] Ask question in selection mode: AI responds with context from selected text
- [ ] Switch mode dropdown to "Whole-book": Mode changes, selected text context hidden
- [ ] Close chat and select different text: Tooltip appears again

**Loading States:**
- [ ] Send message: Input disables, send button shows spinner, typing dots appear
- [ ] Response arrives: Loading stops, input re-enables, message appears
- [ ] Send another message while first is loading: Second send attempt is ignored (button disabled)

**Error Handling:**
- [ ] Disconnect network, send message: Error message appears in chat, "Retry" button shown
- [ ] Click "Retry" button: Message resends, loading indicator appears
- [ ] Backend returns 500 error: Error message appears, conversation remains accessible

**Accessibility Testing:**
- [ ] Tab through chat UI: All buttons, input, citations are focusable
- [ ] Focus indicators visible: Clear outline or highlight on focused elements
- [ ] Press Enter in input: Message sends
- [ ] Press Escape with chat open: Chat panel closes
- [ ] Use screen reader (NVDA/VoiceOver): Panel announces "Study Assistant opened", messages have labels
- [ ] Check contrast ratios: All text meets WCAG AA (4.5:1 for normal, 3:1 for large)

**Animation Testing:**
- [ ] Open chat: Panel slides in from right in 300ms, smooth motion
- [ ] Close chat: Panel slides out to right in 300ms
- [ ] New message appears: Fades in over 300ms
- [ ] Loading dots: Bounce animation is smooth, not janky
- [ ] Open DevTools Performance: Record animation, verify 60fps (no dropped frames)

**Edge Cases:**
- [ ] Send message with 5000 characters: Message displays with scroll, doesn't break layout
- [ ] Send URL (100 characters, no spaces): Word breaks properly, doesn't overflow bubble
- [ ] Receive response with 10 citations: All citations display, scrollable if needed
- [ ] Citation with 200-character heading: Heading truncates with ellipsis
- [ ] Rapidly click send 10 times: Only one request sent, button remains disabled
- [ ] Close chat while AI is responding: Reopen chat, response is present

### Automated Testing (v1 - Critical Logic Only)

**Priority for v1**: Write automated tests for critical business logic to catch regressions. UI component tests are deferred to future iterations.

**Critical Logic Tests (Required for v1)**:

```typescript
// Test API call logic and state management
describe('Chat API Integration', () => {
  test('sends message to /chat endpoint with correct payload', async () => {
    // Test ChatRequest structure, mode selection, selectedText handling
  });

  test('handles successful response and updates messages state', async () => {
    // Test ChatResponse parsing, citations extraction
  });

  test('handles network errors with retry capability', async () => {
    // Test error state management, retry logic
  });

  test('handles 30-second timeout', async () => {
    // Test timeout logic with AbortController
  });
});

describe('Chat State Management', () => {
  test('switches between whole-book and selection modes correctly', () => {
    // Test mode state changes, persistence across messages
  });

  test('maintains conversation history when mode switches', () => {
    // Test messages array persistence
  });

  test('disables input during loading state', () => {
    // Test loading state, button disabled logic
  });
});
```

**UI Component Tests (Deferred to Future)**:
- Visual rendering tests (snapshot tests)
- Animation timing tests
- Responsive layout tests
- Accessibility tests (ARIA, keyboard navigation)
- Theme adaptation tests

## Deployment & Rollback Strategy

**Approach**: Feature flag deployment with old UI preserved for safety.

**Implementation**:
1. **Feature Flag**: Add `enableNewChatUI` flag (default: `false`)
   - Location: Configuration file or environment variable
   - Controls which UI version loads: `<ChatPanelPlaceholder />` (new) vs `<ChatPanelPlaceholderLegacy />` (old)

2. **Code Organization**:
   - Keep old UI files: Rename current files to `*.legacy.tsx` and `*.legacy.module.css`
   - New UI uses original filenames
   - Flag check at import/render level

3. **Rollback Process**:
   - **Instant rollback**: Toggle flag to `false` (no redeployment needed)
   - **Gradual rollout**: Start with flag `true` for internal users, then expand
   - **Cleanup**: Remove legacy code after 1 sprint (2 weeks) of stable new UI

4. **Monitoring**:
   - Track console errors by UI version
   - Monitor user feedback channels
   - Set up alerts for critical failures

**Timeline**: Keep old code until **[DATE + 2 weeks]**, then remove if no issues.

## Implementation Plan

This specification will be followed by a detailed `tasks.md` file that breaks down the implementation into testable, atomic tasks following the red-green-refactor TDD cycle.

**High-level Implementation Phases:**

1. **Phase 1 - Foundation** (2-3 hours)
   - Rewrite `ChatPanelPlaceholder.module.css` with mobile-first responsive structure
   - Update panel layout structure in `ChatPanelPlaceholder.tsx` (header, body, footer)
   - Implement theme-aware color system using Docusaurus CSS variables
   - Test: Panel opens/closes on all screen sizes, colors adapt to theme

2. **Phase 2 - Message Display** (2-3 hours)
   - Redesign message bubble components (user vs AI styling)
   - Implement message fade-in animation
   - Add loading indicator (typing dots with animation)
   - Style empty state with helpful prompt
   - Test: Messages display correctly, animations smooth, loading state clear

3. **Phase 3 - Citations** (2 hours)
   - Redesign citation as card component with icon, title, section, snippet
   - Implement hover/tap styles for citations
   - Add navigation handling on citation click
   - Test: Citations are visually distinct, clickable, navigate correctly

4. **Phase 4 - Text Selection Tooltip** (1-2 hours)
   - Rewrite `TextSelectionTooltip.module.css` with modern design
   - Update tooltip JSX structure (preview, button, close)
   - Implement fade-in/fade-out animations
   - Improve positioning logic (above/below selection)
   - Test: Tooltip appears on selection, positions correctly, opens chat

5. **Phase 5 - Input Area** (1 hour)
   - Style input field and send button
   - Implement button disabled state and loading spinner
   - Ensure input remains accessible on mobile (above keyboard)
   - Test: Input works on mobile with keyboard, button states clear

6. **Phase 6 - Accessibility** (1 hour)
   - Add ARIA labels to all interactive elements
   - Implement keyboard navigation (Tab, Enter, Escape)
   - Add focus indicators
   - Test with screen reader and keyboard-only navigation

7. **Phase 7 - Polish & Testing** (2 hours)
   - Fine-tune animations and transitions
   - Test across all devices and themes
   - Fix any edge cases discovered during testing
   - Verify all success criteria are met

**Total Estimated Time**: 11-14 hours

## Approval & Next Steps

This specification requires approval before proceeding to implementation.

**Approval Checklist:**
- [ ] User requirements accurately captured
- [ ] Visual design direction approved
- [ ] Responsive breakpoints agreed upon
- [ ] Color and theme approach confirmed
- [ ] Out-of-scope items acknowledged
- [ ] Success criteria are clear and measurable

**Once Approved:**
1. Create detailed `tasks.md` with atomic, testable tasks
2. Begin Phase 1 implementation
3. Test after each phase
4. Create PHR (Prompt History Record) after completion
5. Suggest ADR if any architectural decisions are made

---

**Questions for User:**

1. Do you approve the visual design direction (message bubbles, citation cards, color scheme)?
2. Are the responsive breakpoints appropriate for your target users?
3. Do you want any specific animations or transitions not mentioned?
4. Should citations open in the same tab or a new tab when clicked?
5. Any other features or requirements not covered in this spec?
