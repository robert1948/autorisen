/**
 * Voice UI Components
 * Voice-enabled user interface components for speech interaction
 * 
 * Author: CapeAI Development Team
 * Date: July 25, 2025
 */

import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Upload, Play, Pause, Square, Settings, Loader } from 'lucide-react';
import { useVoiceInteraction } from '../hooks/useVoice';
import { toast } from 'react-hot-toast';

/**
 * Voice Input Button Component
 */
export const VoiceInputButton = ({ 
  onTranscript, 
  className = '',
  size = 'md',
  variant = 'primary',
  showTranscript = true,
  language = 'en-US',
  provider = null 
}) => {
  const voice = useVoiceInteraction({
    language,
    provider,
    onResult: (result) => {
      if (onTranscript) {
        onTranscript(result.text, result);
      }
    }
  });

  const sizeClasses = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-12 h-12 text-base',
    lg: 'w-16 h-16 text-lg',
    xl: 'w-20 h-20 text-xl'
  };

  const variantClasses = {
    primary: 'bg-blue-500 hover:bg-blue-600 text-white',
    secondary: 'bg-gray-500 hover:bg-gray-600 text-white',
    success: 'bg-green-500 hover:bg-green-600 text-white',
    danger: 'bg-red-500 hover:bg-red-600 text-white'
  };

  const getButtonState = () => {
    if (!voice.isSupported) return 'disabled';
    if (voice.isProcessing) return 'processing';
    if (voice.isListening) return 'listening';
    return 'idle';
  };

  const buttonState = getButtonState();

  return (
    <div className={`voice-input-container ${className}`}>
      <button
        onClick={voice.isListening ? voice.stopListening : voice.startListening}
        disabled={!voice.isSupported || voice.isProcessing}
        className={`
          voice-input-btn
          ${sizeClasses[size]}
          ${variantClasses[variant]}
          rounded-full
          flex items-center justify-center
          transition-all duration-200
          ${buttonState === 'listening' ? 'animate-pulse ring-4 ring-blue-300' : ''}
          ${buttonState === 'processing' ? 'opacity-75' : ''}
          ${buttonState === 'disabled' ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
        `}
        title={
          !voice.isSupported ? 'Voice input not supported' :
          voice.isProcessing ? 'Processing...' :
          voice.isListening ? 'Click to stop listening' :
          'Click to start voice input'
        }
      >
        {voice.isProcessing ? (
          <Loader className="animate-spin" />
        ) : voice.isListening ? (
          <MicOff />
        ) : (
          <Mic />
        )}
      </button>

      {/* Transcript Display */}
      {showTranscript && voice.transcript && (
        <div className="mt-2 p-3 bg-gray-50 rounded-lg border">
          <p className="text-sm text-gray-700">{voice.transcript}</p>
          {voice.confidence > 0 && (
            <div className="mt-1 flex items-center justify-between">
              <span className="text-xs text-gray-500">
                Confidence: {(voice.confidence * 100).toFixed(1)}%
              </span>
              <div className="w-16 bg-gray-200 rounded-full h-1">
                <div 
                  className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                  style={{ width: `${voice.confidence * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {voice.error && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{voice.error}</p>
        </div>
      )}
    </div>
  );
};

/**
 * Text-to-Speech Button Component
 */
export const TextToSpeechButton = ({ 
  text, 
  voiceProfile = null,
  className = '',
  size = 'md',
  showControls = true,
  autoPlay = false
}) => {
  const voice = useVoiceInteraction();
  const [hasPlayed, setHasPlayed] = useState(false);

  useEffect(() => {
    if (autoPlay && text && !hasPlayed && voice.isInitialized) {
      voice.speak(text);
      setHasPlayed(true);
    }
  }, [autoPlay, text, hasPlayed, voice.isInitialized, voice.speak]);

  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-10 h-10 text-base'
  };

  const handleSpeak = async () => {
    if (!text?.trim()) {
      toast.error('No text to speak');
      return;
    }

    try {
      await voice.speak(text);
    } catch (error) {
      toast.error('Failed to speak text');
    }
  };

  return (
    <div className={`tts-container flex items-center gap-2 ${className}`}>
      <button
        onClick={handleSpeak}
        disabled={voice.isProcessing || !text?.trim()}
        className={`
          tts-btn
          ${sizeClasses[size]}
          bg-green-500 hover:bg-green-600 text-white
          rounded-full flex items-center justify-center
          transition-all duration-200
          ${voice.isProcessing ? 'opacity-75' : 'hover:scale-105'}
          ${!text?.trim() ? 'opacity-50 cursor-not-allowed' : ''}
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500
        `}
        title={
          !text?.trim() ? 'No text to speak' :
          voice.isProcessing ? 'Processing...' :
          'Click to speak text'
        }
      >
        {voice.isProcessing ? (
          <Loader className="animate-spin" />
        ) : (
          <Volume2 />
        )}
      </button>

      {/* Audio Controls */}
      {showControls && voice.audioUrl && (
        <div className="flex items-center gap-1">
          {voice.isSpeaking ? (
            <button
              onClick={voice.pause}
              className="w-6 h-6 bg-yellow-500 hover:bg-yellow-600 text-white rounded-full flex items-center justify-center"
              title="Pause"
            >
              <Pause size={12} />
            </button>
          ) : (
            <button
              onClick={voice.resume}
              className="w-6 h-6 bg-green-500 hover:bg-green-600 text-white rounded-full flex items-center justify-center"
              title="Resume"
            >
              <Play size={12} />
            </button>
          )}
          
          <button
            onClick={voice.stop}
            className="w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center"
            title="Stop"
          >
            <Square size={12} />
          </button>
        </div>
      )}
    </div>
  );
};

/**
 * Audio File Upload Component
 */
export const AudioFileUpload = ({ 
  onTranscript, 
  className = '',
  acceptedFormats = ['wav', 'mp3', 'ogg', 'webm', 'm4a'],
  maxSize = 25 * 1024 * 1024, // 25MB
  language = 'en-US'
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef(null);
  const voice = useVoiceInteraction({ language });

  const handleFileUpload = async (file) => {
    if (!file) return;

    // Validate file type
    const fileExt = file.name.split('.').pop()?.toLowerCase();
    if (!acceptedFormats.includes(fileExt)) {
      toast.error(`Unsupported file format. Accepted: ${acceptedFormats.join(', ')}`);
      return;
    }

    // Validate file size
    if (file.size > maxSize) {
      toast.error(`File too large. Maximum size: ${Math.round(maxSize / 1024 / 1024)}MB`);
      return;
    }

    setIsProcessing(true);
    try {
      const result = await voice.processAudioFile(file);
      if (onTranscript) {
        onTranscript(result.text, result);
      }
      toast.success('Audio processed successfully');
    } catch (error) {
      toast.error(`Failed to process audio: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  return (
    <div className={`audio-upload-container ${className}`}>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all duration-200
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}
          ${isProcessing ? 'opacity-50 pointer-events-none' : 'hover:border-blue-400 hover:bg-gray-50'}
        `}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedFormats.map(f => `.${f}`).join(',')}
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <div className="flex flex-col items-center gap-3">
          {isProcessing ? (
            <Loader className="w-8 h-8 text-blue-500 animate-spin" />
          ) : (
            <Upload className="w-8 h-8 text-gray-400" />
          )}
          
          <div>
            <p className="text-sm font-medium text-gray-700">
              {isProcessing ? 'Processing audio...' : 'Upload audio file'}
            </p>
            <p className="text-xs text-gray-500">
              {isProcessing ? 'Please wait' : `Drag & drop or click to select (${acceptedFormats.join(', ')}, max ${Math.round(maxSize / 1024 / 1024)}MB)`}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Voice Settings Panel Component
 */
export const VoiceSettingsPanel = ({ 
  onSettingsChange,
  className = '',
  showProviders = true,
  showVoiceProfiles = true,
  showLanguages = true 
}) => {
  const voice = useVoiceInteraction();
  const [settings, setSettings] = useState({
    language: 'en-US',
    provider: null,
    voiceProfile: null,
    speechRate: 1.0,
    volume: 1.0
  });

  useEffect(() => {
    if (onSettingsChange) {
      onSettingsChange(settings);
    }
  }, [settings, onSettingsChange]);

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  if (!voice.isInitialized) {
    return (
      <div className={`voice-settings-loading ${className}`}>
        <Loader className="w-6 h-6 animate-spin" />
        <span>Loading voice settings...</span>
      </div>
    );
  }

  return (
    <div className={`voice-settings-panel ${className} space-y-4`}>
      <div className="flex items-center gap-2 mb-4">
        <Settings className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Voice Settings</h3>
      </div>

      {/* Language Selection */}
      {showLanguages && voice.config?.supported_languages && (
        <div className="setting-group">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Language
          </label>
          <select
            value={settings.language}
            onChange={(e) => updateSetting('language', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {voice.config.supported_languages.map(lang => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Provider Selection */}
      {showProviders && voice.config?.available_providers && (
        <div className="setting-group">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Speech Provider
          </label>
          <select
            value={settings.provider || ''}
            onChange={(e) => updateSetting('provider', e.target.value || null)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Auto-select</option>
            {voice.config.available_providers.map(provider => (
              <option key={provider} value={provider}>
                {provider.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Voice Profile Selection */}
      {showVoiceProfiles && voice.voiceProfiles && (
        <div className="setting-group">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Voice Profile
          </label>
          <select
            value={settings.voiceProfile || ''}
            onChange={(e) => updateSetting('voiceProfile', e.target.value || null)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Default</option>
            {voice.voiceProfiles.map(profile => (
              <option key={profile.voice_id} value={profile.voice_id}>
                {profile.name} ({profile.gender}, {profile.provider})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Speech Rate */}
      <div className="setting-group">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Speech Rate: {settings.speechRate.toFixed(1)}x
        </label>
        <input
          type="range"
          min="0.5"
          max="2.0"
          step="0.1"
          value={settings.speechRate}
          onChange={(e) => updateSetting('speechRate', parseFloat(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Volume */}
      <div className="setting-group">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Volume: {Math.round(settings.volume * 100)}%
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={settings.volume}
          onChange={(e) => updateSetting('volume', parseFloat(e.target.value))}
          className="w-full"
        />
      </div>
    </div>
  );
};

/**
 * Voice-Enhanced AI Chat Component
 */
export const VoiceEnabledAIChat = ({ 
  onMessage, 
  messages = [],
  className = '',
  enableVoiceInput = true,
  enableVoiceOutput = true,
  autoSpeak = false 
}) => {
  const [inputText, setInputText] = useState('');
  const voice = useVoiceInteraction({
    onResult: (result) => {
      setInputText(result.text);
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && onMessage) {
      onMessage(inputText.trim());
      setInputText('');
    }
  };

  const handleVoiceTranscript = (transcript) => {
    setInputText(transcript);
  };

  return (
    <div className={`voice-ai-chat ${className}`}>
      {/* Messages */}
      <div className="messages-container space-y-4 mb-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`
                message-bubble max-w-xs lg:max-w-md px-4 py-2 rounded-lg
                ${message.isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}
              `}
            >
              <p>{message.text}</p>
              
              {/* TTS Button for AI messages */}
              {!message.isUser && enableVoiceOutput && (
                <div className="mt-2 flex justify-end">
                  <TextToSpeechButton
                    text={message.text}
                    size="sm"
                    showControls={false}
                    autoPlay={autoSpeak && index === messages.length - 1}
                  />
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="flex items-center gap-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message or use voice input..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            
            {/* Voice Input Button */}
            {enableVoiceInput && (
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                <VoiceInputButton
                  onTranscript={handleVoiceTranscript}
                  size="sm"
                  showTranscript={false}
                />
              </div>
            )}
          </div>
          
          <button
            type="submit"
            disabled={!inputText.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export {
  VoiceInputButton,
  TextToSpeechButton,
  AudioFileUpload,
  VoiceSettingsPanel,
  VoiceEnabledAIChat
};
