# Implementation Plan: Chat UI Redesign

**Branch**: `003-chat-ui-redesign` | **Date**: 2025-12-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-chat-ui-redesign/spec.md`

## Summary

This plan defines the architecture for redesigning the Study Assistant chat UI to be modern, responsive, and professional while maintaining 100% functional compatibility with the existing RAG backend. The redesign is purely visual - we're refactoring the presentation layer (JSX structure + CSS) without touching business logic, API contracts, or state management. The approach prioritizes mobile-first responsive design, theme-aware styling using Docusaurus CSS variables, and smooth animations for a polished user experience.

**Key Principle**: Structure-Before-Content - we change how the UI looks and responds, not what it does functionally.

## Technical Context

**Language/Version**: TypeScript 5.x (Docusaurus React components)
**Primary Dependencies**:
- React 18.x (Docusaurus bundled)
- Docusaurus 3.x (theming system, CSS variables)
- CSS Modules (component-scoped styling)

**Storage**: N/A (UI only, backend unchanged)
**Testing**: Manual responsive testing (mobile/tablet/desktop), automated tests for critical API/state logic only
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) on mobile (320px+), tablet (768px+), desktop (1024px+)
**Project Type**: Web (frontend component redesign within Docusaurus static site)
**Performance Goals**:
- 60fps animations (GPU-accelerated transform/opacity only)
- <300ms panel open/close animation
- <100ms tooltip appearance on text selection
- <5KB bundle size increase (CSS changes only)

**Constraints**:
- Zero backend changes (RAG API, embeddings, vector DB all untouched)
- 100% feature parity with existing chat functionality
- Must work without JavaScript for screen readers (semantic HTML)
- Theme compatibility (light/dark mode auto-adaptation)
- Mobile keyboard must not hide input field

**Scale/Scope**:
- 4 existing files to refactor (ChatPanelPlaceholder.tsx/css, TextSelectionTooltip.tsx/css)
- 3 new component files to create (CitationCard, LoadingIndicator, ErrorMessage)
- ~600 lines of CSS rewrite (mobile-first responsive structure)
- ~50 lines of JSX restructuring (layout changes, no logic changes)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Assignment.md as Single Source of Truth
- **Status**: PASS
- **Verification**: Feature aligns with hackathon assignment's RAG chatbot requirement. No invented robotics/hardware features. Scope is UI redesign for existing chat system.

### ✅ II. Structure-Before-Content
- **Status**: PASS
- **Verification**: This plan defines complete UI structure (component hierarchy, CSS architecture, responsive breakpoints) BEFORE writing code. Spec.md was reviewed and clarified before planning.

### ✅ III. Spec-Driven Development (SDD Workflow)
- **Status**: PASS
- **Verification**:
  - `/sp.specify` → spec.md created (✓)
  - `/sp.clarify` → clarify.md created with 10 resolved Q&A sections (✓)
  - `/sp.plan` → This file (✓)
  - Next: `/sp.tasks` → tasks.md (pending approval of this plan)

### ✅ IV. Adaptive Learning Without Hiding Safety
- **Status**: N/A (not applicable to UI redesign)
- **Verification**: This feature does not involve personalization or content adaptation.

### ✅ V. RAG Chatbot: Whole-Book and Selection-Based Q&A
- **Status**: PASS
- **Verification**: Both modes preserved in redesign. Mode selector remains in header. Selection-based tooltip improved but functionally identical.

### ✅ VI. Code Quality, Examples, and UI/UX Standards
- **Status**: PASS
- **Verification**:
  - Clean, modern, responsive design (mobile-first breakpoints)
  - Accessibility: ARIA labels, keyboard navigation, focus indicators, screen reader announcements
  - TypeScript for type safety
  - No janky popups (panel slides in smoothly from right)

### ✅ VII. Separation of Concerns and Small, Testable Changes
- **Status**: PASS
- **Verification**:
  - Clear separation: UI (this feature) vs backend (unchanged)
  - Small components extracted (CitationCard, LoadingIndicator, ErrorMessage)
  - Incremental implementation via 7 phases (each testable independently)
  - Feature flag for safe rollback

**Constitution Check Result**: ✅ ALL GATES PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/003-chat-ui-redesign/
├── spec.md                  # Feature requirements, user stories, mockups
├── clarify.md               # 10 sections of clarification Q&A (resolved)
├── plan.md                  # This file (/sp.plan command output)
└── tasks.md                 # Phase 2 output (/sp.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
src/components/chat/
├── ChatPanelPlaceholder.tsx              # REFACTOR: Layout structure, extract citations
├── ChatPanelPlaceholder.module.css       # REWRITE: Mobile-first responsive, theme-aware
├── ChatPanelPlaceholder.legacy.tsx       # RENAME: Backup of old UI for rollback
├── ChatPanelPlaceholder.legacy.module.css# RENAME: Backup of old CSS for rollback
├── TextSelectionTooltip.tsx              # REFACTOR: Modern tooltip design
├── TextSelectionTooltip.module.css       # REWRITE: Positioning, animations
├── AskTheTextbookButton.tsx              # MINOR UPDATES: Hide when chat open (mobile)
├── AskTheTextbookButton.module.css       # MINOR UPDATES: Responsive positioning
├── CitationCard.tsx                      # NEW: Extract citation display logic
├── CitationCard.module.css               # NEW: Card design, hover effects
├── LoadingIndicator.tsx                  # NEW: Animated typing dots
├── LoadingIndicator.module.css           # NEW: Bounce animation
├── ErrorMessage.tsx                      # NEW: Inline error with retry button
└── ErrorMessage.module.css               # NEW: Error styling

tests/ (if automated tests added in future)
├── ChatPanel.api.test.ts                 # FUTURE: API integration tests
└── ChatPanel.state.test.ts               # FUTURE: State management tests
```

**Structure Decision**:
- All new components remain in `src/components/chat/` (no subdirectory) for simplicity and cohesion
- Old files renamed with `.legacy` suffix for instant rollback via feature flag
- Each component has co-located CSS module (standard Docusaurus pattern)

## Architecture Overview

### Current Architecture (Before Redesign)

```
┌─────────────────────────────────────────────────────────┐
│                 User's Browser                          │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Docusaurus Page (e.g., /docs/module-1/chapter-1)│ │
│  │                                                  │ │
│  │  AskTheTextbookButton (floating)                │ │
│  │           │                                       │ │
│  │           ├──> Opens ChatPanelPlaceholder        │ │
│  │                       │                           │ │
│  │                       ├──> Whole-book mode        │ │
│  │                       └──> Selection mode         │ │
│  │                                                  │ │
│  │  TextSelectionTooltip (on text select)          │ │
│  │           │                                       │ │
│  │           └──> Opens ChatPanelPlaceholder        │ │
│  │                 (in selection mode)              │ │
│  └──────────────────────────────────────────────────┘ │
│                       │                                │
│                       │ POST /api/chat                 │
│                       ▼                                │
└───────────────────────┼─────────────────────────────────┘
                        │
                        ▼
           ┌─────────────────────────┐
           │   FastAPI Backend       │
           │   (RAG Service)         │
           │                         │
           │  - Qdrant (embeddings)  │
           │  - OpenAI API           │
           │  - Neon Postgres        │
           └─────────────────────────┘
```

**Current Issues**:
- ChatPanelPlaceholder: Not responsive (breaks on mobile <768px)
- Citations: Displayed as plain links, not visually distinct
- Loading state: Simple spinner emoji, no animated feedback
- Theme: Partially adapts, inconsistent colors
- Tooltip: Basic design, poor positioning on small screens

### New Architecture (After Redesign)

```
┌─────────────────────────────────────────────────────────┐
│                 User's Browser                          │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Docusaurus Page                                  │ │
│  │                                                  │ │
│  │  AskTheTextbookButton (floating)                │ │
│  │    - Hides when chat open (mobile)              │ │
│  │    - Responsive positioning                      │ │
│  │           │                                       │ │
│  │           ├──> Opens ChatPanelPlaceholder ──────┐│ │
│  │                 (NEW DESIGN)                    ││ │
│  │                                                 ││ │
│  │                  ┌──────────────────────────┐  ││ │
│  │                  │ ChatPanelPlaceholder     │  ││ │
│  │                  │                          │  ││ │
│  │                  │  Header                  │  ││ │
│  │                  │  ├─ Title + Mode Selector│  ││ │
│  │                  │  └─ Close Button         │  ││ │
│  │                  │                          │  ││ │
│  │                  │  Content (scrollable)    │  ││ │
│  │                  │  ├─ Selected Text Context│  ││ │
│  │                  │  ├─ ErrorMessage (NEW)   │  ││ │
│  │                  │  └─ Messages             │  ││ │
│  │                  │     ├─ User Message      │  ││ │
│  │                  │     └─ AI Message        │  ││ │
│  │                  │        ├─ Text           │  ││ │
│  │                  │        └─ Citations      │  ││ │
│  │                  │           └─ CitationCard│  ││ │
│  │                  │              (NEW)       │  ││ │
│  │                  │                          │  ││ │
│  │                  │  ├─ LoadingIndicator     │  ││ │
│  │                  │     (NEW, animated dots) │  ││ │
│  │                  │                          │  ││ │
│  │                  │  Footer (fixed)          │  ││ │
│  │                  │  ├─ Input (textarea)     │  ││ │
│  │                  │  └─ Send Button          │  ││ │
│  │                  └──────────────────────────┘  ││ │
│  │                                                 ││ │
│  │  TextSelectionTooltip (on text select) ────────┘│ │
│  │    - Modern design, smart positioning            │ │
│  │    - Fade in/out animations                      │ │
│  │    - Disabled on mobile (<768px)                 │ │
│  └──────────────────────────────────────────────────┘ │
│                       │                                │
│                       │ POST /api/chat (UNCHANGED)     │
│                       ▼                                │
└───────────────────────┼─────────────────────────────────┘
                        │
                        ▼
           ┌─────────────────────────┐
           │   FastAPI Backend       │
           │   (NO CHANGES)          │
           └─────────────────────────┘
```

**Key Improvements**:
1. **Responsive Layout**: Mobile-first CSS, panel adapts 100% width (mobile) → 80% (tablet) → 450px (desktop)
2. **Component Extraction**: CitationCard, LoadingIndicator, ErrorMessage are standalone, reusable, testable
3. **Theme Integration**: All colors use `--ifm-*` CSS variables with fallbacks
4. **Animations**: GPU-accelerated slide-in (panel), fade-in (messages), bounce (loading dots)
5. **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation, screen reader announcements

## CSS Architecture

### Mobile-First Responsive Breakpoints

```css
/* Base Styles (Mobile: 320px - 575px) */
.chatPanel {
  width: 100%;
  height: 100dvh; /* Dynamic viewport height for mobile keyboard */
  position: fixed;
  top: 0;
  right: 0;
  z-index: 2000;
}

/* Small Tablets (576px - 767px) */
@media (min-width: 576px) {
  .chatPanel {
    width: 90%;
    max-width: 500px;
  }
}

/* Tablets (768px - 991px) */
@media (min-width: 768px) {
  .chatPanel {
    width: 80%;
    max-width: 500px;
    height: 85vh;
    border-radius: 12px 0 0 12px;
  }
}

/* Desktop (992px+) */
@media (min-width: 992px) {
  .chatPanel {
    width: 450px;
    height: 80vh;
    max-height: 700px;
    border-radius: 12px;
    top: 50%;
    transform: translateY(-50%);
  }
}
```

### Theme-Aware Color System

**Strategy**: Use Docusaurus CSS variables with hex fallbacks for graceful degradation.

```css
/* Panel Background */
.chatPanel {
  background: var(--ifm-background-surface-color, #ffffff);
  color: var(--ifm-color-content, #1c1e21);
  border: 1px solid var(--ifm-color-emphasis-300, #e0e0e0);
}

/* User Message Bubble */
.userMessage {
  background: var(--ifm-color-primary-lightest, #e7f2ff);
  border-left: 4px solid var(--ifm-color-primary, #0066cc);
}

/* AI Message Bubble */
.aiMessage {
  background: var(--ifm-color-emphasis-100, #f5f5f5);
  border: 1px solid var(--ifm-color-emphasis-300, #e0e0e0);
}

/* Citation Card */
.citationCard {
  background: var(--ifm-background-color, #ffffff);
  border: 1px solid var(--ifm-color-emphasis-200, #e0e0e0);
}

.citationCard:hover {
  border-color: var(--ifm-color-primary, #0066cc);
  background: var(--ifm-color-primary-contrast-background, #f0f7ff);
}

/* Loading Indicator */
.loadingDot {
  background: var(--ifm-color-primary, #0066cc);
}

/* Error Message */
.errorMessage {
  background: var(--ifm-color-danger-contrast-background, #fff5f5);
  border-left: 4px solid var(--ifm-color-danger, #d32f2f);
  color: var(--ifm-color-danger-dark, #b71c1c);
}
```

**Theme Transition** (smooth color change on theme toggle):
```css
.chatPanel,
.userMessage,
.aiMessage,
.citationCard {
  transition: background-color 200ms, border-color 200ms, color 200ms;
}
```

### Animation System

**GPU-Accelerated Properties Only** (transform, opacity) for 60fps performance.

```css
/* Panel Slide-In (from right) */
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

/* Message Fade-In */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message {
  animation: fadeIn 300ms ease-in;
}

/* Loading Dots Bounce */
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

.loadingDot {
  animation: bounce 1.4s infinite;
  animation-delay: calc(var(--i) * 0.2s); /* Stagger dots */
}

/* Tooltip Fade-In */
@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tooltip {
  animation: tooltipFadeIn 200ms ease-out;
}

/* Reduced Motion Support (Accessibility) */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Component Structure

### 1. ChatPanelPlaceholder (Refactored)

**File**: `src/components/chat/ChatPanelPlaceholder.tsx`

**Changes**:
- **JSX Structure**: Reorganize into `<Header>`, `<Content>`, `<Footer>` sections
- **Extract Citations**: Replace inline citation rendering with `<CitationCard>` component
- **Extract Loading**: Replace inline spinner with `<LoadingIndicator>` component
- **Extract Error**: Replace inline error banner with `<ErrorMessage>` component
- **No Logic Changes**: All state management, API calls, event handlers remain identical

**New JSX Structure**:
```tsx
<div className={styles.overlay} onClick={handleOverlayClick}>
  <div className={styles.panel}>
    {/* Header: Fixed at top */}
    <header className={styles.header}>
      <h2 className={styles.title}>Study Assistant</h2>
      <select
        className={styles.modeSelector}
        value={mode}
        onChange={handleModeChange}
      >
        <option value="whole-book">📚 Whole-book</option>
        <option value="selection">📌 Selection</option>
      </select>
      <button className={styles.closeButton} onClick={onClose}>✕</button>
    </header>

    {/* Content: Scrollable messages area */}
    <div className={styles.content}>
      {/* Selection Context (if mode === 'selection') */}
      {mode === 'selection' && selectedText && (
        <div className={styles.selectionContext}>
          <span className={styles.contextIcon}>📌</span>
          <p className={styles.contextText}>"{selectedText}"</p>
        </div>
      )}

      {/* Error Message (if error) */}
      {error && (
        <ErrorMessage
          message={error}
          onRetry={handleRetry}
          onDismiss={() => setError(null)}
        />
      )}

      {/* Messages List */}
      <div className={styles.messagesList}>
        {messages.length === 0 && !loading && (
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon}>💬</span>
            <p className={styles.emptyText}>
              {mode === 'whole-book'
                ? 'Ask anything about the textbook...'
                : 'Ask about the selected text...'}
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`${styles.message} ${
              message.role === 'user' ? styles.userMessage : styles.aiMessage
            }`}
          >
            <div className={styles.messageRole}>
              {message.role === 'user' ? '👤 You' : '🤖 Assistant'}
            </div>
            <div className={styles.messageText}>{message.text}</div>

            {/* Citations (for AI messages) */}
            {message.role === 'assistant' && message.citations?.length > 0 && (
              <div className={styles.citations}>
                <h4 className={styles.citationsTitle}>📚 Sources:</h4>
                {message.citations.map((citation, citIndex) => (
                  <CitationCard
                    key={citIndex}
                    citation={citation}
                    baseUrl={siteConfig.baseUrl}
                  />
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Loading Indicator */}
        {loading && <LoadingIndicator />}

        <div ref={messagesEndRef} />
      </div>
    </div>

    {/* Footer: Fixed at bottom */}
    <footer className={styles.footer}>
      <textarea
        className={styles.input}
        placeholder={
          mode === 'whole-book'
            ? 'Ask anything about the textbook...'
            : 'Ask about the selected text...'
        }
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading}
        maxLength={1000}
        rows={2}
      />
      <button
        className={styles.sendButton}
        onClick={handleSend}
        disabled={loading || !input.trim()}
      >
        {loading ? '⏳' : '→'} Send
      </button>
    </footer>
  </div>
</div>
```

### 2. CitationCard (New Component)

**File**: `src/components/chat/CitationCard.tsx`

```tsx
import React from 'react';
import styles from './CitationCard.module.css';

interface CitationCardProps {
  citation: {
    docPath: string;
    heading: string;
    snippet: string;
  };
  baseUrl?: string;
}

export default function CitationCard({ citation, baseUrl = '/' }: CitationCardProps): JSX.Element {
  // Build full URL from docPath
  const getCitationUrl = (docPath: string): string => {
    let cleanPath = docPath.replace(/^\/docs\//, '').replace(/^docs\//, '');
    return `${baseUrl}docs/${cleanPath}`.replace(/\/+/g, '/');
  };

  return (
    <a
      href={getCitationUrl(citation.docPath)}
      className={styles.card}
      aria-label={`Citation: ${citation.heading}`}
    >
      <div className={styles.icon}>📄</div>
      <div className={styles.content}>
        <h5 className={styles.heading}>{citation.heading}</h5>
        <p className={styles.snippet}>{citation.snippet}</p>
      </div>
      <div className={styles.arrow}>→</div>
    </a>
  );
}
```

**File**: `src/components/chat/CitationCard.module.css`

```css
.card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--ifm-background-color, #ffffff);
  border: 1px solid var(--ifm-color-emphasis-200, #e0e0e0);
  border-radius: 8px;
  text-decoration: none;
  transition: all 200ms ease;
  margin-bottom: 0.5rem;
}

.card:hover {
  border-color: var(--ifm-color-primary, #0066cc);
  background: var(--ifm-color-primary-contrast-background, #f0f7ff);
  transform: translateX(4px);
}

.icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.content {
  flex: 1;
  min-width: 0; /* Allow text truncation */
}

.heading {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ifm-color-primary, #0066cc);

  /* Truncate long headings */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.snippet {
  margin: 0;
  font-size: 0.8rem;
  color: var(--ifm-color-emphasis-700, #666);
  line-height: 1.4;

  /* Clamp to 2 lines */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.arrow {
  font-size: 1rem;
  color: var(--ifm-color-primary, #0066cc);
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 200ms;
}

.card:hover .arrow {
  opacity: 1;
}

/* Mobile: Larger touch targets */
@media (max-width: 768px) {
  .card {
    padding: 1rem;
  }

  .heading {
    font-size: 0.9rem;
  }

  .snippet {
    font-size: 0.85rem;
  }
}
```

### 3. LoadingIndicator (New Component)

**File**: `src/components/chat/LoadingIndicator.tsx`

```tsx
import React from 'react';
import styles from './LoadingIndicator.module.css';

export default function LoadingIndicator(): JSX.Element {
  return (
    <div className={styles.container} role="status" aria-live="polite" aria-label="AI is typing">
      <div className={styles.dots}>
        <span className={styles.dot} style={{ '--i': 0 } as React.CSSProperties} />
        <span className={styles.dot} style={{ '--i': 1 } as React.CSSProperties} />
        <span className={styles.dot} style={{ '--i': 2 } as React.CSSProperties} />
      </div>
      <p className={styles.text}>AI is typing...</p>
    </div>
  );
}
```

**File**: `src/components/chat/LoadingIndicator.module.css`

```css
.container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--ifm-background-surface-color, #f5f5f5);
  border-radius: 12px;
  border: 1px solid var(--ifm-color-emphasis-200, #e0e0e0);
  margin-bottom: 1rem;
}

.dots {
  display: flex;
  gap: 0.25rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--ifm-color-primary, #0066cc);
  animation: bounce 1.4s infinite;
  animation-delay: calc(var(--i) * 0.2s);
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
}

.text {
  margin: 0;
  font-size: 0.9rem;
  color: var(--ifm-color-emphasis-700, #666);
  font-style: italic;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .dot {
    animation: none;
  }
}
```

### 4. ErrorMessage (New Component)

**File**: `src/components/chat/ErrorMessage.tsx`

```tsx
import React from 'react';
import styles from './ErrorMessage.module.css';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export default function ErrorMessage({ message, onRetry, onDismiss }: ErrorMessageProps): JSX.Element {
  return (
    <div className={styles.container} role="alert">
      <div className={styles.icon}>⚠️</div>
      <div className={styles.content}>
        <p className={styles.message}>{message}</p>
        <div className={styles.actions}>
          {onRetry && (
            <button className={styles.retryButton} onClick={onRetry}>
              ↻ Retry
            </button>
          )}
          {onDismiss && (
            <button className={styles.dismissButton} onClick={onDismiss}>
              Dismiss
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
```

**File**: `src/components/chat/ErrorMessage.module.css`

```css
.container {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--ifm-color-danger-contrast-background, #fff5f5);
  border-left: 4px solid var(--ifm-color-danger, #d32f2f);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.content {
  flex: 1;
}

.message {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  color: var(--ifm-color-danger-dark, #b71c1c);
  line-height: 1.4;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.retryButton,
.dismissButton {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 200ms;
}

.retryButton {
  background: var(--ifm-color-danger, #d32f2f);
  color: white;
}

.retryButton:hover {
  background: var(--ifm-color-danger-dark, #b71c1c);
}

.dismissButton {
  background: transparent;
  color: var(--ifm-color-danger, #d32f2f);
  border: 1px solid var(--ifm-color-danger, #d32f2f);
}

.dismissButton:hover {
  background: var(--ifm-color-danger-contrast-background, #fff5f5);
}
```

### 5. TextSelectionTooltip (Refactored)

**File**: `src/components/chat/TextSelectionTooltip.tsx`

**Changes**:
- Add smart positioning (flip above/below selection based on available space)
- Add fade-in/fade-out animations
- Hide on mobile (<768px) via CSS media query
- Show first 50 chars of selected text as preview
- Add close button (X) for explicit dismissal

**New JSX Structure**:
```tsx
import React, { useEffect, useState } from 'react';
import styles from './TextSelectionTooltip.module.css';

interface TextSelectionTooltipProps {
  selectedText: string;
  position: { top: number; left: number };
  onAskAbout: () => void;
  onDismiss: () => void;
  visible: boolean;
}

export default function TextSelectionTooltip({
  selectedText,
  position,
  onAskAbout,
  onDismiss,
  visible
}: TextSelectionTooltipProps): JSX.Element {
  const [placement, setPlacement] = useState<'above' | 'below'>('above');

  useEffect(() => {
    if (visible && position.top < 100) {
      // Not enough space above, place below
      setPlacement('below');
    } else {
      setPlacement('above');
    }
  }, [visible, position]);

  if (!visible) return null;

  const preview = selectedText.length > 50
    ? selectedText.substring(0, 50) + '...'
    : selectedText;

  return (
    <div
      className={`${styles.tooltip} ${styles[placement]}`}
      style={{ top: position.top, left: position.left }}
    >
      <div className={styles.preview}>
        "{preview}"
      </div>
      <button className={styles.closeButton} onClick={onDismiss} aria-label="Close">
        ✕
      </button>
      <button className={styles.askButton} onClick={onAskAbout}>
        💬 Ask about this
      </button>
    </div>
  );
}
```

**File**: `src/components/chat/TextSelectionTooltip.module.css`

```css
.tooltip {
  position: absolute;
  z-index: 2100;
  background: var(--ifm-background-surface-color, #ffffff);
  border: 1px solid var(--ifm-color-emphasis-300, #e0e0e0);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.75rem;
  max-width: 300px;
  animation: tooltipFadeIn 200ms ease-out;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tooltip.above {
  transform: translateY(-100%) translateY(-8px);
}

.tooltip.below {
  transform: translateY(8px);
}

.preview {
  font-size: 0.85rem;
  color: var(--ifm-color-emphasis-700, #666);
  font-style: italic;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.closeButton {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: none;
  border: none;
  font-size: 1rem;
  color: var(--ifm-color-emphasis-600, #888);
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
}

.closeButton:hover {
  color: var(--ifm-color-emphasis-900, #333);
}

.askButton {
  width: 100%;
  padding: 0.5rem 1rem;
  background: var(--ifm-color-primary, #0066cc);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 200ms;
}

.askButton:hover {
  background: var(--ifm-color-primary-dark, #0052a3);
}

/* Hide on mobile */
@media (max-width: 768px) {
  .tooltip {
    display: none;
  }
}
```

## Implementation Phases

### Phase 0: Setup & Backup (15 minutes)

**Goal**: Prepare for refactor with zero-risk rollback mechanism.

**Tasks**:
1. Create feature flag configuration
2. Rename existing files to `.legacy.*` versions
3. Verify old UI still works with legacy files
4. Commit backup state

**Acceptance**:
- [ ] Old UI renders correctly from `ChatPanelPlaceholder.legacy.tsx`
- [ ] Feature flag `enableNewChatUI` toggles between old and new (initially `false`)
- [ ] Git commit: "feat: backup old chat UI for rollback"

---

### Phase 1: CSS Foundation (Mobile-First) (2 hours)

**Goal**: Rewrite `ChatPanelPlaceholder.module.css` with mobile-first responsive structure and theme-aware colors.

**Tasks**:
1. Define base styles for mobile (320px - 575px)
2. Add responsive breakpoints (576px, 768px, 992px, 1440px)
3. Implement theme-aware color system with CSS variables + fallbacks
4. Add panel slide-in animation
5. Add smooth theme transition (200ms)

**Acceptance**:
- [ ] Panel is 100% width on mobile, 450px on desktop
- [ ] Panel height accounts for mobile keyboard (`100dvh`)
- [ ] All colors use `--ifm-*` variables with hex fallbacks
- [ ] Panel slides in from right in 300ms
- [ ] Colors transition smoothly when theme toggles (200ms)
- [ ] Manual test: Open panel on iPhone SE (375px), iPad (768px), MacBook (1440px)
- [ ] Manual test: Toggle theme with panel open, verify smooth color change

---

### Phase 2: Component Extraction (1.5 hours)

**Goal**: Create 3 new standalone components (CitationCard, LoadingIndicator, ErrorMessage).

**Tasks**:
1. Create `CitationCard.tsx` + `.module.css`
2. Create `LoadingIndicator.tsx` + `.module.css`
3. Create `ErrorMessage.tsx` + `.module.css`
4. Test each component in isolation (render in Storybook or standalone page)

**Acceptance**:
- [ ] CitationCard displays doc title, heading, snippet (2-line clamp)
- [ ] CitationCard hover effect: border color change, translateX(4px)
- [ ] LoadingIndicator shows 3 animated dots with staggered bounce
- [ ] LoadingIndicator includes "AI is typing..." text with ARIA label
- [ ] ErrorMessage displays error text, retry button, dismiss button
- [ ] All components have proper TypeScript types
- [ ] Manual test: Render each component standalone, verify styling and animations

---

### Phase 3: ChatPanelPlaceholder Refactor (2 hours)

**Goal**: Restructure JSX layout, integrate new components, preserve all logic.

**Tasks**:
1. Reorganize JSX into `<header>`, `<div className="content">`, `<footer>` sections
2. Replace inline citations with `<CitationCard>` component
3. Replace inline loading spinner with `<LoadingIndicator>` component
4. Replace inline error banner with `<ErrorMessage>` component
5. Update CSS classes to match new layout structure
6. Test: Verify all existing functionality works (send message, citations, mode switch)

**Acceptance**:
- [ ] Header contains title, mode selector, close button (fixed at top)
- [ ] Content area scrolls independently with messages
- [ ] Footer contains input and send button (fixed at bottom)
- [ ] Citations render as `<CitationCard>` components
- [ ] Loading state renders `<LoadingIndicator>` component
- [ ] Error state renders `<ErrorMessage>` component
- [ ] Manual test: Send message, verify response with citations appears
- [ ] Manual test: Trigger error (disconnect network), verify error UI and retry button

---

### Phase 4: TextSelectionTooltip Redesign (1 hour)

**Goal**: Modernize tooltip with smart positioning, animations, preview text.

**Tasks**:
1. Rewrite `TextSelectionTooltip.module.css` with new design
2. Add smart positioning logic (flip above/below based on `position.top`)
3. Add fade-in/fade-out animation
4. Show first 50 chars of selected text as preview
5. Add close button (X) for dismissal
6. Hide tooltip on mobile via CSS media query

**Acceptance**:
- [ ] Tooltip appears above selection if space available, below if not
- [ ] Tooltip fades in over 200ms
- [ ] Preview text shows first 50 chars with "..." if longer
- [ ] Close button (X) dismisses tooltip
- [ ] Tooltip hidden on mobile (<768px)
- [ ] Manual test: Select text on desktop, verify tooltip appears near selection
- [ ] Manual test: Select text at top of page, verify tooltip flips below

---

### Phase 5: Message Bubbles & Animations (1.5 hours)

**Goal**: Style user/AI message bubbles with distinct designs and fade-in animations.

**Tasks**:
1. Style user message bubble (align right, primary color background)
2. Style AI message bubble (align left, gray background)
3. Add message fade-in animation (opacity + translateY)
4. Style empty state (centered icon + text)
5. Add reduced motion support (`@media (prefers-reduced-motion: reduce)`)

**Acceptance**:
- [ ] User messages aligned right, blue/primary background
- [ ] AI messages aligned left, gray background
- [ ] Messages fade in over 300ms with slight upward motion
- [ ] Empty state shows centered icon and helpful prompt
- [ ] Animations disabled for users with `prefers-reduced-motion: reduce`
- [ ] Manual test: Send multiple messages, verify smooth fade-in
- [ ] Manual test: Enable reduced motion in browser, verify animations disabled

---

### Phase 6: Input Area & Accessibility (1.5 hours)

**Goal**: Polish input area, add keyboard navigation, ARIA labels, focus indicators.

**Tasks**:
1. Style input textarea (multiline, auto-expand up to 5 rows, 1000 char limit)
2. Style send button (disabled states, loading spinner)
3. Add keyboard navigation (Enter = send, Shift+Enter = newline, Escape = close)
4. Add ARIA labels to all interactive elements
5. Add visible focus indicators (outline on Tab focus)
6. Test with screen reader (NVDA/VoiceOver)

**Acceptance**:
- [ ] Input expands to max 5 rows, then scrolls
- [ ] Input has 1000 char limit (enforced with `maxLength`)
- [ ] Send button disabled when input empty or loading
- [ ] Enter key sends message, Shift+Enter adds newline
- [ ] Escape key closes panel
- [ ] All buttons/inputs have ARIA labels
- [ ] Tab navigation works: input → send button → close button → mode selector
- [ ] Focus indicators visible on all elements
- [ ] Manual test: Navigate entire chat UI with keyboard only
- [ ] Manual test: Use screen reader, verify announcements ("Study Assistant opened", "AI is typing")

---

### Phase 7: Final Polish & Testing (2 hours)

**Goal**: Comprehensive testing across devices, themes, edge cases. Fix any issues found.

**Tasks**:
1. Test on physical devices (iPhone, iPad, Android, laptop)
2. Test light/dark theme switching with chat open
3. Test edge cases (long messages, many citations, rapid clicks)
4. Verify performance (60fps animations, no jank)
5. Run automated tests for API/state logic (if implemented)
6. Update feature flag to `enableNewChatUI: true` by default

**Acceptance**:
- [ ] All devices tested: iPhone SE, iPad Mini, Android phone, MacBook
- [ ] Theme toggle smooth (no flash of wrong colors)
- [ ] Long messages (5000 chars) display correctly with scroll
- [ ] 10+ citations all render without performance issues
- [ ] Rapid send clicks handled gracefully (button disabled during loading)
- [ ] Chrome DevTools Performance: animations at 60fps, no dropped frames
- [ ] Automated tests pass (API calls, state management, mode switching)
- [ ] Feature flag enabled: `enableNewChatUI: true`

---

## Risk Mitigation

### Risk 1: Breaking Existing Functionality

**Likelihood**: Medium | **Impact**: High | **Severity**: HIGH

**Mitigation**:
- Feature flag for instant rollback without redeployment
- Keep old UI files (`.legacy.*`) for 1 sprint after launch
- No changes to API contracts, interfaces, state management
- Incremental testing after each phase
- Automated tests for critical logic (API calls, state transitions)

**Contingency**: If critical bug found after deploy, toggle flag to `false` (rollback to old UI in seconds).

---

### Risk 2: Responsive Layout Issues on Specific Devices

**Likelihood**: Medium | **Impact**: Medium | **Severity**: MEDIUM

**Mitigation**:
- Mobile-first CSS approach (start with mobile, add desktop enhancements)
- Test on physical devices (not just browser emulators)
- Use `100dvh` for mobile panel height (accounts for address bar, keyboard)
- Add safe area insets for iOS notch (`padding-bottom: env(safe-area-inset-bottom)`)

**Contingency**: If layout breaks on specific device, add device-specific media query hotfix.

---

### Risk 3: Theme Color Variables Not Available in Custom Themes

**Likelihood**: Low | **Impact**: Low | **Severity**: LOW

**Mitigation**:
- Use CSS variables with fallback hex values: `var(--ifm-color-primary, #0066cc)`
- Fallbacks are sane defaults from standard Docusaurus theme
- Test with custom theme (if available) during development

**Contingency**: If custom theme missing variables, fallback colors ensure chat still looks decent.

---

### Risk 4: Animations Causing Performance Issues on Low-End Devices

**Likelihood**: Low | **Impact**: Medium | **Severity**: LOW

**Mitigation**:
- Only animate GPU-accelerated properties (transform, opacity)
- Avoid animating width, height, margin, box-shadow (cause reflow)
- Add `@media (prefers-reduced-motion: reduce)` to disable animations for accessibility
- Test on low-end Android device during Phase 7

**Contingency**: If performance issues found, reduce animation duration or disable specific animations.

---

## Architectural Decisions Requiring ADR Documentation

Based on the three-part test (Impact + Alternatives + Scope), the following decisions meet ADR significance criteria:

### Decision 1: Feature Flag Rollback Strategy

**Context**: Need safe way to deploy new UI without risk of breaking production chat.

**Impact**: Long-term deployment and rollback mechanism for all future UI changes.

**Alternatives Considered**:
- A) Git revert (requires redeployment, slow)
- B) Feature flag toggle (instant rollback, no redeploy)
- C) Gradual A/B rollout (complex, overkill for single feature)

**Decision**: Feature flag with `.legacy.*` backup files (Option B).

**Rationale**: Instant rollback without redeployment. Keep old code for 1 sprint, then clean up.

**Recommendation**: 📋 Suggest ADR after implementation: `/sp.adr feature-flag-rollback-strategy`

---

### Decision 2: Component Extraction vs Monolithic ChatPanel

**Context**: Citations, loading, errors are currently inline in ChatPanelPlaceholder.tsx. Should we extract?

**Impact**: Long-term component architecture, reusability, testability.

**Alternatives Considered**:
- A) Keep all UI inline (simple but hard to test/reuse)
- B) Extract to separate components in same directory (modular, testable)
- C) Extract to shared `/components/common/` directory (overkill, premature)

**Decision**: Extract to separate components in `/components/chat/` (Option B).

**Rationale**: Improves testability, reusability, and code organization without over-engineering.

**Recommendation**: 📋 Suggest ADR after implementation: `/sp.adr component-extraction-architecture`

---

### Decision 3: CSS Modules vs Styled-Components for Styling

**Context**: Need styling solution that works with Docusaurus, supports theming, is maintainable.

**Impact**: Long-term styling architecture for all Docusaurus components.

**Alternatives Considered**:
- A) CSS Modules (Docusaurus default, scoped styles, CSS variables)
- B) Styled-Components (CSS-in-JS, dynamic styles, larger bundle)
- C) Tailwind CSS (utility-first, requires setup, overkill)

**Decision**: CSS Modules with Docusaurus CSS variables (Option A).

**Rationale**: No additional dependencies, works seamlessly with Docusaurus theme system, smaller bundle.

**Recommendation**: 📋 Suggest ADR after implementation: `/sp.adr css-architecture-strategy`

---

## Success Criteria Validation

### Functionality (Must-Pass)

- [ ] **SC-001**: All existing chat functionality works identically (100% feature parity)
- [ ] **SC-002**: Chat panel fully functional on iPhone SE (375px width)
- [ ] **SC-003**: Chat panel fully functional on iPad (768px width)
- [ ] **SC-004**: Chat panel fully functional on desktop (1440px+ width)
- [ ] **SC-005**: Zero console errors or warnings related to chat rendering

### Visual Quality (Must-Pass)

- [ ] **SC-006**: All color contrast ratios meet WCAG AA standards (verified with contrast checker)
- [ ] **SC-007**: Chat panel matches Docusaurus theme in light and dark modes
- [ ] **SC-008**: All animations run at 60fps (verified with Chrome DevTools Performance tab)
- [ ] **SC-009**: User and AI messages clearly visually distinct

### User Experience (Must-Pass)

- [ ] **SC-010**: Full chat interaction (open, ask, receive, close) completes in <30 seconds on mobile
- [ ] **SC-011**: Citation cards immediately recognizable as clickable sources
- [ ] **SC-012**: Loading states clear and don't cause confusion
- [ ] **SC-013**: Text selection tooltip appears within 100ms on desktop

### Accessibility (Must-Pass)

- [ ] **SC-014**: All interactive elements reachable via keyboard (Tab)
- [ ] **SC-015**: Screen reader announces critical state changes (opened, loading, error, message)
- [ ] **SC-016**: Focus indicators visible on all interactive elements

### Performance (Must-Pass)

- [ ] **SC-017**: Chat panel opens in <300ms
- [ ] **SC-018**: No layout shift when messages added (CLS score remains low)
- [ ] **SC-019**: Bundle size increase <5KB (CSS changes only)

---

## Complexity Tracking

No constitution violations requiring justification. All decisions align with project principles.

---

## Next Steps

1. **User Approval**: Review this plan, approve architecture decisions, confirm scope
2. **ADR Suggestions**: After approval, suggest documenting the 3 architectural decisions listed above
3. **Task Generation**: Run `/sp.tasks` to generate dependency-ordered, testable tasks for implementation
4. **Implementation**: Execute Phase 0 → Phase 7 with validation after each phase
5. **PHR Creation**: After completion, create Prompt History Record for this planning session

---

**Plan Status**: ✅ READY FOR REVIEW
**Constitution Check**: ✅ ALL GATES PASSED
**Risks Identified**: 4 (all mitigated)
**ADR Suggestions**: 3 (pending user consent)
