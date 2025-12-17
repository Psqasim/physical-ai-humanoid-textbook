---
id: 0007
title: Landing Page UX Improvement
stage: implement
date: 2025-12-16
surface: agent
model: claude-opus-4-5-20251101
feature: 004-language-rag
branch: 001-multilingual-support
user: Psqasim
command: /sp.implement
labels: [ui, ux, landing-page, docusaurus, hackathon]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - src/pages/index.tsx
  - src/pages/index.module.css
tests:
  - Manual visual inspection
  - Responsive testing (mobile/tablet/desktop)
---

## Prompt

Improve ROOT landing page UI/UX with:
- Hero section with language indicator (EN/UR/JA)
- Voice mode badge visibility
- 4-card grid with entire card clickable
- Links ONLY to existing routes: /, /docs/intro, /chat
- Minimal, hackathon-ready design
- CSS Modules only, no heavy libraries

## Response snapshot

### A) ROOT PAGE UX STRUCTURE

Layout:
1. **Hero Section** - Title, subtitle, language strip, voice badge, CTA button
2. **4-Card Grid** - Feature cards linking to existing routes
3. **Author Section** - Credits with social links

**Why this works for hackathons:**
- Single scroll view shows all value propositions
- Clear visual hierarchy guides user attention
- Clickable cards reduce friction to key features
- Language/voice badges demonstrate multilingual AI capabilities immediately

### B) 4-CARD GRID DESIGN

| Card | Icon | Title | Description | Route |
|------|------|-------|-------------|-------|
| 1 | 📚 | Course Textbook | Comprehensive modules covering ROS 2, digital twins, and AI-powered robotics | /docs/intro |
| 2 | 💬 | Study Assistant | AI-powered chat with voice input. Ask questions in English, Urdu, or Japanese | /chat |
| 3 | 🌐 | Multilingual Learning | Full content in EN, اردو, 日本語 with auto language detection | /docs/intro |
| 4 | ⚡ | How It Works | RAG-powered answers from textbook content with source citations | /chat |

### C) JSX IMPLEMENTATION

- `LanguageStrip` - Shows "Available in: EN اردو 日本語"
- `VoiceBadge` - Shows "🎤 Voice questions supported"
- `FeatureCard` - Entire card wrapped in `<Link>` for clickability
- `CardGrid` - CSS Grid 2x2 layout, 1-column on mobile
- Semantic HTML: `<article>`, `<section>`, ARIA labels

### D) CSS MODULES

- Grid: `grid-template-columns: repeat(2, 1fr)` → `1fr` on mobile
- Hover: `box-shadow` + `border-color` change (no transform)
- Responsive: 3 breakpoints (996px tablet, 600px mobile)
- ~200 lines total, well-organized sections

### E) VOICE MODE VISIBILITY

Badge placement: Hero section, below subtitle
Text: "🎤 Voice questions supported"
Style: Pill shape with subtle border, high contrast

### F) ACCESSIBILITY

- `aria-label` on language strip and cards
- `aria-hidden="true"` on decorative icons
- `sr-only` class for screen-reader-only headings
- Min tap target size via padding
- Color contrast maintained via Docusaurus CSS variables

## Outcome

- ✅ Impact: Complete landing page redesign with multilingual and voice visibility
- 🧪 Tests: Manual visual inspection required
- 📁 Files: 2 files modified (index.tsx, index.module.css)
- 🔁 Next prompts: Test responsive behavior, verify card links work
- 🧠 Reflection: Kept design minimal per hackathon constraints; used CSS Grid for simplicity

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (manual testing)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add i18n translation for card content
