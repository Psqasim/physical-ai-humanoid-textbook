# Tasks: Chat UI Redesign

**Input**: Design documents from `/specs/003-chat-ui-redesign/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by implementation phase to enable incremental testing and validation at each checkpoint.

## Format: `[ID] [P?] [Phase] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Phase]**: Which implementation phase this task belongs to (Phase 0-7)
- Include exact file paths in descriptions

## Path Conventions

All chat components are in: `src/components/chat/`
Legacy files use `.legacy.*` suffix for rollback safety

---

## Phase 0: Setup & Backup (15-30 minutes)

**Purpose**: Prepare for refactor with zero-risk rollback mechanism

**⚠️ CRITICAL**: This phase creates safety net for instant rollback if issues arise

- [ ] T001 [Phase 0] Create feature flag configuration
  - Add `enableNewChatUI` boolean flag (default: `false`)
  - Location: Create config file or use existing config system
  - Flag controls: ChatPanelPlaceholder component selection (new vs legacy)
  - **Acceptance**: Flag exists, can be toggled without code changes

- [ ] T002 [Phase 0] Rename existing ChatPanelPlaceholder files to legacy versions
  - Rename `src/components/chat/ChatPanelPlaceholder.tsx` → `ChatPanelPlaceholder.legacy.tsx`
  - Rename `src/components/chat/ChatPanelPlaceholder.module.css` → `ChatPanelPlaceholder.legacy.module.css`
  - Update imports in legacy file to reference legacy CSS module
  - **Acceptance**: Legacy files exist, imports updated correctly

- [ ] T003 [Phase 0] Rename existing TextSelectionTooltip files to legacy versions
  - Rename `src/components/chat/TextSelectionTooltip.tsx` → `TextSelectionTooltip.legacy.tsx`
  - Rename `src/components/chat/TextSelectionTooltip.module.css` → `TextSelectionTooltip.legacy.module.css`
  - Update imports in legacy file to reference legacy CSS module
  - **Acceptance**: Legacy files exist, imports updated correctly

- [ ] T004 [Phase 0] Verify old UI still works with legacy files
  - Import and render `ChatPanelPlaceholder.legacy.tsx` in parent component
  - Test: Open chat, send message, receive response, close chat
  - Test: Select text, tooltip appears, opens chat in selection mode
  - **Acceptance**: All existing functionality works from legacy files

- [ ] T005 [Phase 0] Commit backup state to version control
  - Git commit: "feat: backup old chat UI for rollback (Phase 0)"
  - Commit message includes: feature branch name, purpose of backup
  - **Acceptance**: Commit exists in git history with proper message

**Checkpoint**: ✅ Old UI preserved, rollback mechanism ready

---

## Phase 1: CSS Foundation (Mobile-First) (1.5-2 hours)

**Purpose**: Rewrite ChatPanelPlaceholder.module.css with mobile-first responsive structure and theme-aware colors

**Goal**: Panel layout adapts to all screen sizes, uses Docusaurus theme colors, smooth animations

- [ ] T006 [P] [Phase 1] Define base mobile styles for chat panel (320px-575px)
  - Create new `src/components/chat/ChatPanelPlaceholder.module.css`
  - Base styles: width 100%, height 100dvh (dynamic viewport height)
  - Position: fixed, top: 0, right: 0, z-index: 2000
  - Background: `var(--ifm-background-surface-color, #ffffff)`
  - Border: `1px solid var(--ifm-color-emphasis-300, #e0e0e0)`
  - Color: `var(--ifm-color-content, #1c1e21)`
  - **Acceptance**: Panel fills screen on mobile, proper padding, readable text

- [ ] T007 [P] [Phase 1] Add responsive breakpoints (576px, 768px, 992px, 1440px)
  - @media (min-width: 576px): width 90%, max-width 500px
  - @media (min-width: 768px): width 80%, max-width 500px, height 85vh, border-radius 12px 0 0 12px
  - @media (min-width: 992px): width 450px, height 80vh, max-height 700px, border-radius 12px, top 50%, transform translateY(-50%)
  - @media (min-width: 1440px): maintain 450px width, no further changes
  - **Acceptance**: Panel width correct at each breakpoint (test at 375px, 768px, 1024px, 1440px)

- [ ] T008 [P] [Phase 1] Implement theme-aware color system with CSS variables
  - User message background: `var(--ifm-color-primary-lightest, #e7f2ff)`
  - User message border-left: `4px solid var(--ifm-color-primary, #0066cc)`
  - AI message background: `var(--ifm-color-emphasis-100, #f5f5f5)`
  - AI message border: `1px solid var(--ifm-color-emphasis-300, #e0e0e0)`
  - All colors use `var(--ifm-*)` with hex fallbacks
  - **Acceptance**: Toggle theme light/dark, all colors adapt correctly

- [ ] T009 [Phase 1] Add panel slide-in animation (from right)
  - Define @keyframes slideInRight: translateX(100%) opacity 0 → translateX(0) opacity 1
  - Apply to .panel: animation slideInRight 300ms cubic-bezier(0.4, 0, 0.2, 1)
  - **Acceptance**: Panel slides in smoothly over 300ms when opened

- [ ] T010 [Phase 1] Add smooth theme transition (200ms)
  - Apply to .panel, .userMessage, .aiMessage, .citationCard
  - Transition properties: background-color 200ms, border-color 200ms, color 200ms
  - **Acceptance**: Toggle theme with panel open, colors transition smoothly (no flash)

- [ ] T011 [Phase 1] Style header section (fixed at top)
  - .header: display flex, justify-content space-between, padding 1rem
  - Background: `var(--ifm-background-surface-color)`
  - Border-bottom: `1px solid var(--ifm-color-emphasis-200)`
  - Position: sticky, top: 0, z-index: 1
  - **Acceptance**: Header stays fixed at top when messages scroll

- [ ] T012 [Phase 1] Style content section (scrollable messages area)
  - .content: flex 1, overflow-y auto, padding 1rem
  - Scroll behavior: smooth
  - Custom scrollbar styling (optional, for webkit browsers)
  - **Acceptance**: Content scrolls independently, header/footer remain fixed

- [ ] T013 [Phase 1] Style footer section (fixed at bottom)
  - .footer: display flex, gap 0.5rem, padding 1rem
  - Background: `var(--ifm-background-surface-color)`
  - Border-top: `1px solid var(--ifm-color-emphasis-200)`
  - Position: sticky, bottom: 0, z-index: 1
  - **Acceptance**: Footer stays fixed at bottom, input always accessible

- [ ] T014 [Phase 1] Add reduced motion support (accessibility)
  - @media (prefers-reduced-motion: reduce)
  - Set all animation-duration to 0.01ms
  - Set all transition-duration to 0.01ms
  - **Acceptance**: Enable reduced motion in browser, verify animations disabled

**Manual Testing for Phase 1**:
- [ ] T015 [Phase 1] Test panel on mobile (iPhone SE 375px)
  - Panel is 100% width, no horizontal scroll
  - Header, content, footer layout correct
  - Mobile keyboard appears without hiding input
  - **Acceptance**: All UI elements accessible and functional on mobile

- [ ] T016 [Phase 1] Test panel on tablet (iPad 768px)
  - Panel is 80% width, max 500px
  - Border radius on left side only
  - Content scrolls smoothly
  - **Acceptance**: Panel width appropriate, not cramped or too wide

- [ ] T017 [Phase 1] Test panel on desktop (MacBook 1440px)
  - Panel is 450px width, centered vertically
  - Border radius on all corners
  - Height is 80vh, max 700px
  - **Acceptance**: Optimal reading experience, panel doesn't stretch

- [ ] T018 [Phase 1] Test theme adaptation
  - Open panel in light mode, verify colors
  - Toggle to dark mode, verify smooth transition
  - All text remains readable (proper contrast)
  - **Acceptance**: No flash of wrong colors, smooth 200ms transition

**Checkpoint**: ✅ Responsive layout works on all screen sizes, theme integration complete

---

## Phase 2: Component Extraction (1-1.5 hours)

**Purpose**: Create 3 new standalone components (CitationCard, LoadingIndicator, ErrorMessage)

**Goal**: Reusable, testable components with proper TypeScript types and styling

### CitationCard Component

- [ ] T019 [P] [Phase 2] Create CitationCard.tsx component file
  - File: `src/components/chat/CitationCard.tsx`
  - TypeScript interface: CitationCardProps { citation: { docPath, heading, snippet }, baseUrl?: string }
  - Implement getCitationUrl function (clean path, build full URL)
  - Return: `<a>` element with icon, heading, snippet, arrow
  - **Acceptance**: Component renders with proper TypeScript types

- [ ] T020 [P] [Phase 2] Create CitationCard.module.css stylesheet
  - File: `src/components/chat/CitationCard.module.css`
  - .card: display flex, gap 0.75rem, padding 0.75rem
  - Background: `var(--ifm-background-color, #ffffff)`
  - Border: `1px solid var(--ifm-color-emphasis-200, #e0e0e0)`
  - Border-radius: 8px, transition: all 200ms ease
  - .card:hover: border-color primary, background primary-contrast, translateX(4px)
  - .heading: font-weight 600, color primary, overflow hidden, text-overflow ellipsis
  - .snippet: font-size 0.8rem, color emphasis-700, -webkit-line-clamp 2
  - .arrow: opacity 0, transition opacity 200ms; .card:hover .arrow: opacity 1
  - **Acceptance**: Card displays with icon, heading (truncated), snippet (2-line clamp), hover effect

- [ ] T021 [Phase 2] Add mobile responsive styles for CitationCard
  - @media (max-width: 768px): padding 1rem, larger touch target
  - .heading: font-size 0.9rem
  - .snippet: font-size 0.85rem
  - **Acceptance**: Card is tappable on mobile, text readable

### LoadingIndicator Component

- [ ] T022 [P] [Phase 2] Create LoadingIndicator.tsx component file
  - File: `src/components/chat/LoadingIndicator.tsx`
  - No props needed (self-contained)
  - Return: container with 3 dots + "AI is typing..." text
  - ARIA attributes: role="status", aria-live="polite", aria-label="AI is typing"
  - Dots use inline style: `style={{ '--i': 0/1/2 } as React.CSSProperties}`
  - **Acceptance**: Component renders with proper ARIA labels

- [ ] T023 [P] [Phase 2] Create LoadingIndicator.module.css stylesheet
  - File: `src/components/chat/LoadingIndicator.module.css`
  - .container: display flex, align-items center, gap 0.75rem, padding 1rem
  - Background: `var(--ifm-background-surface-color, #f5f5f5)`
  - Border: `1px solid var(--ifm-color-emphasis-200, #e0e0e0)`
  - Border-radius: 12px
  - .dot: width 8px, height 8px, border-radius 50%, background primary
  - @keyframes bounce: 0% translateY(0), 30% translateY(-8px), 60% translateY(0)
  - .dot: animation bounce 1.4s infinite, animation-delay calc(var(--i) * 0.2s)
  - .text: font-size 0.9rem, color emphasis-700, font-style italic
  - @media (prefers-reduced-motion): .dot animation none
  - **Acceptance**: 3 dots bounce with staggered timing, smooth animation

### ErrorMessage Component

- [ ] T024 [P] [Phase 2] Create ErrorMessage.tsx component file
  - File: `src/components/chat/ErrorMessage.tsx`
  - TypeScript interface: ErrorMessageProps { message: string, onRetry?: () => void, onDismiss?: () => void }
  - Return: container with icon, message, retry button (if onRetry), dismiss button (if onDismiss)
  - ARIA attribute: role="alert"
  - **Acceptance**: Component renders with proper TypeScript types and ARIA

- [ ] T025 [P] [Phase 2] Create ErrorMessage.module.css stylesheet
  - File: `src/components/chat/ErrorMessage.module.css`
  - .container: display flex, gap 0.75rem, padding 1rem
  - Background: `var(--ifm-color-danger-contrast-background, #fff5f5)`
  - Border-left: `4px solid var(--ifm-color-danger, #d32f2f)`
  - Border-radius: 8px
  - .message: color danger-dark, font-size 0.9rem
  - .retryButton: background danger, color white, padding 0.5rem 1rem, border-radius 6px
  - .retryButton:hover: background danger-dark
  - .dismissButton: background transparent, color danger, border 1px solid danger
  - .dismissButton:hover: background danger-contrast-background
  - **Acceptance**: Error displays with red theme, buttons functional

### Testing for Phase 2

- [ ] T026 [Phase 2] Test CitationCard component standalone
  - Create test page or use existing page to render CitationCard
  - Test data: { docPath: "/docs/chapter1/intro", heading: "Introduction to ROS 2", snippet: "ROS 2 is a robot framework..." }
  - Verify: icon, heading, snippet display, hover effect works, click navigates
  - **Acceptance**: Card is visually distinct, clickable, navigates correctly

- [ ] T027 [Phase 2] Test LoadingIndicator component standalone
  - Render LoadingIndicator on test page
  - Verify: 3 dots visible, bounce animation smooth, "AI is typing..." text shown
  - Test reduced motion: enable in browser, verify animation disabled
  - **Acceptance**: Animation is smooth (60fps), ARIA label announced by screen reader

- [ ] T028 [Phase 2] Test ErrorMessage component standalone
  - Render ErrorMessage with message, onRetry, onDismiss
  - Verify: error icon, message text, retry button, dismiss button all visible
  - Click retry: onRetry callback fires
  - Click dismiss: onDismiss callback fires
  - **Acceptance**: All buttons functional, error styling correct

**Checkpoint**: ✅ 3 new components created, tested in isolation, ready for integration

---

## Phase 3: ChatPanelPlaceholder Refactor (1.5-2 hours)

**Purpose**: Restructure JSX layout, integrate new components, preserve all logic

**Goal**: Modern layout structure with extracted components, 100% functional compatibility

- [ ] T029 [Phase 3] Create new ChatPanelPlaceholder.tsx file with component structure
  - File: `src/components/chat/ChatPanelPlaceholder.tsx`
  - Copy existing props interface from legacy file (ChatPanelPlaceholderProps)
  - Copy all existing state hooks: messages, loading, error, mode, input, etc.
  - Copy all existing functions: handleSend, handleModeChange, handleRetry, etc.
  - **Acceptance**: All business logic preserved, no logic changes

- [ ] T030 [Phase 3] Restructure JSX into header, content, footer sections
  - Header: h2 title, mode selector dropdown, close button
  - Content: selection context (if mode === 'selection'), error message, messages list, loading indicator, messagesEndRef
  - Footer: textarea input, send button
  - Apply CSS module classes: styles.header, styles.content, styles.footer
  - **Acceptance**: Three-section layout renders correctly

- [ ] T031 [Phase 3] Implement header section with title, mode selector, close button
  - `<header className={styles.header}>`
  - Title: `<h2 className={styles.title}>Study Assistant</h2>`
  - Mode selector: `<select className={styles.modeSelector} value={mode} onChange={handleModeChange}>`
  - Options: "📚 Whole-book" (value="whole-book"), "📌 Selection" (value="selection")
  - Close button: `<button className={styles.closeButton} onClick={onClose}>✕</button>`
  - **Acceptance**: Header displays title, mode selector, close button (all functional)

- [ ] T032 [Phase 3] Implement content section with scrollable messages area
  - `<div className={styles.content}>`
  - Selection context (conditional): if mode === 'selection' && selectedText, show context box
  - Error message (conditional): if error, render `<ErrorMessage message={error} onRetry={handleRetry} onDismiss={() => setError(null)} />`
  - Messages list div: map over messages array
  - Loading indicator (conditional): if loading, render `<LoadingIndicator />`
  - messagesEndRef: `<div ref={messagesEndRef} />`
  - **Acceptance**: Content scrolls, all conditional elements render correctly

- [ ] T033 [Phase 3] Implement empty state (when no messages)
  - Conditional: `{messages.length === 0 && !loading && (...)}``
  - Display: centered icon (💬), helpful text based on mode
  - Text for whole-book: "Ask anything about the textbook..."
  - Text for selection: "Ask about the selected text..."
  - **Acceptance**: Empty state shows on first open, disappears after first message

- [ ] T034 [Phase 3] Implement message rendering with user/AI styling
  - Map over messages: `{messages.map((message, index) => (...))}``
  - Conditional className: `${styles.message} ${message.role === 'user' ? styles.userMessage : styles.aiMessage}`
  - Message structure: role label ("👤 You" / "🤖 Assistant"), message text
  - **Acceptance**: User messages align right (blue), AI messages align left (gray)

- [ ] T035 [Phase 3] Replace inline citations with CitationCard component
  - Conditional: `{message.role === 'assistant' && message.citations?.length > 0 && (...)}`
  - Render citations title: "📚 Sources:"
  - Map over citations: `{message.citations.map((citation, citIndex) => <CitationCard key={citIndex} citation={citation} baseUrl={siteConfig.baseUrl} />)}`
  - Import CitationCard component at top of file
  - **Acceptance**: Citations display as cards within AI messages

- [ ] T036 [Phase 3] Replace inline loading spinner with LoadingIndicator component
  - Conditional: `{loading && <LoadingIndicator />}`
  - Import LoadingIndicator component at top of file
  - **Acceptance**: Loading indicator appears when waiting for response

- [ ] T037 [Phase 3] Replace inline error banner with ErrorMessage component
  - Conditional: `{error && <ErrorMessage message={error} onRetry={handleRetry} onDismiss={() => setError(null)} />}`
  - Import ErrorMessage component at top of file
  - Implement handleRetry function (resend last message)
  - **Acceptance**: Error message displays, retry button resends message, dismiss clears error

- [ ] T038 [Phase 3] Implement footer section with input and send button
  - `<footer className={styles.footer}>`
  - Textarea: `<textarea className={styles.input} placeholder={...} value={input} onChange={...} onKeyDown={handleKeyDown} disabled={loading} maxLength={1000} rows={2} />`
  - Placeholder text based on mode: whole-book vs selection
  - Send button: `<button className={styles.sendButton} onClick={handleSend} disabled={loading || !input.trim()}>`
  - Button content: `{loading ? '⏳' : '→'} Send`
  - **Acceptance**: Input field works, send button sends message, disabled states correct

- [ ] T039 [Phase 3] Style header elements in CSS module
  - .header: display flex, justify-content space-between, align-items center
  - .title: margin 0, font-size 1.25rem, font-weight 600
  - .modeSelector: padding 0.5rem, border-radius 6px, border 1px solid emphasis-300
  - .closeButton: background none, border none, font-size 1.5rem, cursor pointer
  - **Acceptance**: Header elements properly aligned and styled

- [ ] T040 [Phase 3] Style message bubbles (user vs AI)
  - .message: margin-bottom 1rem, padding 1rem, border-radius 12px, animation fadeIn 300ms
  - .userMessage: background primary-lightest, border-left 4px solid primary, align-self flex-end, max-width 80%
  - .aiMessage: background emphasis-100, border 1px solid emphasis-300, align-self flex-start, max-width 85%
  - .messageRole: font-weight 600, margin-bottom 0.5rem, font-size 0.875rem
  - .messageText: line-height 1.6, word-break break-word
  - **Acceptance**: User and AI messages visually distinct, proper alignment

- [ ] T041 [Phase 3] Style citations section
  - .citations: margin-top 1rem, padding-top 1rem, border-top 1px solid emphasis-200
  - .citationsTitle: font-size 0.875rem, font-weight 600, margin-bottom 0.5rem
  - **Acceptance**: Citations section visually separated from message text

- [ ] T042 [Phase 3] Style empty state
  - .emptyState: text-align center, padding 3rem 1rem, color emphasis-600
  - .emptyIcon: font-size 3rem, margin-bottom 1rem
  - .emptyText: font-size 1rem, line-height 1.5
  - **Acceptance**: Empty state centered, readable, helpful

- [ ] T043 [Phase 3] Style selection context box
  - .selectionContext: background primary-contrast-background, border 1px solid primary, padding 1rem, border-radius 8px, margin-bottom 1rem
  - .contextIcon: font-size 1.25rem, margin-right 0.5rem
  - .contextText: font-style italic, color emphasis-800, line-height 1.4
  - **Acceptance**: Selection context visually distinct, shows selected text

- [ ] T044 [Phase 3] Style footer input and button
  - .input: flex 1, padding 0.75rem, border 1px solid emphasis-300, border-radius 8px, resize vertical, font-family inherit
  - .input:focus: outline none, border-color primary, box-shadow 0 0 0 2px primary-lightest
  - .sendButton: padding 0.75rem 1.5rem, background primary, color white, border none, border-radius 8px, cursor pointer, font-weight 500
  - .sendButton:hover: background primary-dark
  - .sendButton:disabled: opacity 0.5, cursor not-allowed
  - **Acceptance**: Input field expands, send button has clear states

- [ ] T045 [Phase 3] Add message fade-in animation
  - @keyframes fadeIn: from { opacity 0, transform translateY(10px) }, to { opacity 1, transform translateY(0) }
  - Apply to .message: animation fadeIn 300ms ease-in
  - **Acceptance**: Messages fade in smoothly when sent or received

### Testing for Phase 3

- [ ] T046 [Phase 3] Test chat panel opening and closing
  - Click floating button to open chat
  - Verify: panel slides in from right, header/content/footer visible
  - Click close button (X)
  - Verify: panel closes (slides out or disappears)
  - **Acceptance**: Open/close functionality works correctly

- [ ] T047 [Phase 3] Test sending message in whole-book mode
  - Open chat (mode should default to "Whole-book")
  - Type question in input field
  - Click send button
  - Verify: user message appears (aligned right, blue), loading indicator shows
  - Wait for response
  - Verify: AI message appears (aligned left, gray), loading stops
  - **Acceptance**: Message flow works, user/AI messages visually distinct

- [ ] T048 [Phase 3] Test citations rendering as CitationCard
  - Send question that returns citations
  - Verify: citations display as cards (icon, heading, snippet)
  - Verify: "📚 Sources:" title above citations
  - Hover over citation card (desktop)
  - Verify: border color changes, card shifts right slightly
  - Click citation card
  - Verify: navigates to correct document section
  - **Acceptance**: Citations render as cards, clickable, navigation works

- [ ] T049 [Phase 3] Test mode switching (whole-book ↔ selection)
  - Open chat in whole-book mode
  - Change mode selector to "Selection"
  - Verify: mode changes, input placeholder updates
  - Send message in selection mode
  - Verify: message sent with correct mode
  - Switch back to "Whole-book"
  - Verify: conversation history preserved
  - **Acceptance**: Mode switching works, history preserved

- [ ] T050 [Phase 3] Test loading indicator
  - Send message, observe loading state
  - Verify: LoadingIndicator component appears (3 bouncing dots, "AI is typing...")
  - Verify: input field disabled, send button shows spinner
  - Response arrives
  - Verify: loading indicator disappears, input re-enabled
  - **Acceptance**: Loading states clear, animations smooth

- [ ] T051 [Phase 3] Test error handling
  - Disconnect network (DevTools: throttling → offline)
  - Send message
  - Verify: ErrorMessage component appears with error text and retry button
  - Click "Retry" button
  - Verify: message resends, loading indicator appears
  - Reconnect network, wait for response
  - Verify: response arrives, error message dismissed
  - **Acceptance**: Error handling works, retry functional

- [ ] T052 [Phase 3] Test empty state
  - Open chat for first time (no messages)
  - Verify: empty state displays (icon, helpful text)
  - Send first message
  - Verify: empty state disappears, message appears
  - **Acceptance**: Empty state helpful, disappears after first message

**Checkpoint**: ✅ ChatPanelPlaceholder refactored, all functionality works, components integrated

---

## Phase 4: TextSelectionTooltip Redesign (1-1.5 hours)

**Purpose**: Modernize tooltip with smart positioning, animations, preview text

**Goal**: Professional tooltip that appears near selection, fades smoothly, shows preview

- [ ] T053 [Phase 4] Create new TextSelectionTooltip.tsx file
  - File: `src/components/chat/TextSelectionTooltip.tsx`
  - TypeScript interface: TextSelectionTooltipProps { selectedText, position { top, left }, onAskAbout, onDismiss, visible }
  - State: placement ('above' | 'below'), initially 'above'
  - useEffect: if visible && position.top < 100, set placement to 'below', else 'above'
  - Return null if !visible
  - **Acceptance**: Component renders with proper TypeScript types

- [ ] T054 [Phase 4] Implement tooltip JSX structure
  - Container div: className={`${styles.tooltip} ${styles[placement]}`}
  - Inline style: `style={{ top: position.top, left: position.left }}`
  - Preview div: show first 50 chars of selectedText, add "..." if longer
  - Close button: `<button className={styles.closeButton} onClick={onDismiss}>✕</button>`
  - Ask button: `<button className={styles.askButton} onClick={onAskAbout}>💬 Ask about this</button>`
  - **Acceptance**: Tooltip structure complete with preview, close, ask button

- [ ] T055 [Phase 4] Create TextSelectionTooltip.module.css stylesheet
  - File: `src/components/chat/TextSelectionTooltip.module.css`
  - .tooltip: position absolute, z-index 2100, background surface-color, border 1px solid emphasis-300, border-radius 8px, box-shadow 0 4px 12px rgba(0,0,0,0.15), padding 0.75rem, max-width 300px
  - Animation: fadeIn 200ms ease-out
  - @keyframes tooltipFadeIn: from { opacity 0, transform translateY(-4px) }, to { opacity 1, transform translateY(0) }
  - **Acceptance**: Tooltip displays with proper styling and shadow

- [ ] T056 [Phase 4] Add smart positioning styles (above/below)
  - .tooltip.above: transform translateY(-100%) translateY(-8px)
  - .tooltip.below: transform translateY(8px)
  - **Acceptance**: Tooltip positions above selection by default, below if no space above

- [ ] T057 [Phase 4] Style preview text
  - .preview: font-size 0.85rem, color emphasis-700, font-style italic, margin-bottom 0.5rem, line-height 1.4
  - **Acceptance**: Preview text readable, shows first 50 chars of selection

- [ ] T058 [Phase 4] Style close button
  - .closeButton: position absolute, top 0.5rem, right 0.5rem, background none, border none, font-size 1rem, color emphasis-600, cursor pointer, padding 0.25rem
  - .closeButton:hover: color emphasis-900
  - **Acceptance**: Close button (X) top-right corner, clickable

- [ ] T059 [Phase 4] Style ask button
  - .askButton: width 100%, padding 0.5rem 1rem, background primary, color white, border none, border-radius 6px, font-size 0.875rem, font-weight 500, cursor pointer, transition background 200ms
  - .askButton:hover: background primary-dark
  - **Acceptance**: Ask button full width, clear CTA, hover effect

- [ ] T060 [Phase 4] Hide tooltip on mobile (<768px)
  - @media (max-width: 768px): .tooltip { display: none; }
  - **Acceptance**: Tooltip does not appear when selecting text on mobile

### Testing for Phase 4

- [ ] T061 [Phase 4] Test tooltip appearance on text selection (desktop)
  - On desktop (>768px), select text (20+ characters) on any textbook page
  - Verify: tooltip appears above selection (or below if near top of page)
  - Verify: tooltip shows first 50 chars of selected text with "..."
  - Verify: close button (X) and "Ask about this" button visible
  - **Acceptance**: Tooltip appears within 100ms, positioned correctly

- [ ] T062 [Phase 4] Test tooltip positioning (above vs below)
  - Select text at top of page (position.top < 100px)
  - Verify: tooltip appears below selection
  - Select text in middle of page
  - Verify: tooltip appears above selection
  - **Acceptance**: Smart positioning works based on available space

- [ ] T063 [Phase 4] Test tooltip fade-in animation
  - Select text, observe tooltip appearance
  - Verify: tooltip fades in smoothly over 200ms
  - Open DevTools Performance, record animation
  - Verify: animation runs at 60fps, no dropped frames
  - **Acceptance**: Fade-in animation smooth and performant

- [ ] T064 [Phase 4] Test tooltip dismissal
  - Select text, tooltip appears
  - Click close button (X)
  - Verify: tooltip dismisses (fade out or immediate hide)
  - Select text again, tooltip appears
  - Click outside tooltip
  - Verify: tooltip dismisses (onDismiss called)
  - Select text, press Escape key
  - Verify: tooltip dismisses
  - **Acceptance**: All dismissal methods work (X button, click outside, Escape)

- [ ] T065 [Phase 4] Test "Ask about this" button
  - Select text, tooltip appears
  - Click "💬 Ask about this" button
  - Verify: tooltip dismisses, chat panel opens in selection mode
  - Verify: selected text displayed as context in chat
  - Verify: input field focused for immediate typing
  - **Acceptance**: Tooltip → chat flow seamless, selection mode activated

- [ ] T066 [Phase 4] Test tooltip on mobile (should be hidden)
  - Open DevTools, set mobile viewport (iPhone SE 375px)
  - Select text on textbook page
  - Verify: tooltip does NOT appear
  - **Acceptance**: Tooltip hidden on mobile (<768px) via CSS media query

**Checkpoint**: ✅ Tooltip redesigned, smart positioning works, animations smooth

---

## Phase 5: Message Bubbles & Animations (1-1.5 hours)

**Purpose**: Polish message bubble design and add smooth animations

**Goal**: User/AI messages clearly distinct, fade-in animations smooth, empty state helpful

- [ ] T067 [P] [Phase 5] Refine user message bubble styling
  - .userMessage: align-self flex-end, max-width 80%
  - Background: `var(--ifm-color-primary-lightest, #e7f2ff)` (light blue)
  - Border-left: `4px solid var(--ifm-color-primary, #0066cc)` (accent)
  - Padding: 1rem, border-radius: 12px 12px 0 12px (rounded except bottom-right)
  - **Acceptance**: User messages align right, blue background, distinct from AI

- [ ] T068 [P] [Phase 5] Refine AI message bubble styling
  - .aiMessage: align-self flex-start, max-width 85%
  - Background: `var(--ifm-color-emphasis-100, #f5f5f5)` (light gray)
  - Border: `1px solid var(--ifm-color-emphasis-300, #e0e0e0)`
  - Padding: 1rem, border-radius: 12px 12px 12px 0 (rounded except bottom-left)
  - **Acceptance**: AI messages align left, gray background, distinct from user

- [ ] T069 [Phase 5] Add message fade-in animation (already in Phase 3, verify)
  - Verify @keyframes fadeIn defined: from { opacity 0, transform translateY(10px) }, to { opacity 1, transform translateY(0) }
  - Verify .message has: animation fadeIn 300ms ease-in
  - **Acceptance**: New messages fade in smoothly from slightly below

- [ ] T070 [Phase 5] Style empty state (already in Phase 3, polish)
  - .emptyState: text-align center, padding 3rem 1rem, color emphasis-600
  - .emptyIcon: font-size 3rem, margin-bottom 1rem, display block
  - .emptyText: font-size 1rem, line-height 1.6, max-width 400px, margin 0 auto
  - Add helpful prompt text based on mode (whole-book vs selection)
  - **Acceptance**: Empty state centered, icon large, text helpful

- [ ] T071 [Phase 5] Add reduced motion support for all animations
  - @media (prefers-reduced-motion: reduce): all * and *::before, *::after animation-duration 0.01ms, transition-duration 0.01ms
  - **Acceptance**: Enable reduced motion in browser, verify all animations disabled

### Testing for Phase 5

- [ ] T072 [Phase 5] Test user message styling
  - Send message as user
  - Verify: message aligns right, blue background, border-left accent, rounded corners (except bottom-right)
  - **Acceptance**: User message visually distinct and professional

- [ ] T073 [Phase 5] Test AI message styling
  - Receive response from AI
  - Verify: message aligns left, gray background, border all around, rounded corners (except bottom-left)
  - **Acceptance**: AI message visually distinct from user message

- [ ] T074 [Phase 5] Test message fade-in animation
  - Send message, observe appearance
  - Verify: message fades in over 300ms with slight upward motion
  - Open DevTools Performance, record animation
  - Verify: animation runs at 60fps, no dropped frames
  - **Acceptance**: Fade-in smooth and performant

- [ ] T075 [Phase 5] Test empty state display
  - Open chat for first time (no messages)
  - Verify: empty state displays with large icon, helpful text
  - Text should mention: topics you can ask about, or instruction to select text
  - **Acceptance**: Empty state helpful and inviting, not blank/confusing

- [ ] T076 [Phase 5] Test reduced motion support
  - Enable reduced motion in browser settings (or DevTools)
  - Open chat, send message
  - Verify: all animations disabled (instant appearance, no fade/slide)
  - **Acceptance**: Animations respect user's reduced motion preference

**Checkpoint**: ✅ Message bubbles polished, animations smooth, accessibility supported

---

## Phase 6: Input Area & Accessibility (1-1.5 hours)

**Purpose**: Polish input area, add keyboard navigation, ARIA labels, focus indicators

**Goal**: Chat fully accessible via keyboard, screen reader announces states, focus clear

- [ ] T077 [Phase 6] Style input textarea (auto-expand, char limit)
  - .input: flex 1, padding 0.75rem, border 1px solid emphasis-300, border-radius 8px
  - Font: inherit (match page font), font-size 1rem, line-height 1.5
  - Resize: vertical, min-height: 2.5rem (2 rows), max-height: 7.5rem (5 rows)
  - Max-length: 1000 (enforced with maxLength attribute)
  - **Acceptance**: Input expands to max 5 rows, then scrolls, 1000 char limit enforced

- [ ] T078 [Phase 6] Style send button (disabled states, loading spinner)
  - .sendButton: padding 0.75rem 1.5rem, background primary, color white, border none, border-radius 8px, font-weight 500, cursor pointer
  - .sendButton:hover: background primary-dark
  - .sendButton:disabled: opacity 0.5, cursor not-allowed, background primary (no hover effect)
  - Button content: `{loading ? '⏳' : '→'} Send` (emoji changes based on state)
  - **Acceptance**: Send button clear states (normal, hover, disabled, loading)

- [ ] T079 [Phase 6] Add keyboard navigation (Enter, Shift+Enter, Escape)
  - Implement handleKeyDown function in ChatPanelPlaceholder
  - Enter key (without Shift): call handleSend if input not empty and not loading
  - Shift+Enter: allow default behavior (add newline in textarea)
  - Escape key: call onClose (close chat panel)
  - **Acceptance**: Enter sends message, Shift+Enter adds newline, Escape closes panel

- [ ] T080 [Phase 6] Add ARIA labels to all interactive elements
  - Chat panel: `aria-label="Study Assistant Chat"`
  - Close button: `aria-label="Close chat"`
  - Mode selector: `aria-label="Select chat mode"`
  - Input field: `aria-label="Type your question"`
  - Send button: `aria-label="Send message"`
  - Citation cards: `aria-label="Citation: {heading}"`
  - **Acceptance**: All interactive elements have ARIA labels

- [ ] T081 [Phase 6] Add ARIA live regions for state changes
  - Loading state: LoadingIndicator already has `role="status" aria-live="polite" aria-label="AI is typing"`
  - Error state: ErrorMessage already has `role="alert"`
  - Panel open/close: Add `aria-live="polite"` announcement (optional, may be handled by parent)
  - **Acceptance**: Screen reader announces loading, error states

- [ ] T082 [Phase 6] Add visible focus indicators to all focusable elements
  - Global rule for .panel *:focus-visible: outline 2px solid primary, outline-offset 2px, border-radius 4px
  - Input focus: already styled (border-color primary, box-shadow)
  - Button focus: add outline on :focus-visible
  - Citation card focus: add outline on :focus-visible
  - **Acceptance**: Tab through UI, clear outline visible on focused elements

- [ ] T083 [Phase 6] Ensure tab order is logical (input → send → close → mode)
  - Verify tab order: input field → send button → close button → mode selector
  - Add tabIndex if needed to enforce logical order
  - **Acceptance**: Tab navigation flows logically through UI

### Testing for Phase 6

- [ ] T084 [Phase 6] Test input field expansion and char limit
  - Type short message (1 line)
  - Verify: input height is 2 rows
  - Type long message (5+ lines)
  - Verify: input expands to max 5 rows, then scrolls
  - Type 1000 characters
  - Verify: cannot type more (maxLength enforced)
  - **Acceptance**: Input expands correctly, char limit enforced

- [ ] T085 [Phase 6] Test send button states
  - Input empty
  - Verify: send button disabled (grayed out, not clickable)
  - Type message
  - Verify: send button enabled
  - Click send, observe loading state
  - Verify: send button disabled, shows spinner emoji (⏳)
  - Response arrives
  - Verify: send button re-enabled, shows arrow emoji (→)
  - **Acceptance**: Button states clear, user cannot double-send

- [ ] T086 [Phase 6] Test keyboard shortcuts
  - Type message, press Enter (without Shift)
  - Verify: message sends
  - Type message, press Shift+Enter
  - Verify: newline added, message not sent
  - Press Escape with chat open
  - Verify: chat panel closes
  - **Acceptance**: All keyboard shortcuts work as expected

- [ ] T087 [Phase 6] Test keyboard navigation (Tab)
  - Open chat, press Tab repeatedly
  - Verify tab order: input → send button → close button → mode selector → (repeat or exit panel)
  - All focusable elements reachable
  - **Acceptance**: Logical tab order, all elements accessible

- [ ] T088 [Phase 6] Test focus indicators
  - Use keyboard to navigate (Tab)
  - Verify: clear outline appears on focused element (input, buttons, citations)
  - Outline should be 2px solid primary color, visible against all backgrounds
  - **Acceptance**: Focus indicators visible on all interactive elements

- [ ] T089 [Phase 6] Test screen reader announcements (NVDA/VoiceOver)
  - Open chat with screen reader enabled
  - Verify: screen reader announces "Study Assistant Chat" or similar
  - Send message
  - Verify: screen reader announces "AI is typing" when loading
  - Response arrives
  - Verify: screen reader announces new message (or allows reading of new content)
  - Trigger error
  - Verify: screen reader announces error message
  - **Acceptance**: All critical state changes announced by screen reader

**Checkpoint**: ✅ Input area polished, keyboard navigation works, accessibility complete

---

## Phase 7: Final Polish & Testing (1.5-2 hours)

**Purpose**: Comprehensive testing across devices, themes, edge cases. Fix any issues found.

**Goal**: All success criteria met, chat works flawlessly on all devices and themes

### Cross-Device Testing

- [ ] T090 [P] [Phase 7] Test on iPhone SE (375px width)
  - Open chat, verify: panel 100% width, no horizontal scroll
  - Send message, verify: keyboard appears, input visible above keyboard
  - Receive response with citations, verify: cards readable, tappable
  - Close chat, verify: panel closes smoothly
  - **Acceptance**: All functionality works on smallest mobile device

- [ ] T091 [P] [Phase 7] Test on iPad Mini (768px width, portrait and landscape)
  - Portrait: verify panel width ~80%, content readable
  - Landscape: verify panel width ~40-50%, optimal reading
  - Send message, verify: layout remains stable
  - **Acceptance**: Tablet layout appropriate for both orientations

- [ ] T092 [P] [Phase 7] Test on MacBook (1440px width)
  - Verify: panel width 450px, centered vertically
  - Verify: height 80vh, max 700px
  - Send message with multiple citations, verify: all readable
  - **Acceptance**: Desktop layout optimal, professional appearance

- [ ] T093 [P] [Phase 7] Test on Android phone (various sizes: 360px, 412px)
  - Verify: panel adapts to different Android screen sizes
  - Test: virtual keyboard behavior (input remains visible)
  - **Acceptance**: Works on common Android devices

### Theme Testing

- [ ] T094 [Phase 7] Test light theme
  - Load page in light mode, open chat
  - Verify: all colors readable, proper contrast (use contrast checker tool)
  - Verify: user messages blue, AI messages gray, citations have clear borders
  - **Acceptance**: Light theme looks professional, all text readable

- [ ] T095 [Phase 7] Test dark theme
  - Toggle to dark mode with chat open
  - Verify: colors transition smoothly (200ms), no flash
  - Verify: all colors adapt (panel background dark, text light, messages use dark theme colors)
  - Verify: all text readable in dark mode (proper contrast)
  - **Acceptance**: Dark theme looks professional, smooth transition

- [ ] T096 [Phase 7] Test theme toggling with chat open
  - Open chat, send messages, toggle theme light ↔ dark multiple times
  - Verify: each toggle is smooth, no flashing or broken colors
  - Verify: conversation history remains, layout stable
  - **Acceptance**: Theme toggle seamless, no UI issues

### Edge Case Testing

- [ ] T097 [Phase 7] Test long message (5000 characters)
  - Send or receive message with 5000 characters
  - Verify: message displays with scroll if needed, doesn't break layout
  - Verify: message bubble has max-width, word-break works
  - **Acceptance**: Long messages handled gracefully

- [ ] T098 [Phase 7] Test long URL or word (100+ characters, no spaces)
  - Send message containing very long URL (e.g., base64 data URL)
  - Verify: word breaks properly, doesn't overflow bubble
  - CSS: word-break: break-word, overflow-wrap: anywhere
  - **Acceptance**: Long words don't break layout

- [ ] T099 [Phase 7] Test many citations (10+)
  - Receive response with 10+ citations
  - Verify: all citations display as cards, scrollable
  - Verify: no performance issues (smooth scroll)
  - **Acceptance**: Many citations handled without lag

- [ ] T100 [Phase 7] Test citation with very long heading or snippet
  - Citation with 200-character heading
  - Verify: heading truncates with ellipsis (overflow hidden, text-overflow ellipsis)
  - Citation with 500-character snippet
  - Verify: snippet clamped to 2 lines (line-clamp: 2)
  - **Acceptance**: Long citation text truncates gracefully

- [ ] T101 [Phase 7] Test rapid clicking (double-send prevention)
  - Type message, click send button 10 times rapidly
  - Verify: only one message sent, subsequent clicks ignored (button disabled)
  - **Acceptance**: Double-send prevented by disabled state

- [ ] T102 [Phase 7] Test closing chat while AI is responding
  - Send message, immediately close chat (before response arrives)
  - Reopen chat
  - Verify: response appears in conversation (request continued in background)
  - **Acceptance**: Closing during loading doesn't lose response

### Performance Testing

- [ ] T103 [Phase 7] Test panel animation performance (60fps)
  - Open DevTools Performance tab
  - Record panel opening animation
  - Verify: animation runs at 60fps, no dropped frames
  - Verify: uses GPU-accelerated properties (transform, opacity only)
  - **Acceptance**: All animations smooth, 60fps maintained

- [ ] T104 [Phase 7] Test panel opening speed (<300ms)
  - Click floating button to open chat
  - Measure time from click to panel fully visible
  - Verify: panel opens in <300ms (animation duration)
  - **Acceptance**: Panel opens quickly, feels responsive

- [ ] T105 [Phase 7] Test bundle size increase (<5KB)
  - Build project before and after chat UI changes
  - Compare bundle sizes (CSS only, minimal JS changes)
  - Verify: increase is <5KB (mostly CSS, some JSX restructuring)
  - **Acceptance**: Minimal bundle size impact

- [ ] T106 [Phase 7] Test layout shift (CLS score)
  - Open chat, send messages, scroll
  - Use DevTools Lighthouse to measure CLS (Cumulative Layout Shift)
  - Verify: CLS remains low (no unexpected layout shifts)
  - **Acceptance**: No janky layout shifts when messages load

### Final Validation

- [ ] T107 [Phase 7] Verify all success criteria from spec.md
  - Go through spec.md Success Criteria section (SC-001 through SC-019)
  - Check off each criterion, test if not already verified
  - **Acceptance**: All success criteria met and documented

- [ ] T108 [Phase 7] Run automated tests (if implemented)
  - Run test suite: API integration tests, state management tests
  - Verify: all tests pass, no regressions
  - **Acceptance**: Automated tests pass (if implemented in Phase 3)

- [ ] T109 [Phase 7] Contrast ratio verification (WCAG AA)
  - Use contrast checker tool (WebAIM or browser extension)
  - Check all text/background combinations in light and dark mode
  - Verify: all meet WCAG AA (4.5:1 for normal text, 3:1 for large text)
  - **Acceptance**: All text meets accessibility contrast standards

- [ ] T110 [Phase 7] Feature flag activation
  - Update feature flag `enableNewChatUI` to `true` (enable new UI by default)
  - Test: verify new UI loads instead of legacy UI
  - Keep legacy files for 1 sprint (rollback safety)
  - **Acceptance**: New UI enabled, feature flag toggles correctly

**Checkpoint**: ✅ All testing complete, all success criteria met, ready for production

---

## Post-Implementation Tasks

### Documentation & Cleanup

- [ ] T111 [Post] Create Prompt History Record (PHR)
  - Stage: "tasks" (or "green" if implementing)
  - Title: "Chat UI Redesign Implementation Tasks"
  - Feature: "003-chat-ui-redesign"
  - Include: all task IDs completed, files created/modified, tests run
  - Route: `history/prompts/003-chat-ui-redesign/`
  - **Acceptance**: PHR created with complete task summary

- [ ] T112 [Post] Update constitution.md if needed
  - Review: any new patterns or principles established during implementation
  - Update constitution if new code standards emerged
  - **Acceptance**: Constitution reflects learnings from this feature

- [ ] T113 [Post] Suggest ADRs for architectural decisions
  - Decision 1: Feature flag rollback strategy (from plan.md)
  - Decision 2: Component extraction architecture (CitationCard, LoadingIndicator, ErrorMessage)
  - Decision 3: CSS Modules with Docusaurus theme variables
  - Suggest: `/sp.adr [decision-title]` for each decision
  - Wait for user consent before creating ADRs
  - **Acceptance**: ADR suggestions made, pending user approval

- [ ] T114 [Post] Schedule legacy code cleanup (1 sprint later)
  - Set reminder: remove `.legacy.*` files after 1 sprint (2 weeks) if no issues
  - Files to remove: ChatPanelPlaceholder.legacy.tsx/css, TextSelectionTooltip.legacy.tsx/css
  - Remove feature flag if new UI is stable
  - **Acceptance**: Cleanup scheduled, technical debt tracked

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Setup)**: No dependencies - start immediately
- **Phase 1 (CSS Foundation)**: Depends on Phase 0 (new files created)
- **Phase 2 (Component Extraction)**: Can start in parallel with Phase 1 (different files)
- **Phase 3 (ChatPanel Refactor)**: Depends on Phase 1 (CSS) and Phase 2 (components)
- **Phase 4 (Tooltip Redesign)**: Can start in parallel with Phase 3 (different file)
- **Phase 5 (Message Bubbles)**: Depends on Phase 3 (refines existing CSS from Phase 1)
- **Phase 6 (Accessibility)**: Depends on Phase 3-5 (adds to existing components)
- **Phase 7 (Testing)**: Depends on all previous phases being complete

### Within Each Phase

**Phase 0**: Sequential (T001 → T002 → T003 → T004 → T005)

**Phase 1**: Tasks T006-T008 can run in parallel (different CSS sections), then T009-T014 sequential, then T015-T018 parallel (testing)

**Phase 2**: All component creation tasks (T019-T020, T022-T023, T024-T025) can run in parallel, then T026-T028 (testing) sequential

**Phase 3**: T029-T030 must be first (file creation, structure), then T031-T038 can run in parallel (different JSX sections), then T039-T045 can run in parallel (different CSS rules), then T046-T052 sequential (testing)

**Phase 4**: T053-T054 first (file creation), then T055-T060 can run in parallel (CSS), then T061-T066 sequential (testing)

**Phase 5**: All styling tasks (T067-T071) can run in parallel, then T072-T076 sequential (testing)

**Phase 6**: T077-T078 parallel (CSS), T079-T083 sequential (JS logic + ARIA), then T084-T089 sequential (testing)

**Phase 7**: All device testing (T090-T093) can run in parallel, theme testing (T094-T096) sequential, edge cases (T097-T102) can run in parallel, performance tests (T103-T106) sequential, final validation (T107-T110) sequential

### Parallel Opportunities

**High Parallelism**:
- Phase 1 + Phase 2 can run in parallel (different files)
- Phase 3 + Phase 4 can run in parallel (different files)
- Within phases, many CSS and component tasks can run in parallel

**Sequential Bottlenecks**:
- Phase 0 must complete before any implementation
- Phase 3 requires Phase 1 (CSS) and Phase 2 (components)
- Phase 7 requires all previous phases

---

## Task Summary

**Total Tasks**: 114 (T001-T114)

**Breakdown by Phase**:
- Phase 0 (Setup): 5 tasks
- Phase 1 (CSS Foundation): 13 tasks
- Phase 2 (Components): 10 tasks
- Phase 3 (ChatPanel): 24 tasks
- Phase 4 (Tooltip): 14 tasks
- Phase 5 (Messages): 9 tasks
- Phase 6 (Accessibility): 13 tasks
- Phase 7 (Testing): 21 tasks
- Post-Implementation: 4 tasks

**Estimated Time**: 11-14 hours total (as per plan.md)

**Critical Path**: Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 5 → Phase 6 → Phase 7

**Fastest Path (with parallelism)**: ~8-10 hours if Phase 1+2 and Phase 3+4 run in parallel

---

## Implementation Notes

1. **Start with Phase 0**: Create safety net first (feature flag, legacy backups)
2. **Parallelize where possible**: Phase 1 + Phase 2, many CSS tasks, all device testing
3. **Test after each phase**: Don't skip checkpoints, catch issues early
4. **Use feature flag**: Keep `enableNewChatUI: false` until Phase 7 complete
5. **Commit frequently**: After each phase or logical group of tasks
6. **Validate on real devices**: Don't rely only on browser emulators for mobile testing
7. **Check accessibility**: Use screen reader and keyboard navigation throughout
8. **Monitor performance**: Use DevTools to verify 60fps animations

---

**Next Steps After Approval**:
1. Begin Phase 0 (Setup & Backup)
2. Validate Phase 0 checkpoint
3. Proceed to Phase 1 (CSS Foundation)
4. Continue through phases sequentially or in parallel where possible
5. Create PHR after all phases complete
6. Suggest ADRs for architectural decisions
