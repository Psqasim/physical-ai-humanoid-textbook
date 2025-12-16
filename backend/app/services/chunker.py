"""
Markdown-aware text chunking for RAG embeddings.

Chunks markdown content while:
- Preserving heading hierarchy
- Respecting token limits (500-800 tokens per chunk)
- Adding overlap between chunks (100 tokens)
- Maintaining semantic coherence
"""

import re
from dataclasses import dataclass
from typing import Literal
import tiktoken


@dataclass
class TextChunk:
    """
    A chunk of text with metadata.

    Attributes:
        text: Chunk content
        heading: Current heading context
        chunk_index: Index of chunk within document (0-based)
        token_count: Approximate token count
    """
    text: str
    heading: str
    chunk_index: int
    token_count: int


class MarkdownChunker:
    """
    Chunks markdown content into embedding-friendly pieces.

    Uses tiktoken for accurate token counting with OpenAI models.
    Preserves heading hierarchy and adds overlap for context.
    """

    def __init__(
        self,
        chunk_size: int = 700,
        chunk_overlap: int = 100,
        encoding_name: str = "cl100k_base",  # GPT-4, text-embedding-3-small
    ):
        """
        Initialize chunker with size and overlap parameters.

        Args:
            chunk_size: Target tokens per chunk (default: 700)
            chunk_overlap: Overlap tokens between chunks (default: 100)
            encoding_name: Tiktoken encoding (default: cl100k_base)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.

        Args:
            text: Text to count

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def extract_headings(self, text: str) -> list[tuple[str, int, str]]:
        """
        Extract markdown headings with positions.

        Args:
            text: Markdown content

        Returns:
            List of (heading_text, char_position, heading_level)

        Example:
            "# Title\nContent\n## Section\nMore"
            -> [("Title", 0, "h1"), ("Section", 17, "h2")]
        """
        headings = []
        # Match markdown headings: # Title, ## Subtitle, etc.
        pattern = r"^(#{1,6})\s+(.+)$"

        for match in re.finditer(pattern, text, re.MULTILINE):
            level = len(match.group(1))  # Number of # symbols
            heading_text = match.group(2).strip()
            position = match.start()
            headings.append((heading_text, position, f"h{level}"))

        return headings

    def chunk_by_headings(self, text: str) -> list[TextChunk]:
        """
        Chunk text by markdown headings, respecting token limits.

        Strategy:
        1. Split by headings
        2. If section fits in chunk_size, keep it whole
        3. If section exceeds chunk_size, split with overlap
        4. Preserve heading context for each chunk

        Args:
            text: Markdown content

        Returns:
            List of TextChunk objects
        """
        headings = self.extract_headings(text)
        chunks = []
        chunk_index = 0

        # If no headings, treat entire text as one section
        if not headings:
            return self._split_long_text(text, "Introduction", 0)

        # Process each section between headings
        for i, (heading, pos, level) in enumerate(headings):
            # Find next heading position (or end of text)
            next_pos = headings[i + 1][1] if i + 1 < len(headings) else len(text)

            # Extract section content (including heading)
            section = text[pos:next_pos].strip()
            section_tokens = self.count_tokens(section)

            # If section fits in chunk size, keep it whole
            if section_tokens <= self.chunk_size:
                chunks.append(
                    TextChunk(
                        text=section,
                        heading=heading,
                        chunk_index=chunk_index,
                        token_count=section_tokens,
                    )
                )
                chunk_index += 1
            else:
                # Section too long, split with overlap
                section_chunks = self._split_long_text(section, heading, chunk_index)
                chunks.extend(section_chunks)
                chunk_index += len(section_chunks)

        return chunks

    def _split_long_text(
        self, text: str, heading: str, start_index: int
    ) -> list[TextChunk]:
        """
        Split long text into overlapping chunks.

        Args:
            text: Text to split
            heading: Current heading context
            start_index: Starting chunk index

        Returns:
            List of TextChunk objects
        """
        chunks = []
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)

        # Calculate chunk positions
        current_pos = 0
        chunk_index = start_index

        while current_pos < total_tokens:
            # Extract chunk tokens (up to chunk_size)
            end_pos = min(current_pos + self.chunk_size, total_tokens)
            chunk_tokens = tokens[current_pos:end_pos]

            # Decode tokens back to text
            chunk_text = self.encoding.decode(chunk_tokens)

            chunks.append(
                TextChunk(
                    text=chunk_text,
                    heading=heading,
                    chunk_index=chunk_index,
                    token_count=len(chunk_tokens),
                )
            )

            # Move position forward, accounting for overlap
            if end_pos < total_tokens:
                current_pos = end_pos - self.chunk_overlap
            else:
                break  # Last chunk

            chunk_index += 1

        return chunks

    def chunk_document(self, text: str) -> list[TextChunk]:
        """
        Chunk a full document.

        Main entry point for chunking markdown content.

        Args:
            text: Full markdown document

        Returns:
            List of TextChunk objects with heading context
        """
        return self.chunk_by_headings(text)
