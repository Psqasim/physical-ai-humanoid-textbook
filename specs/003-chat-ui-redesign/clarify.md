# Clarification Questions - Study Assistant UI Redesign

**Feature**: 003-chat-ui-redesign
**Created**: 2025-12-08
**Status**: Clarifications Resolved

## Purpose

This document captures clarification questions that arose during spec review and provides clear answers before implementation begins. Each question is resolved to eliminate ambiguity during coding.

---

## Section 1: Responsive Behavior

### Q1.1: Chat Panel Overlay Behavior on Mobile

**Question**: When chat panel opens on mobile (100% width), should the underlying page content:
- A) Be completely hidden (chat takes over entire screen)
- B) Remain dimly visible behind semi-transparent overlay
- C) Be pushed to the left (slide-out menu style)

**Answer**: **B) Semi-transparent overlay**
- Rationale: Shows user they're still on the same page, can dismiss by tapping overlay
- Implementation: Add `backdrop` div with `rgba(0,0,0,0.5)` background, click to close
- Preserves context while focusing attention on chat

### Q1.2: Virtual Keyboard Handling on Mobile

**Question**: When user taps input on mobile and keyboard appears:
- A) Messages area shrinks to fit above keyboard (content may be compressed)
- B) Panel height remains fixed, keyboard overlays panel (input might be hidden)
- C) Use `viewport-fit=cover` and resize panel dynamically when keyboard shows

**Answer**: **C) Dynamic panel resize**
- Rationale: Most predictable UX, input always visible, messages remain accessible
- Implementation: Use CSS `height: 100dvh` (dynamic viewport height) for panel
- Add `padding-bottom: env(safe-area-inset-bottom)` for iOS home indicator

### Q1.3: Floating Button Position on Mobile

**Question**: When chat opens on mobile (full screen), should floating button:
- A) Hide completely (user must use X button to close)
- B) Remain visible in corner (redundant with X button)
- C) Transform into close button at bottom

**Answer**: **A) Hide completely**
- Rationale: Floating button's job is done (opened chat), X button in header is sufficient
- Implementation: Add `display: none` to floating button when `isOpen === true`
- Simplifies mobile UI, reduces clutter

---

## Section 2: Message Display

### Q2.1: Message Timestamp Display

**Question**: Spec mentions "Timestamp on messages (optional, subtle)". Should timestamps be:
- A) Always visible below each message
- B) Visible only on hover (desktop) / tap (mobile)
- C) Not implemented (defer to future feature)

**Answer**: **C) Not implemented initially**
- Rationale: Adds complexity without clear user value in v1, not in top 5 requirements
- Future: Can add in Phase 2 after user feedback
- Implementation: Skip timestamp logic entirely for now

### Q2.2: Message Grouping

**Question**: If user sends multiple messages rapidly (before AI responds), should they:
- A) All appear as separate bubbles with spacing between each
- B) Group together with reduced spacing (chat app style)
- C) Merge into single bubble with line breaks

**Answer**: **A) Separate bubbles with normal spacing**
- Rationale: Each message is distinct question, don't assume they're related
- Implementation: Each message is standalone `<div>` with consistent margin
- Keeps logic simple, clear visual separation

### Q2.3: Very Long Messages

**Question**: If AI response is extremely long (e.g., 5000 chars), should:
- A) Entire message display with scrollable panel
- B) Message truncated with "Show more" expand button
- C) Message paginated (e.g., "1 of 3")

**Answer**: **A) Scrollable panel**
- Rationale: User asked for full answer, don't hide information behind clicks
- Implementation: No truncation logic, panel has `overflow-y: auto`, messages auto-scroll to bottom
- Performance: React handles virtual rendering efficiently

---

## Section 3: Citations

### Q3.1: Citation Click Behavior

**Question**: When user clicks citation card, should it:
- A) Navigate immediately (current tab), chat panel stays open
- B) Navigate immediately, chat panel closes automatically
- C) Show preview popover first, "Go to section" button navigates

**Answer**: **A) Navigate, chat stays open** (as per user approval)
- Rationale: User may want to reference citation while continuing conversation
- Implementation: `<a href={docPath}>` with no `target="_blank"`, no `onClick` that closes panel
- User can close panel manually if needed

### Q3.2: Citation Snippet Length

**Question**: Citation snippet preview should be:
- A) Fixed 150 characters with ellipsis (as spec suggests)
- B) Variable length based on sentence boundaries (cut at period)
- C) Two lines max (CSS `line-clamp: 2`) regardless of character count

**Answer**: **C) Two lines with CSS clamp**
- Rationale: More visually consistent, works better across different font sizes
- Implementation: `.citationSnippet { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }`
- Responsive: Works on all screen sizes without manual truncation logic

### Q3.3: Multiple Citations Layout

**Question**: If AI response includes 10+ citations, should they:
- A) All display inline (could make message very tall)
- B) Display first 3, then "Show 7 more citations" button
- C) Display in collapsible section, initially collapsed

**Answer**: **A) All display inline**
- Rationale: Citations are evidence, hiding them reduces credibility
- Implementation: Stack vertically with `gap: 0.5rem`, panel scrolls naturally
- Performance: 10 citation cards render instantly, no perf concern

---

## Section 4: Text Selection Tooltip

### Q4.1: Tooltip Positioning Edge Cases

**Question**: If user selects text at top of viewport (no room above) or bottom (no room below):
- A) Tooltip flips to available side (above if bottom selected, below if top selected)
- B) Tooltip always appears in fixed position (e.g., center of screen)
- C) Tooltip appears offset to side (left or right) if no vertical room

**Answer**: **A) Smart flipping**
- Rationale: Tooltip should be near selection for context, flipping is standard UX
- Implementation: Calculate `selectionRect.top`, if `< 100px` place below, else place above
- Add 8px margin between tooltip and selection

### Q4.2: Tooltip on Mobile

**Question**: Text selection tooltip on mobile should:
- A) Appear same as desktop (may overlap native selection handles)
- B) Not appear at all (mobile users use floating button instead)
- C) Appear as bottom sheet sliding up from bottom

**Answer**: **B) Not appear on mobile**
- Rationale: Native mobile selection UI is inconsistent, tooltips conflict with system handles
- Implementation: Add media query `@media (max-width: 768px) { .tooltip { display: none; } }`
- Mobile users can open chat via floating button and paste selected text

### Q4.3: Tooltip Dismissal

**Question**: Tooltip should dismiss when:
- A) User clicks anywhere outside tooltip
- B) User clicks outside OR text selection is cleared
- C) User explicitly clicks X button only

**Answer**: **B) Click outside OR selection cleared**
- Rationale: Most intuitive - if selection disappears, tooltip should too
- Implementation: Add `document.addEventListener('click')` for outside clicks, `document.addEventListener('selectionchange')` to detect cleared selection
- X button is redundant but kept for explicit dismissal

---

## Section 5: Loading & Error States

### Q5.1: Loading Indicator Timing

**Question**: Typing dots animation should:
- A) Appear immediately when send is clicked
- B) Appear after 500ms delay (avoid flash for fast responses)
- C) Appear immediately but with fade-in animation

**Answer**: **A) Appear immediately**
- Rationale: Instant feedback assures user request was received
- Implementation: Add loading message to state immediately on send, no delay
- Fast responses just mean quick animation (feels snappy, not broken)

### Q5.2: Error Recovery

**Question**: When error occurs (network issue, API 500), should:
- A) Show error inline as message with "Retry" button
- B) Show error toast notification at top of panel
- C) Show modal dialog blocking chat

**Answer**: **A) Inline error message**
- Rationale: Error is contextual to specific message, doesn't block other chat functions
- Implementation: Error appears as special message type with red border, alert icon, and retry button
- User can continue conversation even if one message failed

### Q5.3: Request Timeout

**Question**: If backend takes >30 seconds, should:
- A) Request continue indefinitely until response or network failure
- B) Cancel request and show timeout error
- C) Show "Still thinking..." message after 30s, continue waiting

**Answer**: **B) Cancel and show timeout error**
- Rationale: 30s is reasonable limit, likely indicates backend issue
- Implementation: `setTimeout(30000, () => { abortController.abort(); setError('timeout'); })`
- Error message: "Request timed out. Try asking a shorter question."

---

## Section 6: Animations & Performance

### Q6.1: Animation Reduced Motion

**Question**: For users with `prefers-reduced-motion: reduce`, should:
- A) Disable all animations (instant open/close, no fades)
- B) Reduce animation duration (150ms instead of 300ms)
- C) Keep animations but remove bounces/slides (opacity only)

**Answer**: **A) Disable all animations**
- Rationale: Accessibility requirement, some users get motion sickness
- Implementation:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Q6.2: GPU Acceleration

**Question**: To ensure 60fps animations, should explicitly use:
- A) `transform` and `opacity` only (GPU-accelerated)
- B) `transform`, `opacity`, plus `filter` (for shadows)
- C) Any CSS property but with `will-change` hint

**Answer**: **A) Transform and opacity only**
- Rationale: Most performant, works on all devices including low-end mobile
- Implementation: Use `transform: translateX()` for slide, `opacity` for fades, avoid animating `height`, `width`, `box-shadow`, `margin`
- For shadows: set once, don't animate

---

## Section 7: Theme Integration

### Q7.1: Theme Transition

**Question**: When user toggles theme with chat open, should:
- A) Colors change instantly (0ms transition)
- B) Colors transition smoothly (200ms)
- C) Chat panel closes and reopens with new theme

**Answer**: **B) Smooth transition**
- Rationale: Abrupt color change is jarring, smooth transition feels polished
- Implementation: Add `transition: background-color 200ms, color 200ms, border-color 200ms;` to themed elements
- Keep duration short to avoid lag feel

### Q7.2: Custom Theme Variables

**Question**: If user has custom Docusaurus theme with non-standard color names, should:
- A) Use hardcoded fallback colors if variable undefined
- B) Throw error in console and use default colors
- C) Auto-detect primary color and derive palette

**Answer**: **A) Hardcoded fallbacks**
- Rationale: Graceful degradation, chat still works even with non-standard themes
- Implementation:
```css
background: var(--ifm-color-primary, #0066cc);
color: var(--ifm-color-content, #1c1e21);
```
- Fallbacks are sane defaults from standard Docusaurus theme

---

## Section 8: Input & Interaction

### Q8.1: Input Character Limit

**Question**: Should input field have character limit?
- A) No limit (user can type as much as they want)
- B) Soft limit with warning (e.g., "500 chars recommended")
- C) Hard limit (e.g., 1000 chars, can't type more)

**Answer**: **C) Hard limit 1000 chars**
- Rationale: RAG backend likely has embedding limit, prevents API errors
- Implementation: Add `maxLength={1000}` to input, show char counter at 900+ chars
- Error prevention better than error handling

### Q8.2: Input Multiline

**Question**: Should input be single-line or multiline (textarea)?
- A) Single-line input, Enter sends, no multiline support
- B) Multiline textarea, Enter sends, Shift+Enter adds line break
- C) Multiline textarea, always shows 2-3 rows

**Answer**: **B) Multiline with Shift+Enter**
- Rationale: Users may want to format questions with line breaks
- Implementation: Use `<textarea>`, `onKeyDown` checks `event.shiftKey`, auto-expand rows up to max 5
- Mobile: Enter sends (easier than Shift+Enter on touch keyboard)

### Q8.3: Send Button Disabled State

**Question**: Send button should be disabled when:
- A) Input is empty (no whitespace-only messages)
- B) Input is empty OR loading
- C) Loading only (allow sending empty for testing)

**Answer**: **B) Empty OR loading**
- Rationale: Empty messages are pointless, loading prevents multiple requests
- Implementation: `disabled={!input.trim() || loading}`
- Visual: Disabled button is grayed out with cursor: not-allowed

---

## Section 9: Mode Switching

### Q9.1: Mode Toggle Location

**Question**: Mode selector dropdown should be:
- A) In header next to title (as shown in mockup)
- B) In input area next to send button
- C) As tab switcher above messages area

**Answer**: **A) In header**
- Rationale: Mode is panel-level setting, belongs in header with title
- Implementation: `<select>` styled as button/dropdown in top-right of header (left of X button)
- Desktop: 150px wide, Mobile: Icon only (book icon vs. selection icon)

### Q9.2: Mode Switch with Messages

**Question**: If user has conversation in whole-book mode and switches to selection mode:
- A) Warn "This will clear conversation" with confirmation
- B) Keep existing messages, new questions use new mode
- C) Not allowed - disable mode switch after first message

**Answer**: **B) Keep messages, switch mode**
- Rationale: User may want to ask follow-up in different mode
- Implementation: `mode` state changes, existing messages stay, next question uses new mode
- No need to clear history (not confusing, each message shows its mode in context)

### Q9.3: Selection Mode Without Text

**Question**: If user manually switches to "Selection" mode but no text selected:
- A) Show error: "Please select text first"
- B) Allow but show warning in input placeholder: "Select text on page first"
- C) Auto-switch back to whole-book mode

**Answer**: **B) Allow with warning**
- Rationale: User intent is clear, they may select text after opening chat
- Implementation: Mode stays "Selection", placeholder says "Select text on any page to ask...", if they type question, send with empty `selectedText` (backend handles gracefully)

---

## Section 10: Accessibility

### Q10.1: Screen Reader Announcements

**Question**: Screen reader should announce:
- A) Every message as it arrives (may be verbose)
- B) Only critical changes (panel opened, error occurred)
- C) Messages only when user navigates to them

**Answer**: **B) Critical changes only**
- Rationale: Auto-announcements can interrupt user, especially for long AI responses
- Implementation: Use `role="status" aria-live="polite"` for errors, loading ("AI is typing"), panel open/close
- Messages have semantic HTML (`<ul>`, `<li>`) and ARIA labels, but don't auto-announce
- User can navigate to messages with arrow keys

### Q10.2: Focus Management

**Question**: When chat panel opens, focus should:
- A) Immediately move to input field (ready to type)
- B) Move to panel container (user can Tab to input)
- C) Stay on floating button that opened it

**Answer**: **A) Focus on input**
- Rationale: Primary action is typing question, skip Tab step
- Implementation: `useEffect(() => { if (isOpen) inputRef.current?.focus(); }, [isOpen])`
- When panel closes, focus returns to floating button (or element that opened it)

### Q10.3: Keyboard Shortcuts

**Question**: Should chat support keyboard shortcuts beyond Tab/Enter/Escape?
- A) Yes: Ctrl+K opens chat, Ctrl+/ toggles mode
- B) Yes: / focuses input (Discord style)
- C) No: Keep simple, avoid conflicts with browser/OS

**Answer**: **C) No custom shortcuts**
- Rationale: Shortcut conflicts are confusing, standard keys (Tab/Enter/Esc) are sufficient
- Implementation: Only handle Enter (send), Shift+Enter (newline), Escape (close)
- Future: Can add shortcuts after user feedback if requested

---

## Implementation Decisions Summary

All clarification questions have been resolved. Key decisions:

**Responsive**:
- Semi-transparent backdrop on mobile ✅
- Dynamic viewport height for keyboard ✅
- Hide floating button when chat open ✅

**Messages**:
- No timestamps in v1 ✅
- Separate bubbles (no grouping) ✅
- Full messages (no truncation) ✅

**Citations**:
- Navigate in same tab, chat stays open ✅
- 2-line CSS clamp for snippets ✅
- All citations display (no "Show more") ✅

**Tooltip**:
- Smart flip (above/below selection) ✅
- No tooltip on mobile ✅
- Dismiss on outside click or selection clear ✅

**Loading/Errors**:
- Immediate loading indicator ✅
- Inline error messages with retry ✅
- 30-second timeout with cancel ✅

**Animations**:
- Disable for reduced motion ✅
- Transform and opacity only (60fps) ✅
- 200ms theme transition ✅

**Input**:
- 1000 char hard limit ✅
- Multiline with Shift+Enter ✅
- Disabled when empty or loading ✅

**Modes**:
- Mode selector in header ✅
- Keep messages when switching ✅
- Allow selection mode without text (warning) ✅

**Accessibility**:
- Announce critical changes only ✅
- Auto-focus input on open ✅
- No custom keyboard shortcuts ✅

## Ready for Implementation

All ambiguities resolved. Proceeding to task breakdown (`tasks.md`).

---

# Additional Clarifications - Session 2 (2025-12-08)

**Focus**: CSS specifics, component structure, testing approach, rollback plan

## Section 11: Implementation Details

### Q11.1: Exact Color Values for Theme Variables

**Question**: Should we use hardcoded hex values from spec examples, CSS variables with fallbacks, or custom chat-specific CSS variables?

**Answer**: **Use CSS variables with fallbacks**
- Rationale: Ensures automatic theme adaptation when users switch between light/dark mode and stays consistent with future theme updates
- Implementation: Reference `--ifm-*` variables directly with hex fallbacks
- Documentation: List all required Docusaurus variables in spec (see Color System section)

### Q11.2: New Component Files Creation

**Question**: Should we keep all UI within ChatPanelPlaceholder.tsx, extract new components in same directory, or create a new subdirectory?

**Answer**: **Extract new components in same directory**
- Components: CitationCard, LoadingIndicator, ErrorMessage (each with .tsx + .module.css)
- Rationale: Provides modularity for testing and reuse while keeping related files together
- Location: Same directory as ChatPanelPlaceholder.tsx (no subdirectory needed)

### Q11.3: Testing Approach - Manual vs Automated Priority

**Question**: Should v1 be purely manual, include automated tests for critical logic only, or require full automated test suite?

**Answer**: **Automated tests for critical logic only**
- Test: API calls, state management, mode switching, error handling, timeout logic
- Defer: UI component tests, visual rendering, animation timing, accessibility tests
- Rationale: Balances speed with quality, catches regressions without slowing down visual redesign focus

### Q11.4: Rollback Plan if New UI Has Issues

**Question**: Should rollback be via git revert, feature flag toggle, or gradual A/B rollout?

**Answer**: **Feature flag to toggle between old and new UI**
- Implementation: `enableNewChatUI` flag with old code renamed to `*.legacy.*`
- Duration: Keep old code for 1 sprint (2 weeks) after launch
- Rationale: Provides instant rollback without redeployment if critical issues emerge
- Cleanup: Remove legacy code after validation period

---

## Implementation Impact Summary

These clarifications directly impact:

1. **CSS Implementation** (Phase 1): Clear variable naming and fallback strategy
2. **Component Architecture** (Phases 2-4): Three new component files to create
3. **Testing Strategy** (All phases): Focus test effort on logic, manual checks for UI
4. **Deployment Process** (Pre-launch): Feature flag setup required before rollout

All critical ambiguities now resolved. Ready for `/sp.plan` and `/sp.tasks`.
