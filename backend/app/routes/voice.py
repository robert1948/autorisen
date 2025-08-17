"""
Voice Integration API Routes
Provides REST endpoints for speech-to-text and text-to-speech functionality

Author: CapeAI Development Team
Date: July 25, 2025
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import logging
import asyncio
import io
import base64
import json
from datetime import datetime

from ..services.voice_service import (
    VoiceService, VoiceProvider, AudioFormat, VoiceGender, VoiceProfile,
    SpeechToTextResult, TextToSpeechResult, VoiceAnalytics,
    create_voice_service, get_supported_audio_formats, get_supported_languages
)
from ..middleware.auth import get_current_user
from ..middleware.rate_limiting import RateLimitMiddleware

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/voice", tags=["voice"])

# Voice service instance (will be initialized on startup)
voice_service: Optional[VoiceService] = None

# Request/Response models
class SpeechToTextRequest(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio data")
    audio_format: str = Field(default="wav", description="Audio format")
    language: str = Field(default="en-US", description="Language code")
    provider: Optional[str] = Field(None, description="Preferred provider")
    session_id: Optional[str] = Field(None, description="Session ID for analytics")

class TextToSpeechRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech", max_length=5000)
    voice_profile: Optional[str] = Field(None, description="Voice profile ID")
    audio_format: str = Field(default="mp3", description="Output audio format")
    session_id: Optional[str] = Field(None, description="Session ID for analytics")

class VoiceProfileResponse(BaseModel):
    provider: str
    voice_id: str
    name: str
    gender: str
    language: str
    speed: float
    pitch: float
    volume: float

class SpeechToTextResponse(BaseModel):
    text: str
    confidence: float
    provider: str
    language: str
    duration: float
    processing_time: float
    alternatives: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime

class TextToSpeechResponse(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio data")
    audio_format: str
    provider: str
    voice_profile: str
    text_length: int
    audio_duration: float
    processing_time: float
    file_size: int
    timestamp: datetime

class VoiceAnalyticsResponse(BaseModel):
    session_id: str
    user_id: str
    total_requests: int
    speech_to_text_requests: int
    text_to_speech_requests: int
    total_audio_duration: float
    total_processing_time: float
    average_confidence: float
    preferred_provider: Optional[str]
    preferred_voice: Optional[str]
    language_distribution: Dict[str, int]
    error_count: int
    success_rate: float

class VoiceConfigResponse(BaseModel):
    supported_formats: List[str]
    supported_languages: List[str]
    available_providers: List[str]
    voice_profiles: List[VoiceProfileResponse]

# Dependency to get voice service
async def get_voice_service() -> VoiceService:
    """Get voice service instance"""
    global voice_service
    if voice_service is None:
        # Initialize with configuration
        config = {
            'google_cloud_credentials': None,  # Set from environment
            'openai_api_key': None,  # Set from environment
            'elevenlabs_api_key': None,  # Set from environment
        }
        voice_service = create_voice_service(config)
    return voice_service

@router.on_event("startup")
async def startup_voice_service():
    """Initialize voice service on startup"""
    global voice_service
    try:
        config = {
            # These would be loaded from environment variables
            'google_cloud_credentials': None,
            'openai_api_key': None,
            'elevenlabs_api_key': None,
        }
        voice_service = create_voice_service(config)
        logger.info("Voice service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize voice service: {e}")

@router.get("/config", response_model=VoiceConfigResponse)
async def get_voice_config(
    service: VoiceService = Depends(get_voice_service)
):
    """Get voice service configuration and capabilities"""
    try:
        voice_profiles = await service.get_voice_profiles()
        
        profile_responses = [
            VoiceProfileResponse(
                provider=profile.provider.value,
                voice_id=profile.voice_id,
                name=profile.name,
                gender=profile.gender.value,
                language=profile.language,
                speed=profile.speed,
                pitch=profile.pitch,
                volume=profile.volume
            )
            for profile in voice_profiles
        ]
        
        return VoiceConfigResponse(
            supported_formats=get_supported_audio_formats(),
            supported_languages=get_supported_languages(),
            available_providers=[provider.value for provider in VoiceProvider],
            voice_profiles=profile_responses
        )
        
    except Exception as e:
        logger.error(f"Failed to get voice config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get voice configuration")

@router.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(
    request: SpeechToTextRequest,
    current_user: Dict = Depends(get_current_user),
    service: VoiceService = Depends(get_voice_service)
):
    """Convert speech audio to text"""
    try:
        # Decode audio data
        try:
            audio_data = base64.b64decode(request.audio_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid base64 audio data")
        
        # Validate audio format
        try:
            audio_format = AudioFormat(request.audio_format.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail="Unsupported audio format")
        
        # Parse provider if specified
        provider = None
        if request.provider:
            try:
                provider = VoiceProvider(request.provider.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail="Unsupported provider")
        
        # Perform speech-to-text
        result = await service.speech_to_text(
            audio_data=audio_data,
            audio_format=audio_format,
            language=request.language,
            provider=provider,
            session_id=request.session_id,
            user_id=current_user.get('user_id')
        )
        
        return SpeechToTextResponse(
            text=result.text,
            confidence=result.confidence,
            provider=result.provider.value,
            language=result.language,
            duration=result.duration,
            processing_time=result.processing_time,
            alternatives=result.alternatives,
            timestamp=result.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        raise HTTPException(status_code=500, detail="Speech recognition failed")

@router.post("/text-to-speech", response_model=TextToSpeechResponse)
async def text_to_speech(
    request: TextToSpeechRequest,
    current_user: Dict = Depends(get_current_user),
    service: VoiceService = Depends(get_voice_service)
):
    """Convert text to speech audio"""
    try:
        # Validate text length
        if len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Validate audio format
        try:
            audio_format = AudioFormat(request.audio_format.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail="Unsupported audio format")
        
        # Perform text-to-speech
        result = await service.text_to_speech(
            text=request.text,
            voice_profile=request.voice_profile,
            audio_format=audio_format,
            session_id=request.session_id,
            user_id=current_user.get('user_id')
        )
        
        # Encode audio data
        audio_data_b64 = base64.b64encode(result.audio_data).decode('utf-8')
        
        return TextToSpeechResponse(
            audio_data=audio_data_b64,
            audio_format=result.audio_format.value,
            provider=result.provider.value,
            voice_profile=result.voice_profile.voice_id,
            text_length=result.text_length,
            audio_duration=result.audio_duration,
            processing_time=result.processing_time,
            file_size=result.file_size,
            timestamp=result.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}")
        raise HTTPException(status_code=500, detail="Speech synthesis failed")

@router.post("/speech-to-text/upload")
async def speech_to_text_upload(
    audio_file: UploadFile = File(...),
    language: str = Form(default="en-US"),
    provider: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    current_user: Dict = Depends(get_current_user),
    service: VoiceService = Depends(get_voice_service)
):
    """Convert uploaded audio file to text"""
    try:
        # Validate file size (max 25MB)
        if audio_file.size and audio_file.size > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 25MB)")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Determine audio format from filename
        filename = audio_file.filename or ""
        file_ext = filename.split('.')[-1].lower() if '.' in filename else 'wav'
        
        try:
            audio_format = AudioFormat(file_ext)
        except ValueError:
            audio_format = AudioFormat.WAV  # Default fallback
        
        # Parse provider if specified
        provider_enum = None
        if provider:
            try:
                provider_enum = VoiceProvider(provider.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail="Unsupported provider")
        
        # Perform speech-to-text
        result = await service.speech_to_text(
            audio_data=audio_data,
            audio_format=audio_format,
            language=language,
            provider=provider_enum,
            session_id=session_id,
            user_id=current_user.get('user_id')
        )
        
        return SpeechToTextResponse(
            text=result.text,
            confidence=result.confidence,
            provider=result.provider.value,
            language=result.language,
            duration=result.duration,
            processing_time=result.processing_time,
            alternatives=result.alternatives,
            timestamp=result.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload speech-to-text error: {e}")
        raise HTTPException(status_code=500, detail="Audio file processing failed")

@router.post("/text-to-speech/stream")
async def text_to_speech_stream(
    request: TextToSpeechRequest,
    current_user: Dict = Depends(get_current_user),
    service: VoiceService = Depends(get_voice_service)
):
    """Convert text to speech and stream audio response"""
    try:
        # Validate audio format
        try:
            audio_format = AudioFormat(request.audio_format.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail="Unsupported audio format")
        
        # Perform text-to-speech
        result = await service.text_to_speech(
            text=request.text,
            voice_profile=request.voice_profile,
            audio_format=audio_format,
            session_id=request.session_id,
            user_id=current_user.get('user_id')
        )
        
        # Determine content type
        content_type_map = {
            AudioFormat.WAV: "audio/wav",
            AudioFormat.MP3: "audio/mpeg",
            AudioFormat.OGG: "audio/ogg",
            AudioFormat.WEBM: "audio/webm"
        }
        content_type = content_type_map.get(audio_format, "audio/wav")
        
        # Create streaming response
        def generate_audio():
            yield result.audio_data
        
        return StreamingResponse(
            io.BytesIO(result.audio_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=speech.{audio_format.value}",
                "Content-Length": str(len(result.audio_data)),
                "X-Processing-Time": str(result.processing_time),
                "X-Audio-Duration": str(result.audio_duration),
                "X-Provider": result.provider.value
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Streaming TTS error: {e}")
        raise HTTPException(status_code=500, detail="Speech synthesis streaming failed")

@router.get("/profiles", response_model=List[VoiceProfileResponse])
async def get_voice_profiles(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    service: VoiceService = Depends(get_voice_service)
):
    """Get available voice profiles"""
    try:
        provider_enum = None
        if provider:
            try:
                provider_enum = VoiceProvider(provider.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid provider")
        
        profiles = await service.get_voice_profiles(provider_enum)
        
        return [
            VoiceProfileResponse(
                provider=profile.provider.value,
                voice_id=profile.voice_id,
                name=profile.name,
                gender=profile.gender.value,
                language=profile.language,
                speed=profile.speed,
                pitch=profile.pitch,
                volume=profile.volume
            )
            for profile in profiles
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get voice profiles error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get voice profiles")

@router.get("/analytics", response_model=Union[VoiceAnalyticsResponse, Dict[str, VoiceAnalyticsResponse]])
async def get_voice_analytics(
    session_id: Optional[str] = Query(None, description="Specific session ID"),
    current_user: Dict = Depends(get_current_user),
    service: VoiceService = Depends(get_voice_service)
):
    """Get voice interaction analytics"""
    try:
        analytics = await service.get_analytics(session_id)
        
        if session_id:
            if not analytics:
                raise HTTPException(status_code=404, detail="Session not found")
            
            return VoiceAnalyticsResponse(
                session_id=analytics.session_id,
                user_id=analytics.user_id,
                total_requests=analytics.total_requests,
                speech_to_text_requests=analytics.speech_to_text_requests,
                text_to_speech_requests=analytics.text_to_speech_requests,
                total_audio_duration=analytics.total_audio_duration,
                total_processing_time=analytics.total_processing_time,
                average_confidence=analytics.average_confidence,
                preferred_provider=analytics.preferred_provider.value if analytics.preferred_provider else None,
                preferred_voice=analytics.preferred_voice,
                language_distribution=analytics.language_distribution,
                error_count=analytics.error_count,
                success_rate=analytics.success_rate
            )
        else:
            # Return all analytics
            return {
                sid: VoiceAnalyticsResponse(
                    session_id=data.session_id,
                    user_id=data.user_id,
                    total_requests=data.total_requests,
                    speech_to_text_requests=data.speech_to_text_requests,
                    text_to_speech_requests=data.text_to_speech_requests,
                    total_audio_duration=data.total_audio_duration,
                    total_processing_time=data.total_processing_time,
                    average_confidence=data.average_confidence,
                    preferred_provider=data.preferred_provider.value if data.preferred_provider else None,
                    preferred_voice=data.preferred_voice,
                    language_distribution=data.language_distribution,
                    error_count=data.error_count,
                    success_rate=data.success_rate
                )
                for sid, data in analytics.items()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    current_user: Dict = Depends(get_current_user),
    service: VoiceService = Depends(get_voice_service)
):
    """Get voice service performance metrics"""
    try:
        metrics = await service.get_performance_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Get performance metrics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

@router.post("/cache/clear")
async def clear_voice_cache(
    current_user: Dict = Depends(get_current_user),
    service: VoiceService = Depends(get_voice_service)
):
    """Clear voice service caches"""
    try:
        # Check if user has admin privileges
        if not current_user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        await service.clear_cache()
        return {"message": "Voice service caches cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@router.get("/health")
async def voice_health_check(
    service: VoiceService = Depends(get_voice_service)
):
    """Check voice service health"""
    try:
        health = await service.health_check()
        return health
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.post("/test/echo")
async def voice_echo_test(
    request: SpeechToTextRequest,
    current_user: Dict = Depends(get_current_user),
    service: VoiceService = Depends(get_voice_service)
):
    """Test voice system with speech-to-text followed by text-to-speech"""
    try:
        # Decode audio data
        try:
            audio_data = base64.b64decode(request.audio_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid base64 audio data")
        
        # Speech-to-text
        audio_format = AudioFormat(request.audio_format.lower())
        stt_result = await service.speech_to_text(
            audio_data=audio_data,
            audio_format=audio_format,
            language=request.language,
            session_id=request.session_id,
            user_id=current_user.get('user_id')
        )
        
        # Text-to-speech (echo back)
        tts_result = await service.text_to_speech(
            text=f"You said: {stt_result.text}",
            session_id=request.session_id,
            user_id=current_user.get('user_id')
        )
        
        # Encode audio response
        audio_data_b64 = base64.b64encode(tts_result.audio_data).decode('utf-8')
        
        return {
            "original_text": stt_result.text,
            "confidence": stt_result.confidence,
            "echo_audio": audio_data_b64,
            "stt_processing_time": stt_result.processing_time,
            "tts_processing_time": tts_result.processing_time,
            "total_processing_time": stt_result.processing_time + tts_result.processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice echo test error: {e}")
        raise HTTPException(status_code=500, detail="Voice echo test failed")

# WebSocket endpoint for real-time voice interaction
from fastapi import WebSocket
import websockets

@router.websocket("/ws/realtime")
async def voice_websocket(
    websocket: WebSocket,
    service: VoiceService = Depends(get_voice_service)
):
    """WebSocket endpoint for real-time voice interaction"""
    await websocket.accept()
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            # Process audio in real-time
            try:
                # Assume WAV format for simplicity
                stt_result = await service.speech_to_text(
                    audio_data=data,
                    audio_format=AudioFormat.WAV,
                    language="en-US"
                )
                
                # Send text result
                await websocket.send_json({
                    "type": "transcription",
                    "text": stt_result.text,
                    "confidence": stt_result.confidence,
                    "processing_time": stt_result.processing_time
                })
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Voice WebSocket connection closed")
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
        await websocket.close()
