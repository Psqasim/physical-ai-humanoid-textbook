"""
Language detection API endpoints for multilingual support.

This module provides the /api/detect-language endpoint for detecting
the language of user input text.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
import logging
from datetime import datetime

from app.core.i18n import detect_language

logger = logging.getLogger(__name__)

router = APIRouter()


class LanguageDetectionRequest(BaseModel):
    """Request model for language detection."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text to detect language from"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "ROS 2 کیا ہے؟"
            }
        }


class LanguageDetectionResult(BaseModel):
    """Response model for language detection."""
    detectedLanguage: Literal['en', 'ur', 'ja', 'unknown'] = Field(
        ...,
        description="Detected language code"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Detection confidence score (0.0 to 1.0)"
    )
    fallbackApplied: bool = Field(
        ...,
        description="Whether fallback to default language was applied"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "detectedLanguage": "ur",
                "confidence": 0.9,
                "fallbackApplied": False
            }
        }


@router.post("/detect-language", response_model=LanguageDetectionResult)
async def detect_text_language(request: LanguageDetectionRequest):
    """
    Detect the language of input text.

    This endpoint uses the langdetect library to identify the language
    of the provided text. It supports English (en), Urdu (ur), and
    Japanese (ja). If the detected language is not supported or
    detection fails, it falls back to English.

    Args:
        request: LanguageDetectionRequest containing the text to analyze

    Returns:
        LanguageDetectionResult with detected language, confidence, and
        fallback status

    Example:
        ```
        POST /api/detect-language
        {
            "text": "ROS 2 کیا ہے؟"
        }

        Response:
        {
            "detectedLanguage": "ur",
            "confidence": 0.9,
            "fallbackApplied": false
        }
        ```
    """
    try:
        timestamp = datetime.utcnow().isoformat()

        logger.info(f"Language detection request received for text length: {len(request.text)}")

        # Detect language
        result = detect_language(request.text)

        # Log analytics (no PII - no message content logged)
        logger.info(
            f"Language detection analytics - "
            f"timestamp: {timestamp}, "
            f"detected_language: {result['detectedLanguage']}, "
            f"confidence: {result['confidence']:.2f}, "
            f"fallback_applied: {result['fallbackApplied']}, "
            f"text_length: {len(request.text)}"
        )

        return LanguageDetectionResult(**result)

    except Exception as e:
        logger.error(f"Error in language detection endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Language detection failed: {str(e)}"
        )
