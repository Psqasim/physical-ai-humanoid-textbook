# Feature Specification: Multilingual Support (EN / UR / JA)

**Feature Branch**: `001-multilingual-support`
**Created**: 2025-12-11
**Status**: Draft
**Input**: User description: "PROJECT: Physical AI & Humanoid Robotics Textbook — Multilingual Support (EN / UR / JA)"

## Summary

This specification defines multilingual capabilities for the Physical AI & Humanoid Robotics Textbook platform, enabling English, Urdu, and Japanese language support across the Docusaurus frontend, FastAPI backend, and RAG pipeline. The feature ensures global accessibility by providing localized UI strings, language-aware chat interactions, and language-tagged content retrieval with RTL support for Urdu.

---

## Problem Statement & Motivation

### Problem
The Physical AI & Humanoid Robotics Textbook currently supports only English, limiting accessibility for a global audience. Users who speak Urdu or Japanese cannot effectively use the Study Assistant chat interface, navigate the UI, or access translated content in their preferred language. Without language detection and language-aware responses, the learning experience is suboptimal for non-English speakers.

### Motivation
1. **Global Accessibility**: Enable users from Pakistan, Japan, and other regions to learn in their native language
2. **Improved User Experience**: Provide seamless language switching and persistent language preferences
3. **Enhanced RAG Quality**: Ensure chat responses match the user's language and retrieve language-appropriate content
4. **Cultural Inclusivity**: Support RTL text rendering for Urdu speakers and proper font/character support for Japanese
5. **Competitive Advantage**: Position the platform as a truly international educational resource

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Language Selection and Persistence (Priority: P1)

A first-time visitor arrives at the site with their browser set to Urdu. The system detects their language preference, displays the UI in Urdu with proper RTL layout, and persists this choice across sessions.

**Why this priority**: This is the foundation of multilingual support. Without language selection and persistence, no other multilingual features can function effectively. It delivers immediate value by showing users content in their preferred language.

**Independent Test**: Can be fully tested by visiting the site with different browser language settings, selecting languages from the switcher, and verifying persistence across page refreshes and new sessions.

**Acceptance Scenarios**:

1. **Given** a user with browser language set to "ur" (Urdu), **When** they visit the site for the first time, **Then** the UI displays in Urdu with RTL layout and the language switcher shows "Urdu" selected
2. **Given** a user selects "Japanese" from the language switcher, **When** they refresh the page, **Then** the UI remains in Japanese and their choice is persisted in localStorage
3. **Given** a user with browser language set to an unsupported language (e.g., French), **When** they visit the site, **Then** the UI defaults to English
4. **Given** a user on mobile device, **When** they select a language from the mobile menu, **Then** the entire UI updates without page reload

---

### User Story 2 - UI String Translation (Priority: P1)

A user navigating the site in Japanese sees all navbar items, footer links, buttons, error messages, and modal text in Japanese. The translation feels natural and contextually appropriate.

**Why this priority**: UI translations are the most visible aspect of multilingual support. Users immediately notice if buttons, menus, and navigation are not in their language. This directly impacts user trust and usability.

**Independent Test**: Can be tested by switching to each supported language and manually verifying all UI strings (navbar, footer, buttons, modals, error messages) are translated and make contextual sense.

**Acceptance Scenarios**:

1. **Given** the user has selected Japanese, **When** they view the navbar, **Then** all items display in Japanese ("コース" for Course, "学習アシスタント" for Study Assistant)
2. **Given** the user encounters an error (e.g., network failure), **When** the error message displays, **Then** the message is in their selected language
3. **Given** the user views the footer, **When** they read copyright and links, **Then** all text is translated appropriately
4. **Given** the user opens a modal dialog, **When** they read button labels, **Then** buttons show "キャンセル" (Cancel) and "確認" (Confirm) in Japanese

---

### User Story 3 - Study Assistant Language-Aware Chat (Priority: P1)

A user chatting in Urdu with the Study Assistant receives responses in Urdu, drawn from Urdu-tagged content when available, with proper RTL rendering and Urdu-appropriate formatting.

**Why this priority**: The Study Assistant is the core interactive feature. Without language-aware chat, the entire value proposition of multilingual support fails for the primary use case.

**Independent Test**: Can be tested by sending chat messages in each supported language and verifying responses match the input language, use appropriate content, and render correctly.

**Acceptance Scenarios**:

1. **Given** the user types a question in Urdu, **When** they send the message, **Then** the Study Assistant detects Urdu and responds in Urdu with RTL text alignment
2. **Given** the backend has Urdu-tagged documents, **When** the RAG pipeline searches for context, **Then** it prioritizes Urdu documents and falls back to English only if Urdu content is unavailable
3. **Given** the user switches from English to Japanese mid-conversation, **When** they send a new message, **Then** the assistant detects the language change and responds in Japanese
4. **Given** the system cannot detect language confidently, **When** the user sends a message, **Then** the assistant uses the UI language setting as fallback

---

### User Story 4 - Urdu RTL Support (Priority: P2)

An Urdu-speaking user views the entire site with proper right-to-left text rendering, mirrored layouts, and Urdu-specific typography. All UI elements (navbar, sidebar, chat interface) respect RTL conventions.

**Why this priority**: RTL support is essential for Urdu usability but is secondary to basic language functionality. Users can partially use the site with Urdu text even if layout is LTR, but proper RTL significantly improves experience.

**Independent Test**: Can be tested by selecting Urdu and verifying all page layouts, navigation, and text flow from right to left with proper CSS direction handling.

**Acceptance Scenarios**:

1. **Given** the user selects Urdu, **When** they view any page, **Then** text flows right-to-left and UI elements mirror (e.g., hamburger menu on right, scrollbars on left)
2. **Given** the chat interface is in Urdu, **When** messages display, **Then** user messages align right and assistant messages align left (reversed from LTR)
3. **Given** the user navigates the docs sidebar in Urdu, **When** they expand menu items, **Then** chevron icons point left instead of right
4. **Given** forms display in Urdu, **When** input fields render, **Then** text cursor starts at the right and moves left

---

### User Story 5 - Backend Language Detection (Priority: P2)

The backend API correctly identifies the language of incoming chat messages, tags them for analytics, and routes them to language-specific processing pipelines.

**Why this priority**: Language detection is critical for multilingual chat but is primarily a backend concern. It enables other features but is not directly visible to users, making it P2.

**Independent Test**: Can be tested by sending chat requests with various language texts to the API endpoint and verifying the response includes correct language detection metadata.

**Acceptance Scenarios**:

1. **Given** a chat message contains Urdu text, **When** the backend receives the request, **Then** it detects language as "ur" and includes this in the response metadata
2. **Given** a chat message contains mixed English and Japanese, **When** the backend processes it, **Then** it identifies the dominant language (Japanese) and responds accordingly
3. **Given** the backend cannot confidently detect language, **When** it processes the message, **Then** it falls back to the "preferredLanguage" parameter from the request header
4. **Given** the system monitors language usage, **When** messages are processed, **Then** language statistics are logged for analytics

---

### User Story 6 - Language-Tagged Content Retrieval (Priority: P2)

When a user asks a question in Japanese, the RAG pipeline queries Qdrant for Japanese-tagged documents first, then falls back to English if Japanese content is insufficient, ensuring relevant context.

**Why this priority**: Language-specific content retrieval improves answer quality but requires content to be translated and tagged first. It's valuable but not blocking for basic multilingual functionality.

**Independent Test**: Can be tested by creating test documents in multiple languages with specific language tags, then querying in each language and verifying retrieval prioritizes matching language tags.

**Acceptance Scenarios**:

1. **Given** the question is in Japanese and Japanese-tagged documents exist, **When** the RAG pipeline searches, **Then** it returns Japanese documents ranked higher than English
2. **Given** the question is in Urdu but only English documents exist, **When** the search completes, **Then** it returns English documents as fallback
3. **Given** a multilingual query (code example in English + question in Urdu), **When** the system processes it, **Then** it uses the detected primary language for filtering
4. **Given** embeddings are generated for a new document, **When** the document is indexed, **Then** it includes language metadata in Qdrant payload

---

### User Story 7 - Translation Toggle for Documentation (Priority: P3)

A user reading a chapter in English can toggle to view the same chapter in Urdu or Japanese if translations are available, with visual indicators showing translation status and quality.

**Why this priority**: Chapter translation is a content-level feature that depends on translated content availability. It's valuable for learning but lower priority than core UI and chat multilingual functionality.

**Independent Test**: Can be tested by creating test docs with translation files, then verifying the translation toggle button appears and switches between language versions correctly.

**Acceptance Scenarios**:

1. **Given** a chapter has Urdu and Japanese translations, **When** the user views the chapter, **Then** a language toggle appears showing "EN | UR | JA"
2. **Given** the user clicks the Urdu toggle, **When** the page updates, **Then** the chapter content displays in Urdu without changing the URL structure
3. **Given** a chapter has no Japanese translation, **When** the user selects Japanese as UI language, **Then** the chapter content remains in English with a note "Translation not available"
4. **Given** translations have different completion levels, **When** the toggle displays, **Then** incomplete translations show a badge (e.g., "85% complete")

---

### User Story 8 - Voice Input Edge Cases (Priority: P3)

A user speaking into the chat interface in Japanese has their speech correctly transcribed, language-detected, and processed, even with background noise or mixed-language input.

**Why this priority**: Voice input is an advanced feature that enhances accessibility but is not core to the multilingual experience. It's valuable for mobile and accessibility but lower priority.

**Independent Test**: Can be tested using browser speech recognition APIs with test audio in each supported language, verifying transcription accuracy and language detection robustness.

**Acceptance Scenarios**:

1. **Given** the user enables voice input and speaks in Japanese, **When** the transcription completes, **Then** the text is correctly transcribed in Japanese characters
2. **Given** the user speaks with background noise, **When** speech recognition processes, **Then** the system filters noise and detects language correctly
3. **Given** the user switches languages mid-speech (code-switching), **When** transcription completes, **Then** the system detects the dominant language
4. **Given** speech recognition fails, **When** the error occurs, **Then** the user sees an error message in their UI language prompting them to try again

---

### Edge Cases

- **What happens when a user sends a chat message in an unsupported language (e.g., Arabic)?** The system detects it as unsupported, responds in the UI language setting (with a note about limited support), and logs the language for future feature consideration.
- **How does the system handle partially translated pages?** Pages with incomplete translations display available translated content and fall back to English for untranslated sections, with clear visual indicators showing which sections are untranslated.
- **What happens when Qdrant has no documents in the requested language?** The RAG pipeline falls back to English documents, and the response includes a note: "Answered using English resources; [Language] translation pending."
- **How are language-specific special characters handled in search?** The RAG pipeline normalizes characters (e.g., Japanese kanji/hiragana/katakana) and uses language-aware tokenization to ensure accurate semantic search across scripts.
- **What happens when a user has JavaScript disabled?** The language switcher gracefully degrades to a standard dropdown that triggers a page reload with the selected language as a URL parameter.
- **How does the system handle browser translation tools?** The UI detects when browser translation is active and displays a notice recommending users disable it in favor of native language support for better accuracy.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support three languages: English (en), Urdu (ur), and Japanese (ja) across all UI components
- **FR-002**: System MUST detect user language preference from browser settings on first visit and apply appropriate locale
- **FR-003**: System MUST provide a language switcher in the navbar that allows instant switching between en/ur/ja without page reload
- **FR-004**: System MUST persist user language selection in localStorage and apply it on subsequent visits
- **FR-005**: System MUST apply RTL (right-to-left) layout for Urdu, including mirrored UI elements and text direction
- **FR-006**: System MUST translate all UI strings including navbar, footer, buttons, modals, error messages, and loading states
- **FR-007**: System MUST provide a backend endpoint `/api/detect-language` that accepts text and returns detected language code (en/ur/ja)
- **FR-008**: System MUST modify the `/api/chat` endpoint to accept a `preferredLanguage` parameter and return responses in the specified language
- **FR-009**: System MUST configure OpenAI system prompts to enforce "Reply in [detected language]" instruction
- **FR-010**: System MUST tag all Qdrant document embeddings with language metadata in the payload
- **FR-011**: System MUST filter Qdrant searches by language tag, prioritizing user's language and falling back to English if insufficient results
- **FR-012**: System MUST create Docusaurus i18n folder structure (`i18n/[locale]/docusaurus-plugin-content-*/`) for translation files
- **FR-013**: System MUST generate `code.json` translation files for theme strings in each locale
- **FR-014**: System MUST display a translation status indicator on documentation pages showing available language versions
- **FR-015**: System MUST log language usage analytics (language detected, UI language, response language) for monitoring and improvement
- **FR-016**: System MUST render Japanese text using appropriate web fonts that support kanji, hiragana, and katakana
- **FR-017**: System MUST handle language fallback gracefully when content is unavailable in requested language
- **FR-018**: System MUST validate language codes against supported list (en/ur/ja) and reject invalid codes with appropriate error messages

### Key Entities

- **LanguagePreference**: Represents a user's language choice (code: "en" | "ur" | "ja", persisted in localStorage, includes timestamp)
- **TranslationMetadata**: Describes translation status for a document (sourceLanguage, availableLanguages[], completionPercentage, lastUpdated)
- **ChatMessage**: Includes language properties (detectedLanguage, requestedLanguage, responseLanguage) for analytics and quality monitoring
- **DocumentEmbedding**: Qdrant vector with payload containing language tag, chunk text, source document ID, and metadata
- **LanguageDetectionResult**: Backend response containing detectedLanguage code, confidence score (0-1), and fallback indicator

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can switch languages and see UI updates within 300ms without page reload
- **SC-002**: 95% of UI strings are translated in all three languages (en/ur/ja) at launch
- **SC-003**: Chat responses in user's preferred language have 90% accuracy (language match rate measured via analytics)
- **SC-004**: Urdu pages render with proper RTL layout passing manual QA checklist (20 checkpoints covering navbar, sidebar, chat, forms)
- **SC-005**: Language detection API responds within 200ms for messages under 500 characters
- **SC-006**: RAG pipeline returns language-appropriate results within 2 seconds for 95% of queries
- **SC-007**: Zero layout breaks or text overflow issues on mobile devices (320px width) across all three languages
- **SC-008**: Language preference persists correctly for 100% of users (verified via localStorage inspection)
- **SC-009**: Users accessing the site with Japanese browser settings see Japanese UI on first load for 95% of page loads
- **SC-010**: Translation coverage increases by at least 5 chapters per language per month (measured via translation metadata tracking)

---

## Constraints & Non-Goals

### Constraints

- **Performance**: Language detection must not add more than 100ms to chat response latency
- **Fallback Behavior**: When content is unavailable in requested language, system must always fall back to English (never show empty content)
- **Supported Browsers**: RTL layout must work correctly on Chrome 90+, Firefox 88+, Safari 14+, and Edge 90+
- **RTL Specifics**: RTL layout applies only to Urdu (ja/en remain LTR); direction must not affect embedded code blocks or technical diagrams
- **Content Migration**: Existing English content remains authoritative; translations are additive and versioned separately
- **Translation Quality**: Initial translations may use machine translation with human review; quality improves iteratively
- **Infrastructure**: Language detection uses existing OpenAI API (no new third-party services); Qdrant metadata fields stay within existing payload limits

### Non-Goals

- **Not supporting additional languages** beyond en/ur/ja in Phase 1 (future phases may add more)
- **Not translating code examples or API references** (code remains in English universally)
- **Not providing real-time translation** of user-generated content (e.g., forum posts, if added later)
- **Not building custom machine translation models** (use OpenAI for translation tasks)
- **Not supporting automatic language detection from IP geolocation** (browser settings and user choice only)
- **Not creating separate URLs per language** (single URL with client-side language switching; docs follow Docusaurus i18n conventions)
- **Not translating third-party embedded content** (YouTube videos, external links remain in original language)

---

## Data Model Notes

### Language Tag on Documents

Each document stored in Qdrant will include:
- `language` field in metadata payload: one of "en" | "ur" | "ja"
- `original_language` field: source language of the content
- `translation_quality` field: optional score (0-1) if content is machine-translated

### Embeddings Metadata

When generating embeddings for chunks:
- Tag each vector with `{"language": "en"}` or respective language code
- Store `translation_source`: "original" | "human" | "machine" to track translation provenance
- Include `content_type`: "ui" | "docs" | "chat_context" to differentiate embedding use cases

### Frontend State

Language preference stored in localStorage:
```json
{
  "preferredLanguage": "ur",
  "timestamp": "2025-12-11T10:30:00Z",
  "source": "manual" | "browser" | "default"
}
```

### Backend Request/Response

Chat API request includes:
- `preferredLanguage`: user's UI language setting
- Optional `detectedLanguage`: if frontend pre-detects language

Chat API response includes:
- `responseLanguage`: language of the response
- `detectedInputLanguage`: backend-detected language
- `fallbackApplied`: boolean indicating if language fallback was used

---

## Security & Privacy Notes

- **No secrets in prompts**: Language instructions in system prompts do not include API keys, user PII, or sensitive configuration
- **Opt-in translations**: Users explicitly choose their language; system does not track or infer sensitive information from language choice
- **Data minimization**: Language preference stored only in client localStorage; not transmitted to backend unless necessary for chat context
- **XSS prevention**: All translated strings sanitized before rendering; user input in any language is escaped to prevent injection attacks
- **Rate limiting**: Language detection endpoint rate-limited to prevent abuse (100 requests/minute per IP)
- **Logging privacy**: Language analytics logs do not include message content, only metadata (language codes, timestamps, session IDs)
- **Translation review**: Machine-translated content reviewed by native speakers before marking as production-ready to avoid cultural insensitivity or errors

---

## High-Level Rollout Plan

### Phase 1: UI Strings Translation (Weeks 1-2)
1. Set up Docusaurus i18n configuration with `locales: ['en', 'ur', 'ja']`
2. Extract all UI strings to `code.json` files for each locale
3. Translate navbar, footer, buttons, common messages
4. Implement language switcher component with localStorage persistence
5. Add RTL stylesheet for Urdu with direction-aware CSS
6. QA all three languages on desktop and mobile

### Phase 2: Backend Language Detection (Weeks 3-4)
7. Create `/api/detect-language` endpoint using OpenAI or language detection library
8. Update `/api/chat` endpoint to accept `preferredLanguage` parameter
9. Implement OpenAI system prompt templates with language instructions
10. Add language metadata to request/response logging
11. Write integration tests for language detection accuracy

### Phase 3: RAG Pipeline Language Tagging (Weeks 5-6)
12. Update Qdrant schema to include `language` field in payload
13. Re-index existing documents with `language: "en"` tag
14. Modify embedding pipeline to tag new documents by language
15. Implement language-filtered search with fallback logic
16. Benchmark search performance with language filters

### Phase 4: Core Chapter Translation (Weeks 7-10)
17. Identify 5-10 high-priority chapters for translation
18. Generate machine translations using OpenAI API
19. Review and refine translations with native speakers
20. Create translated markdown files in Docusaurus i18n structure
21. Add translation status indicators to doc pages
22. Launch beta with selected chapters in all three languages

### Phase 5: Monitoring & Iteration (Ongoing)
23. Set up language analytics dashboard
24. Monitor language detection accuracy and fallback rates
25. Collect user feedback on translation quality
26. Prioritize next chapters for translation based on usage data
27. Iterate on RTL styling based on QA findings

---

## Files & Repository Structure

### New Directories to Create

```
specs/001-multilingual-support/
├── spec.md                          # This file
├── plan.md                          # Generated by /sp.plan
├── tasks.md                         # Generated by /sp.tasks
├── implement.md                     # Generated by /sp.implement
└── checklists/
    └── requirements.md              # Quality checklist

i18n/
├── ur/
│   ├── docusaurus-plugin-content-docs/
│   │   └── current/
│   │       └── [translated .md files]
│   ├── docusaurus-plugin-content-pages/
│   │   └── [translated page files]
│   └── code.json                    # UI string translations
└── ja/
    ├── docusaurus-plugin-content-docs/
    ├── docusaurus-plugin-content-pages/
    └── code.json

src/components/LanguageSwitcher/     # New component
backend/app/api/language.py          # New language detection endpoint
backend/app/core/i18n.py             # Language utilities
backend/app/services/rag_multilingual.py  # Language-aware RAG
```

### Modified Files

```
docusaurus.config.ts                 # Update i18n config
src/css/custom.css                   # Add RTL styles
backend/app/api/chat.py              # Add language parameter
backend/app/main.py                  # Include language router
backend/app/core/config.py           # Add language settings
```

---

## Clarification Questions

### Question 1: Translation Sourcing Strategy

**Context**: The spec mentions both machine translation and human review for content quality.

**What we need to know**: Should we use OpenAI API for initial translations, hire professional translators, or rely on community contributions?

**Suggested Answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A | Use OpenAI GPT-4 for initial translations with spot-check review | Fastest implementation, lower cost, requires review workflow for quality assurance |
| B | Hire professional translators for all content | Highest quality, higher cost, slower rollout timeline |
| C | Hybrid: OpenAI for UI strings, professional translators for chapter content | Balanced approach, prioritizes user-facing quality where it matters most |
| Custom | Provide your own approach | Explain your preferred translation strategy |

**Your choice**: **Option C - Hybrid Approach**

**Decision**: Use OpenAI GPT-4 for UI string translations (navbar, buttons, messages) with automated deployment, and professional translators for chapter content to ensure educational quality and cultural appropriateness. This balances speed and cost for UI elements while maintaining high quality for learning materials.

---

### Question 2: RTL Layout Scope

**Context**: Urdu requires right-to-left layout, which affects all UI components.

**What we need to know**: Should RTL apply to the entire page layout (including sidebar, navbar structure) or only to text content areas?

**Suggested Answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A | Full RTL mirroring - entire page layout flips including sidebar position, navbar alignment | Most authentic Urdu experience, requires extensive CSS work, potential layout bugs |
| B | Text-only RTL - text direction changes but layout structure stays LTR | Simpler implementation, less authentic but functional, faster to implement |
| C | Hybrid - RTL for content areas and chat, LTR for navigation structure | Balanced approach, maintains familiar navigation while supporting RTL reading |
| Custom | Provide your own RTL strategy | Explain your preferred approach |

**Your choice**: **Option C - Hybrid RTL**

**Decision**: Apply RTL text direction and layout to content areas (documentation pages, blog posts) and chat messages where reading flow is critical. Keep navigation UI (navbar, sidebar, footer) in LTR for consistency and familiarity. This provides authentic Urdu reading experience where it matters most while avoiding complex navigation mirroring issues.

---

### Question 3: Language Detection Confidence Threshold

**Context**: The backend will detect language from user chat messages, but detection confidence varies.

**What we need to know**: What confidence threshold should trigger fallback to UI language setting?

**Suggested Answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A | 70% confidence threshold | Conservative approach, more frequent fallbacks to UI setting, safer for accuracy |
| B | 50% confidence threshold | Balanced approach, fewer fallbacks, trusts detection more |
| C | 90% confidence threshold | Very conservative, heavily relies on UI setting fallback, minimizes detection errors |
| Custom | Provide your own threshold | Specify confidence level (0-100%) |

**Your choice**: **Option B - 50% Confidence Threshold**

**Decision**: Use 50% confidence threshold for language detection. If detection confidence is below 50%, fall back to the user's UI language setting. This balanced approach trusts the detection algorithm for most cases while providing a safety net for ambiguous inputs, allowing the system to be responsive without being overly conservative.

---

## Assumptions & Decisions

Based on the clarification questions answered above, the following assumptions guide this specification:

### Translation Strategy
- **UI Strings**: OpenAI GPT-4 API with automated translation pipeline
- **Chapter Content**: Professional translators with native language expertise
- **Quality Assurance**: Spot-check review for UI, comprehensive review for educational content
- **Cost/Speed Trade-off**: Optimize UI translation for speed, prioritize chapter quality over speed

### RTL Implementation
- **Content Areas**: Full RTL support (text direction, alignment, reading flow)
- **Chat Interface**: RTL layout for Urdu messages and responses
- **Navigation UI**: Remains LTR (navbar, sidebar, footer maintain familiar structure)
- **Code Blocks**: Always LTR regardless of page language
- **CSS Strategy**: Use `[dir="rtl"]` selectors for content-specific RTL rules

### Language Detection
- **Confidence Threshold**: 50% (balanced approach)
- **Fallback Logic**: UI language setting when confidence < 50%
- **Detection Library**: OpenAI API language detection or langdetect library
- **Logging**: Log confidence scores for continuous improvement
- **Edge Cases**: Default to English if both detection and UI setting fail

---

## PR Description & Review Checklist

### One-Line PR Description
"Add multilingual support (EN/UR/JA) with Docusaurus i18n, language-aware RAG pipeline, and RTL layout for Urdu"

### Review Checklist for QA

**Frontend**:
- [ ] Language switcher appears in navbar and functions correctly
- [ ] UI strings translated in all three languages (95%+ coverage)
- [ ] Urdu pages render with proper RTL layout on all major browsers
- [ ] Language preference persists across sessions via localStorage
- [ ] No layout breaks or text overflow on mobile (320px width)
- [ ] Japanese fonts render correctly for kanji/hiragana/katakana

**Backend**:
- [ ] `/api/detect-language` endpoint returns correct language codes
- [ ] `/api/chat` endpoint accepts and respects `preferredLanguage` parameter
- [ ] OpenAI system prompts include language enforcement instructions
- [ ] Language metadata logged in all chat requests/responses

**RAG Pipeline**:
- [ ] Qdrant documents tagged with language field
- [ ] Language-filtered searches return language-appropriate results
- [ ] Fallback to English works when requested language unavailable
- [ ] Search performance within 2 seconds for 95% of queries

**Quality & Edge Cases**:
- [ ] Unsupported language inputs handled gracefully
- [ ] Partially translated pages show clear indicators
- [ ] Language analytics logged without PII
- [ ] XSS prevention verified for all translated strings
- [ ] Rate limiting active on language detection endpoint

**Documentation**:
- [ ] Translation workflow documented in README
- [ ] i18n folder structure explained
- [ ] Language contribution guide created
