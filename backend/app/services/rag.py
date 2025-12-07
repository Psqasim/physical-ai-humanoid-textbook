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

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.core.config import Settings, settings
from app.core.logging import get_logger
from app.models.schemas import ChatRequest, ChatResponse, Citation
from app.services.embeddings import embed_query
from app.services.qdrant import search_similar, SearchResult

logger = get_logger(__name__)


# System prompt for OpenAI chat model
SYSTEM_PROMPT = """You are a helpful AI tutor for the Physical AI & Humanoid Robotics textbook.

CONTEXT FROM TEXTBOOK:
{context}

INSTRUCTIONS:
1. Answer the user's question using ONLY the information provided in the context above.
2. If the context contains information relevant to the question, use it to provide a detailed answer.
3. IMPORTANT FOR VAGUE OR UNCLEAR QUESTIONS:
   - If the user asks vague questions like "explain this", "what is this", "answer the selected text",
     "can u explain", "tell me about this", treat it as: "Explain the main concepts in the provided context"
   - Always assume the user wants you to explain/clarify the content in the context
   - Even if the question is unclear or poorly worded, provide a helpful explanation of the context
   - Focus on the most important concepts, definitions, and examples from the context
4. Cite specific sections when possible (e.g., "According to the Introduction section..." or "As explained in the Communication Patterns section...").
5. If the context does NOT contain enough information to answer the question, politely say:
   "I don't have enough information about that specific topic in the provided sections.
   Try asking a more specific question or use whole-book search for broader queries."
6. Use clear, educational language appropriate for students learning robotics.
7. Format your answer in clear paragraphs (2-4 paragraphs typically), not bullet points unless specifically asked.
8. When explaining code, break down what each part does and why it's important.

Remember: The context above is what the student is currently reading or selected. Your job is to help them understand it, even if they don't ask perfectly!"""


async def retrieve_chunks_whole_book(
    question: str,
    limit: int = 10,
) -> List[SearchResult]:
    """
    Retrieve relevant chunks for whole-book mode.

    Args:
        question: User's question
        limit: Maximum number of chunks to retrieve

    Returns:
        List of SearchResult objects, sorted by relevance
    """
    logger.info(f"Retrieving chunks for whole-book mode (limit={limit})")

    # Generate embedding for question
    query_vector = await embed_query(question)

    # Search Qdrant across entire collection
    results = await search_similar(
        query_vector=query_vector,
        limit=limit,
    )

    logger.info(f"Retrieved {len(results)} chunks from Qdrant")
    return results


async def retrieve_chunks_selection(
    question: str,
    selected_text: str,
    doc_path: str,
    limit: int = 5,
) -> List[SearchResult]:
    """
    Retrieve relevant chunks for selection mode.

    Strategy:
    1. Search within the specified document
    2. Prioritize chunks that contain or are near the selected text
    3. If no results, fall back to whole-book mode

    Args:
        question: User's question
        selected_text: Text selected by user
        doc_path: Document path to filter by
        limit: Maximum number of chunks to retrieve

    Returns:
        List of SearchResult objects, sorted by relevance
    """
    logger.info(f"Retrieving chunks for selection mode (doc={doc_path}, limit={limit})")

    # Generate embedding for the selected text (more relevant than question)
    query_vector = await embed_query(selected_text)

    # Search within the specific document
    results = await search_similar(
        query_vector=query_vector,
        limit=limit,
        doc_path=doc_path,
    )

    # Fallback to whole-book if no results in document
    if not results:
        logger.warning(
            f"No chunks found in {doc_path}, falling back to whole-book mode"
        )
        results = await retrieve_chunks_whole_book(question, limit=limit)

    logger.info(f"Retrieved {len(results)} chunks from Qdrant (selection mode)")
    return results


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

    Args:
        chunks: Retrieved chunks
        max_citations: Maximum number of citations to return

    Returns:
        List of Citation objects
    """
    citations = []

    for chunk in chunks[:max_citations]:
        # Create snippet (first 150 chars or full text if shorter)
        snippet = chunk.text
        if len(snippet) > 150:
            # Try to cut at sentence boundary
            cutoff = snippet[:150].rfind(". ")
            if cutoff > 0:
                snippet = snippet[: cutoff + 1]
            else:
                snippet = snippet[:150] + "..."

        citation = Citation(
            docPath=chunk.doc_path,
            heading=chunk.heading,
            snippet=snippet,
        )
        citations.append(citation)

    return citations


async def generate_answer(
    question: str,
    context: str,
    chat_model: str,
) -> str:
    """
    Generate answer using OpenAI chat model.

    Args:
        question: User's question
        context: Retrieved context from textbook
        chat_model: OpenAI model name (e.g., "gpt-4o-mini")

    Returns:
        Generated answer text
    """
    logger.info(f"Generating answer with model: {chat_model}")

    # Create OpenAI client
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # Format system prompt with context
    system_message = SYSTEM_PROMPT.format(context=context)

    # Call OpenAI chat API
    response = await client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question},
        ],
        temperature=0.3,  # Lower temperature for more factual responses
        max_tokens=800,  # Limit response length
    )

    # Extract answer
    answer = response.choices[0].message.content or ""

    logger.info(f"Generated answer ({len(answer)} chars)")
    return answer


async def answer_chat_request(
    request: ChatRequest,
    db: AsyncSession,
    settings_override: Settings | None = None,
) -> ChatResponse:
    """
    Main RAG pipeline: retrieve, generate, and respond.

    This is the core function that orchestrates the RAG process:
    1. Retrieve relevant chunks based on mode
    2. Build context from chunks
    3. Generate answer using OpenAI
    4. Extract citations
    5. Return structured response

    Args:
        request: Chat request with mode, question, and optional context
        db: Database session (for future enhancements, not used yet)
        settings_override: Optional settings override (for testing)

    Returns:
        ChatResponse with answer, citations, and mode

    Raises:
        ValueError: If request validation fails
        Exception: If OpenAI or Qdrant API calls fail
    """
    config = settings_override or settings

    logger.info(
        f"Processing chat request: mode={request.mode}, "
        f"question_len={len(request.question)}, "
        f"user_id={request.userId or 'anonymous'}"
    )

    # Retrieve chunks based on mode
    if request.mode == "whole-book":
        chunks = await retrieve_chunks_whole_book(
            question=request.question,
            limit=config.CHUNK_RETRIEVAL_LIMIT,
        )
    else:  # selection mode
        if not request.selectedText or not request.docPath:
            raise ValueError(
                "mode='selection' requires both selectedText and docPath"
            )

        chunks = await retrieve_chunks_selection(
            question=request.question,
            selected_text=request.selectedText,
            doc_path=request.docPath,
            limit=min(config.CHUNK_RETRIEVAL_LIMIT, 5),  # Smaller limit for selection
        )

    # Handle case where no chunks were retrieved
    if not chunks:
        logger.warning("No relevant chunks found in Qdrant")
        return ChatResponse(
            answer="I couldn't find relevant information in the textbook to answer your question. Please try rephrasing or asking a different question.",
            citations=[],
            mode=request.mode,
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

    # Generate answer
    try:
        answer = await generate_answer(
            question=request.question,
            context=context,
            chat_model=config.OPENAI_CHAT_MODEL,
        )
    except Exception as e:
        logger.error(f"Failed to generate answer: {e}")
        raise

    # Extract citations
    citations = extract_citations(chunks, max_citations=5)

    # Build response
    response = ChatResponse(
        answer=answer,
        citations=citations,
        mode=request.mode,
    )

    logger.info(
        f"Chat request completed: answer_len={len(answer)}, "
        f"citations={len(citations)}"
    )

    return response
