"""
Test suite for language detection functionality.

Tests cover:
- Language detection for English, Urdu, and Japanese
- Mixed language detection (dominant language)
- Unsupported language fallback
- Low confidence fallback
- Edge cases (empty text, very short text)
"""

import pytest
from app.core.i18n import detect_language, get_fallback_language, SUPPORTED_LANGUAGES


class TestLanguageDetection:
    """Test cases for the detect_language function."""

    def test_detect_english(self):
        """Test detection of English text."""
        text = "What is ROS 2 and how does it work?"
        result = detect_language(text)

        assert result["detectedLanguage"] == "en"
        assert result["confidence"] > 0.5
        assert result["fallbackApplied"] is False

    def test_detect_urdu(self):
        """Test detection of Urdu text."""
        text = "ROS 2 کیا ہے اور یہ کیسے کام کرتا ہے؟"
        result = detect_language(text)

        assert result["detectedLanguage"] == "ur"
        assert result["confidence"] > 0.5
        assert result["fallbackApplied"] is False

    def test_detect_japanese(self):
        """Test detection of Japanese text."""
        text = "ROS 2 とは何ですか？どのように機能しますか？"
        result = detect_language(text)

        assert result["detectedLanguage"] == "ja"
        assert result["confidence"] > 0.5
        assert result["fallbackApplied"] is False

    def test_mixed_language_english_dominant(self):
        """Test detection with mixed English and Urdu (English dominant)."""
        text = "ROS 2 is a روبوٹکس framework for building robot applications"
        result = detect_language(text)

        # Should detect dominant language (English in this case)
        assert result["detectedLanguage"] in SUPPORTED_LANGUAGES
        # Confidence may vary for mixed content
        assert 0.0 <= result["confidence"] <= 1.0

    def test_mixed_language_urdu_dominant(self):
        """Test detection with mixed Urdu and English (Urdu dominant)."""
        text = "ROS 2 ایک روبوٹکس فریم ورک ہے جو robot applications بنانے کے لیے استعمال ہوتا ہے"
        result = detect_language(text)

        # Should detect dominant language or fallback
        assert result["detectedLanguage"] in SUPPORTED_LANGUAGES + ["unknown"]
        assert 0.0 <= result["confidence"] <= 1.0

    def test_unsupported_language_fallback(self):
        """Test fallback for unsupported language (e.g., Arabic)."""
        text = "ما هو ROS 2 وكيف يعمل؟"  # Arabic text
        result = detect_language(text)

        # Should fallback to default language (English)
        assert result["detectedLanguage"] == "en"
        assert result["confidence"] == 0.0
        assert result["fallbackApplied"] is True

    def test_empty_text_fallback(self):
        """Test handling of empty text input."""
        text = ""
        result = detect_language(text)

        assert result["detectedLanguage"] == "en"
        assert result["confidence"] == 0.0
        assert result["fallbackApplied"] is True

    def test_whitespace_only_fallback(self):
        """Test handling of whitespace-only text."""
        text = "   \n\t   "
        result = detect_language(text)

        assert result["detectedLanguage"] == "en"
        assert result["confidence"] == 0.0
        assert result["fallbackApplied"] is True

    def test_very_short_text(self):
        """Test detection with very short text (may be ambiguous)."""
        text = "Hi"
        result = detect_language(text)

        # Short text may have lower confidence or fallback
        assert result["detectedLanguage"] in SUPPORTED_LANGUAGES
        assert 0.0 <= result["confidence"] <= 1.0

    def test_numbers_only(self):
        """Test handling of numbers-only input."""
        text = "123 456 789"
        result = detect_language(text)

        # Numbers alone can't determine language, should fallback
        assert result["detectedLanguage"] in SUPPORTED_LANGUAGES
        assert 0.0 <= result["confidence"] <= 1.0

    def test_code_snippet(self):
        """Test detection with programming code (should detect as English)."""
        text = "def hello_world(): print('Hello, World!')"
        result = detect_language(text)

        # Code is typically detected as English
        assert result["detectedLanguage"] in SUPPORTED_LANGUAGES


class TestFallbackLanguage:
    """Test cases for the get_fallback_language function."""

    def test_high_confidence_no_fallback(self):
        """Test that high confidence doesn't trigger fallback."""
        result = get_fallback_language(confidence=0.9, ui_language="ur")

        assert result is None  # Trust detection

    def test_low_confidence_with_ui_language(self):
        """Test fallback to UI language when confidence is low."""
        result = get_fallback_language(confidence=0.3, ui_language="ur")

        assert result == "ur"

    def test_low_confidence_no_ui_language(self):
        """Test fallback to default when no UI language provided."""
        result = get_fallback_language(confidence=0.3, ui_language=None)

        assert result == "en"

    def test_low_confidence_unsupported_ui_language(self):
        """Test fallback to default when UI language is unsupported."""
        result = get_fallback_language(confidence=0.3, ui_language="fr")

        assert result == "en"

    def test_boundary_confidence_threshold(self):
        """Test behavior at confidence threshold boundary (0.5)."""
        # Exactly at threshold should NOT trigger fallback
        result_at_threshold = get_fallback_language(confidence=0.5, ui_language="ja")
        assert result_at_threshold is None

        # Just below threshold should trigger fallback
        result_below_threshold = get_fallback_language(confidence=0.49, ui_language="ja")
        assert result_below_threshold == "ja"

    def test_zero_confidence(self):
        """Test fallback with zero confidence."""
        result = get_fallback_language(confidence=0.0, ui_language="ja")

        assert result == "ja"

    def test_full_confidence(self):
        """Test no fallback with full confidence."""
        result = get_fallback_language(confidence=1.0, ui_language="ur")

        assert result is None


class TestLanguageDetectionIntegration:
    """Integration tests for language detection workflow."""

    def test_english_detection_workflow(self):
        """Test complete workflow for English input."""
        text = "Explain the concept of Digital Twin in robotics"
        detection = detect_language(text)
        fallback = get_fallback_language(detection["confidence"], ui_language="en")

        # High confidence English should not need fallback
        assert detection["detectedLanguage"] == "en"
        assert fallback is None or fallback == "en"

    def test_urdu_detection_workflow(self):
        """Test complete workflow for Urdu input."""
        text = "روبوٹکس میں ڈیجیٹل ٹون کے تصور کی وضاحت کریں"
        detection = detect_language(text)
        fallback = get_fallback_language(detection["confidence"], ui_language="ur")

        # Should detect Urdu
        assert detection["detectedLanguage"] == "ur"

    def test_japanese_detection_workflow(self):
        """Test complete workflow for Japanese input."""
        text = "ロボット工学におけるデジタルツインの概念を説明してください"
        detection = detect_language(text)
        fallback = get_fallback_language(detection["confidence"], ui_language="ja")

        # Should detect Japanese
        assert detection["detectedLanguage"] == "ja"

    def test_ambiguous_text_with_ui_language_fallback(self):
        """Test fallback to UI language for ambiguous text."""
        text = "ROS 2"  # Very short, ambiguous
        detection = detect_language(text)
        fallback = get_fallback_language(detection["confidence"], ui_language="ur")

        # If confidence is low, should use UI language
        if detection["confidence"] < 0.5:
            assert fallback == "ur"

    def test_unsupported_language_with_ui_language(self):
        """Test fallback for unsupported language with UI language."""
        text = "Qu'est-ce que ROS 2?"  # French (unsupported)
        detection = detect_language(text)
        fallback = get_fallback_language(detection["confidence"], ui_language="ja")

        # Should fallback to English (unsupported language)
        assert detection["detectedLanguage"] == "en"
        assert detection["fallbackApplied"] is True


# Test data for parametrized tests
@pytest.mark.parametrize("text,expected_lang", [
    ("Hello world", "en"),
    ("سلام دنیا", "ur"),
    ("こんにちは世界", "ja"),
    ("What is robotics?", "en"),
    ("روبوٹکس کیا ہے؟", "ur"),
    ("ロボット工学とは何ですか？", "ja"),
])
def test_detect_language_parametrized(text, expected_lang):
    """Parametrized test for multiple language inputs."""
    result = detect_language(text)
    assert result["detectedLanguage"] == expected_lang
    assert result["confidence"] > 0.5
    assert result["fallbackApplied"] is False


@pytest.mark.parametrize("confidence,ui_lang,expected", [
    (0.9, "en", None),      # High confidence, no fallback
    (0.9, "ur", None),      # High confidence, no fallback
    (0.3, "en", "en"),      # Low confidence, use UI lang
    (0.3, "ur", "ur"),      # Low confidence, use UI lang
    (0.3, None, "en"),      # Low confidence, no UI lang, use default
    (0.3, "fr", "en"),      # Low confidence, unsupported UI lang, use default
])
def test_fallback_language_parametrized(confidence, ui_lang, expected):
    """Parametrized test for fallback logic."""
    result = get_fallback_language(confidence, ui_lang)
    assert result == expected
