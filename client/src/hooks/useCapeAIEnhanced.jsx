// Enhanced CapeAI Hook with Real AI Integration
import { useState, useEffect, useCallback, useRef } from 'react';
import { useLocation } from 'react-router-dom';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export function useCapeAIEnhanced() {
  const [isVisible, setIsVisible] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [contextualSuggestions, setContextualSuggestions] = useState([]);
  const [availableActions, setAvailableActions] = useState([]);
  const [error, setError] = useState(null);
  
  const location = useLocation();
  const abortControllerRef = useRef(null);
  
  // Initialize session and load conversation history
  useEffect(() => {
    initializeSession();
    loadContextualSuggestions();
  }, [location.pathname]);
  
  const initializeSession = useCallback(async () => {
    // Generate new session ID if none exists
    if (!sessionId) {
      const newSessionId = generateSessionId();
      setSessionId(newSessionId);
      
      // Load existing conversation if available
      try {
        await loadConversationHistory(newSessionId);
      } catch (error) {
        console.warn('Could not load conversation history:', error);
      }
    }
  }, [sessionId]);
  
  const generateSessionId = () => {
    return `cape_ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };
  
  const loadConversationHistory = async (sessionId) => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE}/ai/conversation/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const formattedMessages = data.messages.map(msg => ({
          id: `${msg.timestamp}_${msg.type}`,
          type: msg.type,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          suggestions: msg.suggestions || [],
          actions: msg.actions || []
        }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error('Error loading conversation history:', error);
    }
  };
  
  const loadContextualSuggestions = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE}/ai/suggestions?current_path=${encodeURIComponent(location.pathname)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setContextualSuggestions(data.suggestions || []);
        setAvailableActions(data.actions || []);
      }
    } catch (error) {
      console.warn('Could not load contextual suggestions:', error);
    }
  };
  
  const sendMessage = useCallback(async (message, context = {}) => {
    if (!message.trim() || isLoading) return;
    
    setIsLoading(true);
    setError(null);
    
    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    
    // Add user message immediately
    const userMessage = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const token = localStorage.getItem('authToken');
      const requestBody = {
        message: message,
        context: {
          ...context,
          currentPath: location.pathname,
          timestamp: new Date().toISOString(),
          sessionId: sessionId
        },
        session_id: sessionId
      };
      
      const response = await fetch(`${API_BASE}/ai/prompt`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody),
        signal: abortControllerRef.current.signal
      });
      
      if (!response.ok) {
        throw new Error(`AI service error: ${response.status}`);
      }
      
      const aiResponse = await response.json();
      
      // Add AI response
      const assistantMessage = {
        id: `assistant_${Date.now()}`,
        type: 'assistant',
        content: aiResponse.response,
        timestamp: new Date(),
        suggestions: aiResponse.suggestions || [],
        actions: aiResponse.actions || []
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update contextual suggestions if provided
      if (aiResponse.suggestions) {
        setContextualSuggestions(aiResponse.suggestions);
      }
      if (aiResponse.actions) {
        setAvailableActions(aiResponse.actions);
      }
      
    } catch (error) {
      if (error.name === 'AbortError') {
        return; // Request was cancelled
      }
      
      console.error('Error sending message to AI:', error);
      setError('Sorry, I encountered an error. Please try again.');
      
      // Add error message
      const errorMessage = {
        id: `error_${Date.now()}`,
        type: 'assistant',
        content: 'I apologize, but I\'m having trouble connecting right now. Please try again in a moment.',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [isLoading, sessionId, location.pathname]);
  
  const executeAction = useCallback(async (action) => {
    if (action.action.startsWith('/')) {
      // Navigate to URL
      window.location.href = action.action;
    } else if (action.action === 'start_onboarding') {
      // Trigger onboarding
      setMessages(prev => [...prev, {
        id: `system_${Date.now()}`,
        type: 'assistant',
        content: 'Let me guide you through CapeControl! I\'ll walk you through the key features step by step.',
        timestamp: new Date()
      }]);
      // You can integrate with your onboarding system here
    } else if (action.action === 'show_agent_modal') {
      // Trigger agent selection modal
      console.log('Opening agent selection modal...');
      // You can dispatch an event or call a function to open the modal
    } else {
      // Custom action handler
      console.log('Executing custom action:', action);
    }
  }, []);
  
  const clearConversation = useCallback(async () => {
    try {
      const token = localStorage.getItem('authToken');
      await fetch(`${API_BASE}/ai/conversation/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      setMessages([]);
      setError(null);
      
    } catch (error) {
      console.error('Error clearing conversation:', error);
    }
  }, [sessionId]);
  
  const toggleVisibility = useCallback(() => {
    setIsVisible(prev => !prev);
    setError(null);
  }, []);
  
  // Smart suggestions based on current context
  const getSmartSuggestions = useCallback(() => {
    const currentPath = location.pathname;
    
    // Combine contextual suggestions with path-specific ones
    const pathSuggestions = {
      '/': ['How do I get started?', 'What can CapeControl do?', 'Show me the dashboard'],
      '/dashboard': ['Explain my metrics', 'How can I optimize costs?', 'Recommend AI agents'],
      '/agents': ['Which agent is best for me?', 'How do I install an agent?', 'Compare agent features'],
      '/profile': ['How do I update my settings?', 'Explain billing options', 'How do I manage notifications?']
    };
    
    const pathSpecific = pathSuggestions[currentPath] || [];
    return [...contextualSuggestions, ...pathSpecific].slice(0, 4);
  }, [location.pathname, contextualSuggestions]);
  
  // Welcome message for new sessions
  useEffect(() => {
    if (messages.length === 0 && sessionId) {
      const welcomeMessage = {
        id: `welcome_${Date.now()}`,
        type: 'assistant',
        content: '👋 Hi! I\'m CapeAI, your intelligent assistant. I\'m here to help you navigate CapeControl and make the most of our AI agents platform. What would you like to know?',
        timestamp: new Date(),
        suggestions: getSmartSuggestions(),
        actions: availableActions
      };
      setMessages([welcomeMessage]);
    }
  }, [sessionId]); // Only run when sessionId changes
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);
  
  return {
    // State
    isVisible,
    messages,
    isLoading,
    error,
    sessionId,
    contextualSuggestions,
    availableActions,
    
    // Actions
    sendMessage,
    toggleVisibility,
    executeAction,
    clearConversation,
    loadContextualSuggestions,
    
    // Computed
    smartSuggestions: getSmartSuggestions(),
    hasConversation: messages.length > 0,
    isInitialized: sessionId !== null,
    
    // Utils
    generateSessionId
  };
}
