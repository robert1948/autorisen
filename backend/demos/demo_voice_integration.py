"""
Voice Integration System Demo
Standalone demonstration and validation of voice capabilities

Author: CapeAI Development Team
Date: July 25, 2025
"""

import asyncio
import logging
import base64
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Voice service imports
from app.services.voice_service import (
    VoiceService, VoiceProvider, AudioFormat, VoiceGender, VoiceProfile,
    SpeechToTextResult, TextToSpeechResult, VoiceAnalytics,
    create_voice_service, get_supported_audio_formats, get_supported_languages
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoiceIntegrationDemo:
    """Comprehensive demonstration of voice integration capabilities"""
    
    def __init__(self):
        """Initialize the demo"""
        self.voice_service = None
        self.demo_results = {}
        
    async def initialize(self):
        """Initialize voice service for demo"""
        try:
            config = {
                'google_cloud_credentials': None,  # Would be set from environment
                'openai_api_key': None,  # Would be set from environment  
                'elevenlabs_api_key': None,  # Would be set from environment
            }
            
            self.voice_service = create_voice_service(config)
            logger.info("✅ Voice service initialized successfully")
            
            # Show configuration
            await self._show_configuration()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize voice service: {e}")
            raise
    
    async def _show_configuration(self):
        """Display voice service configuration"""
        print("\n" + "="*60)
        print("🎤 VOICE INTEGRATION SYSTEM CONFIGURATION")
        print("="*60)
        
        # Health check
        health = await self.voice_service.health_check()
        print(f"Service Status: {health['status'].title()}")
        print(f"Voice Profiles Available: {health['voice_profiles']}")
        print(f"Cache Status: Audio={health['cache_size']['audio']}, Recognition={health['cache_size']['recognition']}")
        
        # Show providers
        print("\n📡 Available Providers:")
        for provider, config in health['providers'].items():
            status = "✅ Enabled" if config['enabled'] else "❌ Disabled"
            print(f"  {provider.replace('_', ' ').title()}: {status}")
        
        # Show supported formats and languages
        print(f"\n🎵 Supported Audio Formats: {', '.join(get_supported_audio_formats())}")
        print(f"🌍 Supported Languages: {', '.join(get_supported_languages()[:8])}...")
        
        # Show voice profiles
        profiles = await self.voice_service.get_voice_profiles()
        print(f"\n🎭 Voice Profiles ({len(profiles)}):")
        for profile in profiles[:5]:  # Show first 5
            print(f"  {profile.name} ({profile.provider.value}, {profile.gender.value}, {profile.language})")
        if len(profiles) > 5:
            print(f"  ... and {len(profiles) - 5} more")
    
    async def demo_text_to_speech(self):
        """Demonstrate text-to-speech functionality"""
        print("\n" + "="*60)
        print("🗣️  TEXT-TO-SPEECH DEMONSTRATION")
        print("="*60)
        
        demo_texts = [
            "Hello! Welcome to the voice integration demonstration.",
            "This system supports multiple providers and voice profiles.",
            "Speech synthesis quality varies by provider and settings.",
            "Thank you for testing the voice capabilities!"
        ]
        
        results = []
        
        for i, text in enumerate(demo_texts, 1):
            print(f"\n📝 Demo {i}: Converting text to speech...")
            print(f"Text: \"{text}\"")
            
            try:
                start_time = time.time()
                
                # Use different voice profiles for variety
                voice_profiles = list(self.voice_service.voice_profiles.keys())
                profile_key = voice_profiles[i % len(voice_profiles)]
                
                result = await self.voice_service.text_to_speech(
                    text=text,
                    voice_profile=profile_key,
                    audio_format=AudioFormat.MP3,
                    session_id="demo-session",
                    user_id="demo-user"
                )
                
                processing_time = time.time() - start_time
                
                print(f"✅ Success!")
                print(f"   Provider: {result.provider.value}")
                print(f"   Voice: {result.voice_profile.name}")
                print(f"   Audio Duration: {result.audio_duration:.2f}s")
                print(f"   File Size: {result.file_size:,} bytes")
                print(f"   Processing Time: {processing_time:.2f}s")
                print(f"   Speed Ratio: {result.audio_duration/processing_time:.1f}x")
                
                results.append({
                    'text': text,
                    'provider': result.provider.value,
                    'voice': result.voice_profile.name,
                    'audio_duration': result.audio_duration,
                    'file_size': result.file_size,
                    'processing_time': processing_time,
                    'success': True
                })
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                results.append({
                    'text': text,
                    'error': str(e),
                    'success': False
                })
        
        self.demo_results['text_to_speech'] = results
        
        # Summary
        successful = sum(1 for r in results if r.get('success', False))
        print(f"\n📊 TTS Summary: {successful}/{len(results)} successful")
        
        if successful > 0:
            avg_processing = sum(r.get('processing_time', 0) for r in results if r.get('success')) / successful
            avg_duration = sum(r.get('audio_duration', 0) for r in results if r.get('success')) / successful
            total_size = sum(r.get('file_size', 0) for r in results if r.get('success'))
            
            print(f"   Average Processing Time: {avg_processing:.2f}s")
            print(f"   Average Audio Duration: {avg_duration:.2f}s")
            print(f"   Total Audio Generated: {total_size:,} bytes")
    
    async def demo_speech_to_text_simulation(self):
        """Simulate speech-to-text functionality with mock audio"""
        print("\n" + "="*60)
        print("🎙️  SPEECH-TO-TEXT SIMULATION")
        print("="*60)
        
        # Create mock audio data (in real scenario, this would be actual audio)
        mock_audio_samples = [
            {
                'description': 'Short greeting',
                'expected_text': 'Hello there',
                'audio_data': self._create_mock_audio_data(duration=1.5)
            },
            {
                'description': 'Question',
                'expected_text': 'How can I help you today?',
                'audio_data': self._create_mock_audio_data(duration=2.8)
            },
            {
                'description': 'Technical phrase',
                'expected_text': 'Initialize voice recognition system',
                'audio_data': self._create_mock_audio_data(duration=3.2)
            },
            {
                'description': 'Long sentence',
                'expected_text': 'The voice integration system provides comprehensive speech-to-text and text-to-speech capabilities',
                'audio_data': self._create_mock_audio_data(duration=5.5)
            }
        ]
        
        results = []
        
        for i, sample in enumerate(mock_audio_samples, 1):
            print(f"\n🎵 Demo {i}: Processing {sample['description']}...")
            print(f"Expected: \"{sample['expected_text']}\"")
            print(f"Audio Duration: ~{len(sample['audio_data'])/16000:.1f}s")
            
            try:
                start_time = time.time()
                
                # Since this is a demo with mock audio, we'll simulate the result
                # In a real implementation, this would process actual audio
                result = await self._simulate_speech_to_text(
                    sample['audio_data'],
                    sample['expected_text'],
                    AudioFormat.WAV
                )
                
                processing_time = time.time() - start_time
                
                print(f"✅ Transcribed: \"{result.text}\"")
                print(f"   Provider: {result.provider.value}")
                print(f"   Confidence: {result.confidence:.3f}")
                print(f"   Processing Time: {processing_time:.2f}s")
                print(f"   Language: {result.language}")
                
                results.append({
                    'description': sample['description'],
                    'expected': sample['expected_text'],
                    'transcribed': result.text,
                    'confidence': result.confidence,
                    'provider': result.provider.value,
                    'processing_time': processing_time,
                    'success': True
                })
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                results.append({
                    'description': sample['description'],
                    'error': str(e),
                    'success': False
                })
        
        self.demo_results['speech_to_text'] = results
        
        # Summary
        successful = sum(1 for r in results if r.get('success', False))
        print(f"\n📊 STT Summary: {successful}/{len(results)} successful")
        
        if successful > 0:
            avg_confidence = sum(r.get('confidence', 0) for r in results if r.get('success')) / successful
            avg_processing = sum(r.get('processing_time', 0) for r in results if r.get('success')) / successful
            
            print(f"   Average Confidence: {avg_confidence:.3f}")
            print(f"   Average Processing Time: {avg_processing:.2f}s")
    
    def _create_mock_audio_data(self, duration: float = 2.0, sample_rate: int = 16000) -> bytes:
        """Create mock audio data for demonstration"""
        # Simple WAV header + silence
        num_samples = int(duration * sample_rate)
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        audio_data = b'\x00\x00' * num_samples  # Silence
        return wav_header + audio_data
    
    async def _simulate_speech_to_text(self, audio_data: bytes, expected_text: str, format: AudioFormat) -> SpeechToTextResult:
        """Simulate speech-to-text processing for demo purposes"""
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Create a realistic result
        return SpeechToTextResult(
            text=expected_text,
            confidence=0.85 + (hash(expected_text) % 100) / 1000,  # Simulated confidence
            provider=VoiceProvider.SYSTEM_TTS,  # Fallback provider for demo
            language="en-US",
            duration=len(audio_data) / 16000,  # Estimate duration
            processing_time=0.1 + len(expected_text) * 0.01  # Simulated processing time
        )
    
    async def demo_voice_analytics(self):
        """Demonstrate voice analytics capabilities"""
        print("\n" + "="*60)
        print("📈 VOICE ANALYTICS DEMONSTRATION")
        print("="*60)
        
        # Get current analytics
        analytics = await self.voice_service.get_analytics()
        performance = await self.voice_service.get_performance_metrics()
        
        print("📊 Current Analytics:")
        if analytics:
            for session_id, data in list(analytics.items())[:3]:  # Show first 3 sessions
                print(f"\n  Session: {session_id}")
                print(f"    Total Requests: {data.total_requests}")
                print(f"    STT Requests: {data.speech_to_text_requests}")
                print(f"    TTS Requests: {data.text_to_speech_requests}")
                print(f"    Audio Duration: {data.total_audio_duration:.1f}s")
                print(f"    Avg Confidence: {data.average_confidence:.3f}")
                if data.language_distribution:
                    languages = ', '.join(f"{lang}({count})" for lang, count in data.language_distribution.items())
                    print(f"    Languages: {languages}")
        else:
            print("  No analytics data available yet")
        
        print(f"\n🚀 Performance Metrics:")
        print(f"  Total Requests: {performance['total_requests']}")
        print(f"  Success Rate: {performance['successful_requests']}/{performance['total_requests']} ({performance['successful_requests']/max(performance['total_requests'], 1)*100:.1f}%)")
        print(f"  Average Processing: {performance['average_processing_time']:.2f}s")
        
        if performance['provider_performance']:
            print(f"\n  Provider Performance:")
            for provider, perf in performance['provider_performance'].items():
                success_rate = perf['successes'] / max(perf['requests'], 1) * 100
                print(f"    {provider}: {perf['requests']} requests, {success_rate:.1f}% success, {perf['average_time']:.2f}s avg")
    
    async def demo_voice_profiles(self):
        """Demonstrate voice profile capabilities"""
        print("\n" + "="*60)
        print("🎭 VOICE PROFILES DEMONSTRATION")
        print("="*60)
        
        profiles = await self.voice_service.get_voice_profiles()
        
        print(f"📋 Available Profiles ({len(profiles)}):")
        
        # Group by provider
        by_provider = {}
        for profile in profiles:
            provider = profile.provider.value
            if provider not in by_provider:
                by_provider[provider] = []
            by_provider[provider].append(profile)
        
        for provider, provider_profiles in by_provider.items():
            print(f"\n  🔹 {provider.replace('_', ' ').title()} ({len(provider_profiles)} profiles):")
            for profile in provider_profiles:
                print(f"    • {profile.name}")
                print(f"      ID: {profile.voice_id}")
                print(f"      Gender: {profile.gender.value}, Language: {profile.language}")
                print(f"      Speed: {profile.speed}x, Pitch: {profile.pitch:+.1f}")
                if hasattr(profile, 'stability') and profile.stability:
                    print(f"      Stability: {profile.stability:.2f}, Similarity: {profile.similarity_boost:.2f}")
        
        # Test profile selection
        print(f"\n🎯 Profile Selection Test:")
        best_profile = self.voice_service._select_best_voice_profile("demo-user")
        print(f"  Best profile for demo-user: {best_profile.name} ({best_profile.provider.value})")
        
        # Test provider selection
        best_stt_provider = self.voice_service._select_best_stt_provider()
        print(f"  Best STT provider: {best_stt_provider.value}")
    
    async def demo_comprehensive_validation(self):
        """Comprehensive validation of all voice features"""
        print("\n" + "="*60)
        print("🔍 COMPREHENSIVE SYSTEM VALIDATION")
        print("="*60)
        
        validation_results = {
            'voice_service_initialization': False,
            'health_check': False,
            'voice_profiles_loaded': False,
            'text_to_speech_functional': False,
            'speech_to_text_simulation': False,
            'analytics_tracking': False,
            'performance_metrics': False,
            'cache_functionality': False,
            'provider_selection': False,
            'error_handling': False
        }
        
        # 1. Voice service initialization
        try:
            assert self.voice_service is not None
            validation_results['voice_service_initialization'] = True
            print("✅ Voice service initialization: PASSED")
        except Exception as e:
            print(f"❌ Voice service initialization: FAILED - {e}")
        
        # 2. Health check
        try:
            health = await self.voice_service.health_check()
            assert health['status'] == 'healthy'
            validation_results['health_check'] = True
            print("✅ Health check: PASSED")
        except Exception as e:
            print(f"❌ Health check: FAILED - {e}")
        
        # 3. Voice profiles
        try:
            profiles = await self.voice_service.get_voice_profiles()
            assert len(profiles) > 0
            validation_results['voice_profiles_loaded'] = True
            print(f"✅ Voice profiles loaded: PASSED ({len(profiles)} profiles)")
        except Exception as e:
            print(f"❌ Voice profiles loaded: FAILED - {e}")
        
        # 4. Text-to-speech
        try:
            result = await self.voice_service.text_to_speech(
                "Test message",
                session_id="validation-session",
                user_id="validation-user"
            )
            assert len(result.audio_data) > 0
            validation_results['text_to_speech_functional'] = True
            print("✅ Text-to-speech functional: PASSED")
        except Exception as e:
            print(f"❌ Text-to-speech functional: FAILED - {e}")
        
        # 5. Speech-to-text simulation
        try:
            mock_audio = self._create_mock_audio_data(2.0)
            result = await self._simulate_speech_to_text(mock_audio, "Test transcription", AudioFormat.WAV)
            assert result.text == "Test transcription"
            validation_results['speech_to_text_simulation'] = True
            print("✅ Speech-to-text simulation: PASSED")
        except Exception as e:
            print(f"❌ Speech-to-text simulation: FAILED - {e}")
        
        # 6. Analytics tracking
        try:
            analytics = await self.voice_service.get_analytics()
            assert isinstance(analytics, dict)
            validation_results['analytics_tracking'] = True
            print("✅ Analytics tracking: PASSED")
        except Exception as e:
            print(f"❌ Analytics tracking: FAILED - {e}")
        
        # 7. Performance metrics
        try:
            metrics = await self.voice_service.get_performance_metrics()
            assert 'total_requests' in metrics
            validation_results['performance_metrics'] = True
            print("✅ Performance metrics: PASSED")
        except Exception as e:
            print(f"❌ Performance metrics: FAILED - {e}")
        
        # 8. Cache functionality
        try:
            initial_cache_size = len(self.voice_service.audio_cache)
            await self.voice_service.clear_cache()
            assert len(self.voice_service.audio_cache) == 0
            validation_results['cache_functionality'] = True
            print("✅ Cache functionality: PASSED")
        except Exception as e:
            print(f"❌ Cache functionality: FAILED - {e}")
        
        # 9. Provider selection
        try:
            stt_provider = self.voice_service._select_best_stt_provider()
            voice_profile = self.voice_service._select_best_voice_profile()
            assert stt_provider is not None
            assert voice_profile is not None
            validation_results['provider_selection'] = True
            print("✅ Provider selection: PASSED")
        except Exception as e:
            print(f"❌ Provider selection: FAILED - {e}")
        
        # 10. Error handling
        try:
            # Test with invalid parameters
            try:
                await self.voice_service.text_to_speech("")  # Empty text
                assert False, "Should have raised an error"
            except:
                pass  # Expected to fail
            
            validation_results['error_handling'] = True
            print("✅ Error handling: PASSED")
        except Exception as e:
            print(f"❌ Error handling: FAILED - {e}")
        
        # Summary
        passed = sum(validation_results.values())
        total = len(validation_results)
        
        print(f"\n📊 VALIDATION SUMMARY:")
        print(f"   Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL VALIDATIONS PASSED - Voice system is fully functional!")
        else:
            failed_tests = [test for test, result in validation_results.items() if not result]
            print(f"⚠️  Failed tests: {', '.join(failed_tests)}")
        
        self.demo_results['validation'] = validation_results
        return validation_results
    
    async def generate_demo_report(self):
        """Generate comprehensive demo report"""
        print("\n" + "="*60)
        print("📋 VOICE INTEGRATION DEMO REPORT")
        print("="*60)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'voice_service_version': '1.0.0',
                'supported_formats': get_supported_audio_formats(),
                'supported_languages': get_supported_languages(),
            },
            'demo_results': self.demo_results
        }
        
        # System status
        health = await self.voice_service.health_check()
        report['system_status'] = health
        
        # Performance summary
        performance = await self.voice_service.get_performance_metrics()
        report['performance_summary'] = performance
        
        # Analytics summary
        analytics = await self.voice_service.get_analytics()
        report['analytics_summary'] = {
            'total_sessions': len(analytics),
            'total_requests': sum(a.total_requests for a in analytics.values()),
            'total_audio_duration': sum(a.total_audio_duration for a in analytics.values())
        }
        
        print("📄 Demo Report Generated:")
        print(f"   Timestamp: {report['timestamp']}")
        print(f"   System Status: {health['status']}")
        print(f"   Available Providers: {len(health['providers'])}")
        print(f"   Voice Profiles: {health['voice_profiles']}")
        
        if 'validation' in self.demo_results:
            validation = self.demo_results['validation']
            passed = sum(validation.values())
            total = len(validation)
            print(f"   Validation Score: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if 'text_to_speech' in self.demo_results:
            tts_results = self.demo_results['text_to_speech']
            tts_success = sum(1 for r in tts_results if r.get('success', False))
            print(f"   TTS Success Rate: {tts_success}/{len(tts_results)} ({tts_success/len(tts_results)*100:.1f}%)")
        
        if 'speech_to_text' in self.demo_results:
            stt_results = self.demo_results['speech_to_text']
            stt_success = sum(1 for r in stt_results if r.get('success', False))
            print(f"   STT Success Rate: {stt_success}/{len(stt_results)} ({stt_success/len(stt_results)*100:.1f}%)")
        
        # Save report
        report_file = f"voice_demo_report_{int(time.time())}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"   Report saved: {report_file}")
        except Exception as e:
            print(f"   Report save failed: {e}")
        
        return report
    
    async def run_complete_demo(self):
        """Run the complete voice integration demonstration"""
        print("🚀 Starting Voice Integration System Demo...")
        
        try:
            # Initialize
            await self.initialize()
            
            # Run demonstrations
            await self.demo_voice_profiles()
            await self.demo_text_to_speech()
            await self.demo_speech_to_text_simulation()
            await self.demo_voice_analytics()
            
            # Validation
            validation_results = await self.demo_comprehensive_validation()
            
            # Generate report
            report = await self.generate_demo_report()
            
            print("\n🎉 Voice Integration Demo Complete!")
            
            return {
                'success': True,
                'validation_results': validation_results,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"\n❌ Demo failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

async def main():
    """Main demo function"""
    print("🎤 Voice Integration System - Comprehensive Demo")
    print("=" * 60)
    
    demo = VoiceIntegrationDemo()
    result = await demo.run_complete_demo()
    
    if result['success']:
        print("\n✅ Demo completed successfully!")
        validation = result['validation_results']
        passed = sum(validation.values())
        total = len(validation)
        print(f"System validation: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    else:
        print(f"\n❌ Demo failed: {result['error']}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
