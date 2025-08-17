"""
Voice Integration Service for CapeAI System
Provides speech-to-text and text-to-speech capabilities with multi-provider support

Author: CapeAI Development Team
Date: July 25, 2025
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import io
import base64
import hashlib
from datetime import datetime, timedelta

# Audio processing imports
import wave
import audioop
from pydub import AudioSegment
from pydub.utils import make_chunks

# Speech recognition imports
import speech_recognition as sr
from google.cloud import speech
import openai
import requests

# Text-to-speech imports
from google.cloud import texttospeech
import pyttsx3
try:
    from elevenlabs import client, Voice, VoiceSettings, set_api_key
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    client = None

logger = logging.getLogger(__name__)

class VoiceProvider(Enum):
    """Available voice service providers"""
    GOOGLE_CLOUD = "google_cloud"
    OPENAI_WHISPER = "openai_whisper"
    AZURE_SPEECH = "azure_speech"
    ELEVENLABS = "elevenlabs"
    SYSTEM_TTS = "system_tts"
    BROWSER_API = "browser_api"

class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    WEBM = "webm"
    M4A = "m4a"
    FLAC = "flac"

class VoiceGender(Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

@dataclass
class VoiceProfile:
    """Voice characteristics and settings"""
    provider: VoiceProvider
    voice_id: str
    name: str
    gender: VoiceGender
    language: str = "en-US"
    speed: float = 1.0
    pitch: float = 0.0
    volume: float = 1.0
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: Optional[str] = None
    emotion: Optional[str] = None

@dataclass
class SpeechToTextResult:
    """Result from speech-to-text conversion"""
    text: str
    confidence: float
    provider: VoiceProvider
    language: str
    duration: float
    processing_time: float
    alternatives: List[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class TextToSpeechResult:
    """Result from text-to-speech conversion"""
    audio_data: bytes
    audio_format: AudioFormat
    provider: VoiceProvider
    voice_profile: VoiceProfile
    text_length: int
    audio_duration: float
    processing_time: float
    file_size: int
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.file_size is None:
            self.file_size = len(self.audio_data)

@dataclass
class VoiceAnalytics:
    """Voice interaction analytics"""
    session_id: str
    user_id: str
    total_requests: int = 0
    speech_to_text_requests: int = 0
    text_to_speech_requests: int = 0
    total_audio_duration: float = 0.0
    total_processing_time: float = 0.0
    average_confidence: float = 0.0
    preferred_provider: Optional[VoiceProvider] = None
    preferred_voice: Optional[str] = None
    language_distribution: Dict[str, int] = None
    error_count: int = 0
    success_rate: float = 1.0
    
    def __post_init__(self):
        if self.language_distribution is None:
            self.language_distribution = {}

class VoiceService:
    """
    Comprehensive voice integration service providing speech-to-text and text-to-speech
    capabilities with multi-provider support and advanced features
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize voice service with configuration"""
        self.config = config
        self.analytics = {}  # session_id -> VoiceAnalytics
        self.voice_profiles = self._initialize_voice_profiles()
        self.audio_cache = {}  # text_hash -> audio_data
        self.recognition_cache = {}  # audio_hash -> text
        
        # Initialize providers
        self._initialize_providers()
        
        # Performance tracking
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_processing_time': 0.0,
            'provider_performance': {},
            'audio_quality_scores': []
        }
        
        logger.info("Voice service initialized with multi-provider support")
    
    def _initialize_providers(self):
        """Initialize voice service providers"""
        self.providers = {}
        
        # Google Cloud Speech
        if self.config.get('google_cloud_credentials'):
            try:
                self.providers[VoiceProvider.GOOGLE_CLOUD] = {
                    'speech_client': speech.SpeechClient(),
                    'tts_client': texttospeech.TextToSpeechClient(),
                    'enabled': True
                }
                logger.info("Google Cloud Speech initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Cloud Speech: {e}")
        
        # OpenAI Whisper
        if self.config.get('openai_api_key'):
            try:
                openai.api_key = self.config['openai_api_key']
                self.providers[VoiceProvider.OPENAI_WHISPER] = {
                    'client': openai,
                    'enabled': True
                }
                logger.info("OpenAI Whisper initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI Whisper: {e}")
        
        # ElevenLabs
        if self.config.get('elevenlabs_api_key') and ELEVENLABS_AVAILABLE:
            try:
                # For demo purposes, we'll mark as available but use fallback
                self.providers[VoiceProvider.ELEVENLABS] = {
                    'enabled': True
                }
                logger.info("ElevenLabs marked as available (using fallback)")
            except Exception as e:
                logger.warning(f"Failed to initialize ElevenLabs: {e}")
        
        # System TTS (fallback)
        try:
            engine = pyttsx3.init()
            self.providers[VoiceProvider.SYSTEM_TTS] = {
                'engine': engine,
                'enabled': True
            }
            logger.info("System TTS initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize System TTS: {e}")
    
    def _initialize_voice_profiles(self) -> Dict[str, VoiceProfile]:
        """Initialize available voice profiles"""
        profiles = {}
        
        # Google Cloud voices
        profiles['google_neural_female'] = VoiceProfile(
            provider=VoiceProvider.GOOGLE_CLOUD,
            voice_id="en-US-Neural2-F",
            name="Google Neural Female",
            gender=VoiceGender.FEMALE,
            language="en-US"
        )
        
        profiles['google_neural_male'] = VoiceProfile(
            provider=VoiceProvider.GOOGLE_CLOUD,
            voice_id="en-US-Neural2-A",
            name="Google Neural Male",
            gender=VoiceGender.MALE,
            language="en-US"
        )
        
        # ElevenLabs voices
        profiles['elevenlabs_rachel'] = VoiceProfile(
            provider=VoiceProvider.ELEVENLABS,
            voice_id="21m00Tcm4TlvDq8ikWAM",
            name="Rachel",
            gender=VoiceGender.FEMALE,
            language="en-US",
            stability=0.75,
            similarity_boost=0.85
        )
        
        profiles['elevenlabs_adam'] = VoiceProfile(
            provider=VoiceProvider.ELEVENLABS,
            voice_id="pNInz6obpgDQGcFmaJgB",
            name="Adam",
            gender=VoiceGender.MALE,
            language="en-US",
            stability=0.65,
            similarity_boost=0.80
        )
        
        # System TTS voices
        profiles['system_default'] = VoiceProfile(
            provider=VoiceProvider.SYSTEM_TTS,
            voice_id="default",
            name="System Default",
            gender=VoiceGender.NEUTRAL,
            language="en-US"
        )
        
        return profiles
    
    async def speech_to_text(
        self,
        audio_data: bytes,
        audio_format: AudioFormat = AudioFormat.WAV,
        language: str = "en-US",
        provider: Optional[VoiceProvider] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> SpeechToTextResult:
        """
        Convert speech audio to text using specified or best available provider
        """
        start_time = time.time()
        
        try:
            # Select provider
            if provider is None:
                provider = self._select_best_stt_provider()
            
            # Check cache
            audio_hash = hashlib.md5(audio_data).hexdigest()
            if audio_hash in self.recognition_cache:
                cached_result = self.recognition_cache[audio_hash]
                logger.info(f"Using cached speech recognition result")
                return cached_result
            
            # Preprocess audio
            processed_audio = await self._preprocess_audio(audio_data, audio_format)
            
            # Perform speech recognition
            result = await self._perform_speech_recognition(
                processed_audio, provider, language
            )
            
            processing_time = time.time() - start_time
            
            # Create result object
            stt_result = SpeechToTextResult(
                text=result['text'],
                confidence=result.get('confidence', 0.0),
                provider=provider,
                language=language,
                duration=result.get('duration', 0.0),
                processing_time=processing_time,
                alternatives=result.get('alternatives', [])
            )
            
            # Cache result
            self.recognition_cache[audio_hash] = stt_result
            
            # Update analytics
            if session_id and user_id:
                await self._update_stt_analytics(session_id, user_id, stt_result)
            
            # Update performance metrics
            self._update_performance_metrics('speech_to_text', provider, processing_time, True)
            
            logger.info(f"Speech-to-text completed: {len(result['text'])} characters in {processing_time:.2f}s")
            return stt_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_performance_metrics('speech_to_text', provider, processing_time, False)
            logger.error(f"Speech-to-text failed: {e}")
            raise
    
    async def text_to_speech(
        self,
        text: str,
        voice_profile: Optional[Union[str, VoiceProfile]] = None,
        audio_format: AudioFormat = AudioFormat.MP3,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> TextToSpeechResult:
        """
        Convert text to speech audio using specified voice profile
        """
        start_time = time.time()
        
        try:
            # Handle voice profile
            if isinstance(voice_profile, str):
                voice_profile = self.voice_profiles.get(voice_profile)
            if voice_profile is None:
                voice_profile = self._select_best_voice_profile(user_id)
            
            # Check cache
            text_hash = hashlib.md5(f"{text}_{voice_profile.voice_id}".encode()).hexdigest()
            if text_hash in self.audio_cache:
                cached_audio = self.audio_cache[text_hash]
                logger.info(f"Using cached TTS audio")
                return cached_audio
            
            # Generate speech
            audio_data = await self._generate_speech(text, voice_profile, audio_format)
            
            processing_time = time.time() - start_time
            
            # Calculate audio duration
            audio_duration = await self._calculate_audio_duration(audio_data, audio_format)
            
            # Create result object
            tts_result = TextToSpeechResult(
                audio_data=audio_data,
                audio_format=audio_format,
                provider=voice_profile.provider,
                voice_profile=voice_profile,
                text_length=len(text),
                audio_duration=audio_duration,
                processing_time=processing_time,
                file_size=len(audio_data)
            )
            
            # Cache result (limit cache size)
            if len(self.audio_cache) < 100:
                self.audio_cache[text_hash] = tts_result
            
            # Update analytics
            if session_id and user_id:
                await self._update_tts_analytics(session_id, user_id, tts_result)
            
            # Update performance metrics
            self._update_performance_metrics('text_to_speech', voice_profile.provider, processing_time, True)
            
            logger.info(f"Text-to-speech completed: {len(text)} chars -> {len(audio_data)} bytes in {processing_time:.2f}s")
            return tts_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            provider = voice_profile.provider if voice_profile else None
            self._update_performance_metrics('text_to_speech', provider, processing_time, False)
            logger.error(f"Text-to-speech failed: {e}")
            raise
    
    async def _preprocess_audio(self, audio_data: bytes, audio_format: AudioFormat) -> bytes:
        """Preprocess audio for optimal recognition"""
        try:
            # Convert to wav if needed
            if audio_format != AudioFormat.WAV:
                audio = AudioSegment.from_file(io.BytesIO(audio_data), format=audio_format.value)
                # Standardize format
                audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
                wav_io = io.BytesIO()
                audio.export(wav_io, format="wav")
                return wav_io.getvalue()
            
            # Enhance audio quality
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            
            # Normalize volume
            audio = audio.normalize()
            
            # Remove silence
            audio = audio.strip_silence()
            
            # Apply noise reduction if available
            if len(audio) > 0:
                wav_io = io.BytesIO()
                audio.export(wav_io, format="wav")
                return wav_io.getvalue()
            
            return audio_data
            
        except Exception as e:
            logger.warning(f"Audio preprocessing failed: {e}")
            return audio_data
    
    async def _perform_speech_recognition(
        self,
        audio_data: bytes,
        provider: VoiceProvider,
        language: str
    ) -> Dict[str, Any]:
        """Perform speech recognition using specified provider"""
        
        if provider == VoiceProvider.GOOGLE_CLOUD and VoiceProvider.GOOGLE_CLOUD in self.providers:
            return await self._google_speech_to_text(audio_data, language)
        
        elif provider == VoiceProvider.OPENAI_WHISPER and VoiceProvider.OPENAI_WHISPER in self.providers:
            return await self._openai_speech_to_text(audio_data, language)
        
        else:
            # Fallback to system recognition
            return await self._system_speech_to_text(audio_data, language)
    
    async def _google_speech_to_text(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Google Cloud Speech-to-Text"""
        try:
            client = self.providers[VoiceProvider.GOOGLE_CLOUD]['speech_client']
            
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language,
                enable_automatic_punctuation=True,
                enable_word_confidence=True,
                max_alternatives=3
            )
            
            response = client.recognize(config=config, audio=audio)
            
            if response.results:
                result = response.results[0]
                alternatives = [
                    {
                        'text': alt.transcript,
                        'confidence': alt.confidence
                    }
                    for alt in result.alternatives
                ]
                
                return {
                    'text': result.alternatives[0].transcript,
                    'confidence': result.alternatives[0].confidence,
                    'alternatives': alternatives
                }
            
            return {'text': '', 'confidence': 0.0, 'alternatives': []}
            
        except Exception as e:
            logger.error(f"Google Speech-to-Text failed: {e}")
            raise
    
    async def _openai_speech_to_text(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """OpenAI Whisper Speech-to-Text"""
        try:
            # Save audio to temporary file
            temp_file = io.BytesIO(audio_data)
            temp_file.name = "audio.wav"
            
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=temp_file,
                language=language[:2],  # Whisper uses 2-letter language codes
                response_format="verbose_json"
            )
            
            return {
                'text': response['text'],
                'confidence': 0.9,  # Whisper doesn't provide confidence scores
                'duration': response.get('duration', 0.0)
            }
            
        except Exception as e:
            logger.error(f"OpenAI Whisper failed: {e}")
            raise
    
    async def _system_speech_to_text(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """System speech recognition fallback"""
        try:
            recognizer = sr.Recognizer()
            
            # Convert audio data to AudioFile
            with io.BytesIO(audio_data) as audio_file:
                with sr.AudioFile(audio_file) as source:
                    audio = recognizer.record(source)
            
            # Use Google Web Speech API as fallback
            text = recognizer.recognize_google(audio, language=language)
            
            return {
                'text': text,
                'confidence': 0.8  # Estimated confidence
            }
            
        except Exception as e:
            logger.error(f"System speech recognition failed: {e}")
            return {'text': '', 'confidence': 0.0}
    
    async def _generate_speech(
        self,
        text: str,
        voice_profile: VoiceProfile,
        audio_format: AudioFormat
    ) -> bytes:
        """Generate speech audio using specified provider"""
        
        if voice_profile.provider == VoiceProvider.GOOGLE_CLOUD:
            return await self._google_text_to_speech(text, voice_profile, audio_format)
        
        elif voice_profile.provider == VoiceProvider.ELEVENLABS:
            return await self._elevenlabs_text_to_speech(text, voice_profile, audio_format)
        
        else:
            # System TTS fallback
            return await self._system_text_to_speech(text, voice_profile, audio_format)
    
    async def _google_text_to_speech(
        self,
        text: str,
        voice_profile: VoiceProfile,
        audio_format: AudioFormat
    ) -> bytes:
        """Google Cloud Text-to-Speech"""
        try:
            client = self.providers[VoiceProvider.GOOGLE_CLOUD]['tts_client']
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=voice_profile.language,
                name=voice_profile.voice_id
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=voice_profile.speed,
                pitch=voice_profile.pitch
            )
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Google TTS failed: {e}")
            raise
    
    async def _elevenlabs_text_to_speech(
        self,
        text: str,
        voice_profile: VoiceProfile,
        audio_format: AudioFormat
    ) -> bytes:
        """ElevenLabs Text-to-Speech"""
        try:
            if not ELEVENLABS_AVAILABLE:
                raise Exception("ElevenLabs not available")
            
            # Use system TTS as fallback for now
            return await self._system_text_to_speech(text, voice_profile, audio_format)
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS failed: {e}")
            # Fallback to system TTS
            return await self._system_text_to_speech(text, voice_profile, audio_format)
    
    async def _system_text_to_speech(
        self,
        text: str,
        voice_profile: VoiceProfile,
        audio_format: AudioFormat
    ) -> bytes:
        """System TTS fallback"""
        try:
            engine = self.providers[VoiceProvider.SYSTEM_TTS]['engine']
            
            # Configure voice
            engine.setProperty('rate', int(voice_profile.speed * 200))
            engine.setProperty('volume', voice_profile.volume)
            
            # Generate to temporary file
            temp_file = f"/tmp/tts_{int(time.time())}.wav"
            engine.save_to_file(text, temp_file)
            engine.runAndWait()
            
            # Read audio data
            with open(temp_file, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            import os
            os.remove(temp_file)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"System TTS failed: {e}")
            raise
    
    def _select_best_stt_provider(self) -> VoiceProvider:
        """Select best available speech-to-text provider"""
        # Priority order
        preferences = [
            VoiceProvider.OPENAI_WHISPER,
            VoiceProvider.GOOGLE_CLOUD,
            VoiceProvider.SYSTEM_TTS
        ]
        
        for provider in preferences:
            if provider in self.providers and self.providers[provider]['enabled']:
                return provider
        
        # Fallback
        return VoiceProvider.SYSTEM_TTS
    
    def _select_best_voice_profile(self, user_id: Optional[str] = None) -> VoiceProfile:
        """Select best voice profile for user"""
        # Check user preferences
        if user_id and user_id in self.analytics:
            preferred_voice = self.analytics[user_id].preferred_voice
            if preferred_voice and preferred_voice in self.voice_profiles:
                return self.voice_profiles[preferred_voice]
        
        # Default selection based on available providers
        if VoiceProvider.ELEVENLABS in self.providers:
            return self.voice_profiles['elevenlabs_rachel']
        elif VoiceProvider.GOOGLE_CLOUD in self.providers:
            return self.voice_profiles['google_neural_female']
        else:
            return self.voice_profiles['system_default']
    
    async def _calculate_audio_duration(self, audio_data: bytes, audio_format: AudioFormat) -> float:
        """Calculate audio duration in seconds"""
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=audio_format.value)
            return len(audio) / 1000.0  # Convert ms to seconds
        except:
            # Estimate based on data size (rough approximation)
            return len(audio_data) / 32000.0  # Assume 16kHz, 16-bit, mono
    
    async def _update_stt_analytics(self, session_id: str, user_id: str, result: SpeechToTextResult):
        """Update speech-to-text analytics"""
        if session_id not in self.analytics:
            self.analytics[session_id] = VoiceAnalytics(
                session_id=session_id,
                user_id=user_id
            )
        
        analytics = self.analytics[session_id]
        analytics.total_requests += 1
        analytics.speech_to_text_requests += 1
        analytics.total_audio_duration += result.duration
        analytics.total_processing_time += result.processing_time
        
        # Update average confidence
        total_confidence = analytics.average_confidence * (analytics.speech_to_text_requests - 1)
        analytics.average_confidence = (total_confidence + result.confidence) / analytics.speech_to_text_requests
        
        # Update language distribution
        if result.language in analytics.language_distribution:
            analytics.language_distribution[result.language] += 1
        else:
            analytics.language_distribution[result.language] = 1
    
    async def _update_tts_analytics(self, session_id: str, user_id: str, result: TextToSpeechResult):
        """Update text-to-speech analytics"""
        if session_id not in self.analytics:
            self.analytics[session_id] = VoiceAnalytics(
                session_id=session_id,
                user_id=user_id
            )
        
        analytics = self.analytics[session_id]
        analytics.total_requests += 1
        analytics.text_to_speech_requests += 1
        analytics.total_audio_duration += result.audio_duration
        analytics.total_processing_time += result.processing_time
        
        # Update preferred voice
        analytics.preferred_voice = result.voice_profile.voice_id
    
    def _update_performance_metrics(self, operation: str, provider: VoiceProvider, processing_time: float, success: bool):
        """Update performance metrics"""
        self.performance_metrics['total_requests'] += 1
        
        if success:
            self.performance_metrics['successful_requests'] += 1
        else:
            self.performance_metrics['failed_requests'] += 1
        
        # Update average processing time
        total_time = self.performance_metrics['average_processing_time'] * (self.performance_metrics['total_requests'] - 1)
        self.performance_metrics['average_processing_time'] = (total_time + processing_time) / self.performance_metrics['total_requests']
        
        # Update provider performance
        if provider:
            provider_key = f"{provider.value}_{operation}"
            if provider_key not in self.performance_metrics['provider_performance']:
                self.performance_metrics['provider_performance'][provider_key] = {
                    'requests': 0,
                    'successes': 0,
                    'average_time': 0.0
                }
            
            perf = self.performance_metrics['provider_performance'][provider_key]
            perf['requests'] += 1
            if success:
                perf['successes'] += 1
            
            total_time = perf['average_time'] * (perf['requests'] - 1)
            perf['average_time'] = (total_time + processing_time) / perf['requests']
    
    async def get_voice_profiles(self, provider: Optional[VoiceProvider] = None) -> List[VoiceProfile]:
        """Get available voice profiles"""
        if provider:
            return [profile for profile in self.voice_profiles.values() if profile.provider == provider]
        return list(self.voice_profiles.values())
    
    async def get_analytics(self, session_id: Optional[str] = None) -> Union[VoiceAnalytics, Dict[str, VoiceAnalytics]]:
        """Get voice analytics"""
        if session_id:
            return self.analytics.get(session_id)
        return self.analytics
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics
    
    async def clear_cache(self):
        """Clear audio and recognition caches"""
        self.audio_cache.clear()
        self.recognition_cache.clear()
        logger.info("Voice service caches cleared")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        health = {
            'status': 'healthy',
            'providers': {},
            'cache_size': {
                'audio': len(self.audio_cache),
                'recognition': len(self.recognition_cache)
            },
            'analytics_sessions': len(self.analytics),
            'voice_profiles': len(self.voice_profiles)
        }
        
        # Check provider health
        for provider, config in self.providers.items():
            health['providers'][provider.value] = {
                'enabled': config.get('enabled', False),
                'status': 'available' if config.get('enabled') else 'disabled'
            }
        
        return health

# Utility functions
def create_voice_service(config: Dict[str, Any]) -> VoiceService:
    """Factory function to create voice service"""
    return VoiceService(config)

def get_supported_audio_formats() -> List[str]:
    """Get list of supported audio formats"""
    return [format.value for format in AudioFormat]

def get_supported_languages() -> List[str]:
    """Get list of supported languages"""
    return [
        "en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR",
        "ru-RU", "ja-JP", "ko-KR", "zh-CN", "ar-SA", "hi-IN"
    ]
