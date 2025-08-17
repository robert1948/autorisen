// client/src/components/CapeAIChat.jsx
import React, { useState, useRef, useEffect } from 'react';
import useCapeAISafe from '../hooks/useCapeAISafe';

export function CapeAIChat({ isOpen = false, onClose }) {
  // ✅ Always call ALL hooks at the top level unconditionally
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  
  // ✅ Hook call is now completely unconditional
  const capeAIData = useCapeAISafe();
  
  // ✅ useEffect must also be at the top level
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [capeAIData?.messages]);
  
  // Don't render if not open
  if (!isOpen) {
    return null;
  }
  
  // Safe fallback if context is not available
  if (!capeAIData) {
    return null;
  }
  
  const { messages = [], sendMessage, isLoading } = capeAIData;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    try {
      await sendMessage(userMessage);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  // Initial welcome message if no messages exist
  const welcomeMessage = "Hello! I'm CapeAI, ready to help you.";
  const displayMessages = messages.length === 0 
    ? [{ id: 'welcome', text: welcomeMessage, from: 'assistant' }]
    : messages;

  return (
    <div 
      className="fixed bottom-6 right-6 w-96 h-[500px] bg-white border border-gray-200 rounded-lg shadow-xl flex flex-col z-50"
      role="dialog"
      aria-labelledby="capeai-title"
      aria-describedby="capeai-description"
    >
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="text-xl">🤖</span>
          <div>
            <h3 id="capeai-title" className="font-semibold">CapeAI Assistant</h3>
            <p id="capeai-description" className="text-xs opacity-90">Your AI-powered assistant</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-200 text-xl"
          aria-label="Close chat"
        >
          ×
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {displayMessages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.from === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.from === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="text-sm">{message.text}</p>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 p-3 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask me anything..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

export default CapeAIChat;
