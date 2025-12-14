"""
Internationalization (i18n) core module for language detection and utilities.

This module provides language detection functionality using the langdetect library
and language-related utilities for the multilingual support feature.
"""

from typing import Dict, Optional
from langdetect import detect, DetectorFactory, LangDetectException
import logging

# Set seed for consistent results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ['en', 'ur', 'ja']
DEFAULT_LANGUAGE = 'en'
CONFIDENCE_THRESHOLD = 0.5


def detect_language(text: str) -> Dict[str, any]:
    """
    Detect language from input text using langdetect library.

    Args:
        text: Input text to detect language from

    Returns:
        Dictionary with:
        - detectedLanguage: Language code ('en', 'ur', 'ja', or 'unknown')
        - confidence: Confidence score (0.0 to 1.0)
        - fallbackApplied: Whether fallback to default language was applied

    Note:
        langdetect doesn't return confidence scores, so we use heuristics:
        - If detected language is supported: confidence = 0.9
        - If detected language is unsupported or detection fails: confidence = 0.0
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for language detection")
        return {
            "detectedLanguage": DEFAULT_LANGUAGE,
            "confidence": 0.0,
            "fallbackApplied": True
        }

    try:
        lang_code = detect(text)
        logger.info(f"Detected language: {lang_code} for text length: {len(text)}")

        # Check if detected language is supported
        if lang_code in SUPPORTED_LANGUAGES:
            return {
                "detectedLanguage": lang_code,
                "confidence": 0.9,  # langdetect doesn't return confidence, use heuristic
                "fallbackApplied": False
            }
        else:
            logger.info(f"Unsupported language detected: {lang_code}, falling back to {DEFAULT_LANGUAGE}")
            return {
                "detectedLanguage": DEFAULT_LANGUAGE,
                "confidence": 0.0,
                "fallbackApplied": True
            }
    except LangDetectException as e:
        logger.error(f"Language detection failed: {str(e)}")
        return {
            "detectedLanguage": DEFAULT_LANGUAGE,
            "confidence": 0.0,
            "fallbackApplied": True
        }
    except Exception as e:
        logger.error(f"Unexpected error during language detection: {str(e)}")
        return {
            "detectedLanguage": DEFAULT_LANGUAGE,
            "confidence": 0.0,
            "fallbackApplied": True
        }


def get_fallback_language(confidence: float, ui_language: Optional[str] = None) -> str:
    """
    Determine fallback language based on confidence threshold and UI language.

    Args:
        confidence: Detection confidence score (0.0 to 1.0)
        ui_language: User's UI language preference (optional)

    Returns:
        Language code to use ('en', 'ur', or 'ja')

    Logic:
        - If confidence >= threshold: trust detection
        - If confidence < threshold and ui_language is supported: use ui_language
        - Otherwise: use DEFAULT_LANGUAGE (en)
    """
    if confidence >= CONFIDENCE_THRESHOLD:
        return None  # Trust detection result

    if ui_language and ui_language in SUPPORTED_LANGUAGES:
        logger.info(f"Low confidence ({confidence}), using UI language: {ui_language}")
        return ui_language

    logger.info(f"Low confidence ({confidence}), no UI language, using default: {DEFAULT_LANGUAGE}")
    return DEFAULT_LANGUAGE


def get_language_name(lang_code: str) -> str:
    """
    Get human-readable language name from code.

    Args:
        lang_code: Language code ('en', 'ur', 'ja')

    Returns:
        Human-readable language name
    """
    language_names = {
        'en': 'English',
        'ur': 'Urdu (اردو)',
        'ja': 'Japanese (日本語)'
    }
    return language_names.get(lang_code, 'Unknown')
