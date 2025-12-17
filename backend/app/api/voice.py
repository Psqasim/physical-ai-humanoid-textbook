"""
Voice API endpoints for multilingual speech-based Q&A.

Endpoints:
- POST /api/voice/chat: Voice-to-text, RAG processing, and optional TTS response
- GET /api/voice/audio/{audio_id}: Retrieve generated TTS audio

Flow:
1. User uploads audio → Whisper STT with language detection
2. Transcribed text → RAG pipeline (answer_chat_request)
3. Answer text → Optional TTS generation
4. Return transcription + answer + audio ID (if TTS enabled)
"""

import uuid
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.schemas import (
    ChatRequest,
    VoiceChatResponse,
    VoiceTranscription,
)
from app.services.rag import answer_chat_request
from app.services.voice import (
    transcribe_audio,
    generate_speech,
    validate_audio_file,
    SUPPORTED_AUDIO_FORMATS,
)

logger = get_logger(__name__)
router = APIRouter()

# In-memory cache for TTS audio (simple implementation)
# For production, use Redis or file storage
_audio_cache: dict[str, tuple[bytes, str]] = {}  # audio_id -> (audio_bytes, language)
MAX_CACHE_SIZE = 100  # Maximum cached audio responses


def _cache_audio(audio_bytes: bytes, language: str) -> str:
    """
    Cache audio bytes and return a unique ID.

    Args:
        audio_bytes: MP3 audio data
        language: Language of the audio

    Returns:
        Unique audio ID for retrieval
    """
    global _audio_cache

    # Cleanup old entries if cache is full
    if len(_audio_cache) >= MAX_CACHE_SIZE:
        # Remove oldest entries (first 20%)
        keys_to_remove = list(_audio_cache.keys())[: MAX_CACHE_SIZE // 5]
        for key in keys_to_remove:
            del _audio_cache[key]

    # Generate unique ID
    audio_id = str(uuid.uuid4())[:8]
    _audio_cache[audio_id] = (audio_bytes, language)

    return audio_id


def _get_cached_audio(audio_id: str) -> tuple[bytes, str] | None:
    """
    Retrieve cached audio by ID.

    Args:
        audio_id: Audio ID from previous response

    Returns:
        Tuple of (audio_bytes, language) or None if not found
    """
    return _audio_cache.get(audio_id)


@router.post(
    "/voice/chat",
    response_model=VoiceChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Voice-based Q&A with automatic language detection",
    description="""
    Process voice input through the RAG pipeline:

    1. **Speech-to-Text**: Audio is transcribed using OpenAI Whisper
    2. **Language Detection**: Spoken language is auto-detected (en, ur, ja)
    3. **RAG Processing**: Transcribed question goes through the RAG pipeline
    4. **TTS Response** (optional): Answer is converted to speech

    Supported audio formats: WAV, MP3, WebM, OGG, FLAC, M4A
    Maximum file size: 25MB

    The detected language from audio is used for:
    - Filtering RAG retrieval to same-language chunks
    - Generating response in the detected language
    - TTS voice selection
    """,
    responses={
        200: {
            "description": "Successful voice processing",
            "content": {
                "application/json": {
                    "example": {
                        "transcription": {
                            "text": "What is ROS 2?",
                            "detectedLanguage": "en",
                            "confidence": "high",
                            "durationSeconds": 2.5,
                        },
                        "answer": "ROS 2 is a flexible robotics framework...",
                        "citations": [],
                        "mode": "whole-book",
                        "confidence": "high",
                        "responseLanguage": "en",
                        "hasAudio": True,
                        "audioId": "abc123",
                    }
                }
            },
        },
        400: {
            "description": "Invalid audio file or request",
            "content": {
                "application/json": {
                    "example": {"detail": "Unsupported audio format: image/png"}
                }
            },
        },
        503: {
            "description": "Service unavailable (OpenAI API failure)",
        },
    },
)
async def voice_chat_endpoint(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, WebM, etc.)"),
    generate_audio: bool = Form(
        default=True,
        description="Whether to generate TTS audio response",
    ),
    preferred_language: Literal["en", "ur", "ja"] | None = Form(
        default=None,
        description="Optional language hint (overrides auto-detection)",
    ),
    user_id: str | None = Form(
        default=None,
        description="Optional user ID for session tracking",
    ),
    db: AsyncSession = Depends(get_db),
) -> VoiceChatResponse:
    """
    Process voice input and return transcription + RAG answer.

    Flow:
    1. Validate and read audio file
    2. Transcribe with Whisper (auto language detection)
    3. Process through RAG pipeline
    4. Optionally generate TTS audio
    5. Return combined response

    Args:
        audio: Uploaded audio file
        generate_audio: Whether to create TTS response
        preferred_language: Language hint (optional)
        user_id: User identifier (optional)
        db: Database session

    Returns:
        VoiceChatResponse with transcription, answer, and optional audio ID
    """
    logger.info(
        f"POST /api/voice/chat: "
        f"filename={audio.filename}, "
        f"content_type={audio.content_type}, "
        f"generate_audio={generate_audio}, "
        f"preferred_language={preferred_language}"
    )

    # 1. Validate audio file
    try:
        # Read file content
        audio_data = await audio.read()
        file_size = len(audio_data)

        # Validate format and size
        content_type = audio.content_type or "audio/wav"
        validate_audio_file(content_type, file_size)

        logger.info(f"Audio file validated: {file_size} bytes, {content_type}")

    except ValueError as e:
        logger.warning(f"Invalid audio file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # 2. Transcribe audio with Whisper
    try:
        transcription = await transcribe_audio(
            audio_data=audio_data,
            filename=audio.filename or "audio.wav",
            preferred_language=preferred_language,
        )

        logger.info(
            f"Transcription complete: "
            f"text_len={len(transcription.text)}, "
            f"detected_lang={transcription.detected_language}, "
            f"confidence={transcription.confidence}"
        )

    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech recognition service is temporarily unavailable. Please try again.",
        )

    # Validate transcription has content
    if not transcription.text or len(transcription.text.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not transcribe audio. Please speak clearly and try again.",
        )

    # 3. Determine language for RAG processing
    # Use detected language from audio, or fallback to preferred/English
    response_language = transcription.detected_language
    if response_language == "unknown":
        response_language = preferred_language or "en"

    # 4. Process through RAG pipeline
    try:
        # Create ChatRequest from transcription
        chat_request = ChatRequest(
            mode="whole-book",  # Voice always uses whole-book mode
            question=transcription.text,
            preferredLanguage=response_language,
            userId=user_id,
        )

        # Process through existing RAG pipeline
        chat_response = await answer_chat_request(
            request=chat_request,
            db=db,
            settings_override=None,
        )

        logger.info(
            f"RAG processing complete: "
            f"answer_len={len(chat_response.answer)}, "
            f"citations={len(chat_response.citations)}, "
            f"confidence={chat_response.confidence}"
        )

    except ValueError as e:
        logger.warning(f"RAG validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"RAG processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Q&A service is temporarily unavailable. Please try again.",
        )

    # 5. Generate TTS audio (if requested)
    audio_id = None
    has_audio = False

    if generate_audio:
        try:
            # Generate speech from answer
            # Strip the sources section for cleaner TTS
            answer_for_tts = chat_response.answer
            if "\n\n📚" in answer_for_tts:
                answer_for_tts = answer_for_tts.split("\n\n📚")[0]

            audio_bytes = await generate_speech(
                text=answer_for_tts,
                language=response_language,
            )

            # Cache audio for retrieval
            audio_id = _cache_audio(audio_bytes, response_language)
            has_audio = True

            logger.info(
                f"TTS generated: audio_id={audio_id}, "
                f"size={len(audio_bytes)} bytes"
            )

        except Exception as e:
            # TTS failure should not fail the request
            logger.error(f"TTS generation failed (non-fatal): {e}", exc_info=True)
            has_audio = False

    # 6. Build response
    voice_transcription = VoiceTranscription(
        text=transcription.text,
        detectedLanguage=transcription.detected_language,
        confidence=transcription.confidence,
        durationSeconds=transcription.duration_seconds,
    )

    response = VoiceChatResponse(
        transcription=voice_transcription,
        answer=chat_response.answer,
        citations=chat_response.citations,
        mode=chat_response.mode,
        confidence=chat_response.confidence,
        responseLanguage=chat_response.responseLanguage,
        fallbackApplied=chat_response.fallbackApplied,
        hasAudio=has_audio,
        audioId=audio_id,
    )

    logger.info(
        f"Voice chat complete: "
        f"transcription_lang={transcription.detected_language}, "
        f"response_lang={response_language}, "
        f"has_audio={has_audio}"
    )

    return response


@router.get(
    "/voice/audio/{audio_id}",
    summary="Retrieve generated TTS audio",
    description="""
    Download the TTS audio response generated by a previous /voice/chat request.

    Audio is returned as MP3 format with appropriate Content-Type header.
    Audio IDs expire after a short time (server cache limit).
    """,
    responses={
        200: {
            "description": "MP3 audio file",
            "content": {"audio/mpeg": {}},
        },
        404: {
            "description": "Audio not found or expired",
            "content": {
                "application/json": {
                    "example": {"detail": "Audio not found or expired"}
                }
            },
        },
    },
)
async def get_voice_audio(audio_id: str) -> Response:
    """
    Retrieve cached TTS audio by ID.

    Args:
        audio_id: Audio ID from VoiceChatResponse.audioId

    Returns:
        MP3 audio response

    Raises:
        HTTPException 404: If audio not found or expired
    """
    logger.info(f"GET /api/voice/audio/{audio_id}")

    cached = _get_cached_audio(audio_id)
    if not cached:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio not found or expired. Please make a new voice request.",
        )

    audio_bytes, language = cached

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f'attachment; filename="response_{audio_id}.mp3"',
            "X-Audio-Language": language,
            "Cache-Control": "private, max-age=300",  # 5 min cache
        },
    )


@router.get(
    "/voice/formats",
    summary="List supported audio formats",
    description="Returns list of supported audio MIME types for upload.",
)
async def list_supported_formats() -> dict:
    """
    List supported audio formats for voice input.

    Returns:
        Dict with supported formats and limits
    """
    return {
        "supported_formats": list(SUPPORTED_AUDIO_FORMATS),
        "max_size_mb": 25,
        "supported_languages": ["en", "ur", "ja"],
        "tts_output_format": "mp3",
    }
