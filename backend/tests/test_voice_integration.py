"""
Voice Integration Test Suite
Comprehensive tests for speech-to-text and text-to-speech functionality

Author: CapeAI Development Team
Date: July 25, 2025
"""

import pytest
import asyncio
import json
import base64
import io
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import UploadFile

# Import the voice service and API components
from app.services.voice_service import (
    VoiceService, VoiceProvider, AudioFormat, VoiceGender, VoiceProfile,
    SpeechToTextResult, TextToSpeechResult, VoiceAnalytics,
    create_voice_service, get_supported_audio_formats, get_supported_languages
)
from app.routes.voice import router

class TestVoiceService:
    """Test suite for VoiceService"""
    
    @pytest.fixture
    def voice_config(self):
        """Voice service configuration fixture"""
        return {
            'google_cloud_credentials': None,
            'openai_api_key': 'test-openai-key',
            'elevenlabs_api_key': 'test-elevenlabs-key'
        }
    
    @pytest.fixture
    def voice_service(self, voice_config):
        """Voice service fixture"""
        return VoiceService(voice_config)
    
    @pytest.fixture
    def sample_audio_data(self):
        """Sample audio data fixture"""
        # Create a simple WAV file structure
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        sample_data = b'\x00\x00' * 1000  # 1000 samples of silence
        return wav_header + sample_data
    
    def test_voice_service_initialization(self, voice_service):
        """Test voice service initialization"""
        assert voice_service is not None
        assert isinstance(voice_service.voice_profiles, dict)
        assert len(voice_service.voice_profiles) > 0
        assert voice_service.performance_metrics is not None
        
        # Check that voice profiles are properly initialized
        assert 'google_neural_female' in voice_service.voice_profiles
        assert 'elevenlabs_rachel' in voice_service.voice_profiles
        assert 'system_default' in voice_service.voice_profiles
    
    def test_voice_profile_creation(self):
        """Test voice profile creation"""
        profile = VoiceProfile(
            provider=VoiceProvider.GOOGLE_CLOUD,
            voice_id="test-voice",
            name="Test Voice",
            gender=VoiceGender.FEMALE,
            language="en-US",
            speed=1.2,
            pitch=0.1
        )
        
        assert profile.provider == VoiceProvider.GOOGLE_CLOUD
        assert profile.voice_id == "test-voice"
        assert profile.name == "Test Voice"
        assert profile.gender == VoiceGender.FEMALE
        assert profile.language == "en-US"
        assert profile.speed == 1.2
        assert profile.pitch == 0.1
    
    @pytest.mark.asyncio
    async def test_get_voice_profiles(self, voice_service):
        """Test getting voice profiles"""
        profiles = await voice_service.get_voice_profiles()
        assert len(profiles) > 0
        assert all(isinstance(p, VoiceProfile) for p in profiles)
        
        # Test filtering by provider
        google_profiles = await voice_service.get_voice_profiles(VoiceProvider.GOOGLE_CLOUD)
        assert all(p.provider == VoiceProvider.GOOGLE_CLOUD for p in google_profiles)
    
    @pytest.mark.asyncio
    async def test_health_check(self, voice_service):
        """Test voice service health check"""
        health = await voice_service.health_check()
        
        assert 'status' in health
        assert 'providers' in health
        assert 'cache_size' in health
        assert 'analytics_sessions' in health
        assert 'voice_profiles' in health
        
        assert health['status'] == 'healthy'
        assert isinstance(health['providers'], dict)
        assert isinstance(health['cache_size'], dict)
    
    @pytest.mark.asyncio
    @patch('speech_recognition.Recognizer')
    async def test_system_speech_to_text(self, mock_recognizer, voice_service, sample_audio_data):
        """Test system speech-to-text functionality"""
        # Mock the recognizer
        mock_recognizer_instance = Mock()
        mock_recognizer_instance.recognize_google.return_value = "Hello world"
        mock_recognizer.return_value = mock_recognizer_instance
        
        result = await voice_service._system_speech_to_text(sample_audio_data, "en-US")
        
        assert result['text'] == "Hello world"
        assert result['confidence'] == 0.8
    
    @pytest.mark.asyncio
    @patch('openai.Audio.transcribe')
    async def test_openai_speech_to_text(self, mock_transcribe, voice_service, sample_audio_data):
        """Test OpenAI Whisper speech-to-text"""
        # Mock OpenAI response
        mock_transcribe.return_value = {
            'text': 'This is a test transcription',
            'duration': 5.0
        }
        
        # Add OpenAI provider to service
        voice_service.providers[VoiceProvider.OPENAI_WHISPER] = {
            'client': Mock(),
            'enabled': True
        }
        
        result = await voice_service._openai_speech_to_text(sample_audio_data, "en-US")
        
        assert result['text'] == 'This is a test transcription'
        assert result['confidence'] == 0.9
        assert result['duration'] == 5.0
    
    @pytest.mark.asyncio
    async def test_speech_to_text_full_flow(self, voice_service, sample_audio_data):
        """Test complete speech-to-text flow"""
        with patch.object(voice_service, '_perform_speech_recognition') as mock_recognition:
            mock_recognition.return_value = {
                'text': 'Test transcription',
                'confidence': 0.95,
                'duration': 3.0
            }
            
            result = await voice_service.speech_to_text(
                audio_data=sample_audio_data,
                audio_format=AudioFormat.WAV,
                language="en-US",
                session_id="test-session",
                user_id="test-user"
            )
            
            assert isinstance(result, SpeechToTextResult)
            assert result.text == 'Test transcription'
            assert result.confidence == 0.95
            assert result.language == "en-US"
            assert result.duration == 3.0
    
    @pytest.mark.asyncio
    @patch('pyttsx3.init')
    async def test_system_text_to_speech(self, mock_pyttsx_init, voice_service):
        """Test system text-to-speech"""
        # Mock pyttsx3 engine
        mock_engine = Mock()
        mock_pyttsx_init.return_value = mock_engine
        
        # Add system TTS provider
        voice_service.providers[VoiceProvider.SYSTEM_TTS] = {
            'engine': mock_engine,
            'enabled': True
        }
        
        profile = voice_service.voice_profiles['system_default']
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            with patch('os.remove'):
                mock_open.return_value.__enter__.return_value.read.return_value = b'fake_audio_data'
                
                result = await voice_service._system_text_to_speech(
                    "Hello world", profile, AudioFormat.WAV
                )
                
                assert result == b'fake_audio_data'
                mock_engine.save_to_file.assert_called_once()
                mock_engine.runAndWait.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_text_to_speech_full_flow(self, voice_service):
        """Test complete text-to-speech flow"""
        with patch.object(voice_service, '_generate_speech') as mock_generation:
            with patch.object(voice_service, '_calculate_audio_duration') as mock_duration:
                mock_generation.return_value = b'fake_audio_data'
                mock_duration.return_value = 2.5
                
                result = await voice_service.text_to_speech(
                    text="Hello world",
                    session_id="test-session",
                    user_id="test-user"
                )
                
                assert isinstance(result, TextToSpeechResult)
                assert result.audio_data == b'fake_audio_data'
                assert result.text_length == len("Hello world")
                assert result.audio_duration == 2.5
    
    @pytest.mark.asyncio
    async def test_analytics_tracking(self, voice_service):
        """Test analytics tracking functionality"""
        # Create mock results
        stt_result = SpeechToTextResult(
            text="Test text",
            confidence=0.9,
            provider=VoiceProvider.OPENAI_WHISPER,
            language="en-US",
            duration=3.0,
            processing_time=1.5
        )
        
        tts_result = TextToSpeechResult(
            audio_data=b'test_audio',
            audio_format=AudioFormat.MP3,
            provider=VoiceProvider.GOOGLE_CLOUD,
            voice_profile=voice_service.voice_profiles['google_neural_female'],
            text_length=10,
            audio_duration=2.0,
            processing_time=1.0,
            file_size=100
        )
        
        # Update analytics
        await voice_service._update_stt_analytics("session1", "user1", stt_result)
        await voice_service._update_tts_analytics("session1", "user1", tts_result)
        
        # Check analytics
        analytics = await voice_service.get_analytics("session1")
        assert analytics is not None
        assert analytics.session_id == "session1"
        assert analytics.user_id == "user1"
        assert analytics.total_requests == 2
        assert analytics.speech_to_text_requests == 1
        assert analytics.text_to_speech_requests == 1
        assert analytics.average_confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, voice_service):
        """Test performance metrics tracking"""
        # Update some metrics
        voice_service._update_performance_metrics(
            'speech_to_text', VoiceProvider.OPENAI_WHISPER, 1.5, True
        )
        voice_service._update_performance_metrics(
            'text_to_speech', VoiceProvider.GOOGLE_CLOUD, 2.0, True
        )
        voice_service._update_performance_metrics(
            'speech_to_text', VoiceProvider.OPENAI_WHISPER, 3.0, False
        )
        
        metrics = await voice_service.get_performance_metrics()
        
        assert metrics['total_requests'] == 3
        assert metrics['successful_requests'] == 2
        assert metrics['failed_requests'] == 1
        assert 'openai_whisper_speech_to_text' in metrics['provider_performance']
        assert 'google_cloud_text_to_speech' in metrics['provider_performance']
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, voice_service, sample_audio_data):
        """Test caching functionality"""
        # Test speech-to-text caching
        with patch.object(voice_service, '_perform_speech_recognition') as mock_recognition:
            mock_recognition.return_value = {
                'text': 'Cached text',
                'confidence': 0.8
            }
            
            # First call - should process
            result1 = await voice_service.speech_to_text(sample_audio_data)
            assert mock_recognition.call_count == 1
            
            # Second call with same audio - should use cache
            result2 = await voice_service.speech_to_text(sample_audio_data)
            assert mock_recognition.call_count == 1  # Not called again
            assert result1.text == result2.text
        
        # Test cache clearing
        await voice_service.clear_cache()
        assert len(voice_service.audio_cache) == 0
        assert len(voice_service.recognition_cache) == 0

class TestVoiceAPI:
    """Test suite for Voice API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Mock user fixture"""
        return {
            'user_id': 'test-user',
            'username': 'testuser',
            'is_admin': False
        }
    
    @pytest.fixture
    def mock_voice_service(self):
        """Mock voice service fixture"""
        mock_service = AsyncMock()
        
        # Mock voice profiles
        mock_profiles = [
            VoiceProfile(
                provider=VoiceProvider.GOOGLE_CLOUD,
                voice_id="test-voice",
                name="Test Voice",
                gender=VoiceGender.FEMALE,
                language="en-US"
            )
        ]
        mock_service.get_voice_profiles.return_value = mock_profiles
        
        # Mock config
        mock_service.config = {
            'supported_formats': ['wav', 'mp3'],
            'supported_languages': ['en-US', 'es-ES'],
            'available_providers': ['google_cloud', 'openai_whisper']
        }
        
        return mock_service
    
    def test_get_voice_config(self, client, mock_voice_service):
        """Test voice configuration endpoint"""
        with patch('app.routes.voice.get_voice_service') as mock_get_service:
            mock_get_service.return_value = mock_voice_service
            
            response = client.get("/api/voice/config")
            assert response.status_code == 200
            
            data = response.json()
            assert 'supported_formats' in data
            assert 'supported_languages' in data
            assert 'available_providers' in data
            assert 'voice_profiles' in data
    
    def test_speech_to_text_endpoint(self, client, mock_voice_service, mock_user):
        """Test speech-to-text endpoint"""
        # Mock the dependencies
        with patch('app.routes.voice.get_current_user') as mock_auth:
            with patch('app.routes.voice.get_voice_service') as mock_get_service:
                mock_auth.return_value = mock_user
                mock_get_service.return_value = mock_voice_service
                
                # Mock STT result
                mock_result = SpeechToTextResult(
                    text="Test transcription",
                    confidence=0.95,
                    provider=VoiceProvider.OPENAI_WHISPER,
                    language="en-US",
                    duration=3.0,
                    processing_time=1.5
                )
                mock_voice_service.speech_to_text.return_value = mock_result
                
                # Test request
                payload = {
                    "audio_data": base64.b64encode(b"fake_audio").decode('utf-8'),
                    "audio_format": "wav",
                    "language": "en-US"
                }
                
                response = client.post("/api/voice/speech-to-text", json=payload)
                assert response.status_code == 200
                
                data = response.json()
                assert data['text'] == "Test transcription"
                assert data['confidence'] == 0.95
                assert data['provider'] == 'openai_whisper'
    
    def test_text_to_speech_endpoint(self, client, mock_voice_service, mock_user):
        """Test text-to-speech endpoint"""
        with patch('app.routes.voice.get_current_user') as mock_auth:
            with patch('app.routes.voice.get_voice_service') as mock_get_service:
                mock_auth.return_value = mock_user
                mock_get_service.return_value = mock_voice_service
                
                # Mock TTS result
                profile = VoiceProfile(
                    provider=VoiceProvider.GOOGLE_CLOUD,
                    voice_id="test-voice",
                    name="Test Voice",
                    gender=VoiceGender.FEMALE,
                    language="en-US"
                )
                
                mock_result = TextToSpeechResult(
                    audio_data=b"fake_audio_data",
                    audio_format=AudioFormat.MP3,
                    provider=VoiceProvider.GOOGLE_CLOUD,
                    voice_profile=profile,
                    text_length=10,
                    audio_duration=2.5,
                    processing_time=1.0,
                    file_size=100
                )
                mock_voice_service.text_to_speech.return_value = mock_result
                
                # Test request
                payload = {
                    "text": "Hello world",
                    "audio_format": "mp3"
                }
                
                response = client.post("/api/voice/text-to-speech", json=payload)
                assert response.status_code == 200
                
                data = response.json()
                assert 'audio_data' in data
                assert data['audio_format'] == 'mp3'
                assert data['provider'] == 'google_cloud'
                assert data['text_length'] == 10
    
    def test_voice_profiles_endpoint(self, client, mock_voice_service):
        """Test voice profiles endpoint"""
        with patch('app.routes.voice.get_voice_service') as mock_get_service:
            mock_get_service.return_value = mock_voice_service
            
            response = client.get("/api/voice/profiles")
            assert response.status_code == 200
            
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            
            profile = data[0]
            assert 'provider' in profile
            assert 'voice_id' in profile
            assert 'name' in profile
            assert 'gender' in profile
    
    def test_voice_analytics_endpoint(self, client, mock_voice_service, mock_user):
        """Test voice analytics endpoint"""
        with patch('app.routes.voice.get_current_user') as mock_auth:
            with patch('app.routes.voice.get_voice_service') as mock_get_service:
                mock_auth.return_value = mock_user
                mock_get_service.return_value = mock_voice_service
                
                # Mock analytics data
                mock_analytics = VoiceAnalytics(
                    session_id="test-session",
                    user_id="test-user",
                    total_requests=5,
                    speech_to_text_requests=3,
                    text_to_speech_requests=2,
                    total_audio_duration=15.0,
                    average_confidence=0.85
                )
                mock_voice_service.get_analytics.return_value = mock_analytics
                
                response = client.get("/api/voice/analytics?session_id=test-session")
                assert response.status_code == 200
                
                data = response.json()
                assert data['session_id'] == "test-session"
                assert data['total_requests'] == 5
                assert data['average_confidence'] == 0.85
    
    def test_performance_metrics_endpoint(self, client, mock_voice_service, mock_user):
        """Test performance metrics endpoint"""
        with patch('app.routes.voice.get_current_user') as mock_auth:
            with patch('app.routes.voice.get_voice_service') as mock_get_service:
                mock_auth.return_value = mock_user
                mock_get_service.return_value = mock_voice_service
                
                mock_metrics = {
                    'total_requests': 100,
                    'successful_requests': 95,
                    'failed_requests': 5,
                    'average_processing_time': 1.5
                }
                mock_voice_service.get_performance_metrics.return_value = mock_metrics
                
                response = client.get("/api/voice/performance")
                assert response.status_code == 200
                
                data = response.json()
                assert data['total_requests'] == 100
                assert data['successful_requests'] == 95
    
    def test_health_check_endpoint(self, client, mock_voice_service):
        """Test health check endpoint"""
        with patch('app.routes.voice.get_voice_service') as mock_get_service:
            mock_get_service.return_value = mock_voice_service
            
            mock_health = {
                'status': 'healthy',
                'providers': {'openai_whisper': {'enabled': True}},
                'cache_size': {'audio': 0, 'recognition': 0}
            }
            mock_voice_service.health_check.return_value = mock_health
            
            response = client.get("/api/voice/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data['status'] == 'healthy'
            assert 'providers' in data

class TestVoiceUtilities:
    """Test utility functions"""
    
    def test_create_voice_service(self):
        """Test voice service factory function"""
        config = {'test': 'config'}
        service = create_voice_service(config)
        assert isinstance(service, VoiceService)
        assert service.config == config
    
    def test_get_supported_audio_formats(self):
        """Test getting supported audio formats"""
        formats = get_supported_audio_formats()
        assert isinstance(formats, list)
        assert 'wav' in formats
        assert 'mp3' in formats
        assert 'ogg' in formats
    
    def test_get_supported_languages(self):
        """Test getting supported languages"""
        languages = get_supported_languages()
        assert isinstance(languages, list)
        assert 'en-US' in languages
        assert 'es-ES' in languages
        assert 'fr-FR' in languages

class TestVoiceIntegration:
    """Integration tests for voice functionality"""
    
    @pytest.mark.asyncio
    async def test_voice_echo_flow(self):
        """Test complete voice echo flow"""
        config = {'openai_api_key': 'test-key'}
        service = VoiceService(config)
        
        # Mock the speech-to-text and text-to-speech
        with patch.object(service, 'speech_to_text') as mock_stt:
            with patch.object(service, 'text_to_speech') as mock_tts:
                
                # Mock STT result
                stt_result = SpeechToTextResult(
                    text="Hello world",
                    confidence=0.9,
                    provider=VoiceProvider.OPENAI_WHISPER,
                    language="en-US",
                    duration=2.0,
                    processing_time=1.0
                )
                mock_stt.return_value = stt_result
                
                # Mock TTS result
                profile = service.voice_profiles['system_default']
                tts_result = TextToSpeechResult(
                    audio_data=b"echo_audio",
                    audio_format=AudioFormat.MP3,
                    provider=VoiceProvider.SYSTEM_TTS,
                    voice_profile=profile,
                    text_length=len("You said: Hello world"),
                    audio_duration=3.0,
                    processing_time=1.5,
                    file_size=100
                )
                mock_tts.return_value = tts_result
                
                # Simulate echo flow
                audio_input = b"fake_audio_input"
                
                # Speech-to-text
                transcription = await service.speech_to_text(audio_input)
                assert transcription.text == "Hello world"
                
                # Text-to-speech (echo back)
                echo_text = f"You said: {transcription.text}"
                echo_audio = await service.text_to_speech(echo_text)
                
                assert echo_audio.audio_data == b"echo_audio"
                assert echo_audio.text_length == len(echo_text)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
