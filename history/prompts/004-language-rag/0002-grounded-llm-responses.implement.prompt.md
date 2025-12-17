---
id: 0002
title: Grounded LLM Responses with Language Support
stage: implement
date: 2025-12-16
surface: agent
model: claude-opus-4-5
feature: 004-language-rag
branch: 001-multilingual-support
user: ps_qasim
command: /sp.implement
labels: ["rag", "grounding", "hallucination-prevention", "multilingual", "openai"]
links:
  spec: specs/001-multilingual-support/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/services/rag.py
tests:
  - LLM responds only from context (no hallucination)
  - Not-found message displays in correct language
  - Response language matches preferredLanguage
---

## Prompt

NEXT TASK: Ground LLM responses using retrieved RAG context

GOAL:
- LLM must answer strictly from retrieved chunks
- No hallucination
- Respect responseLanguage from RAG

REQUIREMENTS:
- Update system prompt / prompt builder only
- Inject retrieved chunks as explicit context
- If answer not found, respond with:
  "I could not find this information in the documentation."
- Respond in responseLanguage
- Do NOT change retrieval logic
- Do NOT change ingestion
- Do NOT change frontend

OUTPUT:
- Updated prompt template
- Example request payload sent to LLM
- Confirmation of hallucination prevention

## Response

### Implementation Summary

Updated the system prompt and `generate_answer()` function to enforce strict grounding from RAG context with multilingual response support. The LLM is now constrained to only use information from retrieved chunks and responds in the user's preferred language.

### Changes Made

#### 1. New Language-Specific Constants

```python
# Language-specific response instructions
LANGUAGE_INSTRUCTIONS = {
    "en": "Respond in English.",
    "ur": "اردو میں جواب دیں۔ (Respond in Urdu using Urdu script.)",
    "ja": "日本語で回答してください。(Respond in Japanese.)",
}

# Not-found messages in each language
NOT_FOUND_MESSAGES = {
    "en": "I could not find this information in the documentation...",
    "ur": "مجھے دستاویزات میں یہ معلومات نہیں مل سکیں...",
    "ja": "ドキュメントにこの情報が見つかりませんでした...",
}
```

#### 2. Updated System Prompt with Strict Grounding

```python
SYSTEM_PROMPT = """You are a helpful AI tutor for the Physical AI & Humanoid Robotics textbook.

**RESPONSE LANGUAGE: {response_language_instruction}**

**RETRIEVED CONTEXT FROM TEXTBOOK:**
{context}

**STRICT GROUNDING RULES (MUST FOLLOW):**
1. ONLY use information from the RETRIEVED CONTEXT above. Do NOT use any external knowledge.
2. If the answer is NOT in the context, respond with EXACTLY:
   "{not_found_message}"
3. Do NOT hallucinate, invent, or assume information not present in the context.
4. Every claim you make MUST be traceable to the provided context.

**ANSWERING GUIDELINES:**
...

**REMEMBER:**
- Your job is to explain ONLY what is in the context
- If information is missing, say so clearly - do NOT make things up
- Always respond in the specified language: {response_language}"""
```

#### 3. Updated `generate_answer()` Function

```python
async def generate_answer(
    question: str,
    context: str,
    chat_model: str,
    response_language: LanguageCode = "en",  # NEW parameter
) -> str:
    # Get language-specific instructions and not-found message
    language_instruction = LANGUAGE_INSTRUCTIONS.get(response_language, ...)
    not_found_message = NOT_FOUND_MESSAGES.get(response_language, ...)

    # Format system prompt with all placeholders
    system_message = SYSTEM_PROMPT.format(
        context=context,
        response_language=response_language,
        response_language_instruction=language_instruction,
        not_found_message=not_found_message,
    )

    # Lower temperature (0.2) for factual, grounded responses
    response = await client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
        max_tokens=1000,
    )
```

### Example Request Payload to OpenAI

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful AI tutor...\n\n**RESPONSE LANGUAGE: 日本語で回答してください。**\n\n**RETRIEVED CONTEXT FROM TEXTBOOK:**\n[Source 1]\nDocument: docs/module-1/chapter-1.md\nSection: Introduction to ROS 2\nContent: ROS 2 is a flexible framework for writing robot software...\n---\n\n**STRICT GROUNDING RULES (MUST FOLLOW):**\n1. ONLY use information from the RETRIEVED CONTEXT above...\n2. If the answer is NOT in the context, respond with EXACTLY:\n   \"ドキュメントにこの情報が見つかりませんでした。別の質問をするか、教科書全体を検索してください。\"\n..."
    },
    {
      "role": "user",
      "content": "ROS 2とは何ですか？"
    }
  ],
  "temperature": 0.2,
  "max_tokens": 1000
}
```

### Hallucination Prevention Mechanisms

1. **Explicit Grounding Rules**: System prompt explicitly forbids using external knowledge
2. **Low Temperature (0.2)**: Reduces creative/random responses
3. **Mandatory Not-Found Response**: LLM must use exact phrase when info is missing
4. **Context Boundary**: "RETRIEVED CONTEXT FROM TEXTBOOK" clearly demarcates source
5. **Traceability Requirement**: "Every claim MUST be traceable to the provided context"

### Data Flow

```
User Question (Japanese) + RAG Chunks
    ↓
generate_answer(response_language="ja")
    ↓
Format SYSTEM_PROMPT with:
  - context (RAG chunks)
  - response_language_instruction (日本語で回答してください)
  - not_found_message (Japanese version)
    ↓
OpenAI API (temperature=0.2)
    ↓
Grounded Response in Japanese
```

### Outcome

- LLM is strictly grounded to retrieved context
- Responds in user's preferred language (en/ur/ja)
- Uses language-specific not-found message when info is missing
- Lower temperature reduces hallucination risk
- No changes to retrieval, ingestion, or frontend
