/**
 * Voice Integration Hooks and Components
 * Provides React hooks for speech-to-text and text-to-speech functionality
 * 
 * Author: CapeAI Development Team
 * Date: July 25, 2025
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'react-hot-toast';

// API service for voice operations
class VoiceAPIService {
  constructor(baseURL = '/api/voice') {
    this.baseURL = baseURL;
  }

  async getConfig() {
    const response = await fetch(`${this.baseURL}/config`);
    if (!response.ok) throw new Error('Failed to get voice config');
    return response.json();
  }

  async speechToText(audioData, options = {}) {
    const payload = {
      audio_data: audioData,
      audio_format: options.format || 'wav',
      language: options.language || 'en-US',
      provider: options.provider,
      session_id: options.sessionId
    };

    const response = await fetch(`${this.baseURL}/speech-to-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Speech recognition failed');
    }

    return response.json();
  }

  async textToSpeech(text, options = {}) {
    const payload = {
      text,
      voice_profile: options.voiceProfile,
      audio_format: options.format || 'mp3',
      session_id: options.sessionId
    };

    const response = await fetch(`${this.baseURL}/text-to-speech`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Speech synthesis failed');
    }

    return response.json();
  }

  async getVoiceProfiles(provider = null) {
    const params = provider ? `?provider=${provider}` : '';
    const response = await fetch(`${this.baseURL}/profiles${params}`);
    if (!response.ok) throw new Error('Failed to get voice profiles');
    return response.json();
  }

  async uploadAudioFile(file, options = {}) {
    const formData = new FormData();
    formData.append('audio_file', file);
    formData.append('language', options.language || 'en-US');
    if (options.provider) formData.append('provider', options.provider);
    if (options.sessionId) formData.append('session_id', options.sessionId);

    const response = await fetch(`${this.baseURL}/speech-to-text/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Audio upload failed');
    }

    return response.json();
  }
}

const voiceAPI = new VoiceAPIService();

/**
 * Hook for speech-to-text functionality
 */
export const useSpeechToText = (options = {}) => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);

  useEffect(() => {
    // Check browser support
    const supported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    setIsSupported(supported);
  }, []);

  const startListening = useCallback(async () => {
    if (!isSupported) {
      setError('Speech recognition not supported in this browser');
      return;
    }

    try {
      setError(null);
      setIsListening(true);
      audioChunksRef.current = [];

      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      streamRef.current = stream;

      // Create media recorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm' // Fallback to available format
      });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        setIsListening(false);
        setIsProcessing(true);

        try {
          // Create audio blob
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          
          // Convert to base64
          const arrayBuffer = await audioBlob.arrayBuffer();
          const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

          // Send to API
          const result = await voiceAPI.speechToText(base64Audio, {
            format: 'webm',
            language: options.language || 'en-US',
            provider: options.provider,
            sessionId: options.sessionId
          });

          setTranscript(result.text);
          setConfidence(result.confidence);
          
          if (options.onResult) {
            options.onResult(result);
          }

        } catch (err) {
          setError(err.message);
          toast.error(`Speech recognition failed: ${err.message}`);
        } finally {
          setIsProcessing(false);
        }
      };

      // Start recording
      mediaRecorder.start();
      
    } catch (err) {
      setError(err.message);
      setIsListening(false);
      toast.error(`Failed to start recording: ${err.message}`);
    }
  }, [isSupported, options]);

  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && isListening) {
      mediaRecorderRef.current.stop();
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  }, [isListening]);

  const processAudioFile = useCallback(async (file) => {
    setIsProcessing(true);
    setError(null);

    try {
      const result = await voiceAPI.uploadAudioFile(file, {
        language: options.language || 'en-US',
        provider: options.provider,
        sessionId: options.sessionId
      });

      setTranscript(result.text);
      setConfidence(result.confidence);
      
      if (options.onResult) {
        options.onResult(result);
      }

      return result;

    } catch (err) {
      setError(err.message);
      toast.error(`Audio processing failed: ${err.message}`);
      throw err;
    } finally {
      setIsProcessing(false);
    }
  }, [options]);

  return {
    isListening,
    isProcessing,
    transcript,
    confidence,
    error,
    isSupported,
    startListening,
    stopListening,
    processAudioFile,
    clearTranscript: () => setTranscript('')
  };
};

/**
 * Hook for text-to-speech functionality
 */
export const useTextToSpeech = (options = {}) => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [voiceProfiles, setVoiceProfiles] = useState([]);

  const audioRef = useRef(null);
  const audioContextRef = useRef(null);

  useEffect(() => {
    // Load voice profiles
    const loadProfiles = async () => {
      try {
        const profiles = await voiceAPI.getVoiceProfiles();
        setVoiceProfiles(profiles);
      } catch (err) {
        console.error('Failed to load voice profiles:', err);
      }
    };

    loadProfiles();
  }, []);

  const speak = useCallback(async (text) => {
    if (!text?.trim()) {
      setError('No text provided');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const result = await voiceAPI.textToSpeech(text, {
        voiceProfile: options.voiceProfile,
        format: options.format || 'mp3',
        sessionId: options.sessionId
      });

      // Convert base64 to audio blob
      const audioData = atob(result.audio_data);
      const audioArray = new Uint8Array(audioData.length);
      for (let i = 0; i < audioData.length; i++) {
        audioArray[i] = audioData.charCodeAt(i);
      }
      
      const audioBlob = new Blob([audioArray], { type: `audio/${result.audio_format}` });
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

      // Create audio element and play
      if (audioRef.current) {
        audioRef.current.pause();
      }

      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onplay = () => setIsSpeaking(true);
      audio.onended = () => setIsSpeaking(false);
      audio.onerror = () => {
        setError('Audio playback failed');
        setIsSpeaking(false);
      };

      await audio.play();

      if (options.onComplete) {
        options.onComplete(result);
      }

      return result;

    } catch (err) {
      setError(err.message);
      toast.error(`Speech synthesis failed: ${err.message}`);
      throw err;
    } finally {
      setIsProcessing(false);
    }
  }, [options]);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsSpeaking(false);
    }
  }, []);

  const pause = useCallback(() => {
    if (audioRef.current && isSpeaking) {
      audioRef.current.pause();
      setIsSpeaking(false);
    }
  }, [isSpeaking]);

  const resume = useCallback(async () => {
    if (audioRef.current && !isSpeaking) {
      try {
        await audioRef.current.play();
        setIsSpeaking(true);
      } catch (err) {
        setError('Failed to resume playback');
      }
    }
  }, [isSpeaking]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  return {
    isSpeaking,
    isProcessing,
    error,
    audioUrl,
    voiceProfiles,
    speak,
    stop,
    pause,
    resume
  };
};

/**
 * Combined voice interaction hook
 */
export const useVoiceInteraction = (options = {}) => {
  const speechToText = useSpeechToText(options);
  const textToSpeech = useTextToSpeech(options);
  const [config, setConfig] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const initializeVoice = async () => {
      try {
        const voiceConfig = await voiceAPI.getConfig();
        setConfig(voiceConfig);
        setIsInitialized(true);
      } catch (err) {
        console.error('Failed to initialize voice service:', err);
      }
    };

    initializeVoice();
  }, []);

  const voiceEcho = useCallback(async () => {
    try {
      // Start listening
      await speechToText.startListening();
      
      // Wait for result (this would be handled by the onResult callback)
      // For now, we'll implement a simple version
      
    } catch (err) {
      toast.error(`Voice echo failed: ${err.message}`);
    }
  }, [speechToText]);

  return {
    ...speechToText,
    ...textToSpeech,
    config,
    isInitialized,
    voiceEcho,
    // Prefixed versions to avoid conflicts
    stt: speechToText,
    tts: textToSpeech
  };
};

/**
 * Voice-enabled AI Chat Component
 */
export const VoiceEnabledChat = ({ onMessage, className = '' }) => {
  const voice = useVoiceInteraction({
    onResult: (result) => {
      if (result.text && onMessage) {
        onMessage(result.text);
      }
    }
  });

  return (
    <div className={`voice-chat ${className}`}>
      {/* Voice Input Button */}
      <button
        onClick={voice.isListening ? voice.stopListening : voice.startListening}
        disabled={voice.isProcessing || !voice.isSupported}
        className={`
          voice-btn
          ${voice.isListening ? 'listening' : ''}
          ${voice.isProcessing ? 'processing' : ''}
          ${!voice.isSupported ? 'disabled' : ''}
        `}
        title={
          !voice.isSupported ? 'Voice not supported' :
          voice.isListening ? 'Stop listening' :
          'Start voice input'
        }
      >
        {voice.isProcessing ? (
          <div className="processing-spinner" />
        ) : voice.isListening ? (
          <div className="listening-indicator" />
        ) : (
          <div className="mic-icon" />
        )}
      </button>

      {/* Status Display */}
      {voice.transcript && (
        <div className="transcript-display">
          <p>{voice.transcript}</p>
          {voice.confidence > 0 && (
            <span className="confidence">
              Confidence: {(voice.confidence * 100).toFixed(1)}%
            </span>
          )}
        </div>
      )}

      {/* Error Display */}
      {voice.error && (
        <div className="error-display">
          <p>Error: {voice.error}</p>
        </div>
      )}
    </div>
  );
};

export default {
  useSpeechToText,
  useTextToSpeech,
  useVoiceInteraction,
  VoiceEnabledChat,
  voiceAPI
};
