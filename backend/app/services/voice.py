"""
Voice service for multilingual Speech-to-Text and Text-to-Speech.

This module provides voice capabilities for the Study Assistant:
1. Speech-to-Text (STT) using OpenAI Whisper with auto language detection
2. Text-to-Speech (TTS) using OpenAI TTS API with multilingual support

Supported languages: English (en), Urdu (ur), Japanese (ja)

Usage:
    from app.services.voice import transcribe_audio, generate_speech, VoiceResponse

    # Transcribe audio with language detection
    result = await transcribe_audio(audio_bytes, filename="recording.wav")
    # result.text = "What is ROS 2?"
    # result.detected_language = "en"

    # Generate speech from text
    audio_bytes = await generate_speech(
        text="ROS 2 is a robotics framework...",
        language="en",
        voice="alloy"
    )
"""

import io
from typing import Literal
from dataclasses import dataclass
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Type alias for supported languages
LanguageCode = Literal["en", "ur", "ja"]

# OpenAI Whisper language codes
# Maps our language codes to Whisper's ISO-639-1 codes
WHISPER_LANGUAGE_MAP = {
    "en": "english",
    "ur": "urdu",
    "ja": "japanese",
}

# Reverse mapping for detected language normalization
WHISPER_TO_LANGCODE = {
    "english": "en",
    "urdu": "ur",
    "japanese": "ja",
}

# TTS Voice selection per language
# Using voices that work well for each language
TTS_VOICE_MAP: dict[LanguageCode, str] = {
    "en": "alloy",     # Good for English - neutral, clear
    "ur": "nova",      # Nova works well for RTL languages
    "ja": "shimmer",   # Shimmer has good Japanese pronunciation
}

# Supported audio formats for input
SUPPORTED_AUDIO_FORMATS = {
    "audio/wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/webm",
    "audio/ogg",
    "audio/flac",
    "audio/m4a",
}


@dataclass
class TranscriptionResult:
    """
    Result from speech-to-text transcription.

    Attributes:
        text: Transcribed text from audio
        detected_language: Auto-detected language code (en, ur, ja, or unknown)
        confidence: Detection confidence (high if Whisper detected, low if fallback)
        duration_seconds: Audio duration in seconds (if available)
    """
    text: str
    detected_language: LanguageCode | Literal["unknown"]
    confidence: Literal["high", "low"]
    duration_seconds: float | None = None


@dataclass
class VoiceResponse:
    """
    Complete voice processing result.

    Attributes:
        transcription: Speech-to-text result
        answer_text: RAG-generated answer text
        audio_bytes: TTS audio response (if generated)
        audio_format: Output audio format (mp3)
    """
    transcription: TranscriptionResult
    answer_text: str
    audio_bytes: bytes | None = None
    audio_format: str = "mp3"


async def transcribe_audio(
    audio_data: bytes,
    filename: str = "audio.wav",
    preferred_language: LanguageCode | None = None,
) -> TranscriptionResult:
    """
    Transcribe audio to text using OpenAI Whisper with language detection.

    Whisper automatically detects the spoken language. If a preferred language
    is provided, it's used as a hint but detection still occurs.

    Args:
        audio_data: Raw audio bytes (WAV, MP3, WebM, etc.)
        filename: Filename with extension (used by Whisper for format detection)
        preferred_language: Optional language hint for Whisper

    Returns:
        TranscriptionResult with text and detected language

    Raises:
        ValueError: If audio data is empty or invalid
        Exception: If Whisper API call fails

    Example:
        result = await transcribe_audio(
            audio_data=wav_bytes,
            filename="recording.wav"
        )
        print(f"Transcribed: {result.text}")
        print(f"Language: {result.detected_language}")
    """
    if not audio_data:
        raise ValueError("Audio data cannot be empty")

    logger.info(
        f"Transcribing audio: filename={filename}, "
        f"size={len(audio_data)} bytes, "
        f"preferred_language={preferred_language}"
    )

    async with AsyncOpenAI(api_key=settings.OPENAI_API_KEY) as client:
        # Prepare audio file for Whisper
        audio_file = io.BytesIO(audio_data)
        audio_file.name = filename  # Whisper uses filename extension for format

        # Build transcription request
        # If preferred language is specified, use it as a hint
        language_param = None
        if preferred_language:
            language_param = WHISPER_LANGUAGE_MAP.get(preferred_language)

        try:
            # Use whisper-1 model with verbose response for language detection
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language_param,  # Optional hint
                response_format="verbose_json",  # Get language info
            )

            # Extract transcription text
            text = response.text.strip()

            # Extract detected language from Whisper response
            # Whisper returns language in verbose_json format
            detected_whisper_lang = getattr(response, "language", None)

            # Normalize to our language codes
            if detected_whisper_lang:
                detected_lang = WHISPER_TO_LANGCODE.get(
                    detected_whisper_lang.lower(),
                    "unknown"
                )
                confidence: Literal["high", "low"] = "high"
            else:
                # Fallback: use preferred language or default to English
                detected_lang = preferred_language or "en"
                confidence = "low"

            # Get duration if available
            duration = getattr(response, "duration", None)

            logger.info(
                f"Transcription complete: text_len={len(text)}, "
                f"detected_language={detected_lang}, "
                f"whisper_lang={detected_whisper_lang}, "
                f"confidence={confidence}"
            )

            return TranscriptionResult(
                text=text,
                detected_language=detected_lang,
                confidence=confidence,
                duration_seconds=duration,
            )

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}", exc_info=True)
            raise


async def generate_speech(
    text: str,
    language: LanguageCode = "en",
    voice: str | None = None,
    speed: float = 1.0,
) -> bytes:
    """
    Generate speech audio from text using OpenAI TTS.

    Selects appropriate voice based on language if not specified.

    Args:
        text: Text to convert to speech
        language: Target language for voice selection
        voice: Optional voice override (alloy, echo, fable, onyx, nova, shimmer)
        speed: Speech speed multiplier (0.25 to 4.0, default 1.0)

    Returns:
        MP3 audio bytes

    Raises:
        ValueError: If text is empty or speed is out of range
        Exception: If TTS API call fails

    Example:
        audio = await generate_speech(
            text="ROS 2 is a robotics framework.",
            language="en"
        )
        # Save or stream audio
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if not (0.25 <= speed <= 4.0):
        raise ValueError("Speed must be between 0.25 and 4.0")

    # Select voice based on language if not specified
    selected_voice = voice or TTS_VOICE_MAP.get(language, "alloy")

    logger.info(
        f"Generating speech: text_len={len(text)}, "
        f"language={language}, voice={selected_voice}, speed={speed}"
    )

    async with AsyncOpenAI(api_key=settings.OPENAI_API_KEY) as client:
        try:
            # Use tts-1 model for lower latency (tts-1-hd for higher quality)
            response = await client.audio.speech.create(
                model="tts-1",
                voice=selected_voice,
                input=text,
                speed=speed,
                response_format="mp3",
            )

            # Read audio bytes from response
            audio_bytes = response.content

            logger.info(
                f"TTS complete: audio_size={len(audio_bytes)} bytes, "
                f"format=mp3"
            )

            return audio_bytes

        except Exception as e:
            logger.error(f"TTS generation failed: {e}", exc_info=True)
            raise


async def process_voice_query(
    audio_data: bytes,
    filename: str = "audio.wav",
    preferred_language: LanguageCode | None = None,
    generate_audio_response: bool = True,
) -> tuple[TranscriptionResult, str | None]:
    """
    Process voice input: transcribe audio and detect language.

    This is a convenience function that handles the STT portion of voice chat.
    The RAG processing is done separately to maintain clean separation of concerns.

    Args:
        audio_data: Raw audio bytes
        filename: Audio filename with extension
        preferred_language: Optional language hint
        generate_audio_response: Whether to generate TTS (for return type consistency)

    Returns:
        Tuple of (TranscriptionResult, None)
        - The actual TTS generation happens after RAG processing in the endpoint

    Example:
        transcription, _ = await process_voice_query(audio_bytes)
        # Then pass transcription.text to RAG pipeline
        # Then generate TTS from the answer
    """
    transcription = await transcribe_audio(
        audio_data=audio_data,
        filename=filename,
        preferred_language=preferred_language,
    )

    return transcription, None


def get_audio_content_type(audio_format: str) -> str:
    """
    Get MIME content type for audio format.

    Args:
        audio_format: Audio format (mp3, wav, etc.)

    Returns:
        MIME content type string
    """
    content_types = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "opus": "audio/opus",
        "aac": "audio/aac",
        "flac": "audio/flac",
        "pcm": "audio/pcm",
    }
    return content_types.get(audio_format.lower(), "audio/mpeg")


def validate_audio_file(content_type: str, file_size: int) -> None:
    """
    Validate uploaded audio file.

    Args:
        content_type: MIME type of uploaded file
        file_size: Size of file in bytes

    Raises:
        ValueError: If file is invalid
    """
    # Check content type
    if content_type not in SUPPORTED_AUDIO_FORMATS:
        raise ValueError(
            f"Unsupported audio format: {content_type}. "
            f"Supported: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
        )

    # Check file size (max 25MB for Whisper)
    max_size = 25 * 1024 * 1024  # 25MB
    if file_size > max_size:
        raise ValueError(
            f"Audio file too large: {file_size / (1024*1024):.1f}MB. "
            f"Maximum size: 25MB"
        )

    # Check minimum size (must have some content)
    min_size = 100  # At least 100 bytes
    if file_size < min_size:
        raise ValueError("Audio file is too small or empty")
