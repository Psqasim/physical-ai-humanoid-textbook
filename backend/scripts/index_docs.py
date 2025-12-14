"""
Textbook content indexing script for RAG backend.

This script:
1. Scans all Markdown/MDX files in ../docs (relative to backend/)
2. Strips YAML frontmatter and extracts metadata (doc_path, module_id)
3. Chunks content by heading with token-length fallback
4. Generates embeddings using OpenAI
5. Stores embeddings in Qdrant Cloud with metadata

Usage:
    # Dry run (parse only, no API calls)
    uv run python -m scripts.index_docs --dry-run

    # Index with limit (first N docs)
    uv run python -m scripts.index_docs --limit 5

    # Index entire corpus
    uv run python -m scripts.index_docs

    # Index with language tags (for multilingual support)
    uv run python -m scripts.index_docs --add-language-tags --language en

    # Re-index existing English documents with language tags
    uv run python -m scripts.index_docs --add-language-tags

    # Custom docs directory
    uv run python -m scripts.index_docs --docs-dir /path/to/docs
"""

import asyncio
import re
import sys
from pathlib import Path
from typing import List, Tuple
import argparse

# Third-party imports
try:
    import frontmatter
    import tiktoken
except ImportError:
    print("Error: Required packages not installed.")
    print("Please install with: uv add python-frontmatter tiktoken")
    sys.exit(1)

# Local imports - only import when not in dry-run mode
# This ensures the script can be imported without making network calls


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Index textbook content for RAG backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (parse only, no API calls)
  uv run python -m scripts.index_docs --dry-run

  # Index first 5 documents
  uv run python -m scripts.index_docs --limit 5

  # Index entire corpus
  uv run python -m scripts.index_docs

  # Custom docs directory
  uv run python -m scripts.index_docs --docs-dir /path/to/docs
        """,
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=None,
        help="Path to docs directory (default: ../docs relative to backend/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and analyze files without calling OpenAI/Qdrant",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Index only first N documents (for testing)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for embedding API calls (default: 100)",
    )
    parser.add_argument(
        "--add-language-tags",
        action="store_true",
        help="Add language metadata tags to indexed documents (default language: en)",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        choices=["en", "ur", "ja"],
        help="Language code for documents being indexed (default: en)",
    )
    return parser.parse_args()


def get_docs_directory(custom_path: str | None = None) -> Path:
    """
    Get the docs directory path.

    Args:
        custom_path: Optional custom path to docs directory

    Returns:
        Path to docs directory

    Raises:
        FileNotFoundError: If docs directory doesn't exist
    """
    if custom_path:
        docs_dir = Path(custom_path).resolve()
    else:
        # Default: ../docs relative to backend/
        backend_dir = Path(__file__).parent.parent
        docs_dir = (backend_dir.parent / "docs").resolve()

    if not docs_dir.exists():
        raise FileNotFoundError(f"Docs directory not found: {docs_dir}")

    return docs_dir


def find_markdown_files(docs_dir: Path, limit: int | None = None) -> List[Path]:
    """
    Recursively find all .md and .mdx files in docs directory.

    Args:
        docs_dir: Path to docs directory
        limit: Optional limit on number of files to return

    Returns:
        List of Path objects for Markdown files, sorted by path
    """
    patterns = ["**/*.md", "**/*.mdx"]
    files = []

    for pattern in patterns:
        files.extend(docs_dir.glob(pattern))

    # Sort for consistent ordering
    files = sorted(files)

    if limit:
        files = files[:limit]

    return files


def extract_module_id(doc_path: str) -> int:
    """
    Extract module ID (1-4) from document path.

    Looks for patterns like:
    - /docs/module-1-ros2/... -> 1
    - /docs/module-2-simulation/... -> 2
    - etc.

    Args:
        doc_path: Document path (e.g., "/docs/module-1-ros2/chapter-1.md")

    Returns:
        Module ID (1-4), defaults to 1 if not found
    """
    match = re.search(r"/module-(\d+)", doc_path)
    if match:
        return int(match.group(1))
    return 1  # Default to module 1


def parse_markdown_file(file_path: Path, docs_dir: Path) -> Tuple[str, dict]:
    """
    Parse a Markdown file, stripping frontmatter and extracting metadata.

    Args:
        file_path: Path to Markdown file
        docs_dir: Root docs directory (for computing relative paths)

    Returns:
        Tuple of (content, metadata) where:
        - content: Markdown content with frontmatter stripped
        - metadata: Dict with doc_path, module_id
    """
    # Read file with frontmatter
    post = frontmatter.load(file_path)

    # Compute doc_path (relative to docs dir, with /docs prefix)
    relative_path = file_path.relative_to(docs_dir.parent)
    doc_path = f"/{relative_path.as_posix()}"
    # Remove file extension from doc_path
    doc_path = doc_path.rsplit(".", 1)[0]

    # Extract module ID
    module_id = extract_module_id(doc_path)

    metadata = {
        "doc_path": doc_path,
        "module_id": module_id,
        "file_path": str(file_path),
    }

    return post.content, metadata


def extract_heading_hierarchy(content: str, chunk_start: int) -> str:
    """
    Extract the heading hierarchy for a chunk.

    Finds all headings (## or ###) before chunk_start and builds
    a hierarchy string like "Chapter 1 > Section 1.1".

    Args:
        content: Full document content
        chunk_start: Character position where chunk starts

    Returns:
        Heading hierarchy string (e.g., "Chapter 1 > Section 1.1")
    """
    # Find all headings before chunk_start
    heading_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    headings = []

    for match in heading_pattern.finditer(content[:chunk_start]):
        level = len(match.group(1))  # Number of # characters
        title = match.group(2).strip()
        headings.append((level, title))

    if not headings:
        return "Introduction"

    # Build hierarchy from headings (keep only most recent at each level)
    hierarchy = {}
    for level, title in headings:
        hierarchy[level] = title
        # Clear deeper levels
        for deeper_level in range(level + 1, 4):
            hierarchy.pop(deeper_level, None)

    # Build hierarchy string
    if hierarchy:
        return " > ".join(hierarchy.values())
    return "Introduction"


def chunk_by_headings(content: str, max_tokens: int = 500) -> List[Tuple[str, str]]:
    """
    Chunk content by headings, with token-length fallback.

    Strategy:
    1. Split by ## and ### headings (each section becomes a chunk)
    2. If a chunk exceeds max_tokens, split it further by paragraphs
    3. Each chunk includes heading context

    Args:
        content: Markdown content to chunk
        max_tokens: Maximum tokens per chunk (default: 500)

    Returns:
        List of (chunk_text, heading) tuples
    """
    # Initialize tokenizer
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    chunks = []

    # Split by headings (## or ###)
    heading_pattern = re.compile(r"^(#{1,3}\s+.+)$", re.MULTILINE)
    parts = heading_pattern.split(content)

    current_heading = "Introduction"
    current_text = ""

    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue

        # Check if this part is a heading
        if re.match(r"^#{1,3}\s+", part):
            # Save previous chunk if exists
            if current_text:
                chunks.extend(
                    _split_large_chunk(current_text, current_heading, max_tokens, encoding)
                )

            # Start new chunk with this heading
            current_heading = part.lstrip("#").strip()
            current_text = ""
        else:
            # Accumulate text for current heading
            current_text += "\n\n" + part if current_text else part

    # Save final chunk
    if current_text:
        chunks.extend(_split_large_chunk(current_text, current_heading, max_tokens, encoding))

    return chunks


def _split_large_chunk(
    text: str, heading: str, max_tokens: int, encoding
) -> List[Tuple[str, str]]:
    """
    Split a large chunk into smaller pieces by paragraphs.

    Args:
        text: Text to split
        heading: Heading for this chunk
        max_tokens: Maximum tokens per chunk
        encoding: Tiktoken encoding

    Returns:
        List of (chunk_text, heading) tuples
    """
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return [(text, heading)]

    # Split by paragraphs
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for para in paragraphs:
        para_tokens = encoding.encode(para)
        para_token_count = len(para_tokens)

        if current_tokens + para_token_count <= max_tokens:
            # Add to current chunk
            current_chunk += "\n\n" + para if current_chunk else para
            current_tokens += para_token_count
        else:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append((current_chunk, heading))
            current_chunk = para
            current_tokens = para_token_count

    # Save final chunk
    if current_chunk:
        chunks.append((current_chunk, heading))

    return chunks


async def generate_embeddings_batch(
    texts: List[str], batch_size: int = 100
) -> List[List[float]]:
    """
    Generate embeddings for a list of texts in batches.

    Args:
        texts: List of text strings to embed
        batch_size: Batch size for API calls

    Returns:
        List of embedding vectors
    """
    from app.services.embeddings import batch_embed

    return await batch_embed(texts, batch_size=batch_size)


async def index_document(
    file_path: Path, docs_dir: Path, dry_run: bool = False, language: str = "en", add_language_tags: bool = False
) -> List[dict]:
    """
    Index a single document: parse, chunk, and prepare for embedding.

    Args:
        file_path: Path to document file
        docs_dir: Root docs directory
        dry_run: If True, skip embedding generation
        language: Language code for the document (default: "en")
        add_language_tags: Whether to add language metadata to chunks

    Returns:
        List of chunk dictionaries with metadata
    """
    from app.core.logging import get_logger

    logger = get_logger(__name__)

    # Parse file
    content, metadata = parse_markdown_file(file_path, docs_dir)

    # Chunk content
    chunks_with_headings = chunk_by_headings(content, max_tokens=500)

    if dry_run:
        # Return metadata without embeddings
        return [
            {
                "doc_path": metadata["doc_path"],
                "module_id": metadata["module_id"],
                "heading": heading,
                "chunk_index": idx,
                "text": text[:100] + "..." if len(text) > 100 else text,  # Truncate for display
                "text_length": len(text),
            }
            for idx, (text, heading) in enumerate(chunks_with_headings)
        ]

    # Generate embeddings
    texts = [text for text, _ in chunks_with_headings]

    try:
        embeddings = await generate_embeddings_batch(texts)
    except Exception as e:
        logger.error(f"Failed to generate embeddings for {file_path}: {e}")
        raise

    # Build chunk objects
    chunk_objects = []
    for idx, ((text, heading), embedding) in enumerate(zip(chunks_with_headings, embeddings)):
        chunk_obj = {
            "id": f"{metadata['doc_path']}:{idx}",
            "vector": embedding,
            "doc_path": metadata["doc_path"],
            "module_id": str(metadata["module_id"]),
            "heading": heading,
            "chunk_index": idx,
            "text": text,
        }

        # Add language metadata if requested
        if add_language_tags:
            chunk_obj.update({
                "language": language,
                "original_language": language,
                "translation_source": "original",
                "content_type": "docs",
            })

        chunk_objects.append(chunk_obj)

    return chunk_objects


async def upsert_chunks_to_qdrant(chunks: List[dict]) -> None:
    """
    Upsert chunks to Qdrant Cloud.

    Supports both legacy chunks (without language metadata) and
    multilingual chunks (with language metadata).

    Args:
        chunks: List of chunk dictionaries with embeddings
    """
    # Check if chunks have language metadata
    has_language_metadata = chunks and "language" in chunks[0]

    if has_language_metadata:
        # Use multilingual RAG service for chunks with language metadata
        from app.services.rag_multilingual import MultilingualEmbeddingChunk
        from app.services.qdrant import get_qdrant_client
        from qdrant_client.models import PointStruct
        from uuid import uuid4

        client = get_qdrant_client()
        from app.core.config import settings

        # Convert to PointStruct objects with language metadata
        points = [
            PointStruct(
                id=uuid4(),
                vector=chunk["vector"],
                payload={
                    "chunk_id": chunk["id"],
                    "text": chunk["text"],
                    "doc_path": chunk["doc_path"],
                    "module_id": chunk["module_id"],
                    "heading": chunk["heading"],
                    "chunk_index": chunk["chunk_index"],
                    "language": chunk["language"],
                    "original_language": chunk["original_language"],
                    "translation_source": chunk["translation_source"],
                    "content_type": chunk["content_type"],
                },
            )
            for chunk in chunks
        ]

        await client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=points,
        )
    else:
        # Use legacy service for chunks without language metadata
        from app.services.qdrant import upsert_embeddings, EmbeddingChunk

        embedding_chunks = [
            EmbeddingChunk(
                id=chunk["id"],
                vector=chunk["vector"],
                doc_path=chunk["doc_path"],
                module_id=chunk["module_id"],
                heading=chunk["heading"],
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
            )
            for chunk in chunks
        ]

        await upsert_embeddings(embedding_chunks)


async def main() -> None:
    """Main entry point for indexing script."""
    args = parse_args()

    # Only import these when actually needed (not during dry-run parsing)
    if not args.dry_run:
        # This will trigger network calls when services initialize
        from app.core.logging import get_logger
        from app.services.qdrant import ensure_collection_exists

        logger = get_logger(__name__)
    else:
        # Simple logging for dry-run
        import logging

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Textbook Content Indexing Script")
    logger.info("=" * 60)

    # Get docs directory
    try:
        docs_dir = get_docs_directory(args.docs_dir)
        logger.info(f"Docs directory: {docs_dir}")
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    # Find Markdown files
    files = find_markdown_files(docs_dir, limit=args.limit)
    logger.info(f"Found {len(files)} Markdown files")

    if args.limit:
        logger.info(f"Limiting to first {args.limit} files")

    if args.dry_run:
        logger.info("DRY RUN MODE: Parsing only, no API calls")
    else:
        logger.info("LIVE MODE: Will call OpenAI and Qdrant APIs")
        # Ensure Qdrant collection exists
        logger.info("Ensuring Qdrant collection exists...")
        created = await ensure_collection_exists()
        if created:
            logger.info("✓ Qdrant collection created")
        else:
            logger.info("✓ Qdrant collection already exists")

    # Process each file
    total_chunks = 0
    all_chunks = []

    for i, file_path in enumerate(files, 1):
        logger.info(f"[{i}/{len(files)}] Processing: {file_path.name}")

        try:
            chunks = await index_document(
                file_path,
                docs_dir,
                dry_run=args.dry_run,
                language=args.language,
                add_language_tags=args.add_language_tags
            )
            total_chunks += len(chunks)
            all_chunks.extend(chunks)

            if args.dry_run:
                logger.info(f"  → Generated {len(chunks)} chunks")
            else:
                if args.add_language_tags:
                    logger.info(f"  → Generated {len(chunks)} chunks with embeddings and language tags (lang: {args.language})")
                else:
                    logger.info(f"  → Generated {len(chunks)} chunks with embeddings")

        except Exception as e:
            logger.error(f"  ✗ Failed to process {file_path.name}: {e}")
            continue

    # Upsert to Qdrant (if not dry-run)
    if not args.dry_run and all_chunks:
        logger.info("=" * 60)
        logger.info(f"Uploading {total_chunks} chunks to Qdrant...")

        try:
            await upsert_chunks_to_qdrant(all_chunks)
            logger.info("✓ Successfully uploaded all chunks")
        except Exception as e:
            logger.error(f"✗ Failed to upload chunks: {e}")
            sys.exit(1)

    # Summary
    logger.info("=" * 60)
    logger.info("Indexing Summary")
    logger.info("=" * 60)
    logger.info(f"Files processed: {len(files)}")
    logger.info(f"Total chunks: {total_chunks}")
    logger.info(f"Average chunks per file: {total_chunks / len(files):.1f}")

    if args.dry_run:
        logger.info("")
        logger.info("DRY RUN complete. No data was sent to OpenAI or Qdrant.")
        logger.info("To run with real API calls, remove --dry-run flag:")
        logger.info("  uv run python -m scripts.index_docs")
    else:
        logger.info("")
        logger.info("✓ Indexing complete!")

    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
