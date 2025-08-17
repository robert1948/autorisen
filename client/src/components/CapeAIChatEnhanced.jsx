// Enhanced CapeAI Chat Component with Real AI Integration
import React, { useState, useRef, useEffect } from 'react';
import { useCapeAIEnhanced } from '../hooks/useCapeAIEnhanced';

const CapeAIChatEnhanced = () => {
  const [inputMessage, setInputMessage] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  const {
    isVisible,
    messages,
    isLoading,
    error,
    smartSuggestions,
    availableActions,
    sendMessage,
    toggleVisibility,
    executeAction,
    clearConversation,
    hasConversation
  } = useCapeAIEnhanced();
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;
    
    const message = inputMessage.trim();
    setInputMessage('');
    
    await sendMessage(message, {
      source: 'chat_input',
      userAgent: navigator.userAgent,
      screenWidth: window.innerWidth
    });
  };
  
  const handleSuggestionClick = async (suggestion) => {
    await sendMessage(suggestion, {
      source: 'suggestion_click',
      suggestion: suggestion
    });
  };
  
  const handleActionClick = (action) => {
    executeAction(action);
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };
  
  const formatMessageContent = (content) => {
    // Simple formatting for better readability
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>');
  };
  
  // Don't render if not visible
  if (!isVisible) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={toggleVisibility}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full w-14 h-14 shadow-lg transition-all duration-300 flex items-center justify-center group hover:scale-110"
          aria-label="Open CapeAI Assistant"
        >
          <span className="text-2xl">🤖</span>
          <div className="absolute bottom-full right-0 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <div className="bg-gray-900 text-white text-sm px-3 py-1 rounded-lg whitespace-nowrap">
              Ask CapeAI
            </div>
          </div>
        </button>
      </div>
    );
  }
  
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div className={`bg-white rounded-lg shadow-2xl border transition-all duration-300 ${
        isMinimized ? 'w-80 h-16' : 'w-96 h-[600px]'
      } max-w-[calc(100vw-3rem)] max-h-[calc(100vh-3rem)]`}>
        
        {/* Header */}
        <div className="bg-blue-600 text-white px-4 py-3 rounded-t-lg flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xl">🤖</span>
            <div>
              <h3 className="font-semibold text-sm">CapeAI Assistant</h3>
              <p className="text-blue-100 text-xs">
                {isLoading ? 'Thinking...' : 'Ready to help'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="text-blue-100 hover:text-white transition-colors"
              aria-label={isMinimized ? 'Expand chat' : 'Minimize chat'}
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d={isMinimized 
                  ? "M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" 
                  : "M4 6a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H6a2 2 0 01-2-2V6z"
                } clipRule="evenodd" />
              </svg>
            </button>
            
            <button
              onClick={toggleVisibility}
              className="text-blue-100 hover:text-white transition-colors"
              aria-label="Close chat"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
        
        {/* Chat Content - Hidden when minimized */}
        {!isMinimized && (
          <>
            {/* Messages Area */}
            <div className="flex-1 h-96 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <div className="flex items-center">
                    <span className="text-red-600 mr-2">⚠️</span>
                    <p className="text-red-800 text-sm">{error}</p>
                  </div>
                </div>
              )}
              
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.type === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : message.isError
                        ? 'bg-red-50 border border-red-200 text-red-800'
                        : 'bg-white border shadow-sm'
                  }`}>
                    <div 
                      className="text-sm"
                      dangerouslySetInnerHTML={{ 
                        __html: formatMessageContent(message.content) 
                      }}
                    />
                    
                    {/* Message Actions */}
                    {message.actions && message.actions.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {message.actions.map((action, index) => (
                          <button
                            key={index}
                            onClick={() => handleActionClick(action)}
                            className="block w-full text-left bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-2 rounded text-xs transition-colors"
                          >
                            {action.text}
                          </button>
                        ))}
                      </div>
                    )}
                    
                    <div className="text-xs opacity-60 mt-1">
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white border shadow-sm rounded-lg px-4 py-2 max-w-[80%]">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-sm text-gray-500">CapeAI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
            
            {/* Suggestions */}
            {smartSuggestions.length > 0 && (
              <div className="px-4 py-2 border-t bg-gray-50">
                <div className="flex flex-wrap gap-2">
                  {smartSuggestions.slice(0, 3).map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      disabled={isLoading}
                      className="text-xs bg-white hover:bg-gray-100 border text-gray-700 px-3 py-1 rounded-full transition-colors disabled:opacity-50"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Input Area */}
            <div className="p-4 border-t bg-white rounded-b-lg">
              <form onSubmit={handleSendMessage} className="flex space-x-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask CapeAI anything..."
                  disabled={isLoading}
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                />
                
                <button
                  type="submit"
                  disabled={isLoading || !inputMessage.trim()}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center justify-center min-w-[44px]"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              </form>
              
              {/* Utility Actions */}
              {hasConversation && (
                <div className="mt-2 flex justify-between items-center">
                  <button
                    onClick={clearConversation}
                    className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    Clear conversation
                  </button>
                  
                  <div className="text-xs text-gray-400">
                    Press Enter to send • Shift+Enter for new line
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CapeAIChatEnhanced;
