import { useState, useEffect } from 'react';
import { MessageCircle, X, Minimize2, Maximize2 } from 'lucide-react';
import useCapeAISafe from '../hooks/useCapeAISafe';

export default function CapeAIFloatingButton() {
  // ✅ Always call ALL hooks at the top level unconditionally
  const [position, setPosition] = useState({ x: 20, y: 20 });
  const [isDragging, setIsDragging] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // ✅ Hook call is now completely unconditional
  const capeAIData = useCapeAISafe();
  
  // ✅ useEffect must also be at the top level
  useEffect(() => {
    const updatePosition = () => {
      const screenWidth = window.innerWidth;
      const screenHeight = window.innerHeight;
      
      // Smart positioning: bottom-right for desktop, bottom-center for mobile
      if (screenWidth < 768) {
        setPosition({ x: screenWidth / 2 - 30, y: screenHeight - 100 });
      } else {
        setPosition({ x: 20, y: screenHeight - 100 });
      }
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    return () => window.removeEventListener('resize', updatePosition);
  }, []);
  
  // Safe fallback if context is not available
  if (!capeAIData) {
    return null;
  }
  
  const { isVisible, toggleVisibility, messages, isInitialized, sendMessage } = capeAIData;

  // Don't render if not initialized to prevent errors
  if (!isInitialized) {
    return null;
  }

  // Calculate if there are unread messages (simple logic for now)
  const hasUnreadMessages = messages && messages.length > 1; // More than initial message

  const handleMouseDown = (e) => {
    setIsDragging(true);
    const startX = e.clientX - position.x;
    const startY = e.clientY - position.y;

    const handleMouseMove = (e) => {
      const newX = Math.max(0, Math.min(window.innerWidth - 60, e.clientX - startX));
      const newY = Math.max(0, Math.min(window.innerHeight - 60, e.clientY - startY));
      setPosition({ x: newX, y: newY });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const getContextualMessage = () => {
    const path = window.location.pathname;
    const contextMessages = {
      '/dashboard': 'Need help with your dashboard?',
      '/profile': 'Setting up your profile?',
      '/agents': 'Questions about AI agents?',
      '/settings': 'Need help with settings?',
      '/': 'Welcome! How can I help you get started?'
    };
    return contextMessages[path] || 'Hi! How can I help you today?';
  };

  // Accept optional text to send immediately (used by quick actions)
  const handleSendMessage = async (textOverride) => {
    const textToSend = (textOverride ?? inputMessage).trim();
    if (!textToSend || isLoading) return;
    
    setIsLoading(true);
    try {
      await sendMessage(textToSend);
      // Clear input only if it was typed in input
      if (!textOverride) setInputMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const pulseAnimation = hasUnreadMessages ? 'animate-pulse' : '';
  const notificationDot = hasUnreadMessages ? (
    <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-bounce"></div>
  ) : null;

  if (isMinimized) {
    return (
      <div
        className="fixed z-50 cursor-pointer"
        style={{ left: position.x, bottom: 20 }}
        onClick={() => setIsMinimized(false)}
      >
        <div className="bg-blue-600 text-white p-2 rounded-full shadow-lg hover:bg-blue-700 transition-colors">
          <Maximize2 size={16} />
          {notificationDot}
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Floating Button */}
      <div
        className={`fixed z-50 ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
        style={{ left: position.x, bottom: position.y }}
        onMouseDown={handleMouseDown}
      >
        <div className="relative">
          {/* Main Button */}
          <button
            onClick={toggleVisibility}
            className={`bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-all duration-300 ${pulseAnimation}`}
            onMouseDown={(e) => e.stopPropagation()}
          >
            {isVisible ? <X size={24} /> : <MessageCircle size={24} />}
            {notificationDot}
          </button>

          {/* Minimize Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsMinimized(true);
            }}
            className="absolute -top-2 -right-2 bg-gray-600 text-white p-1 rounded-full opacity-0 hover:opacity-100 transition-opacity"
            onMouseDown={(e) => e.stopPropagation()}
          >
            <Minimize2 size={12} />
          </button>

          {/* Contextual Tooltip */}
          {!isVisible && !isDragging && (
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded-lg whitespace-nowrap opacity-0 hover:opacity-100 transition-opacity pointer-events-none">
              {getContextualMessage()}
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
            </div>
          )}
        </div>
      </div>

      {/* Chat Window */}
      {isVisible && (
        <div
          className="fixed z-40 bg-white rounded-lg shadow-2xl border"
          style={{
            left: Math.min(position.x, window.innerWidth - 380),
            bottom: position.y + 80,
            width: '360px',
            height: '500px',
            maxHeight: '80vh'
          }}
        >
          {/* Chat Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                🤖
              </div>
              <div>
                <h3 className="font-semibold">CapeAI Assistant</h3>
                <p className="text-xs opacity-90">Always here to help</p>
              </div>
            </div>
            <button
              onClick={toggleVisibility}
              className="text-white hover:bg-blue-700 p-1 rounded"
            >
              <X size={18} />
            </button>
          </div>

          {/* Chat Content Area */}
          <div className="h-96 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">👋</div>
                <h4 className="font-semibold text-gray-800 mb-2">Welcome to CapeAI!</h4>
                <p className="text-sm text-gray-600 mb-4">{getContextualMessage()}</p>
                
                {/* Quick Action Buttons */}
                <div className="space-y-2">
                  <button 
                    onClick={() => handleSendMessage('Show me around the platform')}
                    className="w-full bg-blue-50 text-blue-700 p-2 rounded-lg text-sm hover:bg-blue-100 transition-colors"
                    disabled={isLoading}
                  >
                    💡 Show me around the platform
                  </button>
                  <button 
                    onClick={() => handleSendMessage('Help me get started')}
                    className="w-full bg-green-50 text-green-700 p-2 rounded-lg text-sm hover:bg-green-100 transition-colors"
                    disabled={isLoading}
                  >
                    🚀 Help me get started
                  </button>
                  <button 
                    onClick={() => handleSendMessage('I have a specific question')}
                    className="w-full bg-purple-50 text-purple-700 p-2 rounded-lg text-sm hover:bg-purple-100 transition-colors"
                    disabled={isLoading}
                  >
                    ❓ I have a specific question
                  </button>
                </div>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={msg.id || index}
                  className={`flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs p-3 rounded-lg ${
                      msg.from === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-line">{msg.text}</p>
                    <p className="text-xs opacity-75 mt-1">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Input Area */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Type your message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 disabled:opacity-50"
              />
              <button 
                onClick={() => handleSendMessage()}
                disabled={isLoading || !inputMessage.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? '...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
