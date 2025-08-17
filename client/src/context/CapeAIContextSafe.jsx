import { createContext, useState, useCallback, useEffect } from 'react';

// Create context with safer initialization
export const CapeAIContext = createContext({
  isVisible: false,
  messages: [],
  onboardingStep: 0,
  onboardingData: {
    profileComplete: false,
    featuresViewed: false,
    aiIntroduced: false,
    dashboardTour: false,
    firstAgentLaunched: false,
  },
  toggleVisibility: () => {},
  addMessage: () => {},
  sendMessage: () => {},
  setOnboardingStep: () => {},
  updateOnboardingData: () => {},
  isInitialized: false,
});

export const CapeAIProvider = ({ children }) => {
  // Initialize state more safely
  const [isInitialized, setIsInitialized] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [onboardingStep, setOnboardingStep] = useState(0);
  const [onboardingData, setOnboardingData] = useState({
    profileComplete: false,
    featuresViewed: false,
    aiIntroduced: false,
    dashboardTour: false,
    firstAgentLaunched: false,
  });
  
  const [messages, setMessages] = useState([]);

  // Safe initialization after mount
  useEffect(() => {
    try {
      setMessages([
        { 
          id: `initial-${Date.now()}`,
          from: 'assistant', 
          text: 'Hi! I\'m CapeAI, your personal onboarding assistant. I\'m here to help you get the most out of the CapeControl platform. What would you like to explore first?',
          timestamp: new Date()
        }
      ]);
      setIsInitialized(true);
    } catch (error) {
      console.warn('CapeAI initialization error:', error);
    }
  }, []);

  const toggleVisibility = useCallback(() => {
    if (isInitialized) {
      setIsVisible((prev) => !prev);
    }
  }, [isInitialized]);

  const addMessage = useCallback((from, text) => {
    if (!isInitialized) return;
    
    try {
      const newMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        from,
        text,
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, newMessage]);
    } catch (error) {
      console.warn('Error adding message:', error);
    }
  }, [isInitialized]);

  const sendMessage = useCallback(async (userMessage) => {
    if (!isInitialized) return;
    
    try {
      // Add user message immediately
      addMessage('user', userMessage);
      
      // Get current path for context
      const currentPath = window.location.pathname;
      
      // Send to CapeAI backend
      const response = await fetch('/api/cape_ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          context: {
            path: currentPath,
            timestamp: new Date().toISOString()
          }
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        // Add AI response
        addMessage('assistant', data.response);
      } else {
        // Fallback response for errors
        addMessage('assistant', "I apologize, but I'm having trouble connecting right now. Please try again or check the console for more details.");
      }
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage('assistant', "I'm experiencing some technical difficulties. Please try again in a moment.");
    }
  }, [isInitialized, addMessage]);

  const updateOnboardingData = useCallback((updates) => {
    if (!isInitialized) return;
    
    try {
      setOnboardingData((prev) => ({ ...prev, ...updates }));
    } catch (error) {
      console.warn('Error updating onboarding data:', error);
    }
  }, [isInitialized]);

  // Don't provide context until initialized
  const contextValue = {
    isVisible,
    messages,
    onboardingStep,
    onboardingData,
    toggleVisibility,
    addMessage,
    sendMessage,
    setOnboardingStep,
    updateOnboardingData,
    isInitialized,
  };

  return (
    <CapeAIContext.Provider value={contextValue}>
      {children}
    </CapeAIContext.Provider>
  );
};

export default CapeAIProvider;
