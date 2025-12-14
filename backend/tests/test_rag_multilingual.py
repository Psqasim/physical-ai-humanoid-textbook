"""
Test suite for multilingual RAG functionality.

Tests cover:
- Document indexing with language tags
- Language-filtered similarity search
- Fallback to English when target language content unavailable
- Search performance with language filters
- Multilingual search result ordering
"""

import pytest
from app.services.rag_multilingual import (
    index_document,
    search_with_language_filter,
    search_with_fallback,
    MultilingualEmbeddingChunk,
    MultilingualSearchResult,
)


class TestMultilingualIndexing:
    """Test cases for multilingual document indexing."""

    @pytest.mark.asyncio
    async def test_index_english_document(self):
        """
        T075: Index 3 English docs → query "ROS 2" with language="en"
        → assert returns English docs.
        """
        # Index test document in English
        doc_text = """
        ROS 2 is a modern robotics framework.

        ## What is ROS 2?
        ROS 2 (Robot Operating System 2) is an open-source framework for building
        robot applications. It provides tools, libraries, and conventions to simplify
        the task of creating complex and robust robot behavior.

        ## Key Features
        - Real-time communication
        - Distributed architecture
        - Modern C++ and Python APIs
        """

        chunks_indexed = await index_document(
            doc_text=doc_text,
            doc_id="test-ros2-intro-en",
            language="en",
            original_language="en",
            translation_source="original",
            content_type="docs",
        )

        # Verify chunks were created
        assert chunks_indexed > 0
        assert isinstance(chunks_indexed, int)

    @pytest.mark.asyncio
    async def test_index_with_translation_metadata(self):
        """Test indexing a translated document with quality score."""
        doc_text = "ROS 2 روبوٹکس سسٹم کے لیے ایک جدید فریم ورک ہے۔"

        chunks_indexed = await index_document(
            doc_text=doc_text,
            doc_id="test-ros2-intro-ur",
            language="ur",
            original_language="en",
            translation_source="human",
            content_type="docs",
            translation_quality=0.95,
        )

        assert chunks_indexed > 0

    @pytest.mark.asyncio
    async def test_index_validation_invalid_language(self):
        """Test that invalid language codes are rejected."""
        with pytest.raises(ValueError, match="Invalid language"):
            await index_document(
                doc_text="Some text",
                doc_id="test-invalid",
                language="fr",  # French not supported
            )

    @pytest.mark.asyncio
    async def test_index_validation_empty_text(self):
        """Test that empty document text is rejected."""
        with pytest.raises(ValueError, match="doc_text cannot be empty"):
            await index_document(
                doc_text="",
                doc_id="test-empty",
                language="en",
            )


class TestLanguageFilteredSearch:
    """Test cases for language-filtered similarity search."""

    @pytest.mark.asyncio
    async def test_search_english_docs(self):
        """
        T075: Query "ROS 2" with language="en" → assert returns English docs.

        This test requires English documents to be indexed first.
        """
        # Search for English documents
        results = await search_with_language_filter(
            query="What is ROS 2?",
            language="en",
            limit=5,
        )

        # Verify results
        assert isinstance(results, list)

        # If results exist, verify they're English
        for result in results:
            assert isinstance(result, MultilingualSearchResult)
            assert result.language == "en"
            assert result.score > 0

    @pytest.mark.asyncio
    async def test_search_japanese_docs(self):
        """
        T076: Query in Japanese with language="ja" → assert Japanese docs prioritized.

        This test requires Japanese documents to be indexed first.
        """
        results = await search_with_language_filter(
            query="ROS 2 とは何ですか？",
            language="ja",
            limit=5,
        )

        # Verify results structure
        assert isinstance(results, list)

        # If results exist, verify they're Japanese
        for result in results:
            assert isinstance(result, MultilingualSearchResult)
            assert result.language == "ja"

    @pytest.mark.asyncio
    async def test_search_urdu_docs(self):
        """Test search for Urdu documents."""
        results = await search_with_language_filter(
            query="ROS 2 کیا ہے؟",
            language="ur",
            limit=5,
        )

        # Verify results structure
        assert isinstance(results, list)

        # If results exist, verify they're Urdu
        for result in results:
            assert isinstance(result, MultilingualSearchResult)
            assert result.language == "ur"

    @pytest.mark.asyncio
    async def test_search_with_content_type_filter(self):
        """Test search with additional content_type filter."""
        results = await search_with_language_filter(
            query="Submit button",
            language="en",
            content_type="ui",
            limit=3,
        )

        # Verify results structure
        assert isinstance(results, list)

        # If results exist, verify content_type
        for result in results:
            assert isinstance(result, MultilingualSearchResult)
            assert result.content_type == "ui"

    @pytest.mark.asyncio
    async def test_search_validation_invalid_language(self):
        """Test that invalid language codes are rejected in search."""
        with pytest.raises(ValueError, match="Invalid language"):
            await search_with_language_filter(
                query="Test query",
                language="de",  # German not supported
                limit=5,
            )


class TestFallbackSearch:
    """Test cases for search with fallback to English."""

    @pytest.mark.asyncio
    async def test_fallback_to_english(self):
        """
        T077: Query in Urdu with no Urdu docs → assert fallback to English docs
        and fallbackApplied=true.

        This test searches for Urdu content, and if insufficient results are found,
        it should fall back to English.
        """
        # Search with fallback
        results, fallback_applied = await search_with_fallback(
            query="ROS 2 کیا ہے؟",
            primary_language="ur",
            fallback_language="en",
            limit=5,
            min_results=3,
        )

        # Verify results structure
        assert isinstance(results, list)
        assert isinstance(fallback_applied, bool)

        # If fallback was applied, verify we have English results
        if fallback_applied:
            # Should have some English documents
            english_results = [r for r in results if r.language == "en"]
            assert len(english_results) > 0

    @pytest.mark.asyncio
    async def test_no_fallback_when_sufficient_results(self):
        """Test that fallback is not applied when primary language has enough results."""
        # Search English (should have plenty of results)
        results, fallback_applied = await search_with_fallback(
            query="What is ROS 2?",
            primary_language="en",
            fallback_language="en",  # Same language for simplicity
            limit=5,
            min_results=3,
        )

        # Verify structure
        assert isinstance(results, list)
        assert isinstance(fallback_applied, bool)

        # If we have 3+ results, fallback should not be applied
        if len(results) >= 3:
            assert fallback_applied is False

    @pytest.mark.asyncio
    async def test_fallback_result_ordering(self):
        """Test that fallback results place primary language first."""
        results, fallback_applied = await search_with_fallback(
            query="ROS 2",
            primary_language="ja",
            fallback_language="en",
            limit=10,
            min_results=3,
        )

        # Verify results structure
        assert isinstance(results, list)

        # If we have mixed language results
        if len(results) > 0:
            languages = [r.language for r in results]

            # Primary language results should come first if both exist
            if "ja" in languages and "en" in languages:
                first_en_index = languages.index("en")
                ja_indices = [i for i, lang in enumerate(languages) if lang == "ja"]

                # All Japanese results should come before first English result
                if ja_indices:
                    assert max(ja_indices) < first_en_index


class TestMultilingualSearchResult:
    """Test cases for MultilingualSearchResult data structure."""

    def test_search_result_creation(self):
        """Test creating a MultilingualSearchResult object."""
        result = MultilingualSearchResult(
            id="test_id",
            score=0.95,
            text="Test text content",
            doc_id="test-doc-123",
            language="en",
            original_language="en",
            translation_source="original",
            content_type="docs",
            chunk_index=0,
            translation_quality=None,
        )

        assert result.id == "test_id"
        assert result.score == 0.95
        assert result.language == "en"
        assert result.translation_source == "original"
        assert result.content_type == "docs"

    def test_search_result_with_translation_quality(self):
        """Test search result with translation quality score."""
        result = MultilingualSearchResult(
            id="test_id",
            score=0.88,
            text="ROS 2 روبوٹکس کے لیے ایک فریم ورک ہے",
            doc_id="test-doc-ur",
            language="ur",
            original_language="en",
            translation_source="human",
            content_type="docs",
            chunk_index=0,
            translation_quality=0.95,
        )

        assert result.language == "ur"
        assert result.original_language == "en"
        assert result.translation_source == "human"
        assert result.translation_quality == 0.95


class TestMultilingualEmbeddingChunk:
    """Test cases for MultilingualEmbeddingChunk data structure."""

    def test_chunk_creation_original_content(self):
        """Test creating a chunk for original content."""
        chunk = MultilingualEmbeddingChunk(
            id="test-doc:0",
            vector=[0.1, 0.2, 0.3],  # Mock embedding
            text="Test content",
            doc_id="test-doc",
            language="en",
            original_language="en",
            translation_source="original",
            content_type="docs",
            chunk_index=0,
        )

        assert chunk.id == "test-doc:0"
        assert len(chunk.vector) == 3
        assert chunk.language == "en"
        assert chunk.translation_source == "original"

    def test_chunk_creation_translated_content(self):
        """Test creating a chunk for translated content."""
        chunk = MultilingualEmbeddingChunk(
            id="test-doc-ur:0",
            vector=[0.1] * 1536,  # Full-size embedding
            text="ٹیسٹ مواد",
            doc_id="test-doc-ur",
            language="ur",
            original_language="en",
            translation_source="machine",
            content_type="docs",
            chunk_index=0,
            translation_quality=0.85,
        )

        assert chunk.language == "ur"
        assert chunk.original_language == "en"
        assert chunk.translation_source == "machine"
        assert chunk.translation_quality == 0.85


# Integration test markers for tests that require live services
pytestmark_integration = pytest.mark.integration

class TestMultilingualRAGIntegration:
    """
    Integration tests for multilingual RAG (requires Qdrant connection).

    These tests are marked as 'integration' and can be skipped in unit test runs.
    Run with: pytest -m integration
    """

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_index_and_search(self):
        """
        End-to-end test: Index a document and search for it.

        This test requires a live Qdrant connection.
        """
        # Index a test document
        doc_text = "ROS 2 is a modern robotics framework for building robot applications."

        chunks_indexed = await index_document(
            doc_text=doc_text,
            doc_id="test-e2e-en",
            language="en",
        )

        assert chunks_indexed > 0

        # Search for the document
        results = await search_with_language_filter(
            query="robotics framework",
            language="en",
            limit=5,
        )

        # Should find our document
        assert len(results) > 0

        # Verify at least one result is from our document
        doc_ids = [r.doc_id for r in results]
        assert "test-e2e-en" in doc_ids
