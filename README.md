# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.

## Multilingual Support

This site supports 3 languages: English, Urdu (اردو), and Japanese (日本語).

### Development Mode (Single Locale)

**Important**: `npm start` only serves ONE locale at a time for fast development.

```bash
# English (default)
npm start

# Urdu (RTL)
npm run start -- --locale ur

# Japanese
npm run start -- --locale ja
```

⚠️ **Don't click the language switcher in dev mode** - it will cause 404 errors because other locales aren't built.

### Production Testing (All Locales)

To test the language switcher and all 3 locales:

```bash
# Build all locales
npm run build

# Serve production build
npm run serve
```

Now the language switcher works! Test at:
- English: http://localhost:3000/physical-ai-humanoid-textbook/
- Urdu: http://localhost:3000/physical-ai-humanoid-textbook/ur/
- Japanese: http://localhost:3000/physical-ai-humanoid-textbook/ja/

### Verify Build

```bash
./test-locales.sh
```

### Backend Language Detection Setup

The backend supports language detection for chat messages:

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add:
# - OPENAI_API_KEY=your-key-here
# - DEFAULT_LANGUAGE=en

# Run backend server
uvicorn app.main:app --reload
```

**Language Detection API**:
- Endpoint: `POST /api/detect-language`
- Request: `{"text": "your message"}`
- Response: `{"detectedLanguage": "en|ur|ja", "confidence": 0.9, "fallbackApplied": false}`

**Chat with Language Support**:
- Endpoint: `POST /api/chat`
- Add `preferredLanguage` field: `{"message": "...", "preferredLanguage": "ur"}`
- Response includes language metadata

### Voice Input

Voice input component supports multilingual speech recognition:

- English (en-US), Urdu (ur-PK), Japanese (ja-JP)
- Noise filtering with confidence-based selection
- Code-switching detection for mixed-language speech
- See `src/components/VoiceInput/README.md` for integration details

### Documentation

- **Development Guide**: See `DEVELOPMENT-GUIDE.md` for detailed workflow
- **Multilingual Workflow**: See `MULTILINGUAL-WORKFLOW.md` for translation details
- **Voice Input Guide**: See `src/components/VoiceInput/README.md` for voice features
