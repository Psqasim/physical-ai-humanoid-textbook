"""
RAG (Retrieval-Augmented Generation) pipeline for Study Assistant.

This module implements the core RAG logic:
1. Retrieve relevant chunks from Qdrant based on user question
2. Build context from retrieved chunks
3. Generate answer using OpenAI chat model
4. Extract citations from retrieved chunks

Supports two modes:
- whole-book: Search entire textbook collection
- selection: Focus on selected text and nearby chunks
"""

from typing import List, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.core.config import Settings, settings
from app.core.logging import get_logger
from app.models.schemas import ChatRequest, ChatResponse, Citation
from app.services.embeddings import embed_query
from app.services.qdrant import search_similar, SearchResult

logger = get_logger(__name__)

# Type alias for supported languages
LanguageCode = Literal["en", "ur", "ja"]


# Language-specific response instructions
LANGUAGE_INSTRUCTIONS = {
    "en": "Respond in English.",
    "ur": "اردو میں جواب دیں۔ (Respond in Urdu using Urdu script.)",
    "ja": "日本語で回答してください。(Respond in Japanese.)",
}

# System prompt for OpenAI chat model - grounded RAG with language support
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
1. For vague questions ("explain this", "what is this", "tell me about this"):
   - Treat as: "Explain the main concepts in the provided context"
   - Focus on key concepts, definitions, and examples FROM THE CONTEXT ONLY
2. Cite specific sections when possible (e.g., "According to the Introduction section...")
3. Use clear, educational language appropriate for students learning robotics.
4. Format answers in 2-4 clear paragraphs, not bullet points unless asked.
5. When explaining code, break down what each part does based on the context.

**REMEMBER:**
- The context is what the student selected or searched for
- Your job is to explain ONLY what is in the context
- If information is missing, say so clearly - do NOT make things up
- Always respond in the specified language: {response_language}"""

# Not-found messages in each language
NOT_FOUND_MESSAGES = {
    "en": "I could not find this information in the documentation. Please try a different question or search the entire textbook.",
    "ur": "مجھے دستاویزات میں یہ معلومات نہیں مل سکیں۔ براہ کرم کوئی دوسرا سوال کریں یا پوری کتاب میں تلاش کریں۔",
    "ja": "ドキュメントにこの情報が見つかりませんでした。別の質問をするか、教科書全体を検索してください。",
}


async def retrieve_chunks_whole_book(
    question: str,
    limit: int = 10,
    language: LanguageCode | None = None,
) -> tuple[List[SearchResult], bool]:
    """
    Retrieve relevant chunks for whole-book mode with language filtering.

    If a language is specified, retrieves chunks in that language first.
    If fewer than 3 results are found, falls back to English.

    Args:
        question: User's question
        limit: Maximum number of chunks to retrieve
        language: Preferred language code ("en", "ur", "ja") or None for all languages

    Returns:
        Tuple of (results, fallback_applied):
        - results: List of SearchResult objects, sorted by relevance
        - fallback_applied: True if English fallback was used
    """
    logger.info(f"Retrieving chunks for whole-book mode (limit={limit}, language={language})")

    # Generate embedding for question
    query_vector = await embed_query(question)

    fallback_applied = False

    # If language is specified, try language-filtered search first
    if language:
        results = await search_similar(
            query_vector=query_vector,
            limit=limit,
            language=language,
        )
        logger.info(f"Language-filtered search ({language}): {len(results)} results")

        # If insufficient results and not already English, fall back to English
        if len(results) < 3 and language != "en":
            logger.info(f"Insufficient {language} results, falling back to English")
            english_results = await search_similar(
                query_vector=query_vector,
                limit=limit - len(results),
                language="en",
            )
            results = results + english_results
            fallback_applied = True
            logger.info(f"After English fallback: {len(results)} total results")
    else:
        # No language filter - search across all languages
        results = await search_similar(
            query_vector=query_vector,
            limit=limit,
        )

    logger.info(f"Retrieved {len(results)} chunks from Qdrant (fallback={fallback_applied})")
    return results, fallback_applied


async def retrieve_chunks_selection(
    question: str,
    selected_text: str,
    doc_path: str,
    limit: int = 5,
    language: LanguageCode | None = None,
) -> tuple[List[SearchResult], bool]:
    """
    Retrieve relevant chunks for selection mode with language filtering.

    Strategy:
    1. Search within the specified document (with optional language filter)
    2. Prioritize chunks that contain or are near the selected text
    3. If no results, fall back to whole-book mode (with language fallback)

    Args:
        question: User's question
        selected_text: Text selected by user
        doc_path: Document path to filter by
        limit: Maximum number of chunks to retrieve
        language: Preferred language code ("en", "ur", "ja") or None for all languages

    Returns:
        Tuple of (results, fallback_applied):
        - results: List of SearchResult objects, sorted by relevance
        - fallback_applied: True if English fallback was used
    """
    logger.info(f"Retrieving chunks for selection mode (doc={doc_path}, limit={limit}, language={language})")

    # Generate embedding for the selected text (more relevant than question)
    query_vector = await embed_query(selected_text)

    fallback_applied = False

    # Search within the specific document with optional language filter
    results = await search_similar(
        query_vector=query_vector,
        limit=limit,
        doc_path=doc_path,
        language=language,
    )

    # Fallback to whole-book if no results in document
    if not results:
        logger.warning(
            f"No chunks found in {doc_path}, falling back to whole-book mode"
        )
        results, fallback_applied = await retrieve_chunks_whole_book(
            question, limit=limit, language=language
        )

    logger.info(f"Retrieved {len(results)} chunks from Qdrant (selection mode, fallback={fallback_applied})")
    return results, fallback_applied


def build_context(chunks: List[SearchResult]) -> str:
    """
    Build context string from retrieved chunks.

    Format each chunk with heading and content for better readability.

    Args:
        chunks: List of retrieved chunks

    Returns:
        Formatted context string
    """
    context_parts = []

    for i, chunk in enumerate(chunks, 1):
        context_part = f"""
[Source {i}]
Document: {chunk.doc_path}
Section: {chunk.heading}
Content: {chunk.text}
---
"""
        context_parts.append(context_part.strip())

    return "\n\n".join(context_parts)


def extract_citations(chunks: List[SearchResult], max_citations: int = 5) -> List[Citation]:
    """
    Extract citations from retrieved chunks.

    Takes the top N chunks by relevance score and creates Citation objects.
    Handles short snippets gracefully, especially for multilingual content
    where headings or short sections may convey meaningful information.

    Args:
        chunks: Retrieved chunks
        max_citations: Maximum number of citations to return

    Returns:
        List of Citation objects (only includes chunks with non-empty text)
    """
    citations = []

    for chunk in chunks[:max_citations]:
        # Skip chunks with empty text
        if not chunk.text or not chunk.text.strip():
            continue

        # Create snippet (first 150 chars or full text if shorter)
        snippet = chunk.text.strip()

        if len(snippet) > 150:
            # Try to cut at sentence boundary
            cutoff = snippet[:150].rfind(". ")
            if cutoff > 0:
                snippet = snippet[: cutoff + 1]
            else:
                snippet = snippet[:150] + "..."

        # For very short snippets (e.g., headings), use them as-is
        # This is especially important for multilingual content (Japanese, Urdu)
        # where fewer characters can convey meaningful information

        citation = Citation(
            docPath=chunk.doc_path,
            heading=chunk.heading,
            snippet=snippet,
        )
        citations.append(citation)

    return citations


def format_sources_section(chunks: List[SearchResult], language: LanguageCode = "en") -> str:
    """
    Format a deterministic sources section from retrieved chunks.

    Sources are extracted ONLY from chunk metadata - the LLM does not generate these.
    This ensures sources are always accurate and traceable to actual retrieved content.

    Args:
        chunks: Retrieved chunks with metadata (doc_path, heading, url_path, module_id)
        language: Response language for the header

    Returns:
        Formatted sources section string to append after the answer

    Example output:
        📚 Sources:
        1. Introduction to ROS 2 - docs/module-1/chapter-1.md
        2. Communication Patterns - docs/module-1/chapter-2.md
    """
    if not chunks:
        return ""

    # Source header in different languages
    source_headers = {
        "en": "📚 Sources:",
        "ur": "📚 ماخذ:",
        "ja": "📚 出典:",
    }

    header = source_headers.get(language, source_headers["en"])
    sources = []
    seen_docs = set()  # Deduplicate by doc_path

    for chunk in chunks:
        # Deduplicate sources by document path
        if chunk.doc_path in seen_docs:
            continue
        seen_docs.add(chunk.doc_path)

        # Format: "Heading - doc_path" or just doc_path if no heading
        if chunk.heading:
            source_line = f"{chunk.heading} - {chunk.doc_path}"
        else:
            source_line = chunk.doc_path

        # Add URL path if available for clickable links
        if chunk.url_path:
            source_line = f"{source_line} ({chunk.url_path})"

        sources.append(source_line)

    if not sources:
        return ""

    # Format as numbered list
    numbered_sources = [f"{i+1}. {src}" for i, src in enumerate(sources[:5])]  # Max 5 sources
    return f"\n\n{header}\n" + "\n".join(numbered_sources)


# Type alias for confidence levels
ConfidenceLevel = Literal["high", "medium", "low"]


def calculate_confidence(
    num_chunks: int,
    fallback_applied: bool,
) -> ConfidenceLevel:
    """
    Calculate deterministic confidence level based on retrieval signals.

    This function uses ONLY retrieval metrics (no LLM involvement) to
    determine confidence, ensuring reproducible results.

    Logic:
    - high: ≥5 chunks retrieved AND no language fallback
    - medium: 3-4 chunks retrieved AND no language fallback
    - low: <3 chunks OR language fallback was applied

    Args:
        num_chunks: Number of chunks retrieved from Qdrant
        fallback_applied: Whether English fallback was used due to insufficient
                         content in the preferred language

    Returns:
        Confidence level: "high", "medium", or "low"

    Examples:
        >>> calculate_confidence(5, False)
        "high"
        >>> calculate_confidence(4, False)
        "medium"
        >>> calculate_confidence(5, True)
        "low"
        >>> calculate_confidence(2, False)
        "low"
    """
    # Fallback always indicates lower confidence (content not in preferred language)
    if fallback_applied:
        return "low"

    # Confidence based on number of relevant chunks found
    if num_chunks >= 5:
        return "high"
    elif num_chunks >= 3:
        return "medium"
    else:
        return "low"


async def generate_answer(
    question: str,
    context: str,
    chat_model: str,
    response_language: LanguageCode = "en",
) -> str:
    """
    Generate grounded answer using OpenAI chat model with language support.

    The system prompt enforces strict grounding - the LLM can only use
    information from the provided context and must respond in the specified language.

    Args:
        question: User's question
        context: Retrieved context from textbook (RAG chunks)
        chat_model: OpenAI model name (e.g., "gpt-4o-mini")
        response_language: Language for the response ("en", "ur", "ja")

    Returns:
        Generated answer text in the specified language

    Example:
        answer = await generate_answer(
            question="What is ROS 2?",
            context="[Source 1]\\nROS 2 is a robotics middleware...",
            chat_model="gpt-4o-mini",
            response_language="ja"
        )
        # Returns answer in Japanese, grounded in context
    """
    logger.info(f"Generating answer with model: {chat_model}, language: {response_language}")

    # Get language-specific instructions and not-found message
    language_instruction = LANGUAGE_INSTRUCTIONS.get(response_language, LANGUAGE_INSTRUCTIONS["en"])
    not_found_message = NOT_FOUND_MESSAGES.get(response_language, NOT_FOUND_MESSAGES["en"])

    # Create OpenAI client with proper async context manager
    async with AsyncOpenAI(api_key=settings.OPENAI_API_KEY) as client:
        # Format system prompt with context and language settings
        system_message = SYSTEM_PROMPT.format(
            context=context,
            response_language=response_language,
            response_language_instruction=language_instruction,
            not_found_message=not_found_message,
        )

        # Call OpenAI chat API
        response = await client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": question},
            ],
            temperature=0.2,  # Lower temperature for more factual, grounded responses
            max_tokens=1000,  # Slightly higher for multilingual responses
        )

        # Extract answer
        answer = response.choices[0].message.content or ""
        logger.info(f"Generated answer ({len(answer)} chars) in {response_language}")
        return answer


async def answer_chat_request(
    request: ChatRequest,
    db: AsyncSession,
    settings_override: Settings | None = None,
) -> ChatResponse:
    """
    Main RAG pipeline: retrieve, generate, and respond with language-aware retrieval.

    This is the core function that orchestrates the RAG process:
    1. Retrieve relevant chunks based on mode and preferred language
    2. Build context from chunks
    3. Generate answer using OpenAI
    4. Extract citations
    5. Return structured response with language metadata

    Language filtering:
    - If preferredLanguage is specified, retrieves chunks in that language first
    - Falls back to English if fewer than 3 results in preferred language
    - Response includes fallbackApplied flag when English fallback was used

    Args:
        request: Chat request with mode, question, optional context, and preferredLanguage
        db: Database session (for future enhancements, not used yet)
        settings_override: Optional settings override (for testing)

    Returns:
        ChatResponse with answer, citations, mode, and language metadata

    Raises:
        ValueError: If request validation fails
        Exception: If OpenAI or Qdrant API calls fail
    """
    config = settings_override or settings

    # Get preferred language from request (defaults to None = search all languages)
    preferred_language = request.preferredLanguage

    logger.info(
        f"Processing chat request: mode={request.mode}, "
        f"question_len={len(request.question)}, "
        f"user_id={request.userId or 'anonymous'}, "
        f"language={preferred_language}"
    )

    # Retrieve chunks based on mode with language filtering
    fallback_applied = False

    if request.mode == "whole-book":
        chunks, fallback_applied = await retrieve_chunks_whole_book(
            question=request.question,
            limit=config.CHUNK_RETRIEVAL_LIMIT,
            language=preferred_language,
        )
    else:  # selection mode
        if not request.selectedText or not request.docPath:
            raise ValueError(
                "mode='selection' requires both selectedText and docPath"
            )

        chunks, fallback_applied = await retrieve_chunks_selection(
            question=request.question,
            selected_text=request.selectedText,
            doc_path=request.docPath,
            limit=min(config.CHUNK_RETRIEVAL_LIMIT, 5),  # Smaller limit for selection
            language=preferred_language,
        )

    # Handle case where no chunks were retrieved
    if not chunks:
        logger.warning("No relevant chunks found in Qdrant")
        return ChatResponse(
            answer="I couldn't find relevant information in the textbook to answer your question. Please try rephrasing or asking a different question.",
            citations=[],
            mode=request.mode,
            responseLanguage=preferred_language or "en",
            fallbackApplied=False,
        )

    # Build context from chunks
    # For selection mode, prepend the selected text to give the AI clear context
    if request.mode == "selection" and request.selectedText:
        context = f"""USER SELECTED THIS TEXT TO ASK ABOUT:

{request.selectedText}

RELEVANT TEXTBOOK SECTIONS:

{build_context(chunks)}"""
    else:
        context = build_context(chunks)

    # Determine response language for LLM
    # If fallback was applied, we still try to respond in preferred language
    # but inform the user that content was from English sources
    response_language: LanguageCode = preferred_language or "en"

    # Generate grounded answer with language support
    try:
        answer = await generate_answer(
            question=request.question,
            context=context,
            chat_model=config.OPENAI_CHAT_MODEL,
            response_language=response_language,
        )
    except Exception as e:
        logger.error(f"Failed to generate answer: {e}")
        raise

    # Extract citations for API response (structured data)
    citations = extract_citations(chunks, max_citations=5)

    # Append deterministic sources section to the answer
    # Sources are extracted from chunk metadata, NOT generated by LLM
    # This ensures sources are always accurate and traceable
    sources_section = format_sources_section(chunks, language=response_language)
    answer_with_sources = answer + sources_section

    # Calculate deterministic confidence based on retrieval signals only
    # No LLM involvement - purely based on chunk count and fallback status
    confidence = calculate_confidence(
        num_chunks=len(chunks),
        fallback_applied=fallback_applied,
    )

    # Build response with language metadata and confidence
    response = ChatResponse(
        answer=answer_with_sources,
        citations=citations,
        mode=request.mode,
        confidence=confidence,
        responseLanguage=response_language,
        fallbackApplied=fallback_applied,
    )

    logger.info(
        f"Chat request completed: answer_len={len(answer_with_sources)}, "
        f"citations={len(citations)}, sources={len(sources_section) > 0}, "
        f"confidence={confidence}, language={response_language}, fallback={fallback_applied}"
    )

    return response